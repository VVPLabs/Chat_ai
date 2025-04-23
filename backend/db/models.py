import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum


def remove_timezone(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


# ------------------ Enums ------------------ #
class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


# ------------------ User ------------------ #
class UserBase(SQLModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class User(SQLModel, table=True):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = Field(default=True)
    password_hash: str = Field(exclude=True)
    image_url: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    projects: List["Project"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="user")
    pomodoro_sessions: List["PomodoroSession"] = Relationship(back_populates="user")
    daily_stats: List["UserDailyStats"] = Relationship(back_populates="user")
    weekly_summaries: List["WeeklyFocusSummary"] = Relationship(back_populates="user")


# ------------------ Project ------------------ #
class ProjectBase(SQLModel):
    name: str
    description: Optional[str] = None


class Project(ProjectBase, table=True):
    project_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    user: Optional["User"] = Relationship(back_populates="projects")
    tasks: List["Task"] = Relationship(back_populates="project")


# ------------------ Task ------------------ #
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: Optional[int] = Field(default=3, ge=1, le=5)


class Task(TaskBase, table=True):
    task_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", index=True)
    project_id: Optional[uuid.UUID] = Field(
        foreign_key="project.project_id", default=None, nullable=True
    )
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    project: Optional["Project"] = Relationship(back_populates="tasks")
    user: Optional["User"] = Relationship(back_populates="tasks")
    pomodoro_sessions: List["PomodoroSession"] = Relationship(back_populates="task")


# ------------------ Pomodoro Session ------------------ #
class PomodoroSession(SQLModel, table=True):
    session_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="task.task_id", index=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", index=True)
    start_time: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    end_time: Optional[datetime] = None
    duration_minutes: int = Field(default=25)

    task: Optional["Task"] = Relationship(back_populates="pomodoro_sessions")
    user: Optional["User"] = Relationship(back_populates="pomodoro_sessions")


# ------------------ User Daily Stats ------------------ #
class UserDailyStatsBase(SQLModel):
    date: datetime
    total_tasks_created: int = 0
    tasks_completed: int = 0
    pomodoro_sessions: int = 0
    focus_minutes: int = 0
    break_minutes: int = 0


class UserDailyStats(UserDailyStatsBase, table=True):
    stats_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )

    user: Optional["User"] = Relationship(back_populates="daily_stats")


# ------------------ Task Progress Snapshot ------------------ #
class TaskProgressSnapshot(SQLModel, table=True):
    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="task.task_id", index=True)
    timestamp: datetime = Field(
        default_factory=lambda: remove_timezone(datetime.now(timezone.utc))
    )
    status: TaskStatus

    task: Optional["Task"] = Relationship()


# ------------------ Weekly Focus Summary ------------------ #
class WeeklyFocusSummary(SQLModel, table=True):
    summary_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.user_id", index=True)
    week_start: datetime
    total_pomodoros: int = 0
    total_focus_minutes: int = 0
    total_tasks_completed: int = 0

    user: Optional["User"] = Relationship(back_populates="weekly_summaries")
