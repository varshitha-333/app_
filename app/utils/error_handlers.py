"""
Centralised HTTP error handlers registered on the Flask app.
"""

import logging

from flask import Flask, jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(400)
    def bad_request(exc):
        return jsonify({"success": False, "error": "Bad request", "details": str(exc)}), 400

    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(exc):
        return jsonify({"success": False, "error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def request_entity_too_large(exc):
        return jsonify({"success": False, "error": "File too large"}), 413

    @app.errorhandler(415)
    def unsupported_media_type(exc):
        return jsonify({"success": False, "error": "Unsupported media type"}), 415

    @app.errorhandler(500)
    def internal_server_error(exc):
        logger.exception("Unhandled server error: %s", exc)
        return jsonify({"success": False, "error": "Internal server error"}), 500
