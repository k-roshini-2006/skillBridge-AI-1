import json
import random
from typing import List, Optional
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import (
    Assessment, AssessmentTypeEnum, Question, Topic, DifficultyEnum
)

TOPIC_QUESTION_TEMPLATES = {
    "Arrays": [
        {
            "question_text": "What happens under the hood when a dynamic array exceeds its capacity during an append operation?",
            "options": {"a": "A fixed block is allocated at the end without moving", "b": "A new array of double capacity is allocated, elements are copied over, and old array is freed", "c": "Elements are converted to a linked list", "d": "An out-of-memory exception is always thrown immediately"},
            "correct_answer": "b",
            "explanation": "Dynamic arrays perform geometric resizing (typically doubling), yielding amortized O(1) append time despite the O(n) reallocation copy.",
            "bloom_level": "Analyze",
            "learning_objective": "Analyze dynamic array geometric resizing mechanics"
        },
        {
            "question_text": "Given an array of size N, what is the best-case time complexity to check if it contains a duplicate without modifying or sorting it?",
            "options": {"a": "O(N) using a Hash Set", "b": "O(1)", "c": "O(N log N)", "d": "O(N^2)"},
            "correct_answer": "a",
            "explanation": "A hash set allows tracking previously seen elements with O(1) average lookup, achieving O(N) overall time and O(N) space.",
            "bloom_level": "Apply",
            "learning_objective": "Apply hashing to optimize array searches"
        },
        {
            "question_text": "In a two-pointer technique applied to a sorted array, moving the left pointer inward typically indicates what?",
            "options": {"a": "Current pair sum is too large", "b": "Current pair sum is too small", "c": "Array is not strictly sorted", "d": "Target value has been exceeded"},
            "correct_answer": "b",
            "explanation": "Since the array is sorted, incrementing the left pointer accesses a larger value, which increases the cumulative two-pointer sum towards the target.",
            "bloom_level": "Understand",
            "learning_objective": "Understand two-pointer convergence invariants"
        }
    ],
    "Linked List": [
        {
            "question_text": "Why is Floyd's Cycle-Finding Algorithm (Tortoise and Hare) guaranteed to detect a cycle in a linked list in O(N) time and O(1) space?",
            "options": {"a": "The fast pointer skips 3 nodes at a time", "b": "The distance between the two pointers decreases by 1 in each step inside the loop", "c": "It uses hash codes stored in pointers", "d": "It reverses the list until head is reached"},
            "correct_answer": "b",
            "explanation": "Because the fast pointer moves at 2 nodes/step and slow at 1 node/step, the relative distance between them closes by exactly 1 node per iteration inside any loop.",
            "bloom_level": "Analyze",
            "learning_objective": "Analyze fast and slow pointer convergence"
        },
        {
            "question_text": "What is the primary memory overhead drawback of a doubly linked list compared to a singly linked list?",
            "options": {"a": "Doubly linked lists cannot store integers", "b": "Each node requires an additional pointer (prev), increasing memory consumption per node", "c": "Traversal takes twice as much time", "d": "Garbage collection cannot reclaim doubly linked nodes"},
            "correct_answer": "b",
            "explanation": "Each node in a doubly linked list stores both next and previous pointers, doubling the pointer overhead per element.",
            "bloom_level": "Understand",
            "learning_objective": "Evaluate memory tradeoffs in doubly linked structures"
        }
    ],
    "Stack": [
        {
            "question_text": "Which classical problem is optimally solved in O(N) time using a Monotonic Decreasing Stack?",
            "options": {"a": "Finding the Next Greater Element for each position", "b": "Finding the shortest path in a weighted graph", "c": "Inverting a binary tree", "d": "Sorting an array in place"},
            "correct_answer": "a",
            "explanation": "A monotonic decreasing stack maintains elements in order and resolves the next greater element for each item as soon as a strictly greater item arrives.",
            "bloom_level": "Apply",
            "learning_objective": "Apply monotonic stack patterns to window and span problems"
        },
        {
            "question_text": "When evaluating an arithmetic expression written in postfix notation (Reverse Polish Notation), what is pushed onto the stack?",
            "options": {"a": "Operators", "b": "Operands and intermediate computation results", "c": "Parentheses only", "d": "Variables only"},
            "correct_answer": "b",
            "explanation": "Operands are pushed onto the stack. When an operator is encountered, the top two operands are popped, evaluated, and the result is pushed back.",
            "bloom_level": "Understand",
            "learning_objective": "Understand postfix evaluation via stack semantics"
        }
    ],
    "Queue": [
        {
            "question_text": "How does a Circular Queue distinguish between an empty queue and a completely full queue when implemented with a fixed array?",
            "options": {"a": "By using a separate boolean flag or keeping one array slot intentionally unused", "b": "It is impossible without reallocating memory", "c": "By setting all values to NULL", "d": "By counting array length on every check"},
            "correct_answer": "a",
            "explanation": "When front == rear, it could mean either empty or full. Standard implementations either track count explicitly or reserve one sentinel slot so that (rear + 1) % N == front denotes full.",
            "bloom_level": "Analyze",
            "learning_objective": "Analyze circular buffer pointer arithmetic and edge conditions"
        },
        {
            "question_text": "In a Priority Queue implemented with a Min-Heap, what is the time complexity to extract the minimum element?",
            "options": {"a": "O(1)", "b": "O(log N)", "c": "O(N)", "d": "O(N log N)"},
            "correct_answer": "b",
            "explanation": "Extracting the root is O(1), but restoring the min-heap invariant via sift-down (heapify) takes O(log N) time.",
            "bloom_level": "Apply",
            "learning_objective": "Apply heap invariants to priority queue operations"
        }
    ],
    "Trees": [
        {
            "question_text": "What is the time complexity of searching in an unbalanced degenerate binary search tree with N nodes?",
            "options": {"a": "O(1)", "b": "O(log N)", "c": "O(N)", "d": "O(N^2)"},
            "correct_answer": "c",
            "explanation": "In the worst case (e.g. inserting strictly sorted values), a BST degenerates into a linear linked list where search degrades to O(N).",
            "bloom_level": "Analyze",
            "learning_objective": "Differentiate balanced vs degenerate tree performance"
        },
        {
            "question_text": "Which tree traversal of a valid Binary Search Tree visits nodes in strictly ascending sorted order?",
            "options": {"a": "Pre-order (Root, Left, Right)", "b": "In-order (Left, Root, Right)", "c": "Post-order (Left, Right, Root)", "d": "Level-order (BFS)"},
            "correct_answer": "b",
            "explanation": "In-order traversal visits left subtree (all smaller keys), then the root key, then right subtree (all larger keys), producing an ordered sequence.",
            "bloom_level": "Understand",
            "learning_objective": "Understand BST in-order property"
        }
    ],
    "Graphs": [
        {
            "question_text": "Dijkstra's shortest path algorithm fails or produces incorrect answers in which scenario?",
            "options": {"a": "Directed acyclic graphs", "b": "Graphs containing negative-weight edges", "c": "Graphs with cycles", "d": "Disconnected components"},
            "correct_answer": "b",
            "explanation": "Dijkstra greedily assumes once a vertex distance is finalized, it cannot be shortened. Negative edges violate this greedy invariant. Bellman-Ford must be used instead.",
            "bloom_level": "Analyze",
            "learning_objective": "Analyze shortest path algorithm constraints and negative weights"
        },
        {
            "question_text": "Which algorithm is used to detect cycles in an undirected graph using disjoint-set data structures?",
            "options": {"a": "Union-Find", "b": "Floyd-Warshall", "c": "Prim's Algorithm", "d": "Topological Sort"},
            "correct_answer": "a",
            "explanation": "Union-Find detects a cycle in an undirected graph if both endpoints of an edge already belong to the same representative connected component.",
            "bloom_level": "Apply",
            "learning_objective": "Apply Union-Find disjoint sets to graph cycle detection"
        }
    ]
}


