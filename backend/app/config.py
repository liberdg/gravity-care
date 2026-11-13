"""Configuration. Les valeurs par défaut servent à la démo ; changez-les hors démonstration."""
import os

SECRET_KEY = os.getenv("GRAVITY_SECRET_KEY", "dev-secret-change-me")
SENSOR_API_KEY = os.getenv("GRAVITY_SENSOR_KEY", "demo-sensor-key")
TOKEN_TTL_SECONDS = 8 * 3600
SILENT_AFTER_HOURS = 24  # capteur « silencieux » si sa dernière mesure a plus de 24 h de retard
