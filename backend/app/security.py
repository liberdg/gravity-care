"""Mots de passe hachés (PBKDF2), jetons signés (HMAC) et contrôle d'accès par rôle.

Niveau PROTOTYPE : suffisant pour la démonstration, pas pour la production.
"""
import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from . import config, models
from .database import get_db
from .errors import ApiError

ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITERATIONS)
    return hmac.compare_digest(digest.hex(), digest_hex)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def make_token(user_id: int) -> str:
    payload = _b64(json.dumps({"sub": user_id, "exp": int(time.time()) + config.TOKEN_TTL_SECONDS}).encode())
    sig = _b64(hmac.new(config.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def read_token(token: str) -> int | None:
    try:
        payload, sig = token.split(".")
        expected = _b64(hmac.new(config.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        data = json.loads(_unb64(payload))
        return data["sub"] if data["exp"] >= time.time() else None
    except Exception:
        return None


def current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> models.User:
    if not authorization or not authorization.startswith("Bearer "):
        raise ApiError(401, "not_authenticated", "Connexion requise.")
    user_id = read_token(authorization[7:])
    user = db.get(models.User, user_id) if user_id else None
    if user is None:
        raise ApiError(401, "invalid_token", "Session invalide ou expirée.")
    return user


def require_roles(*roles: str):
    def checker(user: models.User = Depends(current_user)) -> models.User:
        if user.role not in roles:
            raise ApiError(403, "forbidden", "Votre rôle n'autorise pas cette action.")
        return user

    return checker


def sensor_auth(x_sensor_key: str | None = Header(None)) -> None:
    if not x_sensor_key or not hmac.compare_digest(x_sensor_key, config.SENSOR_API_KEY):
        raise ApiError(401, "invalid_sensor_key", "Clé de capteur manquante ou invalide.")
