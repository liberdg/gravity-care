"""Simulation de capteurs LANCÉE DEPUIS L'INTERFACE (sans second terminal).

Un fil d'exécution en arrière-plan insère les mesures SIMULÉES au fil du temps, comme le ferait un flux de capteurs.
Les données précédentes (mesures et alertes) sont effacées au démarrage ; astronautes, règles et comptes sont conservés.
"""
import threading
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from . import database, models, simulate
from . import engine as eng
from .api import refresh_alerts

SPEEDS = {"lente": 0.5, "normale": 0.15, "rapide": 0.01}  # secondes entre deux envois de mesures

session_factory = None  # surchargé dans les tests


def get_factory():
    return session_factory or database.SessionLocal


class SimulationRunner:
    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._state = self._idle()

    @staticmethod
    def _idle() -> dict:
        return {"running": False, "finished": False, "progress": 0.0, "day": 0, "total_days": 0,
                "speed": None, "error": None}

    def status(self) -> dict:
        with self._lock:
            return dict(self._state)

    def _set(self, **kw) -> None:
        with self._lock:
            self._state.update(kw)

    def start(self, days: int, speed: str) -> None:
        with self._lock:
            if self._state["running"]:
                raise RuntimeError("already running")
            self._state = {**self._idle(), "running": True, "total_days": days, "speed": speed}
        self._stop.clear()
        self._thread = threading.Thread(target=self.run, args=(get_factory(), days, SPEEDS[speed]), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def wait(self, timeout: float = 60.0) -> None:
        if self._thread:
            self._thread.join(timeout)

    def run(self, factory, days: int, interval: float) -> None:
        """Exécution synchrone (utilisée par le fil et par les tests)."""
        self._stop.clear()
        self._set(running=True, finished=False, total_days=days, error=None)
        try:
            with factory() as db:
                astronauts = {a.code: a for a in db.scalars(select(models.Astronaut))}
                if not astronauts:
                    raise RuntimeError("Aucun astronaute en base : lancez python -m app.seed")
                db.execute(delete(models.Alert))
                db.execute(delete(models.Metric))
                db.commit()

                batches: dict[tuple[int, int], list[tuple[str, dict]]] = {}
                for code in astronauts:
                    for r in simulate.generate_readings(code):
                        if r["day"] <= days:
                            batches.setdefault((r["day"], r["hour"]), []).append((code, r))
                today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                start = today - timedelta(days=days - 1)

                keys = sorted(batches)
                for i, key in enumerate(keys, start=1):
                    if self._stop.is_set():
                        break
                    touched = set()
                    for code, r in batches[key]:
                        a = astronauts[code]
                        db.add(models.Metric(astronaut_id=a.id, indicator=r["indicator"], value=r["value"],
                                             unit=eng.INDICATORS[r["indicator"]]["unit"],
                                             recorded_at=simulate.reading_time(start, r["day"], r["hour"]),
                                             source="simulated"))
                        touched.add(code)
                    db.commit()
                    for code in touched:
                        refresh_alerts(db, astronauts[code])
                    self._set(progress=round(i / len(keys), 3), day=key[0])
                    if interval:
                        time.sleep(interval)
        except Exception as exc:  # noqa: BLE001
            self._set(error=str(exc))
        finally:
            self._set(running=False, finished=not self._stop.is_set() and self._state["error"] is None)


runner = SimulationRunner()
