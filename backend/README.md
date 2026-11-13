# GRAVITY CARE : backend

Prototype de hackathon. **Données simulées. Pas un dispositif médical, aucun diagnostic.**

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload       # documentation : http://localhost:8000/docs
python -m pytest -q
```

## Fichiers

- `app/engine.py` : agrégation journalière, ligne de base, z-score, règles de démonstration, prévision, recommandations
- `app/simulate.py` : 3 astronautes fictifs, 30 jours, plusieurs mesures par jour (graines fixes)
- `app/sensor_simulator.py` : envoie les mesures à l'API comme un capteur (clé `X-Sensor-Key`)
- `app/api.py` : endpoints ; `app/security.py` : connexion par rôle ; `app/report.py` : rapport HTML imprimable
- `app/models.py`, `app/schemas.py`, `app/database.py`, `app/config.py`, `app/errors.py`, `app/seed.py`

## Droits

| Rôle | Peut |
|---|---|
| astronaute | voir son propre suivi, accuser réception de ses alertes |
| medecin | tout voir, notes, accusés de réception, rapport |
| responsable | consulter l'équipage (lecture seule) |
| capteur (clé `X-Sensor-Key`) | envoyer des mesures uniquement |

Variables d'environnement : `DATABASE_URL`, `GRAVITY_SECRET_KEY`, `GRAVITY_SENSOR_KEY`.
