"""
Content Marketing Campaign Workflow
Creates complete content marketing campaigns with multiple posts.
"""

from typing import Dict, Any
from loguru import logger

from backend.workflows.base_workflow import BaseWorkflow
from backend.agents import (
    PlanningAgent,
    ResearchAgent,
    ContentCreatorAgent,
    AnalysisAgent,
    QAAgent,
    OutreachAgent,
)


class ContentCampaignWorkflow(BaseWorkflow):
    """
    Content Marketing Campaign Workflow.

    Input:
        - topic: Campaign topic
        - duration_weeks: Campaign duration
        - platforms: Target platforms (blog, social media, email)
        - target_audience: Target audience description

    Output:
        - Campaign strategy and plan
        - 20+ content pieces (blog posts, social media, emails)
        - Publishing calendar
        - Performance tracking setup

    Expected Duration: ~30 minutes
    """

    def __init__(self):
        """Initialize the Content Campaign Workflow."""
        super().__init__(
            workflow_type="content_campaign",
            name="Content Marketing Campaign",
            description="Create comprehensive content marketing campaigns",
        )

        # Initialize agents
        self.planning_agent = PlanningAgent()
        self.research_agent = ResearchAgent()
        self.content_agent = ContentCreatorAgent()
        self.analysis_agent = AnalysisAgent()
        self.qa_agent = QAAgent()
        self.outreach_agent = OutreachAgent()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the content campaign workflow."""
        topic = input_data.get("topic")
        duration_weeks = input_data.get("duration_weeks", 4)
        platforms = input_data.get("platforms", ["blog", "linkedin", "email"])
        target_audience = input_data.get("target_audience", "general")

        logger.info(f"Creating content campaign for: {topic}")

        # Phase 1: Planning
        campaign_plan = await self._create_campaign_plan(
            topic,
            duration_weeks,
            platforms,
            target_audience,
        )

        # Phase 2: Research
        research = await self._conduct_research(topic, target_audience)

        # Phase 3: Content Creation
        content = await self._create_content(
            topic,
            campaign_plan,
            research,
            platforms,
        )

        # Phase 4: Analysis & Optimization
        analysis = await self._analyze_campaign(content)

        # Phase 5: QA Review
        qa_results = await self._quality_review(content)

        # Phase 6: Distribution Setup
        distribution = await self._setup_distribution(content, platforms)

        return {
            "topic": topic,
            "campaign_plan": campaign_plan,
            "research_insights": research,
            "content_pieces": content,
            "total_pieces": len(content.get("all_content", [])),
            "analysis": analysis,
            "qa_results": qa_results,
            "distribution_plan": distribution,
            "duration_weeks": duration_weeks,
        }

    async def _create_campaign_plan(
        self,
        topic: str,
        duration: int,
        platforms: List[str],
        audience: str,
    ) -> Dict[str, Any]:
        """Create campaign strategy and plan."""
        plan = await self.planning_agent.run(
            task=f"Create content marketing campaign plan for {topic}",
            workflow_id=self.workflow_id,
            context={
                "planning_type": "project",
                "duration_weeks": duration,
                "platforms": platforms,
                "target_audience": audience,
            },
        )
        return plan.get("result", {})

    async def _conduct_research(self, topic: str, audience: str) -> Dict[str, Any]:
        """Research topic and audience."""
        research = await self.research_agent.run(
            task=f"Research {topic} and {audience} interests",
            workflow_id=self.workflow_id,
            context={"research_type": "general", "num_sources": 10},
        )
        return research.get("result", {})

    async def _create_content(
        self,
        topic: str,
        plan: Dict[str, Any],
        research: Dict[str, Any],
        platforms: List[str],
    ) -> Dict[str, Any]:
        """Create all content pieces."""
        all_content = []

        # Blog posts
        if "blog" in platforms:
            blog_posts = await self.content_agent.run(
                task=f"Create 5 blog posts about {topic}",
                workflow_id=self.workflow_id,
                context={
                    "content_type": "blog_post",
                    "count": 5,
                    "research": research,
                },
            )
            all_content.append({"type": "blog", "content": blog_posts})

        # Social media
        if any(p in platforms for p in ["linkedin", "twitter", "facebook"]):
            social_posts = await self.content_agent.run(
                task=f"Create social media content for {topic}",
                workflow_id=self.workflow_id,
                context={
                    "content_type": "social_media",
                    "platform": "linkedin",
                    "post_count": 15,
                },
            )
            all_content.append({"type": "social", "content": social_posts})

        # Email campaigns
        if "email" in platforms:
            emails = await self.content_agent.run(
                task=f"Create email campaign for {topic}",
                workflow_id=self.workflow_id,
                context={
                    "content_type": "email",
                    "series_count": 5,
                },
            )
            all_content.append({"type": "email", "content": emails})

        return {"all_content": all_content}

    async def _analyze_campaign(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign content."""
        analysis = await self.analysis_agent.run(
            task="Analyze content campaign effectiveness",
            workflow_id=self.workflow_id,
            context={
                "analysis_type": "descriptive",
                "data": content,
            },
        )
        return analysis.get("result", {})

    async def _quality_review(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """QA review of all content."""
        qa = await self.qa_agent.run(
            task="Review all campaign content",
            workflow_id=self.workflow_id,
            context={"qa_type": "comprehensive", "content": str(content)},
        )
        return qa.get("result", {})

    async def _setup_distribution(
        self,
        content: Dict[str, Any],
        platforms: List[str],
    ) -> Dict[str, Any]:
        """Setup content distribution."""
        distribution = await self.outreach_agent.run(
            task="Setup content distribution schedule",
            workflow_id=self.workflow_id,
            context={
                "outreach_type": "email_campaign",
                "content": content,
                "platforms": platforms,
            },
        )
        return distribution.get("result", {})
