"""
Demo script to showcase all 5 pre-built workflows.
Run this to see the Multi-Agent System in action!
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.workflows import (
    MarketResearchWorkflow,
    ContentCampaignWorkflow,
    LeadGenerationWorkflow,
    ProductLaunchWorkflow,
    CustomerSupportWorkflow,
)
from backend.memory import redis_manager, postgres_manager
from loguru import logger


async def demo_market_research():
    """Demo: Market Research & Competitive Analysis"""
    print("\n" + "=" * 80)
    print("DEMO 1: Market Research & Competitive Analysis")
    print("=" * 80 + "\n")

    workflow = MarketResearchWorkflow()

    input_data = {
        "industry": "Enterprise SaaS",
        "competitors": ["Salesforce", "HubSpot", "Microsoft Dynamics"],
        "focus_areas": ["products", "pricing", "market_share", "customer_satisfaction"],
    }

    print(f"Input: {input_data}\n")
    print("Executing workflow...")

    result = await workflow.run(input_data)

    print(f"\nWorkflow ID: {result.get('workflow_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")

    if result.get("success"):
        print("\n✅ Market Research Completed!")
        print(f"Report Pages: {result['results'].get('report_pages', 20)}")
        print(f"Quality Score: {result['results'].get('quality_score', 0):.2f}")
    else:
        print(f"\n❌ Workflow failed: {result.get('error')}")

    return result


async def demo_content_campaign():
    """Demo: Content Marketing Campaign"""
    print("\n" + "=" * 80)
    print("DEMO 2: Content Marketing Campaign")
    print("=" * 80 + "\n")

    workflow = ContentCampaignWorkflow()

    input_data = {
        "topic": "AI-Powered Business Automation",
        "duration_weeks": 4,
        "platforms": ["blog", "linkedin", "twitter", "email"],
        "target_audience": "CTOs and IT decision makers",
    }

    print(f"Input: {input_data}\n")
    print("Executing workflow...")

    result = await workflow.run(input_data)

    print(f"\nWorkflow ID: {result.get('workflow_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")

    if result.get("success"):
        print("\n✅ Content Campaign Created!")
        print(f"Total Content Pieces: {result['results'].get('total_pieces', 20)}")
        print(f"Duration: {result['results'].get('duration_weeks', 4)} weeks")
    else:
        print(f"\n❌ Workflow failed: {result.get('error')}")

    return result


async def demo_lead_generation():
    """Demo: Lead Generation & Outreach"""
    print("\n" + "=" * 80)
    print("DEMO 3: Lead Generation & Outreach")
    print("=" * 80 + "\n")

    workflow = LeadGenerationWorkflow()

    input_data = {
        "icp_criteria": {
            "industry": "Technology",
            "company_size": "50-500 employees",
            "role": "VP Engineering, CTO",
        },
        "target_count": 100,
        "industry": "SaaS",
    }

    print(f"Input: {input_data}\n")
    print("Executing workflow...")

    result = await workflow.run(input_data)

    print(f"\nWorkflow ID: {result.get('workflow_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")

    if result.get("success"):
        print("\n✅ Lead Generation Completed!")
        print(f"Leads Identified: {result['results'].get('total_leads_identified', 100)}")
        print(
            f"Expected Response Rate: {result['results'].get('expected_response_rate', 0.25) * 100:.1f}%"
        )
    else:
        print(f"\n❌ Workflow failed: {result.get('error')}")

    return result


async def demo_product_launch():
    """Demo: Product Launch Preparation"""
    print("\n" + "=" * 80)
    print("DEMO 4: Product Launch Preparation")
    print("=" * 80 + "\n")

    workflow = ProductLaunchWorkflow()

    input_data = {
        "product_name": "AI Workflow Automation Platform",
        "launch_date": "2025-03-15",
        "target_audience": "Enterprise businesses",
    }

    print(f"Input: {input_data}\n")
    print("Executing workflow...")

    result = await workflow.run(input_data)

    print(f"\nWorkflow ID: {result.get('workflow_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")

    if result.get("success"):
        print("\n✅ Product Launch Package Ready!")
        print(f"Launch Date: {result['results'].get('launch_date')}")
        print(f"QA Approved: {result['results'].get('qa_approved', False)}")
    else:
        print(f"\n❌ Workflow failed: {result.get('error')}")

    return result


async def demo_customer_support():
    """Demo: Customer Support Escalation"""
    print("\n" + "=" * 80)
    print("DEMO 5: Customer Support Escalation")
    print("=" * 80 + "\n")

    workflow = CustomerSupportWorkflow()

    input_data = {
        "issue_description": "Customer unable to access dashboard after recent update",
        "customer_info": {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "company": "TechCorp Inc.",
        },
        "priority": "high",
    }

    print(f"Input: {input_data}\n")
    print("Executing workflow...")

    result = await workflow.run(input_data)

    print(f"\nWorkflow ID: {result.get('workflow_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")

    if result.get("success"):
        print("\n✅ Customer Issue Resolved!")
        print(f"Quality Score: {result['results'].get('quality_score', 0):.2f}")
        print(f"Predicted CSAT: {result['results'].get('csat_predicted', 0) * 100:.1f}%")
        print(f"Status: {result['results'].get('resolution_status', 'resolved')}")
    else:
        print(f"\n❌ Workflow failed: {result.get('error')}")

    return result


async def main():
    """Main demo function."""
    print("\n" + "=" * 80)
    print(" 🤖 MULTI-AGENT BUSINESS AUTOMATION SYSTEM - DEMO")
    print("=" * 80)
    print("\nThis demo will execute all 5 pre-built workflows:")
    print("1. Market Research & Competitive Analysis")
    print("2. Content Marketing Campaign")
    print("3. Lead Generation & Outreach")
    print("4. Product Launch Preparation")
    print("5. Customer Support Escalation")
    print("\n" + "=" * 80 + "\n")

    # Initialize connections
    print("Initializing system...")
    try:
        await redis_manager.connect()
        postgres_manager.connect()
        postgres_manager.create_tables()
        print("✅ System initialized successfully!\n")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return

    results = []

    try:
        # Run all demos
        results.append(await demo_market_research())
        results.append(await demo_content_campaign())
        results.append(await demo_lead_generation())
        results.append(await demo_product_launch())
        results.append(await demo_customer_support())

        # Summary
        print("\n" + "=" * 80)
        print(" 📊 DEMO SUMMARY")
        print("=" * 80 + "\n")

        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful

        print(f"Total Workflows Executed: {len(results)}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")

        total_duration = sum(r.get("duration_seconds", 0) for r in results)
        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")

        print("\n" + "=" * 80)
        print(" ✨ Demo Complete!")
        print("=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        logger.exception(e)
    finally:
        # Cleanup
        print("\nCleaning up...")
        await redis_manager.disconnect()
        postgres_manager.disconnect()
        print("✅ Cleanup complete\n")


if __name__ == "__main__":
    asyncio.run(main())
