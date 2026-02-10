import environ
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"

MINIO_STORAGE_ENDPOINT = env("MINIO_ENDPOINT", default="localhost:9000")
MINIO_STORAGE_ACCESS_KEY = env("MINIO_ACCESS_KEY", default="minioadmin")
MINIO_STORAGE_SECRET_KEY = env("MINIO_SECRET_KEY", default="minioadmin")
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = "documents"