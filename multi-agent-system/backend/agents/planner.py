"""
Planning Agent - Specialized in strategic planning, task breakdown, and resource allocation.
Capabilities: Project planning, timeline estimation, dependency mapping, risk assessment.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from backend.agents.base_agent import BaseAgent


class PlanningAgent(BaseAgent):
    """
    Planning Agent for strategic planning and task breakdown.

    Specializes in:
    - Strategic planning and roadmapping
    - Task breakdown and decomposition
    - Resource allocation and scheduling
    - Timeline estimation and milestones
    - Dependency mapping and critical path
    - Risk assessment and mitigation
    """

    def __init__(self, **kwargs):
        """Initialize the Planning Agent."""
        super().__init__(
            agent_type="planning",
            role="Senior Strategic Planner",
            goal="Create comprehensive, executable plans with clear timelines, dependencies, and resource allocation",
            backstory="""You are an expert strategic planner with extensive experience in
            project management, agile methodologies, and business strategy. You excel at
            breaking down complex initiatives into manageable tasks, identifying dependencies,
            estimating timelines, and allocating resources effectively. Your plans are
            realistic, detailed, and account for potential risks.""",
            tools=[],
            **kwargs,
        )

    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a planning task.

        Args:
            task: Planning task description
            context: Additional context

        Returns:
            Planning results
        """
        logger.info(f"Planning Agent executing task: {task[:100]}...")

        context = context or {}
        planning_type = context.get("planning_type", "project")

        try:
            if planning_type == "project":
                results = await self._create_project_plan(task, context)
            elif planning_type == "task_breakdown":
                results = await self._breakdown_task(task, context)
            elif planning_type == "resource_allocation":
                results = await self._allocate_resources(task, context)
            elif planning_type == "timeline":
                results = await self._create_timeline(task, context)
            elif planning_type == "risk_assessment":
                results = await self._assess_risks(task, context)
            else:
                results = await self._comprehensive_plan(task, context)

            return {
                "status": "completed",
                "planning_type": planning_type,
                "results": results,
                "tokens_used": 0,
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Error in planning task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "results": None,
            }

    async def _create_project_plan(
        self,
        project: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a comprehensive project plan.

        Args:
            project: Project description
            context: Project context

        Returns:
            Project plan
        """
        duration_weeks = context.get("duration_weeks", 8)
        team_size = context.get("team_size", 5)
        priority = context.get("priority", "medium")

        # Break down project into phases
        phases = self._identify_phases(project, context)

        # Create tasks for each phase
        all_tasks = []
        for phase in phases:
            tasks = self._generate_tasks_for_phase(phase)
            all_tasks.extend(tasks)

        # Estimate timelines
        timeline = self._estimate_timeline(all_tasks, duration_weeks)

        # Identify dependencies
        dependencies = self._map_dependencies(all_tasks)

        # Allocate resources
        resource_plan = self._create_resource_plan(all_tasks, team_size)

        return {
            "project": project,
            "phases": phases,
            "tasks": all_tasks,
            "timeline": timeline,
            "dependencies": dependencies,
            "resource_plan": resource_plan,
            "estimated_duration": f"{duration_weeks} weeks",
            "team_size": team_size,
            "priority": priority,
        }

    async def _breakdown_task(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Break down a task into subtasks.

        Args:
            task: Task to break down
            context: Context

        Returns:
            Task breakdown
        """
        complexity = context.get("complexity", "medium")
        subtask_count = {"low": 3, "medium": 5, "high": 8}.get(complexity, 5)

        subtasks = []
        for i in range(subtask_count):
            subtasks.append({
                "id": f"subtask_{i+1}",
                "title": f"Subtask {i+1} for: {task[:50]}",
                "description": f"Detailed implementation of aspect {i+1}",
                "estimated_hours": self._estimate_hours(complexity),
                "priority": self._determine_priority(i, subtask_count),
                "dependencies": self._identify_subtask_dependencies(i, subtasks),
            })

        return {
            "main_task": task,
            "complexity": complexity,
            "subtasks": subtasks,
            "total_estimated_hours": sum(st["estimated_hours"] for st in subtasks),
        }

    async def _allocate_resources(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Allocate resources for tasks.

        Args:
            task: Task description
            context: Resource context

        Returns:
            Resource allocation plan
        """
        available_resources = context.get("resources", [])
        tasks = context.get("tasks", [])

        allocations = []

        for task_item in tasks:
            # Determine required skills
            required_skills = self._identify_required_skills(task_item)

            # Match resources
            matched_resources = self._match_resources(
                required_skills,
                available_resources,
            )

            allocations.append({
                "task": task_item.get("title", ""),
                "required_skills": required_skills,
                "allocated_resources": matched_resources,
                "estimated_hours": task_item.get("estimated_hours", 0),
            })

        return {
            "allocations": allocations,
            "total_tasks": len(tasks),
            "resource_utilization": self._calculate_utilization(allocations),
        }

    async def _create_timeline(
        self,
        project: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create project timeline with milestones.

        Args:
            project: Project description
            context: Timeline context

        Returns:
            Timeline with milestones
        """
        start_date = context.get("start_date", datetime.now())
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)

        duration_weeks = context.get("duration_weeks", 8)
        phases = context.get("phases", self._identify_phases(project, context))

        timeline = {
            "start_date": start_date.isoformat(),
            "end_date": (start_date + timedelta(weeks=duration_weeks)).isoformat(),
            "total_duration": f"{duration_weeks} weeks",
            "phases": [],
            "milestones": [],
        }

        # Distribute phases across timeline
        weeks_per_phase = duration_weeks / len(phases)
        current_date = start_date

        for i, phase in enumerate(phases):
            phase_end = current_date + timedelta(weeks=weeks_per_phase)

            timeline["phases"].append({
                "name": phase["name"],
                "start_date": current_date.isoformat(),
                "end_date": phase_end.isoformat(),
                "duration_weeks": weeks_per_phase,
            })

            # Add milestone at phase end
            timeline["milestones"].append({
                "name": f"{phase['name']} Complete",
                "date": phase_end.isoformat(),
                "deliverables": phase.get("deliverables", []),
            })

            current_date = phase_end

        return timeline

    async def _assess_risks(
        self,
        project: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assess project risks and create mitigation plan.

        Args:
            project: Project description
            context: Risk context

        Returns:
            Risk assessment
        """
        complexity = context.get("complexity", "medium")
        team_size = context.get("team_size", 5)
        timeline_tight = context.get("timeline_tight", False)

        risks = []

        # Identify common risks based on project characteristics
        if complexity == "high":
            risks.append({
                "category": "Technical",
                "description": "High technical complexity may lead to delays",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Conduct technical spike and proof of concept early",
            })

        if team_size < 3:
            risks.append({
                "category": "Resource",
                "description": "Small team size may impact delivery timeline",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "Consider augmenting team or reducing scope",
            })

        if timeline_tight:
            risks.append({
                "category": "Schedule",
                "description": "Tight timeline increases risk of missed deadlines",
                "probability": "high",
                "impact": "high",
                "mitigation": "Implement daily standups and weekly milestone checks",
            })

        # Always include these common risks
        risks.extend([
            {
                "category": "Scope",
                "description": "Scope creep may extend timeline",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "Strict change control process with approval workflow",
            },
            {
                "category": "Quality",
                "description": "Quality issues may require rework",
                "probability": "low",
                "impact": "high",
                "mitigation": "Implement automated testing and code review process",
            },
        ])

        return {
            "project": project,
            "risks": risks,
            "total_risks": len(risks),
            "high_impact_risks": len([r for r in risks if r["impact"] == "high"]),
        }

    async def _comprehensive_plan(
        self,
        project: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create comprehensive plan combining all planning aspects.

        Args:
            project: Project description
            context: Planning context

        Returns:
            Comprehensive plan
        """
        # Create project plan
        project_plan = await self._create_project_plan(project, context)

        # Add timeline
        timeline = await self._create_timeline(project, {
            **context,
            "phases": project_plan["phases"],
        })

        # Assess risks
        risks = await self._assess_risks(project, context)

        return {
            **project_plan,
            "timeline": timeline,
            "risk_assessment": risks,
        }

    # Helper methods

    def _identify_phases(self, project: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify project phases."""
        # Standard software project phases
        return [
            {"name": "Planning & Requirements", "deliverables": ["Requirements doc", "Technical design"]},
            {"name": "Development", "deliverables": ["Core functionality", "Unit tests"]},
            {"name": "Testing", "deliverables": ["Test results", "Bug fixes"]},
            {"name": "Deployment & Launch", "deliverables": ["Production deployment", "Documentation"]},
        ]

    def _generate_tasks_for_phase(self, phase: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tasks for a phase."""
        tasks = []
        phase_name = phase["name"]

        # Generate 3-5 tasks per phase
        for i in range(4):
            tasks.append({
                "id": f"{phase_name.lower().replace(' ', '_')}_{i+1}",
                "title": f"{phase_name} - Task {i+1}",
                "phase": phase_name,
                "estimated_hours": 20 + (i * 10),
                "priority": "high" if i == 0 else "medium",
            })

        return tasks

    def _estimate_timeline(self, tasks: List[Dict[str, Any]], duration_weeks: int) -> Dict[str, Any]:
        """Estimate timeline for tasks."""
        total_hours = sum(task.get("estimated_hours", 0) for task in tasks)

        return {
            "total_hours": total_hours,
            "total_weeks": duration_weeks,
            "average_hours_per_week": total_hours / duration_weeks if duration_weeks > 0 else 0,
        }

    def _map_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map task dependencies."""
        dependencies = []

        # Simple dependency logic: tasks in same phase depend on previous task
        for i, task in enumerate(tasks[1:], 1):
            if task.get("phase") == tasks[i-1].get("phase"):
                dependencies.append({
                    "task": task["id"],
                    "depends_on": [tasks[i-1]["id"]],
                    "type": "finish_to_start",
                })

        return dependencies

    def _create_resource_plan(self, tasks: List[Dict[str, Any]], team_size: int) -> Dict[str, Any]:
        """Create resource allocation plan."""
        return {
            "team_size": team_size,
            "total_tasks": len(tasks),
            "tasks_per_person": len(tasks) / team_size if team_size > 0 else 0,
        }

    def _estimate_hours(self, complexity: str) -> int:
        """Estimate hours based on complexity."""
        return {"low": 8, "medium": 20, "high": 40}.get(complexity, 20)

    def _determine_priority(self, index: int, total: int) -> str:
        """Determine task priority."""
        if index < total * 0.3:
            return "high"
        elif index < total * 0.7:
            return "medium"
        else:
            return "low"

    def _identify_subtask_dependencies(
        self,
        index: int,
        subtasks: List[Dict[str, Any]],
    ) -> List[str]:
        """Identify dependencies for a subtask."""
        if index == 0:
            return []
        return [subtasks[index-1]["id"]]

    def _identify_required_skills(self, task: Dict[str, Any]) -> List[str]:
        """Identify required skills for a task."""
        # In production, use NLP to extract skills from task description
        return ["python", "backend", "api_development"]

    def _match_resources(
        self,
        required_skills: List[str],
        available_resources: List[Dict[str, Any]],
    ) -> List[str]:
        """Match resources to required skills."""
        matched = []
        for resource in available_resources[:2]:  # Match up to 2 resources
            matched.append(resource.get("name", "Resource"))
        return matched

    def _calculate_utilization(self, allocations: List[Dict[str, Any]]) -> float:
        """Calculate resource utilization percentage."""
        if not allocations:
            return 0.0
        return min(85.0, len(allocations) * 15.0)  # Simple heuristic
