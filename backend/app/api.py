from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import config
from . import engine as eng
from . import models, schemas
from .database import get_db
from .errors import ApiError
from .report import build_report
from .security import current_user, make_token, require_roles, sensor_auth, verify_password

router = APIRouter(prefix="/api")
ANY_ROLE = ("astronaute", "medecin", "responsable")


# ---------- utilitaires ----------

def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def check_access(user: models.User, astronaut_id: int) -> None:
    if user.role == "astronaute" and user.astronaut_id != astronaut_id:
        raise ApiError(403, "forbidden", "Accès refusé à cet astronaute.")


def get_astronaut(db: Session, astronaut_id: int) -> models.Astronaut:
    a = db.get(models.Astronaut, astronaut_id)
    if a is None:
        raise ApiError(404, "astronaut_not_found", f"Astronaute {astronaut_id} introuvable.")
    return a


def daily_points(db: Session, a: models.Astronaut, as_of_day: int | None = None) -> dict[str, list[dict]]:
    """Regroupe les mesures brutes en UNE valeur par jour et par indicateur (moyenne ou somme).

    Le jour 1 = date de la première mesure de l'astronaute.
    """
    rows = db.execute(
        select(models.Metric.indicator, models.Metric.recorded_at, models.Metric.value)
        .where(models.Metric.astronaut_id == a.id)
        .order_by(models.Metric.recorded_at)
    ).all()
    if not rows:
        return {}
    first = min(r.recorded_at.date() for r in rows)
    buckets: dict[tuple[str, object], list[float]] = defaultdict(list)
    for r in rows:
        buckets[(r.indicator, r.recorded_at.date())].append(r.value)
    out: dict[str, list[dict]] = defaultdict(list)
    for (ind, d), vals in buckets.items():
        day = (d - first).days + 1
        if as_of_day is not None and day > as_of_day:
            continue
        agg = eng.INDICATORS[ind]["agg"]
        out[ind].append({"day": day, "date": d.isoformat(), "value": round(eng.aggregate(vals, agg), 4), "readings": len(vals)})
    for ind in out:
        out[ind].sort(key=lambda p: p["day"])
    return dict(out)


def compute(db: Session, a: models.Astronaut, as_of_day: int | None = None) -> dict:
    rules = {r.indicator: r.params for r in db.scalars(select(models.Rule))}
    daily = daily_points(db, a, as_of_day)
    findings = []
    for ind, pts in daily.items():
        f = eng.evaluate_indicator(ind, [p["value"] for p in pts], a.baseline_days, rules.get(ind))
        if f:
            findings.append(f)
    calibrated = any(len(p) > a.baseline_days for p in daily.values())
    last_day = max((p[-1]["day"] for p in daily.values()), default=None)
    return {"status": eng.global_status(findings, calibrated), "findings": findings, "daily": daily, "last_day": last_day}


def silence_info(db: Session, a: models.Astronaut) -> tuple[datetime | None, bool, float | None]:
    """Un capteur est « silencieux » si sa dernière mesure a plus de SILENT_AFTER_HOURS de retard
    sur la mesure la plus récente reçue par le système (EF-26)."""
    last = db.scalar(select(func.max(models.Metric.recorded_at)).where(models.Metric.astronaut_id == a.id))
    newest = db.scalar(select(func.max(models.Metric.recorded_at)))
    if last is None or newest is None:
        return last, False, None
    hours = (newest - last).total_seconds() / 3600
    return last, hours > config.SILENT_AFTER_HOURS, round(hours, 1)


def refresh_alerts(db: Session, a: models.Astronaut) -> None:
    """Synchronise les alertes enregistrées avec l'état actuel.

    Une alerte (indicateur, niveau) déjà connue est mise à jour et garde son accusé de réception.
    Les alertes non acquittées qui ne s'appliquent plus sont supprimées.
    """
    rules = {r.indicator: r.id for r in db.scalars(select(models.Rule))}
    findings = {(f.indicator, f.level): f for f in compute(db, a)["findings"]}
    existing = list(db.scalars(select(models.Alert).where(models.Alert.astronaut_id == a.id)))
    known = set()
    for al in existing:
        key = (al.indicator, al.level)
        if key in findings:
            al.explanation = findings[key].explanation
            known.add(key)
        elif not al.acknowledged:
            db.delete(al)
    for key, f in findings.items():
        if key not in known:
            db.add(models.Alert(astronaut_id=a.id, indicator=f.indicator, level=f.level,
                                rule_id=rules.get(f.indicator), explanation=f.explanation, created_at=now_utc()))
    db.commit()


