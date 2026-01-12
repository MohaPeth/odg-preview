from flask import Blueprint, jsonify
from flask_cors import cross_origin

from src.models.mining_data import db, MiningDeposit, BlockchainTransaction, Operator
from src.models.geospatial_layers import GeospatialLayer


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
@cross_origin()
def get_dashboard_summary():
    """Résumé global pour le dashboard Onboarding.

    Retourne des indicateurs simples calculés directement depuis la base :
    - gisements actifs
    - transactions blockchain confirmées
    - volume total tracé (toutes matières)
    - volume d'or tracé
    - couches géospatiales actives/visibles
    - opérateurs enregistrés
    """
    try:
        # Gisements actifs
        active_deposits = (
            MiningDeposit.query.filter(MiningDeposit.status == "Actif").count()
        )

        # Statistiques blockchain de base
        total_transactions = BlockchainTransaction.query.count()
        confirmed_transactions = (
            BlockchainTransaction.query
            .filter(BlockchainTransaction.status == "confirmed")
            .count()
        )

        # Volume total tracé (tous matériaux, seulement confirmed)
        total_tracked_volume = (
            db.session.query(db.func.coalesce(db.func.sum(BlockchainTransaction.quantity), 0))
            .filter(BlockchainTransaction.status == "confirmed")
            .scalar()
        ) or 0

        # Volume d'or tracé (material_type = 'Or')
        gold_tracked_volume = (
            db.session.query(db.func.coalesce(db.func.sum(BlockchainTransaction.quantity), 0))
            .filter(
                BlockchainTransaction.status == "confirmed",
                BlockchainTransaction.material_type == "Or",
            )
            .scalar()
        ) or 0

        # Couches géospatiales actives/visibles
        active_layers = (
            GeospatialLayer.query
            .filter(
                GeospatialLayer.status == "actif",
                GeospatialLayer.is_visible.is_(True),
            )
            .count()
        )

        # Opérateurs
        operators_count = Operator.query.count()

        return jsonify(
            {
                "success": True,
                "data": {
                    "deposits": {
                        "active": active_deposits,
                    },
                    "blockchain": {
                        "transactions": {
                            "total": total_transactions,
                            "confirmed": confirmed_transactions,
                        },
                        "volumes": {
                            "total": float(total_tracked_volume),
                            "gold": float(gold_tracked_volume),
                        },
                    },
                    "geospatial": {
                        "activeLayers": active_layers,
                    },
                    "operators": {
                        "total": operators_count,
                    },
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
