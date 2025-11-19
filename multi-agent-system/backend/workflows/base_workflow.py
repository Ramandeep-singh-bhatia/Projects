"""
Base Workflow class that all workflows inherit from.
Provides common functionality for workflow execution and management.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from loguru import logger

from backend.memory import redis_manager, postgres_manager
from backend.config import settings


class BaseWorkflow(ABC):
    """
    Base class for all workflows in the system.

    Attributes:
        workflow_id: Unique identifier for the workflow
        workflow_type: Type of workflow
        status: Current workflow status
        results: Workflow execution results
    """

    def __init__(
        self,
        workflow_type: str,
        name: str,
        description: str,
    ):
        """
        Initialize the base workflow.

        Args:
            workflow_type: Type identifier for the workflow
            name: Workflow name
            description: Workflow description
        """
        self.workflow_id = f"{workflow_type}_{uuid.uuid4().hex[:12]}"
        self.workflow_type = workflow_type
        self.name = name
        self.description = description
        self.status = "initialized"
        self.results: Dict[str, Any] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @abstractmethod
    async def execute(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute the workflow.

        Args:
            input_data: Input data for the workflow

        Returns:
            Workflow execution results
        """
        pass

    async def run(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Main workflow execution wrapper with error handling and tracking.

        Args:
            input_data: Input data for the workflow

        Returns:
            Workflow results with metadata
        """
        self.start_time = datetime.utcnow()
        self.status = "running"

        logger.info(
            f"Starting workflow {self.workflow_id} ({self.workflow_type})"
        )

        # Create workflow execution record
        if settings.enable_audit_trail:
            postgres_manager.create_workflow_execution(
                workflow_id=self.workflow_id,
                workflow_type=self.workflow_type,
                input_data=input_data,
                metadata={"name": self.name, "description": self.description},
            )

        # Save initial state to Redis
        await redis_manager.save_workflow_state(
            self.workflow_id,
            {
                "type": self.workflow_type,
                "status": "running",
                "input_data": input_data,
                "started_at": self.start_time.isoformat(),
            },
        )

        try:
            # Execute the workflow
            self.results = await self.execute(input_data)

            # Mark as completed
            self.status = "completed"
            self.end_time = datetime.utcnow()
            duration = (self.end_time - self.start_time).total_seconds()

            # Update workflow state
            await redis_manager.update_workflow_state(
                self.workflow_id,
                {
                    "status": "completed",
                    "results": self.results,
                    "completed_at": self.end_time.isoformat(),
                    "duration_seconds": duration,
                },
            )

            # Update database record
            if settings.enable_audit_trail:
                postgres_manager.update_workflow_execution(
                    workflow_id=self.workflow_id,
                    status="completed",
                    output_data=self.results,
                    completed_at=self.end_time,
                    duration_seconds=duration,
                )

            logger.info(
                f"Workflow {self.workflow_id} completed successfully in {duration:.2f}s"
            )

            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "workflow_type": self.workflow_type,
                "status": self.status,
                "results": self.results,
                "duration_seconds": duration,
                "metadata": {
                    "started_at": self.start_time.isoformat(),
                    "completed_at": self.end_time.isoformat(),
                },
            }

        except Exception as e:
            # Mark as failed
            self.status = "failed"
            self.end_time = datetime.utcnow()
            duration = (self.end_time - self.start_time).total_seconds()

            # Update workflow state
            await redis_manager.update_workflow_state(
                self.workflow_id,
                {
                    "status": "failed",
                    "error": str(e),
                    "failed_at": self.end_time.isoformat(),
                    "duration_seconds": duration,
                },
            )

            # Update database record
            if settings.enable_audit_trail:
                postgres_manager.update_workflow_execution(
                    workflow_id=self.workflow_id,
                    status="failed",
                    completed_at=self.end_time,
                    duration_seconds=duration,
                    error_message=str(e),
                )

            logger.error(f"Workflow {self.workflow_id} failed: {e}")

            return {
                "success": False,
                "workflow_id": self.workflow_id,
                "workflow_type": self.workflow_type,
                "status": self.status,
                "error": str(e),
                "duration_seconds": duration,
            }

    async def checkpoint(self, checkpoint_data: Dict[str, Any]):
        """
        Save a workflow checkpoint.

        Args:
            checkpoint_data: Data to save in checkpoint
        """
        if not settings.enable_workflow_checkpointing:
            return

        checkpoint_key = f"checkpoint:{self.workflow_id}:{datetime.now().timestamp()}"

        await redis_manager.set(
            checkpoint_key,
            {
                "workflow_id": self.workflow_id,
                "timestamp": datetime.now().isoformat(),
                "data": checkpoint_data,
            },
            ttl=3600,  # 1 hour TTL
        )

        logger.debug(f"Checkpoint saved for workflow {self.workflow_id}")

    async def get_state(self) -> Optional[Dict[str, Any]]:
        """
        Get current workflow state from Redis.

        Returns:
            Workflow state or None
        """
        return await redis_manager.get_workflow_state(self.workflow_id)

    def __repr__(self) -> str:
        """String representation of the workflow."""
        return (
            f"<{self.__class__.__name__}("
            f"id={self.workflow_id}, "
            f"type={self.workflow_type}, "
            f"status={self.status})>"
        )
