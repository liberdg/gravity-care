"""Données SIMULÉES : trois astronautes fictifs, 30 jours. Jamais de vraies données.

Chaque jour, des « capteurs » produisent plusieurs mesures par indicateur ; le système les regroupe
(voir engine.aggregate). Les graines fixes rendent la démonstration reproductible.
"""
import random
from datetime import datetime, timedelta
from statistics import mean

DAYS = 30
SEED = {"A": 18, "B": 39, "C": 20}  # graines choisies pour que le scénario de démo soit reproductible

# mu, sd : valeur journalière normale ; n : nombre de mesures par jour ; hours : heures d'envoi ; agg : voir engine
SPEC = {
    "heart_rate_rest": dict(mu=58.0, sd=1.5, hours=(2, 8, 14, 20), agg="mean"),
    "spo2": dict(mu=97.5, sd=0.4, hours=(2, 8, 14, 20), agg="mean"),
    "sleep_hours": dict(mu=7.2, sd=0.3, hours=(7,), agg="sum"),
    "activity_minutes": dict(mu=120.0, sd=8.0, hours=(8, 20), agg="sum"),
    "hrv": dict(mu=55.0, sd=3.0, hours=(2, 8, 14, 20), agg="mean"),
    "radiation_dose": dict(mu=0.50, sd=0.03, hours=(2, 8, 14, 20), agg="sum"),
}

ASTRONAUTS = [
    {"code": "A", "alias": "Astro-A", "mission_role": "Commandant (fictif)"},
    {"code": "B", "alias": "Astro-B", "mission_role": "Ingénieur de vol (fictif)"},
    {"code": "C", "alias": "Astro-C", "mission_role": "Spécialiste de mission (fictif)"},
]

# Anomalies injectées
B_START_DAY = 18
B_SLEEP_SLOPE = 0.2   # heures perdues par jour depuis B_START_DAY
B_HR_SLOPE = 1.0      # bpm gagnés par jour
B_HRV_SLOPE = 1.5     # ms perdues par jour
C_DAYS = (29, 30)
C_SPO2_DROP = 1.1

DEFAULT_START = datetime(2026, 1, 1)  # début de mission FICTIF pour la base de démonstration


def generate_daily(code: str, seed: int | None = None) -> dict[str, list[float]]:
    rng = random.Random(SEED[code] if seed is None else seed)
    series: dict[str, list[float]] = {}
    for ind, spec in SPEC.items():
        vals = []
        for day in range(1, DAYS + 1):
            v = rng.gauss(spec["mu"], spec["sd"])
            if code == "B" and day >= B_START_DAY:
                k = day - B_START_DAY + 1
                if ind == "sleep_hours":
                    v -= B_SLEEP_SLOPE * k
                if ind == "heart_rate_rest":
                    v += B_HR_SLOPE * k
                if ind == "hrv":
                    v -= B_HRV_SLOPE * k
            if code == "C" and ind == "spo2" and day in C_DAYS:
                v -= C_SPO2_DROP
            vals.append(max(v, 0.0))
        series[ind] = vals
    return series


def generate_readings(code: str, seed: int | None = None) -> list[dict]:
    """Mesures brutes envoyées par les capteurs, triées dans le temps : {day, hour, indicator, value}."""
    base_seed = SEED[code] if seed is None else seed
    daily = generate_daily(code, base_seed)
    rng = random.Random(base_seed + 1000)
    readings = []
    for day in range(1, DAYS + 1):
        for ind, spec in SPEC.items():
            value, hours = daily[ind][day - 1], spec["hours"]
            n = len(hours)
            if n == 1:
                vals = [round(value, 3)]
            elif spec["agg"] == "mean":
                offs = [rng.gauss(0, spec["sd"] * 0.4) for _ in range(n)]
                m = mean(offs)
                vals = [round(value + o - m, 3) for o in offs]
            else:
                vals = [round(value / n, 4)] * n
            for hour, v in zip(hours, vals):
                readings.append({"day": day, "hour": hour, "indicator": ind, "value": v})
    readings.sort(key=lambda r: (r["day"], r["hour"]))
    return readings


def reading_time(start: datetime, day: int, hour: int) -> datetime:
    return start + timedelta(days=day - 1, hours=hour)
