# Guide de résolution des problèmes PostgreSQL

## Problème de connexion PostgreSQL pour ODG Platform

Si vous rencontrez des problèmes de connexion à PostgreSQL, suivez ce guide étape par étape.

### 1. Vérifier que le service PostgreSQL est en cours d'exécution

1. Ouvrez le gestionnaire de services Windows :

   - Appuyez sur `Win + R`, tapez `services.msc` et appuyez sur Entrée
   - Recherchez le service `postgresql-x64-17` (ou la version que vous avez installée)
   - Vérifiez qu'il est en cours d'exécution (status "Démarré")
   - Si ce n'est pas le cas, cliquez-droit et sélectionnez "Démarrer"

2. Vérifiez via la ligne de commande (en administrateur) :
   ```powershell
   Get-Service *postgre*
   ```

### 2. Réinitialiser le mot de passe PostgreSQL

Si le service est en cours d'exécution mais que vous ne pouvez pas vous connecter :

1. Arrêtez le service PostgreSQL en administrateur :

   ```powershell
   net stop postgresql-x64-17
   ```

2. Accédez au répertoire des données PostgreSQL :

   ```powershell
   cd "C:\Program Files\PostgreSQL\17\data"
   ```

3. Modifiez le fichier `pg_hba.conf` pour autoriser temporairement toute connexion :

   - Ouvrez le fichier avec un éditeur de texte
   - Remplacez toutes les lignes `scram-sha-256` ou `md5` par `trust`
   - Enregistrez le fichier

4. Redémarrez le service PostgreSQL :

   ```powershell
   net start postgresql-x64-17
   ```

5. Réinitialisez le mot de passe de l'utilisateur postgres :

   ```powershell
   "C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -c "ALTER USER postgres WITH PASSWORD 'root';"
   ```

6. Remettez le fichier `pg_hba.conf` dans son état d'origine :

   - Remplacez toutes les lignes `trust` par `md5`
   - Enregistrez le fichier

7. Redémarrez à nouveau le service PostgreSQL :
   ```powershell
   net stop postgresql-x64-17
   net start postgresql-x64-17
   ```

### 3. Utiliser pgAdmin pour configurer la base de données

1. Ouvrez pgAdmin 4 depuis le menu Démarrer
2. Lors de la première connexion, pgAdmin vous demandera de définir un mot de passe principal
3. Cliquez-droit sur "Servers" et sélectionnez "Register > Server"
4. Dans l'onglet "General", donnez un nom au serveur (ex: "PostgreSQL ODG")
5. Dans l'onglet "Connection", configurez :
   - Host: localhost
   - Port: 5432
   - Maintenance database: postgres
   - Username: postgres
   - Password: root (ou votre mot de passe)
   - Cochez "Save password"
6. Cliquez sur "Save" pour vous connecter

### 4. Créer la base de données et l'utilisateur pour ODG

1. Connectez-vous au serveur PostgreSQL dans pgAdmin
2. Faites un clic-droit sur "Databases" et sélectionnez "Create > Database"
3. Dans l'onglet "General" :
   - Database: odg_database
   - Owner: postgres
4. Cliquez sur "Save"

5. Faites un clic-droit sur "Login/Group Roles" et sélectionnez "Create > Login/Group Role"
6. Dans l'onglet "General" :
   - Name: odg_user
7. Dans l'onglet "Definition" :
   - Password: root
8. Dans l'onglet "Privileges" :
   - Cochez "Can login"
   - Cochez "Create databases"
9. Cliquez sur "Save"

10. Faites un clic-droit sur la base de données "odg_database" et sélectionnez "Query Tool"
11. Exécutez les commandes suivantes :

    ```sql
    -- Accorder les permissions sur la base de données
    GRANT ALL PRIVILEGES ON DATABASE odg_database TO odg_user;
    GRANT ALL ON SCHEMA public TO odg_user;

    -- Installer les extensions PostGIS
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
    CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
    CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

    -- Vérifier l'installation
    SELECT PostGIS_Version();
    ```

### 5. Démarrer l'application ODG

1. Modifiez le fichier `src/config.py` pour utiliser les bonnes informations de connexion :

   ```python
   SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
       'postgresql://odg_user:root@localhost:5432/odg_database'
   ```

2. Exécutez le script de migration vers PostGIS :

   ```powershell
   cd odg-webgis-backend
   python src/migrate_to_postgis.py
   ```

3. Démarrez l'API ODG avec PostgreSQL :

   ```powershell
   python src/main_postgis.py
   ```

4. L'API sera accessible à l'adresse : http://localhost:5000

### Commandes utiles pour le dépannage

- Vérifier la connexion à PostgreSQL :

  ```powershell
  "C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -h localhost -p 5432 -c "SELECT version();"
  ```

- Vérifier si PostGIS est installé :

  ```powershell
  "C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -h localhost -p 5432 -d odg_database -c "SELECT PostGIS_Version();"
  ```

- Lister les bases de données :

  ```powershell
  "C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -h localhost -p 5432 -c "\l"
  ```

- Lister les utilisateurs :
  ```powershell
  "C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -h localhost -p 5432 -c "\du"
  ```
