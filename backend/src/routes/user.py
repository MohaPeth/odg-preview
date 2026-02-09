import os
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, jsonify, request
from src.limiter import limiter
from src.models.user import User
from src.models.mining_data import db

user_bp = Blueprint('user', __name__)

# Durée de vie du JWT (24h)
JWT_EXPIRATION_HOURS = 24


def _create_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),
    }
    secret = os.getenv('SECRET_KEY') or 'dev-secret-key-change-in-production'
    return jwt.encode(payload, secret, algorithm='HS256')


@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json or {}

    username = data.get('username') or data.get('name')
    email = data.get('email')

    if not username or not email:
        return jsonify({'error': 'username/name et email sont obligatoires'}), 400

    role = data.get('role') or 'admin'
    status = data.get('status') or 'active'
    operator_id = data.get('operator_id')

    user = User(
        username=username,
        email=email,
        role=role,
        status=status,
        operator_id=operator_id,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json or {}

    if 'username' in data or 'name' in data:
        user.username = data.get('username') or data.get('name') or user.username

    if 'email' in data:
        user.email = data.get('email', user.email)

    if 'role' in data:
        user.role = data['role']

    if 'status' in data:
        user.status = data['status']

    if 'operator_id' in data:
        user.operator_id = data['operator_id']

    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204


@user_bp.route('/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authentification par email et mot de passe. Retourne un JWT et le profil minimal."""
    data = request.json or {}

    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not email:
        return jsonify({'error': "L'email est obligatoire"}), 400
    if not password:
        return jsonify({'error': 'Le mot de passe est obligatoire'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Identifiants invalides ou utilisateur introuvable'}), 401

    if not user.password_hash:
        return jsonify({
            'error': 'Compte non initialisé. Un administrateur doit définir votre mot de passe.',
        }), 403

    if not user.check_password(password):
        return jsonify({'error': 'Identifiants invalides ou utilisateur introuvable'}), 401

    if user.status != 'active':
        return jsonify({'error': 'Compte désactivé'}), 403

    user.last_login_at = datetime.utcnow()
    db.session.commit()

    token = _create_token(user)
    return jsonify({
        'token': token,
        'user': user.to_dict(),
    })
