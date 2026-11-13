#!/usr/bin/env bash
# Lance GRAVITY CARE (backend + frontend) en une commande. Linux et macOS.
# Windows : utilisez WSL, ou suivez les commandes du README.
set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

command -v python3 >/dev/null || { echo "python3 est requis : sudo apt install python3 python3-venv"; exit 1; }
command -v npm >/dev/null || { echo "npm est requis : sudo apt install nodejs npm"; exit 1; }

echo "==> Backend (API sur http://127.0.0.1:8000)"
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv || { echo "Installez d'abord : sudo apt install python3-venv"; exit 1; }
fi
. .venv/bin/activate
pip install -q -r requirements.txt
python -m app.seed
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACK=$!
trap 'kill $BACK 2>/dev/null' EXIT INT TERM

echo "==> Frontend (site sur http://127.0.0.1:5173)"
cd "$ROOT/frontend"
npm install --no-audit --no-fund
npm run dev -- --host 127.0.0.1
