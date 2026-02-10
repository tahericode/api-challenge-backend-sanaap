from pathlib import Path

import environ


BASE_DIR = Path(__file__).resolve().parents[3]

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")


# Toggle between MinIO and local filesystem storage using an env flag.
# When USE_MINIO=false, files are stored under BASE_DIR/docs instead.
USE_MINIO = env.bool("USE_MINIO", default=True)

if USE_MINIO:
    DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"

    MINIO_STORAGE_ENDPOINT = env("MINIO_ENDPOINT", default="localhost:9000")
    MINIO_STORAGE_ACCESS_KEY = env("MINIO_ACCESS_KEY", default="minioadmin")
    MINIO_STORAGE_SECRET_KEY = env("MINIO_SECRET_KEY", default="minioadmin")
    MINIO_STORAGE_USE_HTTPS = False
    MINIO_STORAGE_MEDIA_BUCKET_NAME = "documents"
else:
    # Local filesystem storage: store uploaded docs under <project-root>/docs
    from django.core.files.storage import FileSystemStorage  # noqa: F401

    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = BASE_DIR / "docs"
    MEDIA_URL = "/media/"
