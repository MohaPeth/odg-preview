from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.mining_data import db, Operator
import json
import re

operators_bp = Blueprint('operators', __name__)


def _slugify(value: str) -> str:
    """Génère un slug simple à partir du nom de l'opérateur."""
    value = (value or "").lower()
    # Remplacer tout ce qui n'est pas alphanumérique par des tirets
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "operator"


@operators_bp.route('/', methods=['GET'])
@cross_origin()
def list_operators():
    """Récupère la liste des opérateurs miniers.
    Optionnellement filtrée par le paramètre de recherche `search`.
    """
    try:
        search = (request.args.get('search') or '').strip()
        query = Operator.query

        if search:
            ilike = f"%{search}%"
            query = query.filter(
                db.or_(
                    Operator.name.ilike(ilike),
                    Operator.country.ilike(ilike),
                    Operator.status.ilike(ilike),
                )
            )

        operators = query.order_by(Operator.name.asc()).all()

        return jsonify({
            'success': True,
            'data': [op.to_dict() for op in operators],
            'count': len(operators),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


@operators_bp.route('/<int:operator_id>', methods=['GET'])
@cross_origin()
def get_operator(operator_id: int):
    """Récupère le détail d'un opérateur spécifique."""
    try:
        operator = Operator.query.get_or_404(operator_id)
        return jsonify({
            'success': True,
            'data': operator.to_dict(),
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


@operators_bp.route('/', methods=['POST'])
@cross_origin()
def create_operator():
    """Crée un nouvel opérateur minier."""
    try:
        data = request.get_json(silent=True) or {}

        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({
                'success': False,
                'error': "Le champ 'name' est obligatoire",
            }), 400

        slug = (data.get('slug') or '').strip() or _slugify(name)

        country = data.get('country')
        status = data.get('status') or 'Actif'
        logo_url = data.get('logoUrl') or data.get('logo_url')
        description = data.get('description')

        commodities = data.get('commodities') or []
        try:
            commodities_json = json.dumps(commodities) if commodities else None
        except (TypeError, ValueError):
            commodities_json = None

        permits_count = data.get('permitsCount') or 0

        operator = Operator(
            name=name,
            slug=slug,
            country=country,
            status=status,
            logo_url=logo_url,
            description=description,
            commodities_json=commodities_json,
            permits_count=permits_count,
        )

        db.session.add(operator)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': operator.to_dict(),
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


@operators_bp.route('/<int:operator_id>', methods=['PUT'])
@cross_origin()
def update_operator(operator_id: int):
    """Met à jour un opérateur existant."""
    try:
        operator = Operator.query.get_or_404(operator_id)
        data = request.get_json(silent=True) or {}

        if 'name' in data:
            name = (data.get('name') or '').strip()
            if name:
                operator.name = name
                # Si aucun slug explicite fourni, on peut régénérer à partir du nom
                if not data.get('slug'):
                    operator.slug = _slugify(name)

        if 'slug' in data and data.get('slug'):
            operator.slug = (data.get('slug') or '').strip()

        if 'country' in data:
            operator.country = data.get('country')

        if 'status' in data:
            operator.status = data.get('status') or operator.status

        if 'logoUrl' in data or 'logo_url' in data:
            operator.logo_url = data.get('logoUrl') or data.get('logo_url')

        if 'description' in data:
            operator.description = data.get('description')

        if 'commodities' in data:
            commodities = data.get('commodities') or []
            try:
                operator.commodities_json = json.dumps(commodities) if commodities else None
            except (TypeError, ValueError):
                operator.commodities_json = operator.commodities_json

        if 'permitsCount' in data:
            operator.permits_count = data.get('permitsCount') or 0

        db.session.commit()

        return jsonify({
            'success': True,
            'data': operator.to_dict(),
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500


@operators_bp.route('/<int:operator_id>', methods=['DELETE'])
@cross_origin()
def delete_operator(operator_id: int):
    """Supprime un opérateur."""
    try:
        operator = Operator.query.get_or_404(operator_id)

        db.session.delete(operator)
        db.session.commit()

        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500
