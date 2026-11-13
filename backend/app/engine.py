"""Moteur d'analyse : agrégation, ligne de base personnelle, z-score, alertes explicables, prévision.

ATTENTION : toutes les règles ci-dessous sont des RÈGLES DE DÉMONSTRATION.
Ce ne sont pas des seuils médicaux et elles ne posent aucun diagnostic.
"""
from dataclasses import dataclass
from math import sqrt
from statistics import mean, stdev

# agg : comment regrouper les mesures d'une journée (moyenne pour un signal continu, somme pour un total)
INDICATORS = {
    "heart_rate_rest": {"label": "Fréquence cardiaque au repos", "unit": "bpm", "min": 20, "max": 250, "agg": "mean"},
    "spo2": {"label": "SpO2", "unit": "%", "min": 50, "max": 100, "agg": "mean"},
    "sleep_hours": {"label": "Sommeil", "unit": "h", "min": 0, "max": 24, "agg": "sum"},
    "activity_minutes": {"label": "Activité physique", "unit": "min", "min": 0, "max": 1440, "agg": "sum"},
    "hrv": {"label": "Variabilité de la fréquence cardiaque (HRV)", "unit": "ms", "min": 5, "max": 300, "agg": "mean"},
    "radiation_dose": {"label": "Dose de radiations (SIMULÉE, sans portée scientifique)", "unit": "mSv", "min": 0, "max": 20, "agg": "sum"},
}

DEFAULT_PARAMS = {
    "warn_z": 2.0,            # |z| minimum pour orange
    "warn_days": 2,           # jours consécutifs requis pour orange
    "crit_z": 3.0,            # |z| minimum pour rouge (un seul jour suffit)
    "crit_persist_days": 4,   # ou |z| >= warn_z pendant ce nombre de jours : rouge
}

DEMO_JUSTIFICATION = (
    "Règle de démonstration : écart à la ligne de base personnelle de l'astronaute. "
    "Ce n'est pas un seuil médical."
)

# Textes fixes et informatifs. Ce ne sont PAS des conseils médicaux.
RECOMMENDATIONS = {
    "heart_rate_rest": "Information : un écart persistant de la fréquence cardiaque au repos peut mériter un échange avec l'équipe médicale.",
    "spo2": "Information : un écart de SpO2 peut venir du capteur. À confirmer par une nouvelle mesure et l'équipe médicale.",
    "sleep_hours": "Information : une baisse durable du sommeil peut justifier d'en parler à l'équipe médicale.",
    "activity_minutes": "Information : un changement d'activité peut être discuté avec l'équipe chargée de l'exercice physique.",
    "hrv": "Information : une baisse de la HRV est un indice indirect de fatigue ou de stress. À interpréter avec l'équipe médicale.",
    "radiation_dose": "Information : valeur simulée pour la démonstration, sans signification scientifique.",
}
RECOMMENDATION_FOOTER = " Ce texte est informatif et ne remplace pas un avis médical."


def aggregate(values: list[float], agg: str) -> float:
    return sum(values) if agg == "sum" else mean(values)


@dataclass(frozen=True)
class Baseline:
    mean: float
    std: float
    n: int


@dataclass(frozen=True)
class Finding:
    indicator: str
    level: str  # "orange" ou "rouge"
    value: float
    baseline: Baseline
    z: float
    explanation: str
    recommendation: str


def compute_baseline(values: list[float]) -> Baseline | None:
    """Moyenne et écart-type des valeurs de référence (au moins 2 valeurs).

    L'écart-type a un plancher (2 % de la moyenne) pour éviter une division par ~0
    quand la base est presque constante. Choix de démonstration, à documenter.
    """
    if len(values) < 2:
        return None
    m = mean(values)
    s = max(stdev(values), 0.02 * abs(m), 1e-6)
    return Baseline(mean=m, std=s, n=len(values))


def zscore(value: float, baseline: Baseline) -> float:
    return (value - baseline.mean) / baseline.std


def evaluate_indicator(
    indicator: str, values: list[float], baseline_days: int, params: dict | None = None
) -> Finding | None:
    """Évalue un indicateur. `values` = une valeur par jour, ordre chronologique.

    Retourne None si pas assez de données (calibration) ou si tout est normal.
    Limite : « jours consécutifs » = jours consécutifs AYANT des mesures.
    """
    p = {**DEFAULT_PARAMS, **(params or {})}
    if len(values) <= baseline_days:
        return None
    baseline = compute_baseline(values[:baseline_days])
    if baseline is None:
        return None
    zs = [zscore(v, baseline) for v in values[baseline_days:]]
    last = zs[-1]

    k = p["crit_persist_days"]
    critical = abs(last) >= p["crit_z"] or (
        len(zs) >= k and all(abs(z) >= p["warn_z"] for z in zs[-k:])
    )
    w = p["warn_days"]
    warning = len(zs) >= w and all(abs(z) >= p["warn_z"] for z in zs[-w:])

    if not (critical or warning):
        return None
    level = "rouge" if critical else "orange"
    info = INDICATORS[indicator]
    sens = "inférieure" if last < 0 else "supérieure"
    explanation = (
        f"{info['label']} : {values[-1]:.2f} {info['unit']}, soit une valeur {sens} "
        f"à la base personnelle ({baseline.mean:.2f} ± {baseline.std:.2f} {info['unit']}, "
        f"écart z = {last:+.1f}). {DEMO_JUSTIFICATION}"
    )
    reco = RECOMMENDATIONS[indicator] + RECOMMENDATION_FOOTER
    return Finding(indicator, level, values[-1], baseline, last, explanation, reco)


def global_status(findings: list[Finding], calibrated: bool) -> str:
    if not calibrated:
        return "calibration"
    if any(f.level == "rouge" for f in findings):
        return "rouge"
    if any(f.level == "orange" for f in findings):
        return "orange"
    return "vert"


def forecast(values: list[float], horizon: int = 3, window: int = 7) -> list[dict] | None:
    """Prévision de tendance par régression linéaire sur les derniers jours.

    Retourne, pour chaque pas k = 1..horizon : valeur projetée et intervalle (low, high).
    Estimation grossière, à présenter avec un avertissement d'incertitude. None si < 4 points.
    """
    ys = values[-window:]
    n = len(ys)
    if n < 4:
        return None
    xs = list(range(n))
    xbar, ybar = mean(xs), mean(ys)
    sxx = sum((x - xbar) ** 2 for x in xs)
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sxx
    intercept = ybar - slope * xbar
    resid = [y - (intercept + slope * x) for x, y in zip(xs, ys)]
    s = sqrt(sum(r * r for r in resid) / (n - 2))
    out = []
    for k in range(1, horizon + 1):
        x = n - 1 + k
        pred = intercept + slope * x
        margin = 1.96 * s * sqrt(1 + 1 / n + (x - xbar) ** 2 / sxx)
        out.append({"step": k, "value": pred, "low": pred - margin, "high": pred + margin})
    return out
