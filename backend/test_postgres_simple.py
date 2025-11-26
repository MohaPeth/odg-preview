# Test de connexion PostgreSQL simple pour ODG Platform
import psycopg2

# Informations de connexion
db_params = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'odg_database',
    'user': 'odg_user',
    'password': 'root'
}

print("=== TEST DE CONNEXION POSTGRESQL SIMPLE POUR ODG ===")
print(f"Connexion à: localhost:5432/odg_database avec utilisateur: odg_user")

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
    print(f"\n[OK] Connexion réussie!")
    print(f"Version PostgreSQL: {version[0] if version else 'Inconnue'}")
    
    # Vérifier si PostGIS est installé
    try:
        cursor.execute("SELECT PostGIS_Version();")
        postgis_version = cursor.fetchone()
        print(f"Version PostGIS: {postgis_version[0] if postgis_version else 'Inconnue'}")
    except psycopg2.Error as e:
        print(f"[ATTENTION] PostGIS n'est pas installé ou activé: {str(e)}")
    
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
        if result:
            print(f"[OK] Données insérées: ID={result[0]}, Nom={result[1]}")
        else:
            print("[ATTENTION] Aucune donnée retournée après insertion")
        
        # Supprimer la table de test
        cursor.execute("DROP TABLE IF EXISTS odg_test_connection;")
        conn.commit()
        print("[OK] Table de test supprimée avec succès")
        
    except psycopg2.Error as e:
        print(f"[ERREUR] Problème lors du test d'écriture: {str(e)}")
    
    # Fermer la connexion
    cursor.close()
    conn.close()
    print("\n[SUCCÈS] Test de connexion PostgreSQL réussi!")
    
except psycopg2.Error as e:
    print(f"\n[ERREUR] Échec de connexion PostgreSQL: {str(e)}")
    print("\nConseil de dépannage:")
    print("1. Vérifiez que le service PostgreSQL est en cours d'exécution")
    print("2. Vérifiez les informations de connexion (nom d'utilisateur, mot de passe, hôte, port)")
    print("3. Assurez-vous que la base de données existe")
    print("4. Vérifiez que l'utilisateur a les permissions nécessaires")
    
except Exception as e:
    print(f"\n[ERREUR] Problème inattendu: {str(e)}")
