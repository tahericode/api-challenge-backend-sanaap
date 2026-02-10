## Document Management System (DMS)

This project is a Django REST Framework–based **Document Management System**.  
It provides secure, role-based APIs for uploading, updating, retrieving, and deleting documents, backed by MinIO object storage, PostgreSQL, Redis, and Celery.

---

## 1. How to Run the Project

### 1.1. Prerequisites

- Python 3.11
- Docker + Docker Compose
- `poetry` (for dependency management) or equivalent

### 1.2. Environment variables

Create a `.env` file in the project root (same level as `manage.py`) with at least:

```env
SECRET_KEY=replace-with-a-strong-secret-key

# Database (if using docker-compose db)
DATABASE_URL=postgres://admin:admin@db:5432/dms

# MinIO (for docker-compose setup)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
```

You can adjust these for your own environment (e.g. local Postgres, MinIO, etc.).

---

### 1.3. Using Taskfile

All common flows are wrapped in `Taskfile.yml`. From the project root:

#### A) Full stack with Docker (recommended)

```bash
task docker-dev
```

This runs:

- `docker compose up --build`

Services:

- `web` – Django + Gunicorn (`web:8000`, exposed at `localhost:8000`)
- `db` – PostgreSQL
- `redis` – Redis (for Celery + caching)
- `minio` – MinIO object storage
- `nginx` – reverse proxy (`http://localhost/`)

#### B) Hybrid dev (Django local, infra via Docker)

```bash
task dev
```

This will:

1. Install dependencies with Poetry (via `install`).
2. Start `db`, `redis`, `minio` via:

   ```bash
   docker compose up -d db redis minio
   ```

3. Run:

   ```bash
   poetry run python manage.py makemigrations
   poetry run python manage.py migrate
   poetry run python manage.py runserver 0.0.0.0:8000
   ```

Django dev server runs at `http://localhost:8000`.

#### C) Pure local Django (no Docker at all)

If you have Postgres, Redis, MinIO configured locally:

```bash
task local-dev
```

This will:

```bash
poetry install
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8000
```

You must ensure your local DB/Redis/MinIO match your settings.

#### D) Creating a superuser

For admin access:

```bash
task createsuperuser
```

Follow the prompts, then log in at `/admin/`.

---

## 2. How to Use the APIs (Postman / HTTP clients)

All protected APIs use **JWT tokens**. No session auth is used in the API layer.

### 2.1. Obtain JWT tokens (login)

**Endpoint**

- `POST /api/users/token/`

**Request body**

```json
{
  "username": "admin",
  "password": "adminpass"
}
```

**Response**

```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>"
}
```

Use `<ACCESS_TOKEN>` in:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

To refresh:

```http
POST /api/users/token/refresh/
Content-Type: application/json

{
  "refresh": "<REFRESH_TOKEN>"
}
```

---

### 2.2. Role-Based Access Control (RBAC)

Roles are implemented using Django `Group`s:

- `admin`
  - Full access to all documents.
  - Can manage users (create/update) and assign roles.
- `editor`
  - Can upload and update documents.
  - Cannot delete documents.
- `viewer`
  - Read-only: can list and retrieve documents.

Create these groups once via `/admin/` and assign your admin user to the `admin` group.

---

### 2.3. User Management Endpoints (admin-only)

Base URL:

- `/api/users/users/`

All these endpoints require an `access` token for a user in the `admin` group:

```http
Authorization: Bearer <ADMIN_ACCESS_TOKEN>
```

#### 2.3.1. Create a user with roles

**Endpoint**

- `POST /api/users/users/`

**Body**

```json
{
  "username": "editor1",
  "email": "editor1@example.com",
  "password": "testpass123",
  "roles": ["editor"]
}
```

#### 2.3.2. List users

**Endpoint**

- `GET /api/users/users/`

#### 2.3.3. Change roles of a user

**Endpoint**

- `POST /api/users/users/{id}/set_roles/`

**Body**

```json
{
  "roles": ["viewer"]
}
```

---

### 2.4. Document API Endpoints

