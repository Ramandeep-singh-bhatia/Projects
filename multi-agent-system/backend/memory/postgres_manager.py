"""
PostgreSQL Manager for persistent storage.
Handles long-term memory, semantic memory, and audit trails.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    JSON,
    Boolean,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from loguru import logger

from backend.config import settings

Base = declarative_base()


# ==================== Database Models ====================


class WorkflowExecution(Base):
    """Workflow execution records."""

    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String(255), unique=True, nullable=False, index=True)
    workflow_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    metadata = Column(JSON)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_workflow_status_type", "status", "workflow_type"),
        Index("ix_workflow_created_at", "created_at"),
    )


class AgentExecution(Base):
    """Agent execution records."""

    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(255), unique=True, nullable=False, index=True)
    workflow_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(100), nullable=False, index=True)
    agent_type = Column(String(100), nullable=False)
    task = Column(Text, nullable=False)
    result = Column(JSON)
    status = Column(String(50), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    tokens_used = Column(Integer)
    cost = Column(Float)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_agent_workflow_id", "workflow_id"),
        Index("ix_agent_type_status", "agent_type", "status"),
        Index("ix_agent_created_at", "created_at"),
    )


class AgentMemory(Base):
    """Long-term agent memory storage."""

    __tablename__ = "agent_memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    memory_id = Column(String(255), unique=True, nullable=False, index=True)
    agent_id = Column(String(100), nullable=False, index=True)
    memory_type = Column(String(50), nullable=False, index=True)
    content = Column(JSON, nullable=False)
    embedding = Column(JSON)  # Vector embedding for semantic search
    importance_score = Column(Float, default=0.5)
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
    tags = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_memory_agent_type", "agent_id", "memory_type"),
        Index("ix_memory_importance", "importance_score"),
    )


class AuditLog(Base):
    """Audit trail for all system actions."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(255), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    actor = Column(String(255))  # Agent or user who performed the action
    details = Column(JSON)
    result = Column(String(50))  # success, failure, pending
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_actor", "actor"),
        Index("ix_audit_timestamp", "timestamp"),
    )


class AgentMetric(Base):
    """Performance metrics for agents."""

    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(String(255), unique=True, nullable=False, index=True)
    agent_type = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    aggregation_period = Column(String(50))  # hourly, daily, weekly
    metadata = Column(JSON)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_metric_type_name", "agent_type", "metric_name"),
        Index("ix_metric_recorded_at", "recorded_at"),
    )


class HumanApproval(Base):
    """Human-in-the-loop approval records."""

    __tablename__ = "human_approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    approval_id = Column(String(255), unique=True, nullable=False, index=True)
    workflow_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(100), nullable=False)
    action_description = Column(Text, nullable=False)
    action_data = Column(JSON)
    impact_level = Column(String(50), nullable=False)  # low, medium, high
    status = Column(String(50), nullable=False, index=True)  # pending, approved, rejected
    requested_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)
    responder = Column(String(255))
    response_comment = Column(Text)
    metadata = Column(JSON)

    __table_args__ = (
        Index("ix_approval_status", "status"),
        Index("ix_approval_workflow", "workflow_id"),
    )


# ==================== PostgreSQL Manager ====================


