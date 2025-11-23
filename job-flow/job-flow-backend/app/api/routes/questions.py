"""
API routes for question database management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ...database import get_db
from ...database.models import Question
from ...schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionMatchRequest, QuestionMatchResponse, QuestionLearnRequest
)

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/", response_model=List[QuestionResponse])
async def list_questions(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(100, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all questions, optionally filtered by category or search term"""
    query = db.query(Question)

    if category:
        query = query.filter(Question.category == category)

    if search:
        query = query.filter(Question.question_text.ilike(f"%{search}%"))

    questions = query.order_by(Question.times_used.desc()).offset(skip).limit(limit).all()
    return questions


@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """Get all unique categories"""
    categories = db.query(Question.category).distinct().all()
    return {"categories": [cat[0] for cat in categories if cat[0]]}


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    """Get a specific question by ID"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    return question


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """Add new question-answer pair"""
    # Check for duplicate
    existing = db.query(Question).filter(
        Question.question_text == question.question_text
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question already exists. Use PUT to update or POST to /learn endpoint."
        )

    db_question = Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    update: QuestionUpdate,
    db: Session = Depends(get_db)
):
    """Update existing question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)

    question.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(question)
    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Delete a question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )

    db.delete(question)
    db.commit()
    return None


@router.get("/match/search", response_model=QuestionMatchResponse)
async def match_question(
    question_text: str = Query(..., min_length=3),
    db: Session = Depends(get_db)
):
    """Find best matching question using fuzzy matching"""
    from fuzzywuzzy import fuzz, process

    # Get all questions from database
    all_questions = db.query(Question).all()

    if not all_questions:
        return QuestionMatchResponse(
            answer=None,
            confidence=0,
            matched_question=None,
            suggestions=[]
        )

    # Build question list for fuzzy matching
    question_texts = {q.question_text: q for q in all_questions}

    # Find best matches using fuzzywuzzy
    matches = process.extract(
        question_text,
        question_texts.keys(),
        scorer=fuzz.token_sort_ratio,
        limit=5
    )

    suggestions = []
    for match_text, score in matches:
        if score > 70:  # Only include decent matches
            q = question_texts[match_text]
            suggestions.append({
                "question": q.question_text,
                "answer": q.answer,
                "score": score,
                "category": q.category,
                "question_id": q.id
            })

    best_match_text, best_score = matches[0] if matches else (None, 0)

    if best_score >= 85:  # High confidence threshold
        best_question = question_texts[best_match_text]

        # Update usage stats
        best_question.times_used += 1
        best_question.last_used = datetime.utcnow()
        db.commit()

        return QuestionMatchResponse(
            answer=best_question.answer,
            confidence=best_score,
            matched_question=best_question.question_text,
            question_id=best_question.id,
            suggestions=suggestions
        )
    else:
        return QuestionMatchResponse(
            answer=None,
            confidence=best_score if matches else 0,
            matched_question=None,
            suggestions=suggestions
        )


@router.post("/learn", response_model=QuestionResponse)
async def learn_question(
    request: QuestionLearnRequest,
    db: Session = Depends(get_db)
):
    """Learn new question from application process"""
    # Check if similar question exists
    existing = db.query(Question).filter(
        Question.question_text.ilike(f"%{request.question_text}%")
    ).first()

    if existing:
        # Update existing
        existing.answer = request.answer
        existing.times_used += 1
        existing.user_verified = True
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    # Create new question
    new_question = Question(
        user_id=1,  # Default to single user
        question_text=request.question_text,
        answer=request.answer,
        category=request.category or "general",
        auto_learned=True,
        user_verified=False
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question


@router.get("/stats/summary")
async def get_question_stats(db: Session = Depends(get_db)):
    """Get statistics about the question database"""
    total_questions = db.query(Question).count()
    verified_questions = db.query(Question).filter(Question.user_verified == True).count()
    auto_learned = db.query(Question).filter(Question.auto_learned == True).count()

    # Category breakdown
    categories = db.query(
        Question.category,
        db.func.count(Question.id).label('count')
    ).group_by(Question.category).all()

    # Most used questions
    most_used = db.query(Question).order_by(
        Question.times_used.desc()
    ).limit(10).all()

    return {
        "total_questions": total_questions,
        "verified_questions": verified_questions,
        "auto_learned_questions": auto_learned,
        "unverified_questions": total_questions - verified_questions,
        "categories": [{"category": cat, "count": count} for cat, count in categories],
        "most_used": [
            {
                "question": q.question_text,
                "times_used": q.times_used,
                "category": q.category
            }
            for q in most_used
        ]
    }
