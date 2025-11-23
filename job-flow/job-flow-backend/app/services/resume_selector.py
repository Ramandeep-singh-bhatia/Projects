"""
Resume Selector Service
Automatically selects the best resume template for a job
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple

from ..database.models import Resume


class ResumeSelectorService:
    """Service for selecting the best resume for a job"""

    def __init__(self, db: Session):
        self.db = db

    async def select_resume(
        self,
        job_description: str,
        job_title: Optional[str] = None
    ) -> Optional[Resume]:
        """
        Select best resume template for job description
        Uses keyword matching, no AI to save costs

        Args:
            job_description: The job description text
            job_title: Optional job title for additional matching

        Returns:
            Resume object or None
        """
        # Get all resumes
        resumes = self.db.query(Resume).all()

        if not resumes:
            return None

        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description.lower())

        if job_title:
            job_keywords.update(self._extract_keywords(job_title.lower()))

        # Score each resume
        best_resume = None
        best_score = 0

        for resume in resumes:
            score = self._score_resume(resume, job_keywords)

            if score > best_score:
                best_score = score
                best_resume = resume

        # Update usage stats for selected resume
        if best_resume:
            best_resume.times_used += 1
            self.db.commit()

        return best_resume

    def select_resume_with_details(
        self,
        job_description: str,
        job_title: Optional[str] = None
    ) -> Dict:
        """
        Select resume and return detailed matching information

        Returns:
            {
                "resume": Resume object or None,
                "score": int (0-100),
                "reasons": List[str],
                "matched_technologies": List[str],
                "matched_focus_areas": List[str]
            }
        """
        resumes = self.db.query(Resume).all()

        if not resumes:
            return {
                "resume": None,
                "score": 0,
                "reasons": ["No resumes available"],
                "matched_technologies": [],
                "matched_focus_areas": []
            }

        job_keywords = self._extract_keywords(job_description.lower())
        if job_title:
            job_keywords.update(self._extract_keywords(job_title.lower()))

        best_resume = None
        best_score = 0
        best_details = {
            "reasons": [],
            "matched_technologies": [],
            "matched_focus_areas": []
        }

        for resume in resumes:
            score, details = self._score_resume_with_details(resume, job_keywords)

            if score > best_score:
                best_score = score
                best_resume = resume
                best_details = details

        # Update usage stats
        if best_resume:
            best_resume.times_used += 1
            self.db.commit()

        return {
            "resume": best_resume,
            "score": min(100, best_score),
            **best_details
        }

    def _score_resume(self, resume: Resume, job_keywords: set) -> int:
        """
        Score a resume against job keywords

        Returns:
            Score (0-100+)
        """
        score = 0

        # Match technologies (10 points each)
        if resume.technologies:
            resume_techs = [t.lower() for t in resume.technologies]
            matched_techs = sum(1 for tech in resume_techs if tech in job_keywords)
            score += matched_techs * 10

        # Match focus areas (20 points each)
        if resume.focus_areas:
            resume_focus = [f.lower() for f in resume.focus_areas]
            matched_focus = sum(
                1 for focus in resume_focus
                if any(focus in keyword for keyword in job_keywords)
            )
            score += matched_focus * 20

        # Match keywords (5 points each)
        if resume.keywords:
            resume_keywords = [k.lower() for k in resume.keywords]
            matched_keywords = sum(1 for kw in resume_keywords if kw in job_keywords)
            score += matched_keywords * 5

        # Prefer master template if no clear winner (5 point boost)
        if resume.is_master:
            score += 5

        # Prefer frequently used resumes (up to 10 points)
        if resume.times_used > 0:
            usage_bonus = min(10, resume.times_used // 5)
            score += usage_bonus

        # Prefer resumes with high success rate (up to 10 points)
        if resume.success_rate > 0:
            success_bonus = int(resume.success_rate * 0.1)
            score += success_bonus

        return score

    def _score_resume_with_details(
        self,
        resume: Resume,
        job_keywords: set
    ) -> Tuple[int, Dict]:
        """
        Score resume and return detailed breakdown

        Returns:
            (score, details_dict)
        """
        score = 0
        reasons = []
        matched_technologies = []
        matched_focus_areas = []

        # Match technologies
        if resume.technologies:
            resume_techs = [t.lower() for t in resume.technologies]
            matched_technologies = [
                tech for tech in resume.technologies
                if tech.lower() in job_keywords
            ]
            if matched_technologies:
                tech_score = len(matched_technologies) * 10
                score += tech_score
                reasons.append(
                    f"Matches {len(matched_technologies)} technologies: {', '.join(matched_technologies[:5])}"
                )

        # Match focus areas
        if resume.focus_areas:
            resume_focus = [f.lower() for f in resume.focus_areas]
            matched_focus_areas = [
                focus for focus in resume.focus_areas
                if any(focus.lower() in keyword for keyword in job_keywords)
            ]
            if matched_focus_areas:
                focus_score = len(matched_focus_areas) * 20
                score += focus_score
                reasons.append(
                    f"Matches focus areas: {', '.join(matched_focus_areas)}"
                )

        # Match keywords
        if resume.keywords:
            resume_keywords = [k.lower() for k in resume.keywords]
            matched_keywords_count = sum(1 for kw in resume_keywords if kw in job_keywords)
            if matched_keywords_count > 0:
                keywords_score = matched_keywords_count * 5
                score += keywords_score
                reasons.append(f"Matches {matched_keywords_count} resume keywords")

        # Master template bonus
        if resume.is_master:
            score += 5
            reasons.append("Master template (versatile)")

        # Usage stats
        if resume.times_used > 0:
            usage_bonus = min(10, resume.times_used // 5)
            score += usage_bonus
            reasons.append(f"Used successfully {resume.times_used} times")

        # Success rate
        if resume.success_rate > 0:
            success_bonus = int(resume.success_rate * 0.1)
            score += success_bonus
            reasons.append(f"Success rate: {resume.success_rate:.1f}%")

        if not reasons:
            reasons.append("Selected as default (no strong match)")

        details = {
            "reasons": reasons,
            "matched_technologies": matched_technologies,
            "matched_focus_areas": matched_focus_areas
        }

        return score, details

    def _extract_keywords(self, text: str) -> set:
        """
        Extract relevant keywords from job description
        Includes tech skills, domains, and common job terms
        """
        tech_keywords = {
            # Programming languages
            'java', 'python', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
            'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',

            # Frontend
            'react', 'angular', 'vue', 'svelte', 'ember', 'jquery', 'html', 'css',
            'sass', 'less', 'webpack', 'vite', 'tailwind', 'bootstrap',

            # Backend
            'node', 'express', 'django', 'flask', 'spring', 'spring boot',
            'fastapi', 'rails', 'laravel', '.net', 'asp.net',

            # Cloud & Infrastructure
            'aws', 'azure', 'gcp', 'google cloud', 'cloud', 'kubernetes', 'k8s',
            'docker', 'terraform', 'ansible', 'jenkins', 'gitlab', 'github actions',
            'circleci', 'travis', 'cloudformation',

            # Databases
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            'dynamodb', 'couchbase', 'neo4j', 'oracle', 'sql server', 'sqlite',
            'mariadb',

            # Data & ML
            'kafka', 'rabbitmq', 'spark', 'hadoop', 'airflow', 'flink',
            'machine learning', 'ml', 'ai', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',

            # Architecture & Patterns
            'distributed systems', 'microservices', 'scalability', 'performance',
            'high availability', 'load balancing', 'caching', 'api', 'rest',
            'graphql', 'grpc', 'websocket', 'event driven', 'serverless',

            # Roles & Domains
            'backend', 'frontend', 'fullstack', 'full stack', 'full-stack',
            'devops', 'sre', 'site reliability', 'infrastructure', 'platform',
            'data engineer', 'data science', 'analytics', 'search', 'security',

            # Methodologies
            'agile', 'scrum', 'kanban', 'ci/cd', 'tdd', 'bdd',

            # Operating Systems & Tools
            'linux', 'unix', 'bash', 'shell', 'git', 'vim', 'vscode',

            # Specific domains
            'e-commerce', 'fintech', 'healthcare', 'payments', 'advertising',
            'gaming', 'social media', 'iot', 'blockchain', 'cryptocurrency'
        }

        found_keywords = set()
        text_lower = text.lower()

        for keyword in tech_keywords:
            if keyword in text_lower:
                found_keywords.add(keyword)

        return found_keywords

    def update_resume_success_rate(self, resume_id: int, got_response: bool):
        """
        Update resume success rate based on application outcome

        Args:
            resume_id: ID of the resume
            got_response: Whether the application got a response
        """
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()

        if not resume:
            return

        # Simple moving average calculation
        # This could be enhanced with more sophisticated tracking
        if resume.times_used > 0:
            current_successes = resume.success_rate * resume.times_used / 100
            new_successes = current_successes + (1 if got_response else 0)
            resume.success_rate = (new_successes / resume.times_used) * 100
        else:
            resume.success_rate = 100.0 if got_response else 0.0

        self.db.commit()
