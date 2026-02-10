import environ
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
    }
}