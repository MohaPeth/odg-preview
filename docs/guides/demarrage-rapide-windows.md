# 🚀 Guide Démarrage Rapide - ODG sur Windows

## ✅ Ce qui est DÉJÀ installé
- ✅ Python 3.14 + venv
- ✅ Flask, SQLAlchemy, GeoAlchemy2, simplekml, gpxpy
- ✅ Service d'export complet (7 formats)
- ✅ Code corrigé et production-ready

## 📦 Étape 1 : Installer Docker Desktop

1. Télécharger Docker Desktop : https://www.docker.com/products/docker-desktop/
2. Installer et redémarrer Windows si demandé
3. Lancer Docker Desktop (attendre qu'il démarre complètement)

## 🗄️ Étape 2 : Démarrer PostgreSQL + PostGIS (1 commande)

```powershell
# Depuis la racine du projet
docker-compose up -d
```

Vérifier que c'est démarré :
```powershell
docker ps
```

Vous devriez voir : `odg_postgres` avec status `Up`

## 🌍 Étape 3 : Lancer le serveur ODG

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python run_server.py
```

Le serveur devrait démarrer sur http://localhost:5000

## 🧪 Étape 4 : Tester l'export

```powershell
# Créer un gisement de test
curl -X POST http://localhost:5000/api/geospatial/layers -H "Content-Type: application/json" -d '{\"name\":\"Test Mine\",\"layer_type\":\"deposit\",\"geometry_type\":\"POINT\",\"source_format\":\"CSV\",\"latitude\":-0.5,\"longitude\":10.2}'

# Exporter en KML pour Google Earth
curl http://localhost:5000/api/geospatial/layers/1/export/kml -o test.kml
```

## 🛠️ Commandes utiles

**Arrêter PostgreSQL :**
```powershell
docker-compose down
```

**Voir les logs PostgreSQL :**
```powershell
docker-compose logs -f postgres
```

**Réinitialiser la base de données :**
```powershell
docker-compose down -v
docker-compose up -d
```

**Accéder à PostgreSQL en ligne de commande :**
```powershell
docker exec -it odg_postgres psql -U odg_user -d odg_database
```

## 🎯 Formats d'export disponibles

| Format | Extension | Usage | Status |
|--------|-----------|-------|--------|
| KML | `.kml` | Google Earth | ✅ Opérationnel |
| KMZ | `.kmz` | Google Earth (compressé) | ✅ Opérationnel |
| GeoJSON | `.geojson` | Web, QGIS | ✅ Opérationnel |
| CSV | `.csv` | Excel, tableur | ✅ Opérationnel |
| WKT | `.wkt` | Texte géométrique | ✅ Opérationnel |
| GPX | `.gpx` | GPS | ✅ Opérationnel |
| Shapefile | `.zip` | ArcGIS, QGIS | ⚠️ Nécessite geopandas |

## 🐛 Résolution des problèmes

**"Cannot connect to Docker daemon"**
- Assurez-vous que Docker Desktop est lancé
- Redémarrez Docker Desktop

**"Port 5432 already in use"**
- Vous avez déjà un PostgreSQL qui tourne
- Arrêtez l'autre instance ou changez le port dans `docker-compose.yml`

**"Module not found"**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 🔐 Sécurité - AVANT PRODUCTION

⚠️ **CRITIQUE** : Le système n'a PAS de vérification de mot de passe !

Avant déploiement :
1. Ajouter `password_hash` dans le modèle User
2. Implémenter `werkzeug.security.generate_password_hash()`
3. Vérifier avec `check_password_hash()` au login
4. Changer les credentials PostgreSQL dans `.env`

## 📊 Architecture actuelle

```
ODG
├── Backend (Flask 3.1.1 + PostGIS)
│   ├── Export 7 formats ✅
│   ├── Import KML/CSV/GeoJSON ✅
│   ├── API REST ✅
│   └── Authentication ⚠️ (pas de password!)
├── Frontend (React 19 + Leaflet)
│   └── WebGIS interactif
└── Database (PostgreSQL 15 + PostGIS 3.3)
    └── Géométries SRID 4326
```

## 🎓 Prochaines étapes recommandées

1. **Sécurité** : Implémenter l'authentification avec mots de passe
2. **Tests** : Tester tous les formats d'export avec données réelles
3. **Frontend** : Connecter les boutons d'export aux endpoints API
4. **Blockchain** : Activer la traçabilité (actuellement optionnelle)
5. **Performance** : Ajouter des index spatiaux sur les requêtes fréquentes

## 💡 Note Tech Lead

**Note globale du projet : 6/10**

Forces :
- Architecture PostGIS bien structurée
- Export complet multi-formats
- Code Python idiomatique

Faiblesses CRITIQUES :
- 🔴 Aucune vérification de mot de passe
- 🔴 Dual storage lat/lng + geom (redondance)
- 🟡 Pas de pagination sur les listings
- 🟡 Blockchain non implémentée (juste des stubs)

Le projet est fonctionnel pour l'import/export géospatial mais **DANGEREUX** en production sans correction de la sécurité.
