"""
Base Agent class that all specialized agents inherit from.
Provides core functionality for agent execution, memory management,
communication, and performance tracking.
"""

import uuid
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod

from crewai import Agent
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from loguru import logger

from backend.config import settings
from backend.memory import redis_manager, postgres_manager


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.

    Attributes:
        agent_id: Unique identifier for the agent instance
        agent_type: Type/name of the agent (e.g., 'research', 'analysis')
        role: Agent's role description
        goal: Agent's primary objective
        backstory: Agent's background context
        tools: List of tools available to the agent
        memory: Agent's memory store
    """

    def __init__(
        self,
        agent_type: str,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        verbose: bool = True,
        allow_delegation: bool = True,
        max_iterations: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize the base agent.

        Args:
            agent_type: Type identifier for the agent
            role: Role description
            goal: Primary objective
            backstory: Background context
            tools: List of tools available to the agent
            verbose: Enable verbose logging
            allow_delegation: Allow agent to delegate tasks
            max_iterations: Maximum number of iterations
            **kwargs: Additional agent configuration
        """
        self.agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self.max_iterations = max_iterations or settings.max_agent_iterations

        # Performance tracking
        self.execution_count = 0
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.success_count = 0
        self.failure_count = 0

        # Memory stores
        self.short_term_memory: List[Dict[str, Any]] = []
        self.episodic_memory: List[Dict[str, Any]] = []

        # Initialize CrewAI agent
        self.crew_agent = self._create_crew_agent(**kwargs)

        logger.info(f"Initialized {self.agent_type} agent: {self.agent_id}")

    def _create_crew_agent(self, **kwargs) -> Agent:
        """
        Create the underlying CrewAI agent.

        Args:
            **kwargs: Additional configuration for CrewAI agent

        Returns:
            Configured CrewAI Agent instance
        """
        # Determine which model to use based on agent type
        model = self._get_model_for_agent()

        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=self.tools,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation,
            max_iter=self.max_iterations,
            llm=model,
            **kwargs,
        )

    def _get_model_for_agent(self) -> str:
        """
        Determine which LLM model to use based on agent type.
        Reasoning agents use GPT-4, execution agents use GPT-3.5.

        Returns:
            Model name string
        """
        # Reasoning-heavy agents use the more powerful model
        reasoning_agents = ['research', 'analysis', 'planning', 'coordinator']

        if self.agent_type in reasoning_agents:
            return settings.reasoning_model
        else:
            return settings.execution_model

    @abstractmethod
    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a specific task.

        Args:
            task: Task description
            context: Additional context for task execution

        Returns:
            Task execution result
        """
        pass

    async def run(
        self,
        task: str,
        workflow_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Main execution method that wraps task execution with tracking and error handling.

        Args:
            task: Task description
            workflow_id: ID of the parent workflow
            context: Additional context

        Returns:
            Execution result with metadata
        """
        execution_id = f"{self.agent_id}_{uuid.uuid4().hex[:8]}"
        start_time = datetime.utcnow()

        logger.info(f"Agent {self.agent_id} starting task: {task[:100]}...")

        # Create execution record
        if settings.enable_audit_trail:
            postgres_manager.create_agent_execution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                task=task,
                metadata=context or {},
            )

        try:
            # Load relevant memories
            await self._load_relevant_memories(task)

            # Execute the task
            result = await self.execute_task(task, context)

            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()

            # Update metrics
            self.execution_count += 1
            self.success_count += 1

            # Save to short-term memory
            await self._save_to_short_term_memory(task, result)

            # Update execution record
            if settings.enable_audit_trail:
                postgres_manager.update_agent_execution(
                    execution_id=execution_id,
                    status="completed",
                    result=result,
                    completed_at=datetime.utcnow(),
                    duration_seconds=duration,
                    tokens_used=result.get("tokens_used", 0),
                    cost=result.get("cost", 0.0),
                )

            # Record metrics
            if settings.enable_agent_metrics:
                await self._record_metrics(duration, result)

            logger.info(
                f"Agent {self.agent_id} completed task successfully in {duration:.2f}s"
            )

            return {
                "success": True,
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "execution_id": execution_id,
                "result": result,
                "duration_seconds": duration,
                "metadata": {
                    "tokens_used": result.get("tokens_used", 0),
                    "cost": result.get("cost", 0.0),
                },
            }

        except Exception as e:
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()

            # Update failure metrics
            self.execution_count += 1
            self.failure_count += 1

            # Update execution record
            if settings.enable_audit_trail:
                postgres_manager.update_agent_execution(
                    execution_id=execution_id,
                    status="failed",
                    completed_at=datetime.utcnow(),
                    duration_seconds=duration,
                    error_message=str(e),
                )

            logger.error(f"Agent {self.agent_id} failed: {e}")

            return {
                "success": False,
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "execution_id": execution_id,
                "error": str(e),
                "duration_seconds": duration,
            }

    async def _load_relevant_memories(self, task: str):
        """
        Load relevant memories from Redis and PostgreSQL.

        Args:
            task: Current task to find relevant memories for
        """
        try:
            # Load short-term memory from Redis
            short_term = await redis_manager.get_agent_memory(
                self.agent_id,
                "short_term",
            )
            if short_term:
                self.short_term_memory = short_term

            # Load long-term memories from PostgreSQL
            if settings.enable_long_term_memory:
                long_term = postgres_manager.get_agent_memories(
                    agent_id=self.agent_id,
                    memory_type="long_term",
                    limit=10,
                )
                # Process and add to context
                logger.debug(f"Loaded {len(long_term)} long-term memories")

        except Exception as e:
            logger.error(f"Error loading memories: {e}")

    async def _save_to_short_term_memory(
        self,
        task: str,
        result: Dict[str, Any],
    ):
        """
        Save task and result to short-term memory.

        Args:
            task: Task description
            result: Task result
        """
        try:
            memory_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "task": task,
                "result": result,
            }

            await redis_manager.append_to_agent_memory(
                self.agent_id,
                "short_term",
                memory_entry,
            )

            # Keep only last 20 entries in short-term memory
            if len(self.short_term_memory) > 20:
                self.short_term_memory = self.short_term_memory[-20:]
                await redis_manager.save_agent_memory(
                    self.agent_id,
                    "short_term",
                    self.short_term_memory,
                )

        except Exception as e:
            logger.error(f"Error saving to short-term memory: {e}")

    async def save_to_long_term_memory(
        self,
        content: Dict[str, Any],
        importance_score: float = 0.5,
        tags: Optional[List[str]] = None,
    ):
        """
        Save important information to long-term memory in PostgreSQL.

        Args:
            content: Memory content
            importance_score: Importance score (0-1)
            tags: Tags for categorization
        """
        if not settings.enable_long_term_memory:
            return

        try:
            memory_id = f"{self.agent_id}_{uuid.uuid4().hex[:12]}"

            postgres_manager.save_agent_memory(
                memory_id=memory_id,
                agent_id=self.agent_id,
                memory_type="long_term",
                content=content,
                importance_score=importance_score,
                tags=tags or [],
            )

            logger.debug(f"Saved to long-term memory: {memory_id}")

        except Exception as e:
            logger.error(f"Error saving to long-term memory: {e}")

    async def _record_metrics(self, duration: float, result: Dict[str, Any]):
        """
        Record performance metrics.

        Args:
            duration: Task duration in seconds
            result: Task result
        """
        try:
            metric_id = f"{self.agent_type}_{uuid.uuid4().hex[:8]}"

            # Record duration metric
            postgres_manager.record_agent_metric(
                metric_id=f"{metric_id}_duration",
                agent_type=self.agent_type,
                metric_name="task_duration",
                metric_value=duration,
                aggregation_period="hourly",
            )

            # Record success rate
            success_rate = (
                self.success_count / self.execution_count
                if self.execution_count > 0
                else 0
            )
            postgres_manager.record_agent_metric(
                metric_id=f"{metric_id}_success_rate",
                agent_type=self.agent_type,
                metric_name="success_rate",
                metric_value=success_rate,
                aggregation_period="hourly",
            )

        except Exception as e:
            logger.error(f"Error recording metrics: {e}")

    async def communicate(
        self,
        recipient_agent_id: str,
        message: Dict[str, Any],
        priority: str = "normal",
    ):
        """
        Send a message to another agent via Redis pub/sub.

        Args:
            recipient_agent_id: Target agent ID
            message: Message content
            priority: Message priority (low, normal, high)
        """
        try:
            channel = f"agent:{recipient_agent_id}:inbox"

            message_envelope = {
                "from": self.agent_id,
                "to": recipient_agent_id,
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat(),
                "content": message,
            }

            await redis_manager.publish(channel, message_envelope)

            logger.debug(
                f"Agent {self.agent_id} sent message to {recipient_agent_id}"
            )

        except Exception as e:
            logger.error(f"Error communicating with agent: {e}")

    async def request_human_approval(
        self,
        workflow_id: str,
        action_description: str,
        action_data: Dict[str, Any],
        impact_level: str = "medium",
    ) -> bool:
        """
        Request human approval for high-impact actions.

        Args:
            workflow_id: Parent workflow ID
            action_description: Description of the action
            action_data: Action details
            impact_level: Impact level (low, medium, high)

        Returns:
            bool: True if approved, False if rejected
        """
        if not settings.enable_human_in_loop:
            return True

        try:
            approval_id = f"approval_{uuid.uuid4().hex[:12]}"

            # Create approval request
            approval = postgres_manager.create_approval_request(
                approval_id=approval_id,
                workflow_id=workflow_id,
                agent_id=self.agent_id,
                action_description=action_description,
                action_data=action_data,
                impact_level=impact_level,
            )

            logger.info(
                f"Agent {self.agent_id} requested approval: {approval_id}"
            )

            # In a real implementation, this would wait for human approval
            # For now, we'll return True for demonstration
            # TODO: Implement WebSocket notification and wait for approval

            return True

        except Exception as e:
            logger.error(f"Error requesting approval: {e}")
            return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get agent performance statistics.

        Returns:
            Dictionary of performance metrics
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": (
                self.success_count / self.execution_count
                if self.execution_count > 0
                else 0
            ),
            "total_tokens_used": self.total_tokens_used,
            "total_cost": self.total_cost,
        }

    def __repr__(self) -> str:
        """String representation of the agent."""
        return (
            f"<{self.__class__.__name__}("
            f"id={self.agent_id}, "
            f"type={self.agent_type}, "
            f"executions={self.execution_count})>"
        )
