"""
Configuration pytest pour ODG backend.
Utilise SQLite en mémoire pour éviter PostgreSQL/PostGIS pendant les tests.
"""
import os
import sys

# Configurer l'environnement avant tout import de l'app
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("FLASK_ENV", "development")

# S'assurer que le backend est sur le path (depuis backend/)
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

import pytest
from src.main import create_app, db


@pytest.fixture
def app():
    """Application Flask en mode test."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Client de test HTTP."""
    with app.app_context():
        db.create_all()
    return app.test_client()