def _ensure_topic_questions(db: Session, topic: Topic, min_needed: int = 5):
    """Ensures at least min_needed questions exist in the DB for the given topic."""
    count = db.query(Question).filter(Question.topic_id == topic.id).count()
    if count >= min_needed:
        return

    templates = TOPIC_QUESTION_TEMPLATES.get(topic.name, [])
    for t in templates:
        existing = db.query(Question).filter(
            Question.topic_id == topic.id,
            Question.question_text == t["question_text"]
        ).first()
        if not existing:
            q = Question(
                topic_id=topic.id,
                difficulty=DifficultyEnum.medium,
                bloom_level=t.get("bloom_level", "Understand"),
                question_text=t["question_text"],
                options=t["options"],
                correct_answer=t["correct_answer"],
                explanation=t["explanation"],
                learning_objective=t["learning_objective"]
            )
            db.add(q)
    db.commit()


def build_weak_topic_assessment(db: Session, student_id: str, course_id: str,
                                 weak_topic_ids: List[str], questions_per_topic: int = 5) -> dict:
    """Stage 2: quiz built ONLY from weak topics."""
    assessment = Assessment(student_id=student_id, course_id=course_id,
                             type=AssessmentTypeEnum.weak_topic)
    db.add(assessment)
    db.flush()

    questions = []
    for topic_id in weak_topic_ids:
        topic = db.query(Topic).get(topic_id)
        if topic:
            _ensure_topic_questions(db, topic, min_needed=5)

        pool = (
            db.query(Question)
            .filter(Question.topic_id == topic_id)
            .filter(
                (Question.generated_for_student_id.is_(None)) |
                (Question.generated_for_student_id != student_id)
            )
            .all()
        )
        random.shuffle(pool)
        questions.extend(pool[:questions_per_topic])

    random.shuffle(questions)
    db.commit()
    return {"assessment_id": assessment.id, "questions": questions}


