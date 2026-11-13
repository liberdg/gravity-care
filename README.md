# GRAVITY CARE

Logiciel de surveillance de la santé d'astronautes (NASA Space Apps Challenge 2026, projet tutoré EPL).

> **Prototype pédagogique.** Pas un dispositif médical, aucun diagnostic. Toutes les données sont **simulées**.

Principe : **collecter → analyser → évaluer → alerter → accompagner**. Les capteurs (simulés) envoient les mesures
automatiquement : personne ne saisit de mesure. Chaque astronaute est comparé à sa propre ligne de base (7 premiers
jours) ; les alertes sont expliquées, avec des règles de **démonstration** (pas des seuils médicaux).

## Lancer (Linux / macOS)

Une seule commande, depuis la racine du dépôt :

```
./start.sh
```

Puis ouvrez **http://127.0.0.1:5173** (l'API est sur http://127.0.0.1:8000/docs). Arrêt : `Ctrl+C`.

### Sans le script (étape par étape)

Terminal 1 : backend

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2 : frontend

```
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Sous Windows : utilisez WSL, ou remplacez `source .venv/bin/activate` par `.venv\Scripts\activate` et `python3` par `python`.

## Utiliser le site

1. Page d'accueil, puis **Tableau de bord** : connectez-vous (comptes ci-dessous).
2. Cliquez sur **Lancer la simulation des capteurs** : les mesures simulées arrivent toutes seules et le tableau de bord
   se remplit en direct (vitesse rapide : environ 5 s).
3. Cliquez sur un astronaute : alertes expliquées, courbes, prévision, notes, rapport (médecin).
4. Le curseur **Jour** rejoue la démonstration : au jour 21, Astro-B passe orange ; au jour 30 : A vert, B rouge, C orange.

## Comptes de démonstration

| Identifiant | Mot de passe | Rôle |
|---|---|---|
| medecin | medecin-demo | Médecin au sol (tout, notes, rapport, simulation) |
| responsable | responsable-demo | Responsable de mission (consultation, simulation) |
| astro_a, astro_b, astro_c | astro-a-demo, astro-b-demo, astro-c-demo | Astronaute (son propre suivi) |

## Simulation en ligne de commande (facultatif)

Le bouton du site suffit. Pour envoyer les mesures depuis un terminal, comme le ferait un vrai capteur :

```
cd backend && source .venv/bin/activate
python -m app.seed --reset --empty
uvicorn app.main:app --host 127.0.0.1 --port 8000
# autre terminal :
python -m app.sensor_simulator --interval 0.2
```

## Si ça ne marche pas

| Problème | Solution |
|---|---|
| `python : commande introuvable` | Sur Ubuntu, la commande est `python3` |
| `externally-managed-environment` | Utilisez l'environnement virtuel : `python3 -m venv .venv` puis `source .venv/bin/activate` |
| `ensurepip is not available` | `sudo apt install python3-venv` |
| `npm : commande introuvable` ou Node trop ancien | `sudo apt install nodejs npm`, ou installez Node 20 avec nvm |
| `npm ERESOLVE` | Déjà géré par `frontend/.npmrc`. Sinon : `npm install --legacy-peer-deps` |
| Le site s'affiche mais « Impossible de joindre le serveur » | Le backend ne tourne pas : lancez-le (port 8000) |
| Tableau de bord vide | Cliquez sur « Lancer la simulation des capteurs » |

## Tests

```
cd backend && python -m pytest -q
cd frontend && npm test
```

## Structure

`backend/` API FastAPI, moteur d'analyse, simulateur · `frontend/` site React (accueil, méthode, tableau de bord) ·
`data/` note sur les données · `docs/` documentation · `start.sh` lancement en une commande.

## Limites

Aucune donnée réelle · règles d'alerte de démonstration · la valeur absolue de z déclenche aussi une alerte sur une
hausse (ex. sommeil) · sécurité de niveau prototype (changer `GRAVITY_SECRET_KEY` et `GRAVITY_SENSOR_KEY` hors démo) ·
le mode hors-ligne garde l'interface et les dernières données consultées.