# ---------- connexion ----------

@router.post("/auth/login", response_model=schemas.SessionOut)
def login(body: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.username == body.username))
    if user is None or not verify_password(body.password, user.password_hash):
        raise ApiError(401, "bad_credentials", "Identifiant ou mot de passe incorrect.")
    return schemas.SessionOut(token=make_token(user.id), role=user.role, username=user.username,
                              astronaut_id=user.astronaut_id)


@router.get("/auth/me", response_model=schemas.SessionOut)
def me(user: models.User = Depends(current_user)):
    return schemas.SessionOut(token="", role=user.role, username=user.username, astronaut_id=user.astronaut_id)


# ---------- capteurs (réception automatique des mesures) ----------

@router.get("/sensors/astronauts", dependencies=[Depends(sensor_auth)])
def sensor_astronauts(db: Session = Depends(get_db)):
    return [{"id": a.id, "code": a.code} for a in db.scalars(select(models.Astronaut).order_by(models.Astronaut.id))]


@router.post("/astronauts/{astronaut_id}/metrics", response_model=schemas.MetricOut, status_code=201,
             dependencies=[Depends(sensor_auth)])
def receive_reading(astronaut_id: int, body: schemas.ReadingIn, db: Session = Depends(get_db)):
    """Point d'entrée des capteurs (clé X-Sensor-Key). Aucun utilisateur ne saisit de mesure."""
    a = get_astronaut(db, astronaut_id)
    info = eng.INDICATORS[body.indicator]
    if not info["min"] <= body.value <= info["max"]:
        raise ApiError(422, "value_out_of_range",
                       f"{info['label']} doit être entre {info['min']} et {info['max']} {info['unit']}.")
    when = body.recorded_at
    if when is not None and when.tzinfo is not None:
        when = when.astimezone(timezone.utc).replace(tzinfo=None)
    m = models.Metric(astronaut_id=a.id, indicator=body.indicator, value=body.value, unit=info["unit"],
                      recorded_at=when or now_utc(), source="simulated")
    db.add(m)
    db.commit()
    refresh_alerts(db, a)
    db.refresh(m)
    return m


# ---------- consultation ----------

