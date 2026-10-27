from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.base import get_db
from app.models.models import ChatHistory, Student, User
from app.schemas.schemas import TutorChatIn, TutorChatOut
from app.services.rag_pipeline import rag_pipeline

router = APIRouter(prefix="/tutor", tags=["tutor"])



@router.post("/chat", response_model=TutorChatOut)
async def chat(payload: TutorChatIn, db: Session = Depends(get_db),
              user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    
    # Grounded RAG retrieval and answer synthesis
    rag_result = await rag_pipeline.answer_query(
        db=db,
        query=payload.message,
        course_id=payload.course_id,
        language=payload.language
    )

    # Persist in chat history
    db.add(ChatHistory(
        student_id=student.id,
        message=payload.message,
        response=rag_result["response"],
        source_refs=rag_result.get("sources", [])
    ))
    
    # Award student +10 XP for engaging with AI Tutor
    student.xp_points = (student.xp_points or 0) + 10
    db.commit()

    return TutorChatOut(
        response=rag_result["response"],
        sources=rag_result.get("sources", []),
        confidence=rag_result.get("confidence", 0.90),
        grounded=rag_result.get("grounded", True)
    )


@router.get("/history")
def get_chat_history(course_id: str = None, db: Session = Depends(get_db),
                     user: User = Depends(require_role("student"))):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.student_id == student.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": h.id,
            "message": h.message,
            "response": h.response,
            "source_refs": h.source_refs or [],
            "created_at": h.created_at
        }
        for h in reversed(history)
    ]


@router.get("/suggested-prompts")
def get_suggested_prompts():
    return [
        "Explain the difference between Array memory layout and Linked List nodes.",
        "Why is insertion at the beginning O(1) in a linked list but O(n) in dynamic array?",
        "How does a Circular Queue avoid the drawback of linear queues?",
        "What are the invariants of a Binary Search Tree (BST)?",
        "Compare BFS (Queue-based) vs DFS (Stack-based) graph traversals.",
        "What is the amortized time complexity of inserting into a dynamic array?",
    ]

