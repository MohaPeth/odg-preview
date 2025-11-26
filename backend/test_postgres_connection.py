# Test de connexion PostgreSQL pour ODG Platform
import sys
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ajouter le répertoire parent au chemin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer la configuration
from src.config import get_config

config = get_config()
db_uri = config.SQLALCHEMY_DATABASE_URI

print("=== TEST DE CONNEXION POSTGRESQL POUR ODG PLATFORM ===")
print(f"URI de connexion: {db_uri}")

# Extraire les paramètres de connexion de l'URI
# Format: postgresql://username:password@host:port/dbname
try:
    # Supprimer le préfixe postgresql://
    db_params = db_uri.split('://')[1]
    
    # Séparer les informations d'identification du reste
    auth, rest = db_params.split('@')
    username, password = auth.split(':')
    
    # Séparer l'hôte/port de la base de données
    host_port, dbname = rest.split('/')
    
    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = '5432'  # Port par défaut

    print(f"\nParamètres de connexion:")
    print(f"Hôte: {host}")
    print(f"Port: {port}")
    print(f"Base de données: {dbname}")
    print(f"Utilisateur: {username}")
    print(f"Mot de passe: {'*' * len(password)}")

    # Tester la connexion
    print("\nTest de connexion PostgreSQL...")
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=username,
        password=password
    )
    
    # Vérifier la version de PostgreSQL
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"\n[OK] Connexion réussie!")
    print(f"Version PostgreSQL: {version}")
    
    # Vérifier si PostGIS est installé
    try:
        cursor.execute("SELECT PostGIS_Version();")
        postgis_version = cursor.fetchone()[0]
        print(f"Version PostGIS: {postgis_version}")
    except psycopg2.Error:
        print("[ATTENTION] PostGIS n'est pas installé ou activé sur cette base de données.")
        print("Veuillez installer l'extension PostGIS via pgAdmin.")
    
    # Tester la création d'une table simple
    print("\nTest de création d'une table temporaire...")
    try:
        cursor.execute("DROP TABLE IF EXISTS odg_test_connection;")
        cursor.execute("""
            CREATE TABLE odg_test_connection (
                id SERIAL PRIMARY KEY,
                test_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        
        # Insérer des données de test
        cursor.execute("""
            INSERT INTO odg_test_connection (test_name) 
            VALUES ('Test de connexion ODG Platform');
        """)
        conn.commit()
        
        # Vérifier l'insertion
        cursor.execute("SELECT * FROM odg_test_connection;")
        result = cursor.fetchone()
        print(f"[OK] Données insérées: ID={result[0]}, Nom={result[1]}, Date={result[2]}")
        
        # Supprimer la table de test
        cursor.execute("DROP TABLE IF EXISTS odg_test_connection;")
        conn.commit()
        print("[OK] Table de test supprimée avec succès")
        
    except psycopg2.Error as e:
        print(f"[ERREUR] Problème lors du test d'écriture: {e}")
    
    # Fermer la connexion
    cursor.close()
    conn.close()
    print("\n[SUCCÈS] Test de connexion PostgreSQL réussi!")
    
except psycopg2.Error as e:
    print(f"\n[ERREUR] Échec de connexion PostgreSQL: {e}")
    print("\nConseil de dépannage:")
    print("1. Vérifiez que le service PostgreSQL est en cours d'exécution")
    print("2. Vérifiez les informations de connexion (nom d'utilisateur, mot de passe, hôte, port)")
    print("3. Assurez-vous que la base de données existe")
    print("4. Vérifiez que l'utilisateur a les permissions nécessaires")
    sys.exit(1)
    
except Exception as e:
    print(f"\n[ERREUR] Problème inattendu: {e}")
    sys.exit(1)
