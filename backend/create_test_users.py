#!/usr/bin/env python3
"""
Crée ou met à jour les utilisateurs de test ODG (admin, operator, partner)
avec un mot de passe hashé. À exécuter après la migration add_password_hash_to_users.sql.

Usage:
  cd backend
  python create_test_users.py

Mot de passe par défaut (à changer en production) : voir DEFAULT_PASSWORD ci-dessous.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Mot de passe par défaut pour les comptes de test (CHANGER EN PRODUCTION)
DEFAULT_PASSWORD = os.getenv("ODG_TEST_PASSWORD", "odg2025!")

from src.models.mining_data import db
from src.models.user import User
from src.models.mining_data import Operator

def get_or_create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///odg_dev.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    db.init_app(app)
    return app


def main():
    app = get_or_create_app()
    with app.app_context():
        # Créer un opérateur de test si besoin
        operator = Operator.query.filter_by(name="Opérateur Test").first()
        if not operator:
            operator = Operator(name="Opérateur Test", status="active")
            db.session.add(operator)
            db.session.commit()
            print("Opérateur Test créé.")

        test_users = [
            {"email": "admin@odg.ga", "username": "admin", "role": "admin"},
            {"email": "operator@odg.ga", "username": "operator", "role": "operator", "operator_id": operator.id},
            {"email": "partner@odg.ga", "username": "partner", "role": "partner"},
        ]

        for data in test_users:
            user = User.query.filter_by(email=data["email"]).first()
            if user:
                user.set_password(DEFAULT_PASSWORD)
                user.username = data["username"]
                user.role = data["role"]
                if "operator_id" in data:
                    user.operator_id = data["operator_id"]
                db.session.commit()
                print(f"Utilisateur {data['email']} mis à jour (mot de passe défini).")
            else:
                user = User(
                    email=data["email"],
                    username=data["username"],
                    role=data["role"],
                    status="active",
                    operator_id=data.get("operator_id"),
                )
                user.set_password(DEFAULT_PASSWORD)
                db.session.add(user)
                db.session.commit()
                print(f"Utilisateur {data['email']} créé.")

        print("")
        print("Comptes de test (CHANGER LES MOTS DE PASSE EN PRODUCTION) :")
        print(f"  Mot de passe par défaut : {DEFAULT_PASSWORD}")
        print("  Admin    : admin@odg.ga")
        print("  Operator : operator@odg.ga")
        print("  Partner  : partner@odg.ga")


if __name__ == "__main__":
    main()
