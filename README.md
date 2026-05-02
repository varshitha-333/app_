# Google Drive Flask Backend

Production-ready REST API for Google Drive operations — create folders, create files, edit files, and upload binaries.

---

## Project Structure

```
gdrive_backend/
├── app.py                  # Application factory
├── config.py               # Environment-driven configuration
├── gunicorn.conf.py        # Production WSGI settings
├── requirements.txt
├── .env.example            # Copy to .env and fill in values
├── routes/
│   └── drive.py            # All four Drive endpoints
├── services/
│   └── drive_service.py    # Drive API wrapper
└── utils/
    ├── error_handlers.py   # Global HTTP error handlers
    └── validators.py       # Per-endpoint input validation
```

---

## Setup

### 1 — Google Cloud prerequisites

1. Create a project at [console.cloud.google.com](https://console.cloud.google.com).
2. Enable the **Google Drive API**.
3. Create a **Service Account** → download the JSON key.
4. Share the target Drive folder (or root) with the service account email (`…@….iam.gserviceaccount.com`) as **Editor**.

### 2 — Environment

```bash
cp .env.example .env
# Edit .env — set GOOGLE_SERVICE_ACCOUNT_FILE (or JSON) and other values
```

### 3 — Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4 — Run

**Development**
```bash
FLASK_ENV=development python app.py
```

**Production (Gunicorn)**
```bash
gunicorn -c gunicorn.conf.py "app:create_app()"
```

---

## API Reference

All endpoints return:
```json
{ "success": true,  "data": { … } }   // 200 / 201
{ "success": false, "error": "…", "details": "…" }  // 4xx / 5xx
```

---

### `POST /api/create-folder`

Create a Google Drive folder.

**Request body (JSON)**

| Field       | Type   | Required | Description                     |
|-------------|--------|----------|---------------------------------|
| `name`      | string | ✅       | Folder name                     |
| `parent_id` | string | ❌       | Parent folder ID (Drive root if omitted) |

**Example**
```bash
curl -X POST http://localhost:5000/api/create-folder \
  -H "Content-Type: application/json" \
  -d '{"name": "Hospital Reports", "parent_id": "1BxiMV…"}'
```

---

### `POST /api/create-file`

Create a new Drive file (Google Doc, plain text, etc.).

**Request body (JSON)**

| Field       | Type   | Required | Description                                         |
|-------------|--------|----------|-----------------------------------------------------|
| `name`      | string | ✅       | File name                                           |
| `mime_type` | string | ❌       | MIME type (default: `application/vnd.google-apps.document`) |
| `parent_id` | string | ❌       | Parent folder ID                                    |
| `content`   | string | ❌       | Plain-text content                                  |

**Example**
```bash
curl -X POST http://localhost:5000/api/create-file \
  -H "Content-Type: application/json" \
  -d '{"name": "Delivery Log", "content": "Initial entry."}'
```

---

### `PATCH /api/edit-file`

Rename and/or replace the content of an existing file.

**Request body (JSON)**

| Field         | Type   | Required | Description                         |
|---------------|--------|----------|-------------------------------------|
| `file_id`     | string | ✅       | Drive file ID                       |
| `new_name`    | string | ❌*      | New file name                       |
| `new_content` | string | ❌*      | Replacement text body               |
| `mime_type`   | string | ❌       | MIME of `new_content` (default: `text/plain`) |

\* At least one of `new_name` or `new_content` is required.

**Example**
```bash
curl -X PATCH http://localhost:5000/api/edit-file \
  -H "Content-Type: application/json" \
  -d '{"file_id": "1Cdx…", "new_name": "Delivery Log v2", "new_content": "Updated entry."}'
```

---

### `POST /api/upload-file`

Upload a binary file to Drive (multipart form data).

**Form fields**

| Field        | Type | Required | Description                              |
|--------------|------|----------|------------------------------------------|
| `file`       | file | ✅       | Binary file to upload                    |
| `parent_id`  | str  | ❌       | Parent folder ID                         |
| `drive_name` | str  | ❌       | Override filename in Drive               |

**Example**
```bash
curl -X POST http://localhost:5000/api/upload-file \
  -F "file=@/path/to/report.pdf" \
  -F "parent_id=1BxiMV…"
```

---

## Error Codes

| Code | Meaning                          |
|------|----------------------------------|
| 400  | Bad request / malformed JSON     |
| 404  | Endpoint not found               |
| 413  | File exceeds `MAX_UPLOAD_MB`     |
| 415  | Wrong Content-Type               |
| 422  | Validation error (see `details`) |
| 502  | Google Drive API error           |
| 500  | Unhandled server error           |
