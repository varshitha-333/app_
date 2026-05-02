import os
import logging
from flask import Flask
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

    app.register_blueprint(drive_bp, url_prefix="/api")

    register_error_handlers(app)

    return app

# This 'app' instance is for Gunicorn
app = create_app()

if __name__ == "__main__":
    # Railway provides the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
