"""
Outreach Agent - Specialized in communication and stakeholder engagement.
Capabilities: Email campaigns, meeting scheduling, follow-ups, CRM integration.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from backend.agents.base_agent import BaseAgent


class OutreachAgent(BaseAgent):
    """
    Outreach Agent for communication and engagement.

    Specializes in:
    - Email campaign management
    - Meeting scheduling and calendar management
    - Automated follow-ups
    - CRM integration and updates
    - Stakeholder communication
    - Response tracking and analytics
    """

    def __init__(self, **kwargs):
        """Initialize the Outreach Agent."""
        super().__init__(
            agent_type="outreach",
            role="Senior Outreach Coordinator",
            goal="Manage stakeholder communication, schedule meetings, and drive engagement effectively",
            backstory="""You are an expert in outreach and stakeholder management with
            extensive experience in relationship building, communication strategy, and
            campaign management. You excel at crafting personalized messages, managing
            calendars efficiently, and maintaining strong relationships with diverse
            stakeholders. Your communication is timely, professional, and results-driven.""",
            tools=[],
            **kwargs,
        )

    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an outreach task.

        Args:
            task: Outreach task description
            context: Additional context

        Returns:
            Outreach results
        """
        logger.info(f"Outreach Agent executing task: {task[:100]}...")

        context = context or {}
        outreach_type = context.get("outreach_type", "email_campaign")

        try:
            if outreach_type == "email_campaign":
                results = await self._create_email_campaign(task, context)
            elif outreach_type == "meeting_scheduling":
                results = await self._schedule_meetings(task, context)
            elif outreach_type == "follow_up":
                results = await self._send_follow_ups(task, context)
            elif outreach_type == "crm_update":
                results = await self._update_crm(task, context)
            else:
                results = await self._general_outreach(task, context)

            return {
                "status": "completed",
                "outreach_type": outreach_type,
                "results": results,
                "tokens_used": 0,
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Error in outreach task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "results": None,
            }

    async def _create_email_campaign(
        self,
        campaign_name: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create and manage an email campaign.

        Args:
            campaign_name: Campaign name
            context: Campaign configuration

        Returns:
            Campaign details
        """
        recipients = context.get("recipients", [])
        template = context.get("template", "default")
        schedule = context.get("schedule", "immediate")

        emails = []

        for recipient in recipients:
            email = {
                "id": f"email_{len(emails) + 1}",
                "recipient": recipient.get("email"),
                "recipient_name": recipient.get("name", ""),
                "subject": self._generate_subject(campaign_name, recipient),
                "body": self._generate_email_body(campaign_name, recipient),
                "scheduled_time": self._calculate_send_time(schedule, len(emails)),
                "status": "scheduled",
                "tracking_enabled": True,
            }
            emails.append(email)

        campaign = {
            "name": campaign_name,
            "total_recipients": len(recipients),
            "emails": emails,
            "schedule": schedule,
            "template": template,
            "created_at": datetime.now().isoformat(),
            "expected_completion": self._calculate_completion_time(len(emails), schedule),
        }

        return campaign

    async def _schedule_meetings(
        self,
        purpose: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Schedule meetings with stakeholders.

        Args:
            purpose: Meeting purpose
            context: Meeting context (attendees, duration, preferences)

        Returns:
            Meeting details
        """
        attendees = context.get("attendees", [])
        duration_minutes = context.get("duration", 30)
        preferred_times = context.get("preferred_times", ["9:00 AM", "2:00 PM"])

        meetings = []

        for i, attendee in enumerate(attendees):
            # Find available slot
            meeting_time = self._find_available_slot(
                preferred_times,
                i,
                duration_minutes,
            )

            meeting = {
                "id": f"meeting_{i + 1}",
                "title": purpose,
                "attendees": [attendee.get("email")],
                "organizer": "system@example.com",
                "start_time": meeting_time,
                "end_time": self._calculate_end_time(meeting_time, duration_minutes),
                "duration_minutes": duration_minutes,
                "location": "Virtual/Zoom",
                "description": f"Meeting regarding: {purpose}",
                "status": "scheduled",
                "calendar_invite_sent": True,
            }
            meetings.append(meeting)

        return {
            "purpose": purpose,
            "total_meetings": len(meetings),
            "meetings": meetings,
            "duration_per_meeting": duration_minutes,
        }

    async def _send_follow_ups(
        self,
        context_description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Send follow-up communications.

        Args:
            context_description: Follow-up context
            context: Configuration

        Returns:
            Follow-up details
        """
        previous_interactions = context.get("previous_interactions", [])
        follow_up_type = context.get("follow_up_type", "email")
        delay_days = context.get("delay_days", 3)

        follow_ups = []

        for interaction in previous_interactions:
            follow_up = {
                "id": f"followup_{len(follow_ups) + 1}",
                "type": follow_up_type,
                "recipient": interaction.get("recipient"),
                "original_interaction": interaction.get("id"),
                "subject": f"Following up: {interaction.get('subject', 'Our conversation')}",
                "message": self._generate_follow_up_message(interaction),
                "scheduled_date": self._calculate_follow_up_date(
                    interaction.get("date"),
                    delay_days,
                ),
                "priority": self._determine_follow_up_priority(interaction),
                "status": "scheduled",
            }
            follow_ups.append(follow_up)

        return {
            "context": context_description,
            "total_follow_ups": len(follow_ups),
            "follow_ups": follow_ups,
            "average_delay_days": delay_days,
        }

    async def _update_crm(
        self,
        update_description: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update CRM with interaction data.

        Args:
            update_description: Description of update
            context: CRM update data

        Returns:
            Update results
        """
        contacts = context.get("contacts", [])
        interaction_type = context.get("interaction_type", "email")
        update_fields = context.get("update_fields", ["last_contact", "status"])

        updates = []

        for contact in contacts:
            update = {
                "contact_id": contact.get("id"),
                "contact_name": contact.get("name"),
                "updates": {
                    "last_contact_date": datetime.now().isoformat(),
                    "last_interaction_type": interaction_type,
                    "status": self._determine_contact_status(contact),
                    "engagement_score": self._calculate_engagement_score(contact),
                },
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }
            updates.append(update)

        return {
            "description": update_description,
            "total_updates": len(updates),
            "updates": updates,
            "fields_updated": update_fields,
        }

    async def _general_outreach(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """General outreach task."""
        return {
            "task": task,
            "status": "completed",
            "recipients_contacted": len(context.get("recipients", [])),
        }

    # Helper methods

    def _generate_subject(self, campaign: str, recipient: Dict[str, Any]) -> str:
        """Generate personalized email subject."""
        name = recipient.get("name", "there")
        return f"{campaign}: {name}, let's connect"

    def _generate_email_body(self, campaign: str, recipient: Dict[str, Any]) -> str:
        """Generate personalized email body."""
        name = recipient.get("name", "there")
        company = recipient.get("company", "your company")

        return f"""Hi {name},

I wanted to reach out regarding {campaign}. I've been following {company}'s work
and believe there could be valuable opportunities for collaboration.

Would you be available for a brief call next week to discuss?

Looking forward to connecting!"""

    def _calculate_send_time(self, schedule: str, index: int) -> str:
        """Calculate optimal send time for email."""
        if schedule == "immediate":
            send_time = datetime.now() + timedelta(minutes=index * 2)
        elif schedule == "daily":
            send_time = datetime.now() + timedelta(days=index)
            send_time = send_time.replace(hour=9, minute=0)
        else:
            send_time = datetime.now() + timedelta(hours=index)

        return send_time.isoformat()

    def _calculate_completion_time(self, count: int, schedule: str) -> str:
        """Calculate when campaign will complete."""
        if schedule == "immediate":
            completion = datetime.now() + timedelta(hours=1)
        elif schedule == "daily":
            completion = datetime.now() + timedelta(days=count)
        else:
            completion = datetime.now() + timedelta(hours=count)

        return completion.isoformat()

    def _find_available_slot(
        self,
        preferred_times: List[str],
        index: int,
        duration: int,
    ) -> str:
        """Find available meeting slot."""
        # Simple scheduling: distribute across next week
        base_date = datetime.now() + timedelta(days=1)
        base_date = base_date.replace(hour=9, minute=0, second=0)

        meeting_time = base_date + timedelta(hours=index * 2)
        return meeting_time.isoformat()

    def _calculate_end_time(self, start_time: str, duration_minutes: int) -> str:
        """Calculate meeting end time."""
        start = datetime.fromisoformat(start_time)
        end = start + timedelta(minutes=duration_minutes)
        return end.isoformat()

    def _generate_follow_up_message(self, interaction: Dict[str, Any]) -> str:
        """Generate follow-up message."""
        subject = interaction.get("subject", "our previous conversation")
        return f"I wanted to follow up on {subject}. Do you have any updates?"

    def _calculate_follow_up_date(
        self,
        original_date: Optional[str],
        delay_days: int,
    ) -> str:
        """Calculate follow-up date."""
        if original_date:
            base_date = datetime.fromisoformat(original_date)
        else:
            base_date = datetime.now()

        follow_up_date = base_date + timedelta(days=delay_days)
        return follow_up_date.isoformat()

    def _determine_follow_up_priority(self, interaction: Dict[str, Any]) -> str:
        """Determine follow-up priority."""
        # Simple heuristic
        if interaction.get("importance") == "high":
            return "high"
        elif interaction.get("response_rate", 0) > 0.7:
            return "medium"
        else:
            return "low"

    def _determine_contact_status(self, contact: Dict[str, Any]) -> str:
        """Determine contact status."""
        last_response = contact.get("last_response_date")
        if not last_response:
            return "new"

        # Check if responded recently
        last_response_date = datetime.fromisoformat(last_response)
        days_since = (datetime.now() - last_response_date).days

        if days_since < 7:
            return "engaged"
        elif days_since < 30:
            return "warm"
        else:
            return "cold"

    def _calculate_engagement_score(self, contact: Dict[str, Any]) -> float:
        """Calculate engagement score (0-100)."""
        response_rate = contact.get("response_rate", 0)
        meetings_attended = contact.get("meetings_attended", 0)
        emails_opened = contact.get("emails_opened", 0)

        score = (
            response_rate * 40 +
            min(meetings_attended * 20, 40) +
            min(emails_opened * 2, 20)
        )

        return min(score, 100.0)
