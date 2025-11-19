"""Workflow API endpoints."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.workflows import (
    MarketResearchWorkflow,
    ContentCampaignWorkflow,
    LeadGenerationWorkflow,
    ProductLaunchWorkflow,
    CustomerSupportWorkflow,
)
from backend.memory import redis_manager, postgres_manager

router = APIRouter()


# Pydantic models for request/response
class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution."""

    workflow_type: str = Field(..., description="Type of workflow to execute")
    input_data: Dict[str, Any] = Field(..., description="Input data for the workflow")


class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution."""

    workflow_id: str
    workflow_type: str
    status: str
    message: str


# Workflow registry
WORKFLOW_REGISTRY = {
    "market_research": MarketResearchWorkflow,
    "content_campaign": ContentCampaignWorkflow,
    "lead_generation": LeadGenerationWorkflow,
    "product_launch": ProductLaunchWorkflow,
    "customer_support": CustomerSupportWorkflow,
}


@router.get("/")
async def list_workflows():
    """
    List all available workflows.
    """
    workflows = []

    for workflow_type, workflow_class in WORKFLOW_REGISTRY.items():
        # Instantiate to get metadata
        workflow = workflow_class()

        workflows.append({
            "type": workflow_type,
            "name": workflow.name,
            "description": workflow.description,
        })

    return {
        "total": len(workflows),
        "workflows": workflows,
    }


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    """
    Execute a workflow.

    Args:
        request: Workflow execution request

    Returns:
        Workflow execution response with ID
    """
    workflow_type = request.workflow_type
    input_data = request.input_data

    # Get workflow class
    workflow_class = WORKFLOW_REGISTRY.get(workflow_type)

    if not workflow_class:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow type '{workflow_type}' not found",
        )

    # Instantiate and execute workflow
    workflow = workflow_class()

    # Start execution (async, non-blocking)
    try:
        # Execute workflow
        result = await workflow.run(input_data)

        return WorkflowExecutionResponse(
            workflow_id=workflow.workflow_id,
            workflow_type=workflow_type,
            status=result.get("status", "unknown"),
            message=f"Workflow {workflow.workflow_id} executed successfully" if result.get("success") else "Workflow execution failed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}",
        )


@router.get("/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get workflow status and results.

    Args:
        workflow_id: Workflow ID

    Returns:
        Workflow status and results
    """
    # Get workflow state from Redis
    state = await redis_manager.get_workflow_state(workflow_id)

    if not state:
        # Try PostgreSQL
        execution = postgres_manager.get_workflow_execution(workflow_id)

        if not execution:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow {workflow_id} not found",
            )

        return {
            "workflow_id": workflow_id,
            "type": execution.workflow_type,
            "status": execution.status,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "duration_seconds": execution.duration_seconds,
            "results": execution.output_data,
        }

    return {
        "workflow_id": workflow_id,
        "state": state,
    }


@router.get("/{workflow_id}/progress")
async def get_workflow_progress(workflow_id: str):
    """
    Get detailed workflow progress.

    Args:
        workflow_id: Workflow ID

    Returns:
        Detailed progress information
    """
    state = await redis_manager.get_workflow_state(workflow_id)

    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found",
        )

    # Calculate progress
    status = state.get("status")
    progress_percentage = 0

    if status == "completed":
        progress_percentage = 100
    elif status == "running":
        # Estimate based on phases completed
        progress_percentage = 50  # Simplified

    return {
        "workflow_id": workflow_id,
        "status": status,
        "progress_percentage": progress_percentage,
        "current_phase": state.get("current_phase"),
        "started_at": state.get("started_at"),
        "estimated_completion": state.get("estimated_completion"),
    }


@router.delete("/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """
    Cancel a running workflow.

    Args:
        workflow_id: Workflow ID

    Returns:
        Cancellation confirmation
    """
    state = await redis_manager.get_workflow_state(workflow_id)

    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found",
        )

    if state.get("status") != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Workflow {workflow_id} is not running (status: {state.get('status')})",
        )

    # Update status to cancelled
    await redis_manager.update_workflow_state(
        workflow_id,
        {"status": "cancelled"},
    )

    return {
        "workflow_id": workflow_id,
        "status": "cancelled",
        "message": f"Workflow {workflow_id} has been cancelled",
    }


@router.get("/history/recent")
async def get_recent_workflows(limit: int = Query(default=10, le=100)):
    """
    Get recent workflow executions.

    Args:
        limit: Maximum number of workflows to return

    Returns:
        List of recent workflows
    """
    # Get from PostgreSQL
    session = postgres_manager.get_session()

    try:
        from backend.memory.postgres_manager import WorkflowExecution

        executions = (
            session.query(WorkflowExecution)
            .order_by(WorkflowExecution.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "total": len(executions),
            "workflows": [
                {
                    "workflow_id": exec.workflow_id,
                    "type": exec.workflow_type,
                    "status": exec.status,
                    "started_at": exec.started_at.isoformat(),
                    "duration_seconds": exec.duration_seconds,
                }
                for exec in executions
            ],
        }
    finally:
        session.close()


@router.post("/{workflow_id}/retry")
async def retry_workflow(workflow_id: str):
    """
    Retry a failed workflow.

    Args:
        workflow_id: Workflow ID

    Returns:
        New workflow execution response
    """
    # Get original workflow
    execution = postgres_manager.get_workflow_execution(workflow_id)

    if not execution:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found",
        )

    if execution.status != "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry workflow with status: {execution.status}",
        )

    # Get workflow class
    workflow_class = WORKFLOW_REGISTRY.get(execution.workflow_type)

    if not workflow_class:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow type '{execution.workflow_type}' not found",
        )

    # Create new workflow instance and execute
    workflow = workflow_class()
    result = await workflow.run(execution.input_data)

    return {
        "original_workflow_id": workflow_id,
        "new_workflow_id": workflow.workflow_id,
        "status": result.get("status"),
    }