class PostgresManager:
    """Manages PostgreSQL connections and operations."""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """Establish connection to PostgreSQL."""
        try:
            self.engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=settings.debug,
            )

            # Test connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
            )

            logger.info("PostgreSQL connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get a new database session."""
        if not self.SessionLocal:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.SessionLocal()

    def disconnect(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL connection closed")

    # ==================== Workflow Operations ====================

    def create_workflow_execution(
        self,
        workflow_id: str,
        workflow_type: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution record."""
        session = self.get_session()
        try:
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                status="running",
                input_data=input_data,
                metadata=metadata or {},
                started_at=datetime.utcnow(),
            )
            session.add(execution)
            session.commit()
            session.refresh(execution)
            return execution
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating workflow execution: {e}")
            raise
        finally:
            session.close()

    def update_workflow_execution(
        self,
        workflow_id: str,
        **kwargs,
    ) -> Optional[WorkflowExecution]:
        """Update workflow execution record."""
        session = self.get_session()
        try:
            execution = (
                session.query(WorkflowExecution)
                .filter_by(workflow_id=workflow_id)
                .first()
            )
            if execution:
                for key, value in kwargs.items():
                    setattr(execution, key, value)
                session.commit()
                session.refresh(execution)
            return execution
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating workflow execution: {e}")
            raise
        finally:
            session.close()

    def get_workflow_execution(self, workflow_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution by ID."""
        session = self.get_session()
        try:
            return (
                session.query(WorkflowExecution)
                .filter_by(workflow_id=workflow_id)
                .first()
            )
        finally:
            session.close()

    # ==================== Agent Operations ====================

    def create_agent_execution(
        self,
        execution_id: str,
        workflow_id: str,
        agent_id: str,
        agent_type: str,
        task: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentExecution:
        """Create a new agent execution record."""
        session = self.get_session()
        try:
            execution = AgentExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                agent_id=agent_id,
                agent_type=agent_type,
                task=task,
                status="running",
                metadata=metadata or {},
                started_at=datetime.utcnow(),
            )
            session.add(execution)
            session.commit()
            session.refresh(execution)
            return execution
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating agent execution: {e}")
            raise
        finally:
            session.close()

    def update_agent_execution(
        self,
        execution_id: str,
        **kwargs,
    ) -> Optional[AgentExecution]:
        """Update agent execution record."""
        session = self.get_session()
        try:
            execution = (
                session.query(AgentExecution)
                .filter_by(execution_id=execution_id)
                .first()
            )
            if execution:
                for key, value in kwargs.items():
                    setattr(execution, key, value)
                session.commit()
                session.refresh(execution)
            return execution
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating agent execution: {e}")
            raise
        finally:
            session.close()

    # ==================== Memory Operations ====================

    def save_agent_memory(
        self,
        memory_id: str,
        agent_id: str,
        memory_type: str,
        content: Dict[str, Any],
        importance_score: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentMemory:
        """Save agent memory to database."""
        session = self.get_session()
        try:
            memory = AgentMemory(
                memory_id=memory_id,
                agent_id=agent_id,
                memory_type=memory_type,
                content=content,
                importance_score=importance_score,
                tags=tags or [],
                metadata=metadata or {},
            )
            session.add(memory)
            session.commit()
            session.refresh(memory)
            return memory
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving agent memory: {e}")
            raise
        finally:
            session.close()

    def get_agent_memories(
        self,
        agent_id: str,
        memory_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AgentMemory]:
        """Retrieve agent memories."""
        session = self.get_session()
        try:
            query = session.query(AgentMemory).filter_by(agent_id=agent_id)
            if memory_type:
                query = query.filter_by(memory_type=memory_type)
            return query.order_by(AgentMemory.created_at.desc()).limit(limit).all()
        finally:
            session.close()

    # ==================== Audit Operations ====================

    def create_audit_log(
        self,
        event_id: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        action: str,
        actor: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        result: str = "success",
    ) -> AuditLog:
        """Create an audit log entry."""
        session = self.get_session()
        try:
            log = AuditLog(
                event_id=event_id,
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                actor=actor,
                details=details or {},
                result=result,
            )
            session.add(log)
            session.commit()
            session.refresh(log)
            return log
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating audit log: {e}")
            raise
        finally:
            session.close()

    # ==================== Metrics Operations ====================

    def record_agent_metric(
        self,
        metric_id: str,
        agent_type: str,
        metric_name: str,
        metric_value: float,
        aggregation_period: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentMetric:
        """Record an agent performance metric."""
        session = self.get_session()
        try:
            metric = AgentMetric(
                metric_id=metric_id,
                agent_type=agent_type,
                metric_name=metric_name,
                metric_value=metric_value,
                aggregation_period=aggregation_period,
                metadata=metadata or {},
            )
            session.add(metric)
            session.commit()
            session.refresh(metric)
            return metric
        except Exception as e:
            session.rollback()
            logger.error(f"Error recording metric: {e}")
            raise
        finally:
            session.close()

    # ==================== Human Approval Operations ====================

    def create_approval_request(
        self,
        approval_id: str,
        workflow_id: str,
        agent_id: str,
        action_description: str,
        action_data: Dict[str, Any],
        impact_level: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HumanApproval:
        """Create a human approval request."""
        session = self.get_session()
        try:
            approval = HumanApproval(
                approval_id=approval_id,
                workflow_id=workflow_id,
                agent_id=agent_id,
                action_description=action_description,
                action_data=action_data,
                impact_level=impact_level,
                status="pending",
                metadata=metadata or {},
            )
            session.add(approval)
            session.commit()
            session.refresh(approval)
            return approval
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating approval request: {e}")
            raise
        finally:
            session.close()

    def update_approval_request(
        self,
        approval_id: str,
        status: str,
        responder: str,
        response_comment: Optional[str] = None,
    ) -> Optional[HumanApproval]:
        """Update approval request status."""
        session = self.get_session()
        try:
            approval = (
                session.query(HumanApproval)
                .filter_by(approval_id=approval_id)
                .first()
            )
            if approval:
                approval.status = status
                approval.responder = responder
                approval.response_comment = response_comment
                approval.responded_at = datetime.utcnow()
                session.commit()
                session.refresh(approval)
            return approval
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating approval request: {e}")
            raise
        finally:
            session.close()


# Global PostgreSQL manager instance
postgres_manager = PostgresManager()
