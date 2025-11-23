"""
Question Answering Service
Handles fuzzy matching of questions to find answers from database
"""
from sqlalchemy.orm import Session
from fuzzywuzzy import fuzz, process
from typing import Optional, Dict, List
from datetime import datetime

from ..database.models import Question


class QuestionAnsweringService:
    """Service for matching questions and finding answers"""

    def __init__(self, db: Session):
        self.db = db

    async def find_answer(self, question_text: str) -> Dict:
        """
        Find answer for question using fuzzy matching
        No AI needed - saves costs

        Returns:
            {
                "answer": str or None,
                "confidence": int (0-100),
                "matched_question": str or None,
                "question_id": int or None,
                "suggestions": list[dict]
            }
        """
        # Get all questions from database
        all_questions = self.db.query(Question).all()

        if not all_questions:
            return {
                "answer": None,
                "confidence": 0,
                "matched_question": None,
                "question_id": None,
                "suggestions": []
            }

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
            self.db.commit()

            return {
                "answer": best_question.answer,
                "confidence": best_score,
                "matched_question": best_question.question_text,
                "question_id": best_question.id,
                "suggestions": suggestions
            }
        else:
            return {
                "answer": None,
                "confidence": best_score if matches else 0,
                "matched_question": None,
                "question_id": None,
                "suggestions": suggestions
            }

    def batch_find_answers(self, questions: List[str]) -> Dict[str, Dict]:
        """
        Find answers for multiple questions at once
        More efficient than calling find_answer multiple times

        Args:
            questions: List of question texts

        Returns:
            Dictionary mapping question text to answer result
        """
        results = {}

        # Get all questions once
        all_db_questions = self.db.query(Question).all()

        if not all_db_questions:
            return {q: {
                "answer": None,
                "confidence": 0,
                "matched_question": None,
                "question_id": None
            } for q in questions}

        question_texts = {q.question_text: q for q in all_db_questions}

        # Process each question
        for question_text in questions:
            matches = process.extract(
                question_text,
                question_texts.keys(),
                scorer=fuzz.token_sort_ratio,
                limit=1
            )

            if matches:
                best_match_text, best_score = matches[0]

                if best_score >= 85:
                    best_question = question_texts[best_match_text]

                    # Update usage stats
                    best_question.times_used += 1
                    best_question.last_used = datetime.utcnow()

                    results[question_text] = {
                        "answer": best_question.answer,
                        "confidence": best_score,
                        "matched_question": best_question.question_text,
                        "question_id": best_question.id
                    }
                else:
                    results[question_text] = {
                        "answer": None,
                        "confidence": best_score,
                        "matched_question": None,
                        "question_id": None
                    }
            else:
                results[question_text] = {
                    "answer": None,
                    "confidence": 0,
                    "matched_question": None,
                    "question_id": None
                }

        # Commit all usage updates at once
        self.db.commit()

        return results

    def learn_question(
        self,
        question_text: str,
        answer: str,
        category: Optional[str] = None,
        field_type: Optional[str] = "text"
    ) -> Question:
        """
        Learn a new question or update existing one

        Args:
            question_text: The question text
            answer: The answer
            category: Optional category
            field_type: Field type (text, number, boolean, etc.)

        Returns:
            Question object
        """
        # Check if similar question exists (fuzzy match)
        all_questions = self.db.query(Question).all()

        if all_questions:
            question_texts = {q.question_text: q for q in all_questions}
            matches = process.extract(
                question_text,
                question_texts.keys(),
                scorer=fuzz.token_sort_ratio,
                limit=1
            )

            if matches:
                match_text, score = matches[0]
                if score >= 90:  # Very high confidence - update existing
                    existing = question_texts[match_text]
                    existing.answer = answer
                    existing.times_used += 1
                    existing.user_verified = True
                    existing.updated_at = datetime.utcnow()
                    self.db.commit()
                    self.db.refresh(existing)
                    return existing

        # Create new question
        new_question = Question(
            user_id=1,  # Default to single user
            question_text=question_text,
            answer=answer,
            category=category or "general",
            field_type=field_type,
            auto_learned=True,
            user_verified=False
        )

        self.db.add(new_question)
        self.db.commit()
        self.db.refresh(new_question)
        return new_question

    def get_common_questions_by_platform(self, platform: str) -> List[Question]:
        """
        Get common questions for a specific platform

        Args:
            platform: Platform name (linkedin, workday, etc.)

        Returns:
            List of Question objects
        """
        # Get platform-specific questions
        platform_questions = self.db.query(Question).filter(
            Question.platform_specific == platform
        ).order_by(Question.times_used.desc()).limit(20).all()

        # Get general frequently used questions
        general_questions = self.db.query(Question).filter(
            Question.platform_specific.is_(None)
        ).order_by(Question.times_used.desc()).limit(30).all()

        return platform_questions + general_questions
