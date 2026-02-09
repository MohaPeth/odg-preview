"""Route de health check publique (non protégée par JWT)."""
from sqlalchemy import text

from flask import Blueprint, jsonify
from src.models.mining_data import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health():
    """
    Health check public : vérifie la connexion à la base de données.
    Retourne 200 si OK, 503 si la base est inaccessible.
    """
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({'status': 'ok', 'database': 'connected'}), 200
    except Exception:
        return jsonify({'status': 'error', 'database': 'disconnected'}), 503
