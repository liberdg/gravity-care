from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from . import models
from .errors import ApiError
from .security import current_user, require_roles
from .simulation import SPEEDS, runner

router = APIRouter(prefix="/api/simulation")


class StartIn(BaseModel):
    speed: Literal["lente", "normale", "rapide"] = "normale"
    days: int = Field(30, ge=8, le=30)


@router.get("")
def simulation_status(_: models.User = Depends(current_user)):
    return {**runner.status(), "speeds": list(SPEEDS)}


@router.post("/start", status_code=202)
def start_simulation(body: StartIn, _: models.User = Depends(require_roles("medecin", "responsable"))):
    """Efface les mesures et rejoue un flux de capteurs SIMULÉS en arrière-plan."""
    try:
        runner.start(body.days, body.speed)
    except RuntimeError:
        raise ApiError(409, "already_running", "Une simulation est déjà en cours.")
    return runner.status()


@router.post("/stop")
def stop_simulation(_: models.User = Depends(require_roles("medecin", "responsable"))):
    runner.stop()
    return runner.status()
