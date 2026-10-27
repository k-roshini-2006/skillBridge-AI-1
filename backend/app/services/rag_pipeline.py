import re
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.core.config import settings
from app.models.models import StudyMaterial, Topic, Course

class RAGPipeline:
    def __init__(self):
        self._vectorizers: Dict[str, TfidfVectorizer] = {}
        self._matrices: Dict[str, any] = {}
        self._documents: Dict[str, List[dict]] = {}
        self._initialized: bool = False

    def build_index(self, db: Session, course_id: Optional[str] = None):
        """Indexes study materials from the database into a searchable vector space."""
        query = db.query(StudyMaterial).join(Topic, Topic.id == StudyMaterial.topic_id)
        if course_id:
            query = query.filter(Topic.course_id == course_id)
        materials = query.all()

        docs_by_course: Dict[str, List[dict]] = {}
        for m in materials:
            c_id = m.topic.course_id
            if c_id not in docs_by_course:
                docs_by_course[c_id] = []
            
            # Form clean text chunk combining title, topic name and content
            chunk_text = f"Topic: {m.topic.name}. Title: {m.title}. Content: {m.content or ''}"
            docs_by_course[c_id].append({
                "id": m.id,
                "course_id": c_id,
                "topic_id": m.topic_id,
                "topic_name": m.topic.name,
                "title": m.title,
                "type": m.type,
                "url": m.url,
                "source": m.source or "SkillPath AI Core Curriculum",
                "content": m.content or "",
                "search_text": chunk_text
            })

        for c_id, doc_list in docs_by_course.items():
            corpus = [d["search_text"] for d in doc_list]
            if not corpus:
                continue
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000,
                sublinear_tf=True
            )
            matrix = vectorizer.fit_transform(corpus)
            self._vectorizers[c_id] = vectorizer
            self._matrices[c_id] = matrix
            self._documents[c_id] = doc_list

        self._initialized = True

    def retrieve(self, db: Session, query: str, course_id: Optional[str] = None, top_k: int = 3) -> Tuple[List[dict], float]:
        """
        Retrieves top-k relevant study material chunks matching the query.
        Returns (ranked_chunks, top_similarity_score).
        """
        # Always ensure index is built for current materials
        if not self._initialized or (course_id and course_id not in self._vectorizers):
            self.build_index(db, course_id)

        target_courses = [course_id] if course_id and course_id in self._vectorizers else list(self._vectorizers.keys())
        if not target_courses:
            # Fallback if no course is selected or indexed yet
            self.build_index(db)
            target_courses = list(self._vectorizers.keys())

        all_matches = []
        for c_id in target_courses:
            vec = self._vectorizers.get(c_id)
            mat = self._matrices.get(c_id)
            docs = self._documents.get(c_id, [])
            if not vec or mat is None or not docs:
                continue

            q_vec = vec.transform([query])
            sims = cosine_similarity(q_vec, mat).flatten()
            for doc, score in zip(docs, sims):
                if score > 0.05:  # Relevance threshold
                    all_matches.append({**doc, "score": float(score)})

        all_matches.sort(key=lambda x: x["score"], reverse=True)
        top_chunks = all_matches[:top_k]
        top_score = top_chunks[0]["score"] if top_chunks else 0.0
        return top_chunks, top_score

    async def answer_query(self, db: Session, query: str, course_id: Optional[str] = None, language: str = "english") -> dict:
        """
        Generates grounded RAG response strictly adhering to course materials.
        Mitigates hallucinations by verifying retrieval confidence.
        """
        chunks, top_score = self.retrieve(db, query, course_id, top_k=3)

        # Hallucination Guardrail: low relevance score
        if not chunks or top_score < 0.12:
            return {
                "response": (
                    f"⚠️ **Grounding Guardrail:** I could not locate direct coverage of '{query}' in the current verified course materials.\n\n"
                    "SkillPath AI strictly limits responses to your enrolled syllabus to prevent AI hallucinations. "
                    "Please ask a question related to your active topics (e.g., Arrays, Linked Lists, Stacks, Queues, Trees, Graphs)."
                ),
                "sources": [],
                "confidence": round(top_score, 2),
                "grounded": False
            }

        # Format context from retrieved chunks
        context_blocks = []
        source_names = []
        for i, c in enumerate(chunks, 1):
            source_names.append(f"{c['topic_name']} — {c['title']} ({c['type'].capitalize()})")
            context_blocks.append(f"[Source {i}: {c['topic_name']} - {c['title']}]\n{c['content']}")

        combined_context = "\n\n".join(context_blocks)

        # If LLM API is configured, call external model (e.g., Qwen 2.5)
        if settings.LLM_API_URL and settings.LLM_API_KEY:
            try:
                import httpx
                lang_instruction = "Respond in English." if language.lower() == "english" else f"Respond in {language}."
                system_prompt = (
                    "You are SkillPath AI, an expert adaptive educational tutor. "
                    "Answer the student's question accurately and pedagogically. "
                    "CRITICAL: Answer ONLY based on the provided course context. "
                    "Do NOT extrapolate or invent facts not present in the context. "
                    "Cite sources clearly using Markdown formatting."
                )
                user_prompt = (
                    f"Context:\n{combined_context}\n\n"
                    f"Student Question: {query}\n"
                    f"Language: {lang_instruction}"
                )
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.post(
                        settings.LLM_API_URL,
                        headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                        json={
                            "model": "qwen2.5-3b-instruct",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "max_tokens": 800,
                            "temperature": 0.3
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        llm_text = data["choices"][0]["message"]["content"]
                        return {
                            "response": llm_text,
                            "sources": list(dict.fromkeys(source_names)),
                            "confidence": round(min(1.0, top_score * 1.5), 2),
                            "grounded": True
                        }
            except Exception as e:
                # Fallback to local grounded synthesizer
                pass

        # Native Grounded Pedagogical Synthesizer (Zero-hallucination offline mode)
        primary_chunk = chunks[0]
        secondary_chunk = chunks[1] if len(chunks) > 1 else None

        topic = primary_chunk["topic_name"]
        title = primary_chunk["title"]
        raw_content = primary_chunk["content"]

        # Parse key points and concepts from raw_content
        lines = [line.strip() for line in raw_content.split("\n") if line.strip()]
        summary_points = []
        for line in lines:
            if line.startswith(("-", "*", "•", "1.", "2.", "3.", "4.")):
                summary_points.append(line)
            elif len(line) > 30 and not line.endswith(":"):
                summary_points.append(f"• {line}")

        if not summary_points:
            summary_points = [f"• {p.strip()}." for p in raw_content.split(". ") if len(p.strip()) > 10][:4]

        formatted_points = "\n".join(summary_points[:6])

        # Multilingual handling for Hindi / Hinglish if selected
        is_hindi = "hindi" in language.lower() or "hinglish" in language.lower()
        if is_hindi:
            response_text = (
                f"### 📘 {topic}: {title} (Course Material Grounded)\n\n"
                f"Aapke course curriculum ke aadhar par **{query}** ka mukhya vivaran:\n\n"
                f"{formatted_points}\n\n"
                f"💡 **Key Takeaway:** {topic} me yeh concepts memory organization aur time complexity ke liye mahatvapurna hain. "
                f"Isko practice karne ke liye aap Weak-Topic Quiz ya Mastery Gate attempt kar sakte hain!"
            )
        else:
            response_text = (
                f"### 📘 {topic}: {title}\n\n"
                f"Based strictly on your verified course study materials, here is the breakdown regarding **{query}**:\n\n"
                f"{formatted_points}\n\n"
            )
            if secondary_chunk:
                sec_points = [l.strip() for l in secondary_chunk["content"].split("\n") if l.strip()][:2]
                sec_snippet = " ".join(sec_points)
                response_text += f"**Additional Context ({secondary_chunk['title']}):**\n{sec_snippet}\n\n"

            response_text += (
                f"💡 **Exam & Concept Tip:** Master these points before attempting the {topic} Mastery Gate quiz! "
                f"Let me know if you would like me to generate a practice question on this concept."
            )

        return {
            "response": response_text,
            "sources": list(dict.fromkeys(source_names)),
            "confidence": round(min(1.0, 0.70 + top_score * 0.3), 2),
            "grounded": True
        }

# Global singleton instance
rag_pipeline = RAGPipeline()