def build_mastery_assessment(db: Session, student_id: str, topic_id: str,
                              num_questions: int = 8, exclude_seen: bool = False) -> dict:
    """Stage 3: single-topic mastery gate quiz."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic:
        _ensure_topic_questions(db, topic, min_needed=num_questions)

    query = db.query(Question).filter(Question.topic_id == topic_id)
    if exclude_seen:
        query = query.filter(
            (Question.generated_for_student_id.is_(None)) |
            (Question.generated_for_student_id != student_id)
        )
    pool = query.all()
    random.shuffle(pool)
    selected = pool[:num_questions]

    course_id = topic.course_id if topic else None
    assessment = Assessment(student_id=student_id, course_id=course_id, topic_id=topic_id,
                             type=AssessmentTypeEnum.mastery)
    db.add(assessment)
    db.commit()

    return {"assessment_id": assessment.id, "questions": selected}


def evaluate_mastery(score_pct: float) -> bool:
    return score_pct >= settings.MASTERY_THRESHOLD


async def generate_questions_via_llm(topic_name: str, difficulty: str, count: int,
                                      context_notes: Optional[str] = None) -> List[dict]:
    """Generates dynamic questions via LLM or templates."""
    if not settings.LLM_API_URL or not settings.LLM_API_KEY:
        # Return tailored template questions
        return TOPIC_QUESTION_TEMPLATES.get(topic_name, [])[:count]

    prompt = f"""Generate {count} multiple-choice questions on the topic "{topic_name}"
at {difficulty} difficulty{f' using this reference material: {context_notes}' if context_notes else ''}.

Return ONLY a JSON array, no preamble, no markdown fences. Each item:
{{
  "question_text": "...",
  "options": {{"a": "...", "b": "...", "c": "...", "d": "..."}},
  "correct_answer": "a",
  "explanation": "...",
  "bloom_level": "Understand",
  "learning_objective": "..."
}}"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                settings.LLM_API_URL,
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                json={
                    "model": "qwen2.5-3b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
    except Exception:
        return TOPIC_QUESTION_TEMPLATES.get(topic_name, [])[:count]
