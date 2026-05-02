"""
Lightweight request validators.
Return a list of error strings (empty → valid).
"""

from functools import wraps
from typing import Any

from flask import jsonify, request


# ── Decorator ─────────────────────────────────────────────────────────────────

def require_json(fn):
    """Reject requests that are not JSON-typed."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({"success": False, "error": "Content-Type must be application/json"}), 415
        return fn(*args, **kwargs)
    return wrapper


# ── Per-endpoint validators ───────────────────────────────────────────────────

def validate_create_folder(body: dict | None) -> list[str]:
    errors: list[str] = []
    if not body:
        return ["Request body is empty."]
    if not body.get("name") or not str(body["name"]).strip():
        errors.append("'name' is required and must be a non-empty string.")
    return errors


def validate_create_file(body: dict | None) -> list[str]:
    errors: list[str] = []
    if not body:
        return ["Request body is empty."]
    if not body.get("name") or not str(body["name"]).strip():
        errors.append("'name' is required and must be a non-empty string.")
    if "content" in body and not isinstance(body["content"], str):
        errors.append("'content' must be a string.")
    return errors


def validate_edit_file(body: dict | None) -> list[str]:
    errors: list[str] = []
    if not body:
        return ["Request body is empty."]
    if not body.get("file_id") or not str(body["file_id"]).strip():
        errors.append("'file_id' is required.")
    if "new_name" not in body and "new_content" not in body:
        errors.append("At least one of 'new_name' or 'new_content' must be provided.")
    if "new_name" in body and not isinstance(body["new_name"], str):
        errors.append("'new_name' must be a string.")
    if "new_content" in body and not isinstance(body["new_content"], str):
        errors.append("'new_content' must be a string.")
    return errors


def validate_upload_file(req) -> list[str]:
    errors: list[str] = []
    if "file" not in req.files:
        errors.append("'file' field is required in the multipart form data.")
        return errors
    f = req.files["file"]
    if not f or f.filename == "":
        errors.append("No file was selected.")
    return errors
