"""Agent API endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.agents import (
    ResearchAgent,
    AnalysisAgent,
    PlanningAgent,
    ContentCreatorAgent,
    OutreachAgent,
    QAAgent,
    CoordinatorAgent,
)
from backend.memory import postgres_manager

router = APIRouter()


# Agent registry
AGENT_REGISTRY = {
    "research": ResearchAgent,
    "analysis": AnalysisAgent,
    "planning": PlanningAgent,
    "content": ContentCreatorAgent,
    "outreach": OutreachAgent,
    "qa": QAAgent,
    "coordinator": CoordinatorAgent,
}


class AgentTaskRequest(BaseModel):
    """Request model for agent task execution."""

    agent_type: str = Field(..., description="Type of agent to use")
    task: str = Field(..., description="Task description")
    workflow_id: str = Field(..., description="Workflow ID")
    context: Dict[str, Any] = Field(default={}, description="Task context")


@router.get("/")
async def list_agents():
    """
    List all available agents.
    """
    agents = []

    for agent_type, agent_class in AGENT_REGISTRY.items():
        # Instantiate to get metadata
        agent = agent_class()

        agents.append({
            "type": agent_type,
            "role": agent.role,
            "goal": agent.goal,
            "capabilities": agent.backstory[:200] + "...",
        })

    return {
        "total": len(agents),
        "agents": agents,
    }


@router.post("/execute")
async def execute_agent_task(request: AgentTaskRequest):
    """
    Execute a task with a specific agent.

    Args:
        request: Agent task request

    Returns:
        Task execution result
    """
    agent_type = request.agent_type
    task = request.task
    workflow_id = request.workflow_id
    context = request.context

    # Get agent class
    agent_class = AGENT_REGISTRY.get(agent_type)

    if not agent_class:
        raise HTTPException(
            status_code=404,
            detail=f"Agent type '{agent_type}' not found",
        )

    # Instantiate and execute
    agent = agent_class()

    try:
        result = await agent.run(task, workflow_id, context)

        return {
            "agent_id": agent.agent_id,
            "agent_type": agent_type,
            "result": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}",
        )


@router.get("/{agent_type}/metrics")
async def get_agent_metrics(agent_type: str):
    """
    Get performance metrics for a specific agent type.

    Args:
        agent_type: Agent type

    Returns:
        Agent performance metrics
    """
    if agent_type not in AGENT_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Agent type '{agent_type}' not found",
        )

    # Get metrics from PostgreSQL
    session = postgres_manager.get_session()

    try:
        from backend.memory.postgres_manager import AgentExecution, AgentMetric

        # Get execution statistics
        executions = (
            session.query(AgentExecution)
            .filter_by(agent_type=agent_type)
            .all()
        )

        total_executions = len(executions)
        successful = sum(1 for e in executions if e.status == "completed")
        failed = sum(1 for e in executions if e.status == "failed")
        avg_duration = (
            sum(e.duration_seconds for e in executions if e.duration_seconds) / total_executions
            if total_executions > 0 else 0
        )

        # Get recent metrics
        metrics = (
            session.query(AgentMetric)
            .filter_by(agent_type=agent_type)
            .order_by(AgentMetric.recorded_at.desc())
            .limit(10)
            .all()
        )

        return {
            "agent_type": agent_type,
            "statistics": {
                "total_executions": total_executions,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / total_executions if total_executions > 0 else 0,
                "average_duration_seconds": avg_duration,
            },
            "recent_metrics": [
                {
                    "metric_name": m.metric_name,
                    "value": m.metric_value,
                    "recorded_at": m.recorded_at.isoformat(),
                }
                for m in metrics
            ],
        }
    finally:
        session.close()


@router.get("/executions/recent")
async def get_recent_executions(limit: int = 20):
    """
    Get recent agent executions across all agents.

    Args:
        limit: Maximum number of executions to return

    Returns:
        Recent agent executions
    """
    session = postgres_manager.get_session()

    try:
        from backend.memory.postgres_manager import AgentExecution

        executions = (
            session.query(AgentExecution)
            .order_by(AgentExecution.created_at.desc())
            .limit(limit)
            .all()
        )

        return {
            "total": len(executions),
            "executions": [
                {
                    "execution_id": exec.execution_id,
                    "agent_type": exec.agent_type,
                    "workflow_id": exec.workflow_id,
                    "status": exec.status,
                    "started_at": exec.started_at.isoformat(),
                    "duration_seconds": exec.duration_seconds,
                }
                for exec in executions
            ],
        }
    finally:
        session.close()
