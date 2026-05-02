"""
Drive API routes blueprint.

Endpoints
---------
POST /api/create-folder   — create a Drive folder
POST /api/create-file     — create a blank Drive file
PATCH /api/edit-file      — rename and/or update file content
POST /api/upload-file     — upload a binary file to Drive
"""

import logging
import os
import uuid

from flask import Blueprint, current_app, jsonify, request
from googleapiclient.errors import HttpError
from werkzeug.utils import secure_filename

from services.drive_service import DriveService
from utils.validators import (
    require_json,
    validate_create_file,
    validate_create_folder,
    validate_edit_file,
    validate_upload_file,
)

logger = logging.getLogger(__name__)
drive_bp = Blueprint("drive", __name__)


def _drive() -> DriveService:
    """Return a DriveService bound to the current app config."""
    return DriveService(current_app.config.get_namespace("") if False else current_app.config)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _success(data: dict, status: int = 200):
    return jsonify({"success": True, "data": data}), status


def _error(message: str, status: int = 400, details=None):
    body = {"success": False, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


# ── POST /api/create-folder ───────────────────────────────────────────────────

@drive_bp.post("/create-folder")
@require_json
def create_folder():
    """
    Body (JSON)
    -----------
    name      : str  — required
    parent_id : str  — optional Drive folder ID
    """
    body = request.get_json()
    errors = validate_create_folder(body)
    if errors:
        return _error("Validation failed", 422, errors)

    try:
        folder = _drive().create_folder(
            name=body["name"].strip(),
            parent_id=body.get("parent_id"),
        )
        return _success(folder, 201)

    except HttpError as exc:
        logger.error("Drive API error in create_folder: %s", exc)
        return _error("Google Drive error", 502, str(exc))


# ── POST /api/create-file ─────────────────────────────────────────────────────

@drive_bp.post("/create-file")
@require_json
def create_file():
    """
    Body (JSON)
    -----------
    name      : str  — required
    mime_type : str  — optional (default: Google Doc)
    parent_id : str  — optional Drive folder ID
    content   : str  — optional plain-text body
    """
    body = request.get_json()
    errors = validate_create_file(body)
    if errors:
        return _error("Validation failed", 422, errors)

    try:
        file = _drive().create_file(
            name=body["name"].strip(),
            mime_type=body.get("mime_type", "application/vnd.google-apps.document"),
            parent_id=body.get("parent_id"),
            content=body.get("content"),
        )
        return _success(file, 201)

    except HttpError as exc:
        logger.error("Drive API error in create_file: %s", exc)
        return _error("Google Drive error", 502, str(exc))


# ── PATCH /api/edit-file ──────────────────────────────────────────────────────

@drive_bp.patch("/edit-file")
@require_json
def edit_file():
    """
    Body (JSON)
    -----------
    file_id     : str  — required
    new_name    : str  — optional rename
    new_content : str  — optional new text body
    mime_type   : str  — MIME of new_content (default: text/plain)
    """
    body = request.get_json()
    errors = validate_edit_file(body)
    if errors:
        return _error("Validation failed", 422, errors)

    try:
        updated = _drive().edit_file(
            file_id=body["file_id"],
            new_name=body.get("new_name"),
            new_content=body.get("new_content"),
            mime_type=body.get("mime_type", "text/plain"),
        )
        return _success(updated)

    except HttpError as exc:
        logger.error("Drive API error in edit_file: %s", exc)
        status = 404 if exc.resp.status == 404 else 502
        return _error("Google Drive error", status, str(exc))


# ── POST /api/upload-file ─────────────────────────────────────────────────────

@drive_bp.post("/upload-file")
def upload_file():
    """
    Multipart form data
    -------------------
    file      : FileStorage — required
    parent_id : str         — optional Drive folder ID
    drive_name: str         — optional override for file name in Drive
    """
    errors = validate_upload_file(request)
    if errors:
        return _error("Validation failed", 422, errors)

    upload_file_obj = request.files["file"]
    parent_id = request.form.get("parent_id")
    drive_name = request.form.get("drive_name") or secure_filename(upload_file_obj.filename)
    mime_type = upload_file_obj.mimetype or "application/octet-stream"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    temp_filename = f"{uuid.uuid4().hex}_{secure_filename(upload_file_obj.filename)}"
    temp_path = os.path.join(upload_dir, temp_filename)

    try:
        upload_file_obj.save(temp_path)
        result = _drive().upload_file(
            local_path=temp_path,
            drive_name=drive_name,
            mime_type=mime_type,
            parent_id=parent_id,
        )
        return _success(result, 201)

    except HttpError as exc:
        logger.error("Drive API error in upload_file: %s", exc)
        return _error("Google Drive error", 502, str(exc))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.debug("Temp file cleaned up: %s", temp_path)
