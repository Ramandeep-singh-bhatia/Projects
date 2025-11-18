"""
Content Creation Agent - Specialized in content generation and optimization.
Capabilities: Blog posts, reports, documentation, emails, SEO optimization.
"""

from typing import Dict, Any, Optional, List
from loguru import logger

from backend.agents.base_agent import BaseAgent


class ContentCreatorAgent(BaseAgent):
    """
    Content Creator Agent for generating various types of content.

    Specializes in:
    - Blog posts and articles
    - Technical documentation
    - Business reports
    - Email campaigns
    - SEO optimization
    - Multi-language support
    """

    def __init__(self, **kwargs):
        """Initialize the Content Creator Agent."""
        super().__init__(
            agent_type="content",
            role="Senior Content Strategist",
            goal="Create engaging, high-quality content optimized for target audience and SEO",
            backstory="""You are an expert content creator and copywriter with years of
            experience in crafting compelling narratives, technical documentation, and
            marketing materials. You understand SEO principles, audience psychology, and
            how to communicate complex ideas clearly. Your content is engaging, accurate,
            and drives desired outcomes.""",
            tools=[],
            **kwargs,
        )

    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a content creation task.

        Args:
            task: Content creation task
            context: Additional context

        Returns:
            Created content
        """
        logger.info(f"Content Creator executing task: {task[:100]}...")

        context = context or {}
        content_type = context.get("content_type", "blog_post")

        try:
            if content_type == "blog_post":
                results = await self._create_blog_post(task, context)
            elif content_type == "documentation":
                results = await self._create_documentation(task, context)
            elif content_type == "email":
                results = await self._create_email(task, context)
            elif content_type == "report":
                results = await self._create_report(task, context)
            elif content_type == "social_media":
                results = await self._create_social_content(task, context)
            else:
                results = await self._create_general_content(task, context)

            return {
                "status": "completed",
                "content_type": content_type,
                "results": results,
                "tokens_used": 0,
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Error in content creation task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "results": None,
            }

    async def _create_blog_post(
        self,
        topic: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a blog post.

        Args:
            topic: Blog post topic
            context: Additional context (tone, target_audience, keywords)

        Returns:
            Blog post content
        """
        tone = context.get("tone", "professional")
        target_audience = context.get("target_audience", "general")
        keywords = context.get("keywords", [])
        word_count = context.get("word_count", 1000)

        # Generate outline
        outline = self._generate_outline(topic, 5)

        # Create content structure
        content = {
            "title": self._generate_title(topic, keywords),
            "meta_description": self._generate_meta_description(topic, keywords),
            "outline": outline,
            "body": self._generate_body(topic, outline, word_count),
            "conclusion": self._generate_conclusion(topic),
            "call_to_action": self._generate_cta(target_audience),
            "seo_keywords": keywords,
            "word_count": word_count,
            "reading_time": f"{word_count // 200} minutes",
        }

        return content

    async def _create_documentation(
        self,
        topic: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create technical documentation.

        Args:
            topic: Documentation topic
            context: Context (type, detail_level)

        Returns:
            Documentation content
        """
        doc_type = context.get("doc_type", "api")
        detail_level = context.get("detail_level", "detailed")

        sections = []

        if doc_type == "api":
            sections = [
                {"title": "Overview", "content": f"API documentation for {topic}"},
                {"title": "Authentication", "content": "Authentication requirements and methods"},
                {"title": "Endpoints", "content": "Available API endpoints and usage"},
                {"title": "Request/Response Examples", "content": "Sample requests and responses"},
                {"title": "Error Handling", "content": "Error codes and troubleshooting"},
            ]
        else:
            sections = [
                {"title": "Introduction", "content": f"Introduction to {topic}"},
                {"title": "Getting Started", "content": "Quick start guide"},
                {"title": "Usage", "content": "Detailed usage instructions"},
                {"title": "Examples", "content": "Practical examples"},
                {"title": "Troubleshooting", "content": "Common issues and solutions"},
            ]

        return {
            "title": f"{topic} Documentation",
            "type": doc_type,
            "detail_level": detail_level,
            "sections": sections,
            "table_of_contents": [s["title"] for s in sections],
        }

    async def _create_email(
        self,
        purpose: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create an email.

        Args:
            purpose: Email purpose
            context: Context (recipient, tone, call_to_action)

        Returns:
            Email content
        """
        recipient = context.get("recipient", "Customer")
        tone = context.get("tone", "professional")
        include_cta = context.get("include_cta", True)

        email = {
            "subject": self._generate_email_subject(purpose),
            "greeting": f"Hi {recipient},",
            "body": self._generate_email_body(purpose, tone),
            "closing": "Best regards,",
            "call_to_action": self._generate_cta("email") if include_cta else None,
        }

        return email

    async def _create_report(
        self,
        topic: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a business report.

        Args:
            topic: Report topic
            context: Context (data, findings)

        Returns:
            Report content
        """
        data = context.get("data", {})
        findings = context.get("findings", [])

        report = {
            "title": f"{topic} - Analysis Report",
            "executive_summary": self._generate_executive_summary(topic, findings),
            "sections": [
                {
                    "title": "Introduction",
                    "content": f"This report presents findings on {topic}",
                },
                {
                    "title": "Methodology",
                    "content": "Research methodology and data sources",
                },
                {
                    "title": "Key Findings",
                    "content": findings,
                },
                {
                    "title": "Analysis",
                    "content": "Detailed analysis of findings",
                },
                {
                    "title": "Recommendations",
                    "content": self._generate_recommendations(findings),
                },
                {
                    "title": "Conclusion",
                    "content": "Summary and next steps",
                },
            ],
            "appendices": [],
        }

        return report

    async def _create_social_content(
        self,
        topic: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create social media content.

        Args:
            topic: Content topic
            context: Platform and style

        Returns:
            Social media posts
        """
        platform = context.get("platform", "linkedin")
        post_count = context.get("post_count", 5)

        posts = []

        for i in range(post_count):
            post = {
                "id": i + 1,
                "platform": platform,
                "content": self._generate_social_post(topic, platform),
                "hashtags": self._generate_hashtags(topic, 5),
                "optimal_post_time": "9:00 AM - 11:00 AM",
            }
            posts.append(post)

        return {
            "topic": topic,
            "platform": platform,
            "posts": posts,
            "total_posts": len(posts),
        }

    async def _create_general_content(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create general content."""
        return {
            "title": task,
            "content": f"Generated content for: {task}",
            "word_count": 500,
        }

    # Helper methods

    def _generate_outline(self, topic: str, sections: int) -> List[Dict[str, str]]:
        """Generate content outline."""
        outline = []
        for i in range(sections):
            outline.append({
                "section": f"Section {i+1}",
                "title": f"Key Aspect {i+1} of {topic[:30]}",
                "points": [f"Point {j+1}" for j in range(3)],
            })
        return outline

    def _generate_title(self, topic: str, keywords: List[str]) -> str:
        """Generate SEO-optimized title."""
        keyword = keywords[0] if keywords else topic
        return f"The Complete Guide to {keyword.title()}"

    def _generate_meta_description(self, topic: str, keywords: List[str]) -> str:
        """Generate meta description."""
        return f"Comprehensive guide to {topic}. Learn everything you need to know about {', '.join(keywords[:3])}."

    def _generate_body(self, topic: str, outline: List[Dict[str, str]], word_count: int) -> str:
        """Generate body content."""
        return f"Detailed content about {topic} covering {len(outline)} main sections. (~{word_count} words)"

    def _generate_conclusion(self, topic: str) -> str:
        """Generate conclusion."""
        return f"In conclusion, {topic} is an important subject that requires careful consideration."

    def _generate_cta(self, audience: str) -> str:
        """Generate call-to-action."""
        return "Ready to get started? Contact us today to learn more!"

    def _generate_email_subject(self, purpose: str) -> str:
        """Generate email subject line."""
        return f"Important: {purpose}"

    def _generate_email_body(self, purpose: str, tone: str) -> str:
        """Generate email body."""
        return f"I'm writing to you regarding {purpose}. [Email body content tailored to {tone} tone]"

    def _generate_executive_summary(self, topic: str, findings: List[str]) -> str:
        """Generate executive summary."""
        return f"This report examines {topic} and presents {len(findings)} key findings."

    def _generate_recommendations(self, findings: List[str]) -> List[str]:
        """Generate recommendations."""
        return [
            "Recommendation 1: Implement immediate actions",
            "Recommendation 2: Plan long-term strategy",
            "Recommendation 3: Monitor key metrics",
        ]

    def _generate_social_post(self, topic: str, platform: str) -> str:
        """Generate social media post."""
        if platform == "twitter":
            return f"Quick insight on {topic}! 🚀 [Content optimized for Twitter's character limit]"
        else:
            return f"Excited to share insights on {topic}. Here's what you need to know..."

    def _generate_hashtags(self, topic: str, count: int) -> List[str]:
        """Generate relevant hashtags."""
        base_tags = ["tech", "business", "innovation", "growth", "strategy"]
        return [f"#{tag}" for tag in base_tags[:count]]
