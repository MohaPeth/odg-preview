# 🚀 GUIDE DE DÉMARRAGE - ODG WebGIS API PostGIS

## 📋 CORRECTIONS APPORTÉES

### ✅ Problèmes résolus :

1. **Imports incorrects** : Corrigés tous les `from src.` vers imports relatifs
2. **Erreurs de version** : Gestion sûre des versions Flask et Python
3. **GeoAlchemy2** : Imports simplifiés pour éviter les conflits
4. **Structure de projet** : Scripts de lancement créés

## 🚀 DÉMARRAGE RAPIDE

### Option 1 : Script Windows (.bat)

```cmd
# Double-cliquer sur :
start_postgis.bat
```

### Option 2 : Script Python

```bash
# Depuis le dossier racine :
python run_postgis.py
```

### Option 3 : Démarrage manuel

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer depuis le dossier src/
cd src
python main_postgis.py
```

## 🌐 URLs de Test

- **API Principal** : http://localhost:5000/
- **Health Check** : http://localhost:5000/api/health
- **Version** : http://localhost:5000/api/version
- **Substances** : http://localhost:5000/api/webgis/substances
- **Gisements** : http://localhost:5000/api/webgis/deposits

## 🔧 Commandes CLI

```bash
# Initialiser la base de données
flask init-db

# Migrer depuis SQLite
flask migrate-data

# Créer des données d'exemple
flask create-sample-data
```

## ⚠️ Prérequis

1. **Python 3.8+** installé
2. **PostgreSQL + PostGIS** configuré (optionnel pour tests)
3. **Dépendances** : `pip install -r requirements.txt`

## 🎯 Prochaines Étapes

1. **Tester l'API** avec les URLs ci-dessus
2. **Configurer PostgreSQL** si nécessaire
3. **Lancer le frontend** sur http://localhost:5173
4. **Tester l'intégration** complète

---

✅ **L'application est maintenant prête à fonctionner !**
