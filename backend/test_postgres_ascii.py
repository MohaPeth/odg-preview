# -*- coding: utf-8 -*-
# Test de connexion PostgreSQL ASCII pour ODG Platform
import psycopg2
import sys

# Informations de connexion
db_params = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'odg_database',
    'user': 'odg_user',
    'password': 'root'
}

print("=== TEST DE CONNEXION POSTGRESQL SIMPLE POUR ODG ===")
print("Connexion a: localhost:5432/odg_database avec utilisateur: odg_user")

try:
    # Tester la connexion
    print("\nTest de connexion PostgreSQL...")
    conn = psycopg2.connect(
        host=db_params['host'],
        port=db_params['port'],
        dbname=db_params['dbname'],
        user=db_params['user'],
        password=db_params['password']
    )
    
    # Vérifier la version de PostgreSQL
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("\n[OK] Connexion reussie!")
    if version:
        print("Version PostgreSQL: " + version[0])
    
    # Vérifier si PostGIS est installé
    try:
        cursor.execute("SELECT PostGIS_Version();")
        postgis_version = cursor.fetchone()
        if postgis_version:
            print("Version PostGIS: " + postgis_version[0])
    except psycopg2.Error as e:
        print("[ATTENTION] PostGIS n'est pas installe ou active")
    
    # Tester la création d'une table simple
    print("\nTest de creation d'une table temporaire...")
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
        if result:
            print("[OK] Donnees inserees: ID=" + str(result[0]) + ", Nom=" + result[1])
        
        # Supprimer la table de test
        cursor.execute("DROP TABLE IF EXISTS odg_test_connection;")
        conn.commit()
        print("[OK] Table de test supprimee avec succes")
        
    except psycopg2.Error as e:
        print("[ERREUR] Probleme lors du test d'ecriture")
    
    # Fermer la connexion
    cursor.close()
    conn.close()
    print("\n[SUCCES] Test de connexion PostgreSQL reussi!")
    
except psycopg2.Error as e:
    print("\n[ERREUR] Echec de connexion PostgreSQL")
    print("\nConseil de depannage:")
    print("1. Verifiez que le service PostgreSQL est en cours d'execution")
    print("2. Verifiez les informations de connexion (nom d'utilisateur, mot de passe, hote, port)")
    print("3. Assurez-vous que la base de donnees existe")
    print("4. Verifiez que l'utilisateur a les permissions necessaires")
    sys.exit(1)
    
except Exception as e:
    print("\n[ERREUR] Probleme inattendu")
    sys.exit(1)
