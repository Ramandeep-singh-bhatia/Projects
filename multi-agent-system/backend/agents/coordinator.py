"""
Coordinator Agent - Orchestrates multi-agent workflows and manages agent collaboration.
Capabilities: Task delegation, progress tracking, conflict resolution, output synthesis.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from backend.agents.base_agent import BaseAgent
from backend.memory import redis_manager


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent for workflow orchestration.

    Specializes in:
    - Workflow orchestration and task delegation
    - Progress tracking and monitoring
    - Inter-agent communication facilitation
    - Conflict resolution and decision making
    - Output synthesis and aggregation
    - Bottleneck detection and optimization
    - Adaptive workflow management
    """

    def __init__(self, **kwargs):
        """Initialize the Coordinator Agent."""
        super().__init__(
            agent_type="coordinator",
            role="Senior Workflow Coordinator",
            goal="Orchestrate multi-agent workflows efficiently, ensuring optimal collaboration and timely completion",
            backstory="""You are an expert workflow coordinator with extensive experience
            in managing complex multi-agent systems. You excel at breaking down high-level
            objectives into tasks, delegating to appropriate agents, monitoring progress,
            resolving conflicts, and synthesizing outputs into coherent results. Your
            orchestration ensures efficient, coordinated execution.""",
            tools=[],
            allow_delegation=True,
            **kwargs,
        )

        # Track active workflows and agent assignments
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.agent_assignments: Dict[str, List[str]] = {}

    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a coordination task.

        Args:
            task: Coordination task description
            context: Additional context

        Returns:
            Coordination results
        """
        logger.info(f"Coordinator Agent executing task: {task[:100]}...")

        context = context or {}
        coordination_type = context.get("coordination_type", "orchestration")

        try:
            if coordination_type == "orchestration":
                results = await self._orchestrate_workflow(task, context)
            elif coordination_type == "delegation":
                results = await self._delegate_tasks(task, context)
            elif coordination_type == "monitoring":
                results = await self._monitor_progress(task, context)
            elif coordination_type == "synthesis":
                results = await self._synthesize_outputs(task, context)
            elif coordination_type == "conflict_resolution":
                results = await self._resolve_conflicts(task, context)
            else:
                results = await self._comprehensive_coordination(task, context)

            return {
                "status": "completed",
                "coordination_type": coordination_type,
                "results": results,
                "tokens_used": 0,
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Error in coordination task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "results": None,
            }

    async def _orchestrate_workflow(
        self,
        workflow_goal: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Orchestrate a multi-agent workflow.

        Args:
            workflow_goal: High-level workflow goal
            context: Workflow context

        Returns:
            Orchestration plan
        """
        workflow_id = context.get("workflow_id")
        workflow_type = context.get("workflow_type", "custom")

        # Break down workflow into phases
        phases = self._plan_workflow_phases(workflow_goal, workflow_type)

        # Assign agents to tasks
        agent_assignments = self._assign_agents_to_tasks(phases)

        # Create execution timeline
        timeline = self._create_execution_timeline(phases)

        # Set up monitoring
        monitoring_plan = self._create_monitoring_plan(phases)

        # Save workflow state
        workflow_state = {
            "workflow_id": workflow_id,
            "goal": workflow_goal,
            "type": workflow_type,
            "phases": phases,
            "agent_assignments": agent_assignments,
            "timeline": timeline,
            "status": "planned",
            "created_at": datetime.now().isoformat(),
        }

        if workflow_id:
            await redis_manager.save_workflow_state(workflow_id, workflow_state)
            self.active_workflows[workflow_id] = workflow_state

        return {
            "workflow_id": workflow_id,
            "phases": phases,
            "agent_assignments": agent_assignments,
            "timeline": timeline,
            "monitoring_plan": monitoring_plan,
            "total_tasks": sum(len(phase.get("tasks", [])) for phase in phases),
            "estimated_duration": timeline.get("total_duration"),
        }

    async def _delegate_tasks(
        self,
        delegation_request: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Delegate tasks to appropriate agents.

        Args:
            delegation_request: Task delegation request
            context: Delegation context

        Returns:
            Delegation plan
        """
        tasks = context.get("tasks", [])
        available_agents = context.get("available_agents", [])

        delegations = []

        for task in tasks:
            # Determine best agent for task
            best_agent = self._match_agent_to_task(task, available_agents)

            # Calculate priority
            priority = self._calculate_task_priority(task, tasks)

            delegation = {
                "task_id": task.get("id"),
                "task": task.get("description"),
                "assigned_agent": best_agent,
                "priority": priority,
                "estimated_duration": task.get("estimated_duration", "1 hour"),
                "dependencies": task.get("dependencies", []),
                "status": "assigned",
            }

            delegations.append(delegation)

            # Track assignment
            if best_agent not in self.agent_assignments:
                self.agent_assignments[best_agent] = []
            self.agent_assignments[best_agent].append(task.get("id"))

        return {
            "total_delegations": len(delegations),
            "delegations": delegations,
            "agent_workload": self._calculate_agent_workload(delegations),
        }

    async def _monitor_progress(
        self,
        workflow_id: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Monitor workflow progress.

        Args:
            workflow_id: Workflow to monitor
            context: Monitoring context

        Returns:
            Progress report
        """
        # Get workflow state
        workflow_state = await redis_manager.get_workflow_state(workflow_id)

        if not workflow_state:
            return {
                "error": f"Workflow {workflow_id} not found",
                "status": "not_found",
            }

        # Analyze progress
        phases = workflow_state.get("phases", [])
        completed_tasks = 0
        total_tasks = 0
        current_phase = None

        for phase in phases:
            phase_tasks = phase.get("tasks", [])
            total_tasks += len(phase_tasks)

            completed_in_phase = sum(
                1 for task in phase_tasks
                if task.get("status") == "completed"
            )
            completed_tasks += completed_in_phase

            if completed_in_phase < len(phase_tasks) and not current_phase:
                current_phase = phase.get("name")

        # Calculate progress percentage
        progress_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )

        # Detect bottlenecks
        bottlenecks = self._detect_bottlenecks(workflow_state)

        # Estimate completion time
        estimated_completion = self._estimate_completion_time(
            workflow_state,
            progress_percentage,
        )

        return {
            "workflow_id": workflow_id,
            "status": workflow_state.get("status"),
            "progress_percentage": progress_percentage,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "current_phase": current_phase,
            "bottlenecks": bottlenecks,
            "estimated_completion": estimated_completion,
            "health_score": self._calculate_workflow_health(workflow_state),
        }

    async def _synthesize_outputs(
        self,
        synthesis_goal: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Synthesize outputs from multiple agents.

        Args:
            synthesis_goal: Goal for synthesis
            context: Agent outputs to synthesize

        Returns:
            Synthesized output
        """
        agent_outputs = context.get("agent_outputs", [])

        # Organize outputs by agent type
        outputs_by_type = {}
        for output in agent_outputs:
            agent_type = output.get("agent_type")
            if agent_type not in outputs_by_type:
                outputs_by_type[agent_type] = []
            outputs_by_type[agent_type].append(output)

        # Synthesize by category
        synthesis = {
            "research_findings": self._synthesize_research(
                outputs_by_type.get("research", [])
            ),
            "analysis_insights": self._synthesize_analysis(
                outputs_by_type.get("analysis", [])
            ),
            "plans": self._synthesize_plans(
                outputs_by_type.get("planning", [])
            ),
            "content": self._synthesize_content(
                outputs_by_type.get("content", [])
            ),
        }

        # Create unified output
        unified_output = self._create_unified_output(synthesis, synthesis_goal)

        return {
            "synthesis_goal": synthesis_goal,
            "agent_contributions": len(agent_outputs),
            "synthesis": synthesis,
            "unified_output": unified_output,
            "confidence": self._calculate_synthesis_confidence(agent_outputs),
        }

    async def _resolve_conflicts(
        self,
        conflict_description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Resolve conflicts between agents or outputs.

        Args:
            conflict_description: Description of conflict
            context: Conflict context

        Returns:
            Conflict resolution
        """
        conflict_type = context.get("conflict_type", "output_disagreement")
        conflicting_parties = context.get("parties", [])

        resolution_strategy = self._determine_resolution_strategy(
            conflict_type,
            conflicting_parties,
        )

        resolution = {
            "conflict": conflict_description,
            "type": conflict_type,
            "parties": conflicting_parties,
            "strategy": resolution_strategy,
            "decision": self._make_conflict_decision(
                conflict_type,
                conflicting_parties,
                context,
            ),
            "rationale": self._explain_decision(resolution_strategy),
        }

        return resolution

    async def _comprehensive_coordination(
        self,
        goal: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform comprehensive workflow coordination.

        Args:
            goal: Coordination goal
            context: Context

        Returns:
            Comprehensive coordination results
        """
        # Orchestrate workflow
        orchestration = await self._orchestrate_workflow(goal, context)

        # Delegate tasks
        delegation = await self._delegate_tasks(
            goal,
            {**context, "tasks": orchestration.get("phases", [])[0].get("tasks", [])},
        )

        # Set up monitoring
        workflow_id = context.get("workflow_id")
        if workflow_id:
            monitoring = await self._monitor_progress(workflow_id, context)
        else:
            monitoring = {}

        return {
            "orchestration": orchestration,
            "delegation": delegation,
            "monitoring": monitoring,
        }

    # Helper methods

    def _plan_workflow_phases(
        self,
        goal: str,
        workflow_type: str,
    ) -> List[Dict[str, Any]]:
        """Plan workflow phases based on goal and type."""
        # Standard workflow phases
        if workflow_type == "research":
            return [
                {
                    "name": "Research",
                    "agents": ["research"],
                    "tasks": [{"id": "research_1", "description": "Gather information"}],
                },
                {
                    "name": "Analysis",
                    "agents": ["analysis"],
                    "tasks": [{"id": "analysis_1", "description": "Analyze findings"}],
                },
                {
                    "name": "Report",
                    "agents": ["content", "qa"],
                    "tasks": [
                        {"id": "content_1", "description": "Create report"},
                        {"id": "qa_1", "description": "Review report"},
                    ],
                },
            ]
        else:
            return [
                {"name": "Planning", "agents": ["planning"], "tasks": []},
                {"name": "Execution", "agents": ["research", "content"], "tasks": []},
                {"name": "Quality Assurance", "agents": ["qa"], "tasks": []},
            ]

    def _assign_agents_to_tasks(self, phases: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Assign agents to tasks in each phase."""
        assignments = {}

        for phase in phases:
            for agent_type in phase.get("agents", []):
                if agent_type not in assignments:
                    assignments[agent_type] = []

                task_ids = [task.get("id") for task in phase.get("tasks", [])]
                assignments[agent_type].extend(task_ids)

        return assignments

    def _create_execution_timeline(self, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create execution timeline for phases."""
        total_duration_hours = len(phases) * 2  # 2 hours per phase estimate

        return {
            "total_duration": f"{total_duration_hours} hours",
            "phases": [
                {
                    "name": phase.get("name"),
                    "estimated_duration": "2 hours",
                }
                for phase in phases
            ],
        }

    def _create_monitoring_plan(self, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create monitoring plan for workflow."""
        return {
            "check_interval": "15 minutes",
            "checkpoints": [phase.get("name") for phase in phases],
            "alerts": ["phase_completion", "task_failure", "deadline_risk"],
        }

    def _match_agent_to_task(
        self,
        task: Dict[str, Any],
        available_agents: List[str],
    ) -> str:
        """Match the best agent to a task."""
        task_type = task.get("type", "general")

        # Simple matching logic
        agent_specializations = {
            "research": ["research", "information_gathering"],
            "analysis": ["analysis", "data_processing"],
            "planning": ["planning", "strategy"],
            "content": ["writing", "documentation"],
            "outreach": ["communication", "email"],
            "qa": ["review", "validation"],
        }

        for agent, specializations in agent_specializations.items():
            if agent in available_agents and task_type in specializations:
                return agent

        # Default to first available agent
        return available_agents[0] if available_agents else "general"

    def _calculate_task_priority(
        self,
        task: Dict[str, Any],
        all_tasks: List[Dict[str, Any]],
    ) -> str:
        """Calculate task priority."""
        # Check if task has dependents
        task_id = task.get("id")
        has_dependents = any(
            task_id in t.get("dependencies", [])
            for t in all_tasks
        )

        if has_dependents:
            return "high"
        elif task.get("critical", False):
            return "high"
        else:
            return "medium"

    def _calculate_agent_workload(self, delegations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate workload per agent."""
        workload = {}

        for delegation in delegations:
            agent = delegation.get("assigned_agent")
            workload[agent] = workload.get(agent, 0) + 1

        return workload

    def _detect_bottlenecks(self, workflow_state: Dict[str, Any]) -> List[str]:
        """Detect workflow bottlenecks."""
        bottlenecks = []

        # Check for phases taking too long
        phases = workflow_state.get("phases", [])
        for phase in phases:
            if phase.get("status") == "in_progress":
                # Check duration
                bottlenecks.append(f"Phase '{phase.get('name')}' in progress")

        return bottlenecks

    def _estimate_completion_time(
        self,
        workflow_state: Dict[str, Any],
        progress_percentage: float,
    ) -> str:
        """Estimate workflow completion time."""
        if progress_percentage >= 100:
            return "Completed"

        remaining_percentage = 100 - progress_percentage
        estimated_hours = (remaining_percentage / 20)  # Rough estimate

        return f"{estimated_hours:.1f} hours"

    def _calculate_workflow_health(self, workflow_state: Dict[str, Any]) -> float:
        """Calculate workflow health score (0-100)."""
        score = 100.0

        # Deduct for delays
        status = workflow_state.get("status")
        if status == "delayed":
            score -= 20

        # Deduct for errors
        if workflow_state.get("error_count", 0) > 0:
            score -= 10

        return max(score, 0.0)

    def _synthesize_research(self, research_outputs: List[Dict[str, Any]]) -> str:
        """Synthesize research outputs."""
        if not research_outputs:
            return "No research findings available."

        return f"Research synthesis from {len(research_outputs)} sources."

    def _synthesize_analysis(self, analysis_outputs: List[Dict[str, Any]]) -> str:
        """Synthesize analysis outputs."""
        if not analysis_outputs:
            return "No analysis results available."

        return f"Analysis insights from {len(analysis_outputs)} analyses."

    def _synthesize_plans(self, planning_outputs: List[Dict[str, Any]]) -> str:
        """Synthesize planning outputs."""
        if not planning_outputs:
            return "No planning results available."

        return f"Consolidated plan from {len(planning_outputs)} planning sessions."

    def _synthesize_content(self, content_outputs: List[Dict[str, Any]]) -> str:
        """Synthesize content outputs."""
        if not content_outputs:
            return "No content available."

        return f"Content compilation from {len(content_outputs)} pieces."

    def _create_unified_output(
        self,
        synthesis: Dict[str, str],
        goal: str,
    ) -> str:
        """Create unified output from synthesis."""
        output = f"Unified Output for: {goal}\n\n"

        for key, value in synthesis.items():
            output += f"{key.replace('_', ' ').title()}:\n{value}\n\n"

        return output

    def _calculate_synthesis_confidence(self, outputs: List[Dict[str, Any]]) -> float:
        """Calculate confidence in synthesis."""
        if not outputs:
            return 0.0

        # Average confidence from all outputs
        confidences = [
            output.get("confidence", 0.5)
            for output in outputs
        ]

        return sum(confidences) / len(confidences) if confidences else 0.5

    def _determine_resolution_strategy(
        self,
        conflict_type: str,
        parties: List[str],
    ) -> str:
        """Determine conflict resolution strategy."""
        strategies = {
            "output_disagreement": "consensus_building",
            "resource_conflict": "priority_based_allocation",
            "timeline_conflict": "critical_path_analysis",
        }

        return strategies.get(conflict_type, "facilitated_discussion")

    def _make_conflict_decision(
        self,
        conflict_type: str,
        parties: List[str],
        context: Dict[str, Any],
    ) -> str:
        """Make decision to resolve conflict."""
        # Simple decision logic (in production, use more sophisticated approach)
        if conflict_type == "output_disagreement":
            return "Proceed with consensus from majority of agents"
        else:
            return "Prioritize based on workflow criticality"

    def _explain_decision(self, strategy: str) -> str:
        """Explain conflict resolution decision."""
        explanations = {
            "consensus_building": "Decision based on consensus among conflicting parties",
            "priority_based_allocation": "Resources allocated based on task priority",
            "critical_path_analysis": "Timeline adjusted based on critical path",
        }

        return explanations.get(strategy, "Decision made based on workflow optimization")
