import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

from app.config.config import Config
from app.routes.drive import drive_bp
from app.utils.error_handlers import register_error_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Add a root route for health check
    @app.route('/')
    def index():
        return jsonify({
            "status": "online",
            "message": "Hospital Robot Backend is running",
            "version": "1.0.0"
        })

    app.register_blueprint(drive_bp, url_prefix="/api")

    register_error_handlers(app)

    return app

# This 'app' instance is for Gunicorn
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
