"""
Gunicorn configuration file.
Run with:  gunicorn -c gunicorn.conf.py "app:create_app()"
"""

import multiprocessing
import os

# Server
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
timeout = 120          # seconds — increase for large uploads
keepalive = 5

# Logging
accesslog = "-"        # stdout
errorlog = "-"         # stderr
loglevel = os.getenv("LOG_LEVEL", "info")

# Security
limit_request_line = 4094
limit_request_fields = 100
