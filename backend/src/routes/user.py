from flask import Blueprint, jsonify, request
from datetime import datetime
from src.models.user import User
from src.models.mining_data import db

user_bp = Blueprint('user', __name__)


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
def login():
    """Authentification simplifiée par email.

    Pour l'instant, aucun mot de passe n'est vérifié.
    Cette route permet surtout de récupérer le profil utilisateur (rôle, statut, opérateur associé)
    à partir de son email pour le dashboard interne.
    """
    data = request.json or {}

    email = (data.get('email') or '').strip()
    if not email:
        return jsonify({'error': "L'email est obligatoire"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Identifiants invalides ou utilisateur introuvable'}), 401

    user.last_login_at = datetime.utcnow()
    db.session.commit()

    return jsonify(user.to_dict())
