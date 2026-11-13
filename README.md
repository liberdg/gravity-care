# GRAVITY CARE

Logiciel de surveillance de la santé d'astronautes (NASA Space Apps Challenge 2026, projet tutoré EPL).

> **Prototype pédagogique.** Pas un dispositif médical, aucun diagnostic. Toutes les données sont **simulées**.

Principe : **collecter → analyser → évaluer → alerter → accompagner**. Les capteurs (simulés) envoient les mesures
automatiquement : personne ne saisit de mesure. Chaque astronaute est comparé à sa propre ligne de base (7 premiers
jours) ; les alertes sont expliquées, avec des règles de **démonstration** (pas des seuils médicaux).

## Lancer en 6 commandes

```
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
# dans un autre terminal : cd frontend && npm install && npm run dev
```

Ouvrir http://localhost:5173 (API : http://localhost:8000/docs).

## Comptes de démonstration

| Identifiant | Mot de passe | Rôle |
|---|---|---|
| medecin | medecin-demo | Médecin au sol (tout, notes, rapport) |
| responsable | responsable-demo | Responsable de mission (consultation) |
| astro_a, astro_b, astro_c | astro-a-demo, astro-b-demo, astro-c-demo | Astronaute (son propre suivi) |

## Démonstration automatique (capteurs simulés)

```
cd backend
python -m app.seed --reset --empty
uvicorn app.main:app --reload
# autre terminal :
python -m app.sensor_simulator --interval 0.2
```
Le tableau de bord se remplit tout seul (mise à jour toutes les 5 secondes). Le curseur « Jour de mission » rejoue la
démonstration : au jour 21, Astro-B passe orange ; au jour 30 : A vert, B rouge, C orange.

## Tests

```
cd backend && python -m pytest -q
cd frontend && npm test
```

## Structure

`backend/` API FastAPI, moteur d'analyse, simulateur · `frontend/` interface React · `data/` note sur les données ·
`docs/` documentation.

## Limites

Aucune donnée réelle · règles d'alerte de démonstration · la valeur absolue de z déclenche aussi une alerte sur une
hausse (ex. sommeil) · sécurité de niveau prototype (changer `GRAVITY_SECRET_KEY` et `GRAVITY_SENSOR_KEY` hors démo) ·
le mode hors-ligne garde l'interface et les dernières données consultées.
