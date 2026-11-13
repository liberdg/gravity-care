from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Indicator = Literal["heart_rate_rest", "spo2", "sleep_hours", "activity_minutes", "hrv", "radiation_dose"]


class LoginIn(BaseModel):
    username: str
    password: str


class SessionOut(BaseModel):
    token: str
    role: str
    username: str
    astronaut_id: int | None


class AstronautOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    alias: str
    mission_role: str
    baseline_days: int


class AstronautWithStatus(BaseModel):
    id: int
    code: str
    alias: str
    mission_role: str
    status: str


class ReadingIn(BaseModel):
    """Mesure envoyée par un capteur (ou par le simulateur)."""
    indicator: Indicator
    value: float
    recorded_at: datetime | None = None


class MetricOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    indicator: str
    value: float
    unit: str
    recorded_at: datetime
    source: str


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    astronaut_id: int
    indicator: str
    level: str
    explanation: str
    created_at: datetime
    acknowledged: bool


class StatusOut(BaseModel):
    status: str
    simulated_data: bool = True
    last_day: int | None
    last_reading_at: datetime | None
    sensor_silent: bool
    silent_hours: float | None
    reasons: list[dict]


class NoteIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    astronaut_id: int
    author: str
    text: str
    created_at: datetime