Base URL:

- `/api/documents/`

All document endpoints require:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

Role controls which operations are allowed.

#### 2.4.1. Upload a document (admin/editor)

**Endpoint**

- `POST /api/documents/`

**Headers**

- `Authorization: Bearer <ACCESS_TOKEN>`
- `Idempotency-Key: some-unique-string`

**Body (multipart/form-data)**

- Key: `file` (type: File)

**Example (curl)**

```bash
curl -X POST http://localhost/api/documents/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Idempotency-Key: upload-123" \
  -F "file=@/path/to/myfile.pdf"
```

Behavior:

- File is stored in MinIO (via `django-minio-storage`).
- `Document` metadata is saved in PostgreSQL.
- An `IdempotencyKey` is stored to prevent duplicate uploads.
- A Celery task (`process_document`) is queued (best-effort).

#### 2.4.2. List documents (all roles)

**Endpoint**

- `GET /api/documents/`

**Query parameters**

- `uploaded_by=<user_id>`
- `status=<status>`
- `search=<text>`
- `ordering=created_at` or `ordering=-size`
- `page=<int>`
- `page_size=<int>` (max 100)

#### 2.4.3. Retrieve a document

**Endpoint**

- `GET /api/documents/{id}/`

Returns document metadata.

#### 2.4.4. Secure download URL

**Endpoint**

- `GET /api/documents/{id}/download/`

**Response**

```json
{ "url": "https://minio/..." }
```

#### 2.4.5. Update a document (admin/editor)

**Endpoint**

- `PATCH /api/documents/{id}/`

**Body (example)**

```json
{ "original_name": "renamed-file.pdf" }
```

#### 2.4.6. Delete a document (admin only)

**Endpoint**

- `DELETE /api/documents/{id}/`

---

## 3. Architecture Overview

- `apps/users/`
  - Custom `User` model (`UUID` primary key).
  - `UserViewSet` for admin-only user management.
  - Permissions: `IsAdmin`, `IsEditor`, `IsViewer` (Django `Group`s).
- `apps/documents/`
  - `models/` – `Document`, `IdempotencyKey`, `DocumentVersion`.
  - `api/` – `DocumentViewSet` with filters, search, ordering, pagination.
  - `services/` – `create_document` encapsulates document creation, idempotency, and background processing.
  - `selectors/` – helpers for list/update queries.
  - `tasks.py` – `process_document` Celery task.
- `apps/audit/`
  - `AuditLog` model with signals wired to `Document` create/update/delete.
- `config/`
  - Settings split into `database`, `cache`, `drf`, `storage`.
  - `celery.py` – Celery app config.
  - `urls.py` – API routing and Swagger integration.
- `core/commons/`
  - `pagination/custom_pagination.py` – custom paginator for DRF.

---

## 4. Background Processing

- Celery is configured in `config/celery.py`.
- Document uploads call `process_document.delay(doc.id)` inside a `try/except`:
  - If Redis/broker and worker are running, work is processed async.
  - If not, the API still returns success (only background work is skipped).

Run a worker locally:

```bash
poetry run celery -A config.celery.app worker -l info
```

---

## 5. Audit Logging

- `AuditLog` tracks:
  - `user`, `action` (`create`, `update`, `delete`), `model_name`, `object_id`, `timestamp`.
- Signals in `apps.audit.signals` listen to `Document` `post_save` and `post_delete` and automatically create `AuditLog` rows.

---

## 6. API Documentation (Swagger)

- OpenAPI schema: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`

Powered by **drf-spectacular** and auto-generates from your DRF views/serializers.

---

## 7. Testing

Basic tests:

- `apps/users/tests.py` – auth + admin user management.
- `apps/documents/tests.py` – upload + RBAC enforcement.

Run all tests:

```bash
poetry run python manage.py test
```

---

This README is structured to answer:

- **How to run the system** (Taskfile + Docker + local).
- **How to use the APIs** (JWT auth, RBAC, document endpoints).
- **How it’s designed** (architecture, background tasks, audit logging, docs, tests).