@router.get("/astronauts", response_model=list[schemas.AstronautWithStatus])
def list_astronauts(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    q = select(models.Astronaut).order_by(models.Astronaut.id)
    if user.role == "astronaute":
        q = q.where(models.Astronaut.id == user.astronaut_id)
    return [
        schemas.AstronautWithStatus(id=a.id, code=a.code, alias=a.alias, mission_role=a.mission_role,
                                    status=compute(db, a)["status"])
        for a in db.scalars(q)
    ]


@router.get("/astronauts/{astronaut_id}", response_model=schemas.AstronautOut)
def read_astronaut(astronaut_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    check_access(user, astronaut_id)
    return get_astronaut(db, astronaut_id)


@router.get("/astronauts/{astronaut_id}/metrics", response_model=list[schemas.MetricOut])
def read_metrics(astronaut_id: int, indicator: str | None = None, limit: int = Query(500, ge=1, le=5000),
                 user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Mesures brutes reçues des capteurs (les plus récentes d'abord limitées à `limit`)."""
    check_access(user, astronaut_id)
    a = get_astronaut(db, astronaut_id)
    if indicator is not None and indicator not in eng.INDICATORS:
        raise ApiError(422, "unknown_indicator", f"Indicateur inconnu : {indicator}.")
    q = select(models.Metric).where(models.Metric.astronaut_id == a.id)
    if indicator:
        q = q.where(models.Metric.indicator == indicator)
    rows = list(db.scalars(q.order_by(models.Metric.recorded_at.desc()).limit(limit)))
    return list(reversed(rows))


@router.get("/astronauts/{astronaut_id}/daily")
def read_daily(astronaut_id: int, as_of_day: int | None = Query(None, ge=1),
               user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Valeurs journalières (une par jour et par indicateur), prêtes pour les courbes."""
    check_access(user, astronaut_id)
    return daily_points(db, get_astronaut(db, astronaut_id), as_of_day)


@router.get("/astronauts/{astronaut_id}/status", response_model=schemas.StatusOut)
def read_status(astronaut_id: int, as_of_day: int | None = Query(None, ge=1),
                user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Statut calculé. `as_of_day` (jour de mission) permet de rejouer la démo à une date donnée."""
    check_access(user, astronaut_id)
    a = get_astronaut(db, astronaut_id)
    res = compute(db, a, as_of_day)
    last_at, silent, hours = silence_info(db, a)
    if as_of_day is not None:
        silent = False
    reasons = [{"indicator": f.indicator, "level": f.level, "value": f.value,
                "baseline_mean": round(f.baseline.mean, 3), "baseline_std": round(f.baseline.std, 3),
                "z": round(f.z, 2), "explanation": f.explanation, "recommendation": f.recommendation}
               for f in res["findings"]]
    return schemas.StatusOut(status=res["status"], last_day=res["last_day"], last_reading_at=last_at,
                             sensor_silent=silent, silent_hours=hours, reasons=reasons)


@router.get("/astronauts/{astronaut_id}/forecast")
def read_forecast(astronaut_id: int, as_of_day: int | None = Query(None, ge=1),
                  horizon: int = Query(3, ge=1, le=7),
                  user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Prévision de tendance (régression linéaire sur 7 jours). Estimation grossière, incertaine."""
    check_access(user, astronaut_id)
    daily = daily_points(db, get_astronaut(db, astronaut_id), as_of_day)
    out = {}
    for ind, pts in daily.items():
        f = eng.forecast([p["value"] for p in pts], horizon)
        if f:
            last = pts[-1]["day"]
            out[ind] = [{"day": last + x["step"], "value": round(x["value"], 4),
                         "low": round(x["low"], 4), "high": round(x["high"], 4)} for x in f]
    return {"warning": "Prévision indicative par régression linéaire : incertaine, sans valeur médicale.",
            "forecast": out}


# ---------- alertes ----------

@router.get("/alerts", response_model=list[schemas.AlertOut])
def read_alerts(astronaut_id: int | None = None, level: str | None = None,
                user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    q = select(models.Alert)
    if user.role == "astronaute":
        q = q.where(models.Alert.astronaut_id == user.astronaut_id)
    elif astronaut_id is not None:
        q = q.where(models.Alert.astronaut_id == astronaut_id)
    if user.role == "astronaute" and astronaut_id not in (None, user.astronaut_id):
        raise ApiError(403, "forbidden", "Accès refusé à cet astronaute.")
    if level:
        q = q.where(models.Alert.level == level)
    return list(db.scalars(q.order_by(models.Alert.id)))


@router.post("/alerts/{alert_id}/ack", response_model=schemas.AlertOut)
def ack_alert(alert_id: int, user: models.User = Depends(require_roles("astronaute", "medecin")),
              db: Session = Depends(get_db)):
    al = db.get(models.Alert, alert_id)
    if al is None:
        raise ApiError(404, "alert_not_found", f"Alerte {alert_id} introuvable.")
    check_access(user, al.astronaut_id)
    al.acknowledged = True
    db.commit()
    db.refresh(al)
    return al


# ---------- notes médicales (médecin seulement) ----------

@router.get("/astronauts/{astronaut_id}/notes", response_model=list[schemas.NoteOut])
def read_notes(astronaut_id: int, user: models.User = Depends(require_roles("medecin")),
               db: Session = Depends(get_db)):
    a = get_astronaut(db, astronaut_id)
    return list(db.scalars(select(models.Note).where(models.Note.astronaut_id == a.id).order_by(models.Note.id)))


@router.post("/astronauts/{astronaut_id}/notes", response_model=schemas.NoteOut, status_code=201)
def add_note(astronaut_id: int, body: schemas.NoteIn, user: models.User = Depends(require_roles("medecin")),
             db: Session = Depends(get_db)):
    a = get_astronaut(db, astronaut_id)
    n = models.Note(astronaut_id=a.id, text=body.text, author=user.username, created_at=now_utc())
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


# ---------- rapport (médecin seulement) ----------

@router.get("/astronauts/{astronaut_id}/report", response_class=HTMLResponse)
def read_report(astronaut_id: int, as_of_day: int | None = Query(None, ge=1),
                user: models.User = Depends(require_roles("medecin")), db: Session = Depends(get_db)):
    a = get_astronaut(db, astronaut_id)
    res = compute(db, a, as_of_day)
    reasons = [{"level": f.level, "explanation": f.explanation, "recommendation": f.recommendation}
               for f in res["findings"]]
    notes = list(db.scalars(select(models.Note).where(models.Note.astronaut_id == a.id).order_by(models.Note.id)))
    return HTMLResponse(build_report(a, res["status"], reasons, res["daily"], notes, as_of_day))
