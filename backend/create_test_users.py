#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de création des utilisateurs de test pour ODG Dashboard
"""

import os
import sys
from pathlib import Path

# Charger les variables d'environnement
def load_env_file():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()
os.environ['FLASK_ENV'] = 'development'

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.main import app, db
from src.models.user import User
from src.models.mining_data import Operator

def create_test_users():
    """Créer les utilisateurs de test"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("👤 Création des Utilisateurs de Test")
        print("="*60 + "\n")
        
        # Créer un opérateur de test
        operator = Operator.query.filter_by(name="Opérateur Test").first()
        if not operator:
            operator = Operator(
                name="Opérateur Test",
                slug="operateur-test",
                country="RDC",
                status="Actif",
                description="Opérateur de test pour le dashboard ODG",
                commodities_json='[{"code": "AU", "label": "Or"}]',
                permits_count=1
            )
            db.session.add(operator)
            db.session.commit()
            print("✅ Opérateur de test créé")
        
        # Liste des utilisateurs à créer
        test_users = [
            {
                'username': 'admin',
                'email': 'admin@odg.ga',
                'role': 'admin',
                'operator_id': None
            },
            {
                'username': 'operator',
                'email': 'operator@odg.ga',
                'role': 'operator',
                'operator_id': operator.id
            },
            {
                'username': 'partner',
                'email': 'partner@odg.ga',
                'role': 'partner',
                'operator_id': None
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for user_data in test_users:
            # Vérifier si l'utilisateur existe déjà
            existing_user = User.query.filter_by(email=user_data['email']).first()
            
            if existing_user:
                # Mettre à jour l'utilisateur
                existing_user.username = user_data['username']
                existing_user.role = user_data['role']
                existing_user.operator_id = user_data['operator_id']
                existing_user.status = 'active'
                updated_count += 1
                print(f"🔄 Utilisateur mis à jour: {user_data['email']} ({user_data['role']})")
            else:
                # Créer un nouvel utilisateur
                new_user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    operator_id=user_data['operator_id'],
                    status='active'
                )
                db.session.add(new_user)
                created_count += 1
                print(f"✅ Utilisateur créé: {user_data['email']} ({user_data['role']})")
        
        # Sauvegarder les changements
        db.session.commit()
        
        print("\n" + "="*60)
        print(f"📊 Résumé:")
        print(f"   - Utilisateurs créés: {created_count}")
        print(f"   - Utilisateurs mis à jour: {updated_count}")
        print("="*60 + "\n")
        
        print("🔑 Identifiants de Connexion:\n")
        print("┌─────────────────────────────────────────────────────────┐")
        print("│ ADMINISTRATEUR                                          │")
        print("├─────────────────────────────────────────────────────────┤")
        print("│ Email:    admin@odg.ga                                  │")
        print("│ Username: admin                                         │")
        print("│ Rôle:     admin (accès complet)                         │")
        print("└─────────────────────────────────────────────────────────┘\n")
        
        print("┌─────────────────────────────────────────────────────────┐")
        print("│ OPÉRATEUR                                               │")
        print("├─────────────────────────────────────────────────────────┤")
        print("│ Email:    operator@odg.ga                               │")
        print("│ Username: operator                                      │")
        print("│ Rôle:     operator (gestion des gisements)              │")
        print("└─────────────────────────────────────────────────────────┘\n")
        
        print("┌─────────────────────────────────────────────────────────┐")
        print("│ PARTENAIRE                                              │")
        print("├─────────────────────────────────────────────────────────┤")
        print("│ Email:    partner@odg.ga                                │")
        print("│ Username: partner                                       │")
        print("│ Rôle:     partner (consultation uniquement)             │")
        print("└─────────────────────────────────────────────────────────┘\n")
        
        print("✅ Vous pouvez maintenant vous connecter au dashboard!\n")

if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
