from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Astronaut(Base):
    __tablename__ = "astronaut"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True)
    alias: Mapped[str] = mapped_column(String(50))
    mission_role: Mapped[str] = mapped_column(String(100))
    baseline_days: Mapped[int] = mapped_column(Integer, default=7)
    metrics: Mapped[list["Metric"]] = relationship(back_populates="astronaut", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="astronaut", cascade="all, delete-orphan")
    notes: Mapped[list["Note"]] = relationship(back_populates="astronaut", cascade="all, delete-orphan")


class Metric(Base):
    __tablename__ = "metric"
    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronaut.id"), index=True)
    indicator: Mapped[str] = mapped_column(String(40), index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(10))
    recorded_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    source: Mapped[str] = mapped_column(String(20), default="simulated")  # toujours simulé en MVP
    astronaut: Mapped[Astronaut] = relationship(back_populates="metrics")


class Rule(Base):
    __tablename__ = "rule"
    id: Mapped[int] = mapped_column(primary_key=True)
    indicator: Mapped[str] = mapped_column(String(40), unique=True)
    kind: Mapped[str] = mapped_column(String(40), default="zscore_persistence")
    params: Mapped[dict] = mapped_column(JSON)
    justification: Mapped[str] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)


class Alert(Base):
    __tablename__ = "alert"
    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronaut.id"), index=True)
    indicator: Mapped[str] = mapped_column(String(40))
    level: Mapped[str] = mapped_column(String(10))
    rule_id: Mapped[int | None] = mapped_column(ForeignKey("rule.id"), nullable=True)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    astronaut: Mapped[Astronaut] = relationship(back_populates="alerts")


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(20))  # astronaute, medecin, responsable
    astronaut_id: Mapped[int | None] = mapped_column(ForeignKey("astronaut.id"), nullable=True)


class Note(Base):
    __tablename__ = "note"
    id: Mapped[int] = mapped_column(primary_key=True)
    astronaut_id: Mapped[int] = mapped_column(ForeignKey("astronaut.id"), index=True)
    author: Mapped[str] = mapped_column(String(50), default="medecin")
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    astronaut: Mapped[Astronaut] = relationship(back_populates="notes")
