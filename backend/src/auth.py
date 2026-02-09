"""
Authentification JWT pour ODG.
Lit le header Authorization: Bearer <token>, décode le JWT, attache l'utilisateur à g.current_user.
"""
import os
from functools import wraps

import jwt
from flask import g, request

from src.models.user import User


def _get_secret():
    return os.getenv('SECRET_KEY') or 'dev-secret-key-change-in-production'


def get_current_user_from_token():
    """
    Lit le token JWT depuis le header Authorization et retourne l'utilisateur correspondant.
    Retourne None si pas de token, token invalide ou utilisateur introuvable.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:].strip()
    if not token:
        return None
    try:
        payload = jwt.decode(token, _get_secret(), algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            return None
        user = User.query.get(user_id)
        return user
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        return None


def require_auth(f):
    """Décorateur : exige un JWT valide et attache g.current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user_from_token()
        if not user:
            return {'error': 'Authentification requise ou token invalide/expiré'}, 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_roles(*allowed_roles):
    """Décorateur : exige un JWT valide et un rôle parmi allowed_roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user_from_token()
            if not user:
                return {'error': 'Authentification requise ou token invalide/expiré'}, 401
            if user.role not in allowed_roles:
                return {'error': 'Droits insuffisants'}, 403
            g.current_user = user
            return f(*args, **kwargs)
        return decorated
    return decorator
