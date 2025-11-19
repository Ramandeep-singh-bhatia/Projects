"""Workflows module - Pre-built workflow templates."""

from .base_workflow import BaseWorkflow
from .market_research import MarketResearchWorkflow
from .content_campaign import ContentCampaignWorkflow
from .lead_generation import LeadGenerationWorkflow
from .product_launch import ProductLaunchWorkflow
from .customer_support import CustomerSupportWorkflow

__all__ = [
    "BaseWorkflow",
    "MarketResearchWorkflow",
    "ContentCampaignWorkflow",
    "LeadGenerationWorkflow",
    "ProductLaunchWorkflow",
    "CustomerSupportWorkflow",
]
