"""
Market Research & Competitive Analysis Workflow
Generates comprehensive market analysis reports using multiple agents.
"""

from typing import Dict, Any
from loguru import logger

from backend.workflows.base_workflow import BaseWorkflow
from backend.agents import (
    ResearchAgent,
    AnalysisAgent,
    ContentCreatorAgent,
    QAAgent,
    CoordinatorAgent,
)


class MarketResearchWorkflow(BaseWorkflow):
    """
    Market Research & Competitive Analysis Workflow.

    Input:
        - industry: Industry/market to research
        - competitors: List of competitor names
        - focus_areas: Areas to focus on (e.g., products, pricing, market share)

    Output:
        - 20-page analysis report
        - Competitive landscape overview
        - Market trends and insights
        - Strategic recommendations

    Expected Duration: ~15 minutes
    """

    def __init__(self):
        """Initialize the Market Research Workflow."""
        super().__init__(
            workflow_type="market_research",
            name="Market Research & Competitive Analysis",
            description="Generate comprehensive market research and competitive analysis reports",
        )

        # Initialize agents
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.content_agent = ContentCreatorAgent()
        self.qa_agent = QAAgent()
        self.coordinator = CoordinatorAgent()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the market research workflow.

        Args:
            input_data: Input containing industry, competitors, focus_areas

        Returns:
            Market research report and analysis
        """
        industry = input_data.get("industry")
        competitors = input_data.get("competitors", [])
        focus_areas = input_data.get("focus_areas", ["products", "pricing", "market_share"])

        logger.info(f"Starting market research for {industry}")

        # Phase 1: Research
        logger.info("Phase 1: Conducting research")
        research_results = await self._conduct_research(
            industry,
            competitors,
            focus_areas,
        )

        await self.checkpoint({"phase": "research_completed", "results": research_results})

        # Phase 2: Analysis
        logger.info("Phase 2: Analyzing data")
        analysis_results = await self._analyze_data(
            research_results,
            industry,
        )

        await self.checkpoint({"phase": "analysis_completed", "results": analysis_results})

        # Phase 3: Content Creation
        logger.info("Phase 3: Creating report")
        report = await self._create_report(
            industry,
            competitors,
            research_results,
            analysis_results,
        )

        await self.checkpoint({"phase": "content_created", "report": report})

        # Phase 4: Quality Assurance
        logger.info("Phase 4: Quality assurance")
        qa_results = await self._quality_assurance(report)

        # Final output
        return {
            "industry": industry,
            "competitors": competitors,
            "research_findings": research_results,
            "analysis": analysis_results,
            "report": report,
            "qa_results": qa_results,
            "report_pages": 20,
            "quality_score": qa_results.get("results", {}).get("quality", {}).get("overall_score", 0),
        }

    async def _conduct_research(
        self,
        industry: str,
        competitors: List[str],
        focus_areas: List[str],
    ) -> Dict[str, Any]:
        """Phase 1: Conduct market research."""
        # Industry overview research
        industry_research = await self.research_agent.run(
            task=f"Research {industry} industry overview, trends, and market size",
            workflow_id=self.workflow_id,
            context={
                "research_type": "web_search",
                "num_sources": 15,
            },
        )

        # Competitive research
        competitive_research = await self.research_agent.run(
            task=f"Conduct competitive analysis",
            workflow_id=self.workflow_id,
            context={
                "research_type": "competitive_analysis",
                "competitors": competitors,
                "focus_areas": focus_areas,
            },
        )

        return {
            "industry_overview": industry_research.get("result", {}),
            "competitive_analysis": competitive_research.get("result", {}),
        }

    async def _analyze_data(
        self,
        research_results: Dict[str, Any],
        industry: str,
    ) -> Dict[str, Any]:
        """Phase 2: Analyze research data."""
        # Prepare data for analysis
        analysis_data = {
            "industry": industry,
            "research_findings": research_results,
        }

        analysis = await self.analysis_agent.run(
            task="Analyze market research data and identify key insights",
            workflow_id=self.workflow_id,
            context={
                "analysis_type": "comprehensive",
                "data": analysis_data,
            },
        )

        return analysis.get("result", {})

    async def _create_report(
        self,
        industry: str,
        competitors: List[str],
        research: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Phase 3: Create market research report."""
        report = await self.content_agent.run(
            task=f"Create comprehensive market research report for {industry}",
            workflow_id=self.workflow_id,
            context={
                "content_type": "report",
                "research_data": research,
                "analysis_data": analysis,
                "competitors": competitors,
            },
        )

        return report.get("result", {})

    async def _quality_assurance(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Quality assurance review."""
        qa = await self.qa_agent.run(
            task="Review market research report for quality and accuracy",
            workflow_id=self.workflow_id,
            context={
                "qa_type": "comprehensive",
                "content": str(report),
            },
        )

        return qa
