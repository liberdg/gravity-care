"""Remplit la base avec les données SIMULÉES.

Usage :
  python -m app.seed             # astronautes, règles, comptes et 30 jours de mesures
  python -m app.seed --empty     # sans mesures : à remplir avec le simulateur de capteurs
  python -m app.seed --reset     # recrée la base
"""
import sys
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import engine as eng
from . import models, simulate
from .api import refresh_alerts
from .database import Base, SessionLocal, engine
from .security import hash_password

# Comptes de DÉMONSTRATION (jamais de vrais mots de passe dans le code en production)
DEMO_USERS = [
    ("medecin", "medecin-demo", "medecin", None),
    ("responsable", "responsable-demo", "responsable", None),
    ("astro_a", "astro-a-demo", "astronaute", "A"),
    ("astro_b", "astro-b-demo", "astronaute", "B"),
    ("astro_c", "astro-c-demo", "astronaute", "C"),
]


def seed(db: Session, with_metrics: bool = True, start: datetime = simulate.DEFAULT_START) -> None:
    for ind in eng.INDICATORS:
        db.add(models.Rule(indicator=ind, params=eng.DEFAULT_PARAMS,
                           justification=eng.DEMO_JUSTIFICATION, is_demo=True))
    ids = {}
    for spec in simulate.ASTRONAUTS:
        a = models.Astronaut(**spec, baseline_days=7)
        db.add(a)
        db.flush()
        ids[spec["code"]] = a.id
        if with_metrics:
            for r in simulate.generate_readings(spec["code"]):
                db.add(models.Metric(astronaut_id=a.id, indicator=r["indicator"], value=r["value"],
                                     unit=eng.INDICATORS[r["indicator"]]["unit"],
                                     recorded_at=simulate.reading_time(start, r["day"], r["hour"]),
                                     source="simulated"))
    for username, password, role, code in DEMO_USERS:
        db.add(models.User(username=username, password_hash=hash_password(password), role=role,
                           astronaut_id=ids.get(code)))
    db.commit()
    if with_metrics:
        for a in db.scalars(select(models.Astronaut)):
            refresh_alerts(db, a)


if __name__ == "__main__":
    if "--reset" in sys.argv:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(models.Astronaut).limit(1)):
            print("Base déjà remplie. Utilisez --reset pour la recréer.")
        else:
            seed(db, with_metrics="--empty" not in sys.argv)
            print("Base initialisée : 3 astronautes fictifs, comptes de démonstration, règles."
                  + ("" if "--empty" in sys.argv else " 30 jours de mesures simulées chargées."))
