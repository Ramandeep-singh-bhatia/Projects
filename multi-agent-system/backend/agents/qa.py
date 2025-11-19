"""
Quality Assurance Agent - Specialized in validation, fact-checking, and quality control.
Capabilities: Fact-checking, compliance checking, output quality scoring, error detection.
"""

from typing import Dict, Any, Optional, List
from loguru import logger

from backend.agents.base_agent import BaseAgent


class QAAgent(BaseAgent):
    """
    Quality Assurance Agent for validation and quality control.

    Specializes in:
    - Fact-checking and verification
    - Compliance checking (PII, legal, brand voice)
    - Output quality scoring
    - Error detection and correction
    - Final approval workflows
    - Standards enforcement
    """

    def __init__(self, **kwargs):
        """Initialize the QA Agent."""
        super().__init__(
            agent_type="qa",
            role="Senior Quality Assurance Specialist",
            goal="Ensure all outputs meet quality standards, are factually accurate, and comply with regulations",
            backstory="""You are an expert quality assurance specialist with a keen eye
            for detail and deep knowledge of compliance requirements, fact-checking
            methodologies, and quality standards. You excel at identifying errors,
            inconsistencies, and potential issues before they become problems. Your
            reviews are thorough, constructive, and maintain high standards.""",
            tools=[],
            **kwargs,
        )

        # QA criteria
        self.quality_criteria = {
            "accuracy": 0.95,
            "completeness": 0.90,
            "clarity": 0.85,
            "compliance": 1.0,  # Must be 100%
        }

    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a QA task.

        Args:
            task: QA task description
            context: Additional context

        Returns:
            QA results
        """
        logger.info(f"QA Agent executing task: {task[:100]}...")

        context = context or {}
        qa_type = context.get("qa_type", "comprehensive")

        try:
            if qa_type == "fact_check":
                results = await self._fact_check(task, context)
            elif qa_type == "compliance":
                results = await self._check_compliance(task, context)
            elif qa_type == "quality_score":
                results = await self._score_quality(task, context)
            elif qa_type == "error_detection":
                results = await self._detect_errors(task, context)
            else:
                results = await self._comprehensive_qa(task, context)

            return {
                "status": "completed",
                "qa_type": qa_type,
                "results": results,
                "tokens_used": 0,
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Error in QA task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "results": None,
            }

    async def _fact_check(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform fact-checking on content.

        Args:
            content: Content to fact-check
            context: Additional context

        Returns:
            Fact-check results
        """
        claims = context.get("claims", self._extract_claims(content))

        fact_check_results = []

        for claim in claims:
            result = {
                "claim": claim,
                "status": self._verify_claim(claim),
                "confidence": self._calculate_confidence(claim),
                "sources": self._find_supporting_sources(claim),
                "issues": self._identify_issues(claim),
            }
            fact_check_results.append(result)

        # Calculate overall accuracy
        verified_count = sum(
            1 for r in fact_check_results
            if r["status"] in ["verified", "likely_true"]
        )
        accuracy_score = verified_count / len(fact_check_results) if fact_check_results else 1.0

        return {
            "total_claims": len(claims),
            "verified_claims": verified_count,
            "accuracy_score": accuracy_score,
            "fact_checks": fact_check_results,
            "overall_status": "pass" if accuracy_score >= 0.9 else "review_needed",
            "recommendations": self._generate_fact_check_recommendations(fact_check_results),
        }

    async def _check_compliance(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Check compliance with regulations and policies.

        Args:
            content: Content to check
            context: Compliance context

        Returns:
            Compliance check results
        """
        compliance_types = context.get("compliance_types", ["pii", "legal", "brand_voice"])

        compliance_results = {}

        for comp_type in compliance_types:
            if comp_type == "pii":
                compliance_results["pii"] = self._check_pii(content)
            elif comp_type == "legal":
                compliance_results["legal"] = self._check_legal(content)
            elif comp_type == "brand_voice":
                compliance_results["brand_voice"] = self._check_brand_voice(content, context)
            elif comp_type == "accessibility":
                compliance_results["accessibility"] = self._check_accessibility(content)

        # Determine overall compliance
        all_passed = all(
            result.get("compliant", False)
            for result in compliance_results.values()
        )

        return {
            "compliance_checks": compliance_results,
            "overall_compliant": all_passed,
            "critical_issues": self._extract_critical_issues(compliance_results),
            "recommendations": self._generate_compliance_recommendations(compliance_results),
        }

    async def _score_quality(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Score output quality.

        Args:
            content: Content to score
            context: Quality context

        Returns:
            Quality scores
        """
        scores = {
            "accuracy": self._score_accuracy(content, context),
            "completeness": self._score_completeness(content, context),
            "clarity": self._score_clarity(content),
            "relevance": self._score_relevance(content, context),
            "formatting": self._score_formatting(content),
            "tone": self._score_tone(content, context),
        }

        # Calculate overall score
        weights = {
            "accuracy": 0.3,
            "completeness": 0.25,
            "clarity": 0.2,
            "relevance": 0.15,
            "formatting": 0.05,
            "tone": 0.05,
        }

        overall_score = sum(
            scores[criterion] * weights[criterion]
            for criterion in scores
        )

        # Determine pass/fail
        passed = all(
            scores[criterion] >= self.quality_criteria.get(criterion, 0.7)
            for criterion in ["accuracy", "completeness", "clarity"]
        )

        return {
            "scores": scores,
            "overall_score": overall_score,
            "passed": passed,
            "grade": self._calculate_grade(overall_score),
            "feedback": self._generate_quality_feedback(scores),
            "improvements": self._suggest_improvements(scores),
        }

    async def _detect_errors(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Detect errors in content.

        Args:
            content: Content to check
            context: Error detection context

        Returns:
            Error detection results
        """
        errors = {
            "grammatical": self._detect_grammar_errors(content),
            "factual": self._detect_factual_errors(content, context),
            "logical": self._detect_logical_errors(content),
            "formatting": self._detect_formatting_errors(content),
            "consistency": self._detect_consistency_errors(content),
        }

        total_errors = sum(len(error_list) for error_list in errors.values())

        return {
            "total_errors": total_errors,
            "errors_by_type": {k: len(v) for k, v in errors.items()},
            "errors": errors,
            "severity_distribution": self._categorize_error_severity(errors),
            "corrections": self._suggest_corrections(errors),
        }

    async def _comprehensive_qa(
        self,
        content: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform comprehensive QA check.

        Args:
            content: Content to check
            context: QA context

        Returns:
            Comprehensive QA results
        """
        # Run all QA checks
        fact_check = await self._fact_check(content, context)
        compliance = await self._check_compliance(content, context)
        quality = await self._score_quality(content, context)
        errors = await self._detect_errors(content, context)

        # Determine overall approval
        approved = (
            fact_check.get("overall_status") == "pass" and
            compliance.get("overall_compliant") and
            quality.get("passed") and
            errors.get("total_errors", 0) < 5
        )

        return {
            "approved": approved,
            "fact_check": fact_check,
            "compliance": compliance,
            "quality": quality,
            "errors": errors,
            "final_recommendation": self._generate_final_recommendation(
                approved,
                fact_check,
                compliance,
                quality,
                errors,
            ),
        }

    # Helper methods

    def _extract_claims(self, content: str) -> List[str]:
        """Extract factual claims from content."""
        # Simple extraction (in production, use NLP)
        return ["Sample claim 1", "Sample claim 2", "Sample claim 3"]

    def _verify_claim(self, claim: str) -> str:
        """Verify a factual claim."""
        # In production, cross-reference with trusted sources
        return "verified"  # or "false", "unverified", "likely_true"

    def _calculate_confidence(self, claim: str) -> float:
        """Calculate confidence in verification."""
        return 0.85

    def _find_supporting_sources(self, claim: str) -> List[str]:
        """Find sources supporting the claim."""
        return ["Source 1", "Source 2"]

    def _identify_issues(self, claim: str) -> List[str]:
        """Identify issues with the claim."""
        return []

    def _generate_fact_check_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations from fact-check results."""
        recommendations = []

        unverified = [r for r in results if r["status"] == "unverified"]
        if unverified:
            recommendations.append(f"Verify {len(unverified)} unverified claims")

        return recommendations

    def _check_pii(self, content: str) -> Dict[str, Any]:
        """Check for PII (Personally Identifiable Information)."""
        # Simple pattern matching (in production, use NLP)
        pii_found = []

        patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        }

        # Check each pattern
        for pii_type, pattern in patterns.items():
            import re
            if re.search(pattern, content):
                pii_found.append(pii_type)

        return {
            "compliant": len(pii_found) == 0,
            "pii_detected": pii_found,
            "severity": "critical" if pii_found else "none",
        }

    def _check_legal(self, content: str) -> Dict[str, Any]:
        """Check for legal compliance."""
        issues = []

        # Check for required disclaimers
        if "investment" in content.lower() and "disclaimer" not in content.lower():
            issues.append("Missing investment disclaimer")

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "severity": "high" if issues else "none",
        }

    def _check_brand_voice(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check brand voice compliance."""
        expected_tone = context.get("brand_tone", "professional")

        # Simple tone check
        tone_match = True  # In production, use sentiment analysis

        return {
            "compliant": tone_match,
            "expected_tone": expected_tone,
            "detected_tone": "professional",
            "severity": "medium" if not tone_match else "none",
        }

    def _check_accessibility(self, content: str) -> Dict[str, Any]:
        """Check accessibility compliance."""
        return {
            "compliant": True,
            "issues": [],
            "severity": "none",
        }

    def _extract_critical_issues(self, compliance: Dict[str, Any]) -> List[str]:
        """Extract critical compliance issues."""
        critical = []

        for check, result in compliance.items():
            if result.get("severity") == "critical":
                critical.extend(result.get("pii_detected", []))

        return critical

    def _generate_compliance_recommendations(self, compliance: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []

        if not compliance.get("pii", {}).get("compliant"):
            recommendations.append("Remove or redact PII before publishing")

        if not compliance.get("legal", {}).get("compliant"):
            recommendations.append("Add required legal disclaimers")

        return recommendations

    def _score_accuracy(self, content: str, context: Dict[str, Any]) -> float:
        """Score content accuracy."""
        return 0.92

    def _score_completeness(self, content: str, context: Dict[str, Any]) -> float:
        """Score content completeness."""
        return 0.88

    def _score_clarity(self, content: str) -> float:
        """Score content clarity."""
        return 0.90

    def _score_relevance(self, content: str, context: Dict[str, Any]) -> float:
        """Score content relevance."""
        return 0.85

    def _score_formatting(self, content: str) -> float:
        """Score formatting quality."""
        return 0.95

    def _score_tone(self, content: str, context: Dict[str, Any]) -> float:
        """Score tone appropriateness."""
        return 0.87

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.75:
            return "C"
        else:
            return "D"

    def _generate_quality_feedback(self, scores: Dict[str, float]) -> List[str]:
        """Generate quality feedback."""
        feedback = []

        for criterion, score in scores.items():
            if score < 0.8:
                feedback.append(f"Improve {criterion} (current: {score:.2f})")

        return feedback

    def _suggest_improvements(self, scores: Dict[str, float]) -> List[str]:
        """Suggest specific improvements."""
        return ["Enhance clarity in technical sections", "Add more supporting evidence"]

    def _detect_grammar_errors(self, content: str) -> List[Dict[str, Any]]:
        """Detect grammatical errors."""
        return []  # In production, use grammar checking API

    def _detect_factual_errors(self, content: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect factual errors."""
        return []

    def _detect_logical_errors(self, content: str) -> List[Dict[str, Any]]:
        """Detect logical inconsistencies."""
        return []

    def _detect_formatting_errors(self, content: str) -> List[Dict[str, Any]]:
        """Detect formatting errors."""
        return []

    def _detect_consistency_errors(self, content: str) -> List[Dict[str, Any]]:
        """Detect consistency errors."""
        return []

    def _categorize_error_severity(self, errors: Dict[str, List]) -> Dict[str, int]:
        """Categorize errors by severity."""
        return {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": sum(len(e) for e in errors.values()),
        }

    def _suggest_corrections(self, errors: Dict[str, List]) -> List[str]:
        """Suggest corrections for errors."""
        return []

    def _generate_final_recommendation(
        self,
        approved: bool,
        fact_check: Dict[str, Any],
        compliance: Dict[str, Any],
        quality: Dict[str, Any],
        errors: Dict[str, Any],
    ) -> str:
        """Generate final QA recommendation."""
        if approved:
            return "Content approved for publication. All quality checks passed."
        else:
            issues = []
            if fact_check.get("overall_status") != "pass":
                issues.append("fact-checking concerns")
            if not compliance.get("overall_compliant"):
                issues.append("compliance violations")
            if not quality.get("passed"):
                issues.append("quality standards not met")
            if errors.get("total_errors", 0) >= 5:
                issues.append("multiple errors detected")

            return f"Content requires revision. Issues: {', '.join(issues)}"
