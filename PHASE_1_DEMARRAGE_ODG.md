# 🚀 DÉMARRAGE PHASE 1 - Plateforme ODG

## 📅 **Planning Phase 1 (0-3 mois)**

**Période** : 26 Juillet - 26 Octobre 2025  
**Objectif** : Système SIG complet avec base de données géospatiale avancée

---

## 🎯 **OBJECTIFS PHASE 1**

### **Priorité 1 - Système SIG Avancé (Semaines 1-8)**

- Couches multicouches avec discrimination par substance
- Légende interactive professionnelle
- Interface d'administration SIG
- Migration base de données vers PostGIS

### **Priorité 2 - Dashboard Temps Réel (Semaines 6-10)**

- Actualisation automatique des statistiques
- Widgets interactifs personnalisables
- Mini-carte avec dernières activités
- Timeline des transactions blockchain

### **Priorité 3 - Fonctionnalités Cartographiques (Semaines 8-12)**

- Outils de mesure géospatiale
- Export cartographique professionnel
- Recherche multi-critères avancée
- Popups enrichis avec métadonnées

---

## 🗄️ **ANALYSE DE VOTRE BASE DE DONNÉES ACTUELLE**

### ✅ **Points Forts de la Structure Actuelle**

#### **1. Modèles Bien Conçus**

```python
✅ MiningDeposit     # Gisements avec coordonnées
✅ ExploitationArea  # Zones d'exploitation polygonales
✅ Infrastructure    # Routes, chemins de fer
✅ BlockchainTransaction # Traçabilité blockchain
```

#### **2. Bonnes Pratiques Implémentées**

- **Timestamps automatiques** (created_at, updated_at)
- **Méthodes to_dict()** pour sérialisation JSON
- **Géolocalisation** avec latitude/longitude
- **Métadonnées JSON** pour données flexibles
- **Foreign Keys** potentielles (company)

#### **3. Structure SQLAlchemy Solide**

- **Types de données appropriés** (String, Float, Text, DateTime)
- **Contraintes** (nullable=False, unique=True)
- **Index potentiels** sur colonnes importantes

### ⚠️ **Limitations Identifiées pour Phase 1**

#### **1. Base de Données Non-Géospatiale**

```sql
❌ SQLite simple → ✅ PostGIS recommandé
❌ latitude/longitude séparées → ✅ GEOMETRY/GEOGRAPHY
❌ JSON pour polygones → ✅ Types géométriques natifs
❌ Pas d'index spatiaux → ✅ Index GiST/SP-GiST
```

#### **2. Modèles à Enrichir**

```python
❌ Type minerai limité → ✅ Table Substances dédiée
❌ Pas de gestion permis → ✅ Modèle Permits/Licenses
❌ Communautés manquantes → ✅ Modèle Communities
❌ Points environnementaux absents → ✅ Modèle EnvironmentalPoints
```

#### **3. Relations et Contraintes**

```python
❌ Pas de relations explicites → ✅ Foreign Keys avec relationships
❌ Validation limitée → ✅ Validators géospatiaux
❌ Pas d'audit trail → ✅ Historique des modifications
```

---

## 🏗️ **NOUVELLE ARCHITECTURE BASE DE DONNÉES PHASE 1**

### **🔄 Migration SQLite → PostGIS**

#### **1. Installation PostGIS**

```bash
# Installation PostgreSQL + PostGIS
sudo apt install postgresql postgresql-contrib
sudo apt install postgis postgresql-13-postgis-3

# Création base ODG
sudo -u postgres createdb odg_database
sudo -u postgres psql -d odg_database -c "CREATE EXTENSION postgis;"
```

#### **2. Configuration Flask**

```python
# Nouvelle configuration
SQLALCHEMY_DATABASE_URI = "postgresql://user:password@localhost/odg_database"
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
```

### **📊 Nouveaux Modèles Phase 1**

#### **1. Modèle Substances (Minerais)**

```python
class Substance(db.Model):
    __tablename__ = 'substances'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Or, Diamant, Fer
    symbol = db.Column(db.String(10), unique=True)  # Au, C, Fe
    color_code = db.Column(db.String(7), nullable=False)  # #FFD700
    market_price = db.Column(db.Float)  # Prix actuel
    unit = db.Column(db.String(20), default='kg')  # kg, carats, tonnes
    density = db.Column(db.Float)  # Densité pour calculs volumes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### **2. Gisements Géospatiaux Améliorés**

```python
from geoalchemy2 import Geometry

class MiningDeposit(db.Model):
    __tablename__ = 'mining_deposits'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)

    # Relation avec substances
    substance_id = db.Column(db.Integer, db.ForeignKey('substances.id'), nullable=False)
    substance = db.relationship('Substance', backref='deposits')

    # Géométrie PostGIS native
    geom = db.Column(Geometry('POINT', srid=4326), nullable=False)

    # Métadonnées enrichies
    company = db.Column(db.String(100), nullable=False, index=True)
    estimated_quantity = db.Column(db.Float)  # Quantité numérique
    quantity_unit = db.Column(db.String(20), default='tonnes')
    quality_grade = db.Column(db.Float)  # Teneur/qualité
    discovery_date = db.Column(db.Date)
    depth_min = db.Column(db.Float)  # Profondeur minimum
    depth_max = db.Column(db.Float)  # Profondeur maximum

    # Statut et workflow
    status = db.Column(db.String(50), nullable=False, default='Exploration')
    exploitation_permit = db.Column(db.String(50))  # Numéro de permis
    permit_expiry = db.Column(db.Date)

    # Métadonnées système
    data_source = db.Column(db.String(100))  # Source des données
    confidence_level = db.Column(db.String(20), default='medium')
    last_survey = db.Column(db.Date)

    # Timestamps et audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))  # Utilisateur créateur
    approved_by = db.Column(db.String(100))  # Validateur
    approval_status = db.Column(db.String(20), default='pending')
```

#### **3. Communautés Locales**

```python
class Community(db.Model):
    __tablename__ = 'communities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    geom = db.Column(Geometry('POINT', srid=4326), nullable=False)

    # Données démographiques
    population = db.Column(db.Integer)
    population_year = db.Column(db.Integer, default=2025)
    main_language = db.Column(db.String(50))

    # Services et infrastructure
    has_electricity = db.Column(db.Boolean, default=False)
    has_water = db.Column(db.Boolean, default=False)
    has_school = db.Column(db.Boolean, default=False)
    has_health_center = db.Column(db.Boolean, default=False)

    # Relations avec activités minières
    nearest_mine_distance = db.Column(db.Float)  # Distance en km
    affected_by_mining = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### **4. Points Environnementaux**

```python
class EnvironmentalPoint(db.Model):
    __tablename__ = 'environmental_points'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    geom = db.Column(Geometry('POINT', srid=4326), nullable=False)

    # Type de point environnemental
    env_type = db.Column(db.String(50), nullable=False)  # protected_area, river, forest
    protection_level = db.Column(db.String(50))  # national_park, reserve, etc.
    surface_area = db.Column(db.Float)  # Superficie en hectares

    # Informations écologiques
    biodiversity_index = db.Column(db.Float)
    conservation_status = db.Column(db.String(50))
    threats = db.Column(db.Text)  # Menaces identifiées

    # Réglementation
    legal_framework = db.Column(db.String(200))
    restrictions = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### **5. Zones d'Exploitation Géospatiales**

```python
class ExploitationArea(db.Model):
    __tablename__ = 'exploitation_areas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    geom = db.Column(Geometry('POLYGON', srid=4326), nullable=False)

    # Relations
    deposit_id = db.Column(db.Integer, db.ForeignKey('mining_deposits.id'))
    deposit = db.relationship('MiningDeposit', backref='exploitation_areas')

    company = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)

    # Données opérationnelles
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)

    # Volumes et production
    planned_volume = db.Column(db.Float)
    extracted_volume = db.Column(db.Float, default=0)
    remaining_volume = db.Column(db.Float)

    # Personnel et équipements
    employees_count = db.Column(db.Integer)
    equipment_list = db.Column(db.Text)  # JSON des équipements

    # Impact environnemental
    environmental_impact_assessment = db.Column(db.Text)
    rehabilitation_plan = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 🛠️ **PLAN DE MIGRATION PHASE 1**

### **Semaine 1-2 : Setup Infrastructure**

#### **1. Installation et Configuration**

```bash
# 1. Installation PostGIS
pip install psycopg2-binary geoalchemy2

# 2. Configuration Flask-Migrate
pip install Flask-Migrate
flask db init
flask db migrate -m "Initial migration with PostGIS"
flask db upgrade
```

#### **2. Scripts de Migration**

```python
# Script de migration des données existantes
def migrate_existing_data():
    # Migration MiningDeposit
    for deposit in old_deposits:
        new_deposit = MiningDeposit(
            name=deposit.name,
            geom=f'POINT({deposit.longitude} {deposit.latitude})',
            substance_id=get_substance_id(deposit.type),
            company=deposit.company,
            # ... autres champs
        )
        db.session.add(new_deposit)

    db.session.commit()
```

### **Semaine 3-4 : Nouveaux Modèles et Relations**

#### **1. Création Tables de Référence**

```sql
-- Substances avec données réelles
INSERT INTO substances (name, symbol, color_code, market_price, unit) VALUES
('Or', 'Au', '#FFD700', 65000, 'kg'),
('Diamant', 'C', '#87CEEB', 55000, 'carats'),
('Fer', 'Fe', '#8B0000', 120, 'tonnes'),
('Sable', 'Si', '#F5F5DC', 25, 'tonnes');
```

#### **2. Index Géospatiaux**

```sql
-- Index spatiaux pour performances
CREATE INDEX idx_mining_deposits_geom ON mining_deposits USING GIST (geom);
CREATE INDEX idx_communities_geom ON communities USING GIST (geom);
CREATE INDEX idx_environmental_points_geom ON environmental_points USING GIST (geom);
CREATE INDEX idx_exploitation_areas_geom ON exploitation_areas USING GIST (geom);
```

### **Semaine 5-6 : APIs Géospatiales**

#### **1. Endpoints SIG Avancés**

```python
@webgis_bp.route('/deposits/within-radius', methods=['POST'])
def get_deposits_within_radius():
    """Gisements dans un rayon donné"""
    data = request.get_json()
    center_point = f"POINT({data['lng']} {data['lat']})"
    radius_meters = data['radius'] * 1000  # km to meters

    deposits = db.session.query(MiningDeposit).filter(
        func.ST_DWithin(
            MiningDeposit.geom,
            func.ST_GeomFromText(center_point, 4326),
            radius_meters
        )
    ).all()

    return jsonify({
        'success': True,
        'data': [deposit.to_dict() for deposit in deposits]
    })

@webgis_bp.route('/substances/<substance_name>/deposits', methods=['GET'])
def get_deposits_by_substance(substance_name):
    """Filtrage par substance spécifique"""
    deposits = db.session.query(MiningDeposit).join(Substance).filter(
        Substance.name == substance_name
    ).all()

    return jsonify({
        'success': True,
        'substance': substance_name,
        'data': [deposit.to_dict() for deposit in deposits]
    })
```

### **Semaine 7-8 : Interface SIG Avancée**

#### **1. Composant Légende Interactive**

```jsx
// Nouveau composant LegendPanel.jsx
const LegendPanel = ({
  substances,
  layers,
  onLayerToggle,
  onSubstanceFilter,
}) => {
  return (
    <Card className="legend-panel">
      <CardHeader>
        <CardTitle>Légende Interactive</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Filtrage par substance */}
        <div className="substance-filters">
          <h4>Substances</h4>
          {substances.map((substance) => (
            <div key={substance.id} className="filter-item">
              <Checkbox
                id={`substance-${substance.id}`}
                checked={substance.visible}
                onCheckedChange={(checked) =>
                  onSubstanceFilter(substance.id, checked)
                }
              />
              <div
                className="color-indicator"
                style={{ backgroundColor: substance.color_code }}
              />
              <Label htmlFor={`substance-${substance.id}`}>
                {substance.name} ({substance.symbol})
              </Label>
            </div>
          ))}
        </div>

        {/* Contrôles de couches */}
        <div className="layer-controls">
          <h4>Couches de Données</h4>
          {layers.map((layer) => (
            <div key={layer.id} className="layer-control">
              <Checkbox
                checked={layer.visible}
                onCheckedChange={(checked) => onLayerToggle(layer.id, checked)}
              />
              <Label>{layer.name}</Label>
              <Slider
                value={[layer.opacity]}
                onValueChange={([opacity]) =>
                  onLayerOpacityChange(layer.id, opacity)
                }
                max={100}
                step={1}
                className="opacity-slider"
              />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
```

---

## 📊 **INDICATEURS DE SUCCÈS PHASE 1**

### **Objectifs Quantifiés**

- ✅ **4 nouveaux modèles** de données créés et déployés
- ✅ **Migration PostGIS** complète sans perte de données
- ✅ **Filtrage par substance** fonctionnel (Or, Diamant, Fer, Sable)
- ✅ **Légende interactive** avec 12+ types d'éléments
- ✅ **Performance** : Requêtes géospatiales < 500ms
- ✅ **Interface admin** SIG pour import de données

### **Livrables Attendus**

1. **Base de données PostGIS** opérationnelle
2. **Modèles enrichis** avec relations géospatiales
3. **APIs SIG avancées** avec requêtes spatiales
4. **Interface cartographique** avec discrimination
5. **Documentation** technique et utilisateur

---

## 🚀 **PROCHAINES ÉTAPES IMMÉDIATES**

### **Cette Semaine (26 Jul - 2 Aug)**

1. **Validation architecture** base de données proposée
2. **Setup environnement** PostGIS local
3. **Création scripts** de migration
4. **Tests modèles** en environnement de développement

### **Semaine Suivante (2-9 Aug)**

1. **Migration données** existantes vers PostGIS
2. **Création nouveaux modèles** (Substances, Communities, etc.)
3. **Tests APIs** géospatiales de base
4. **Début interface** de filtrage par substance

Êtes-vous prêt à démarrer cette Phase 1 ? Avez-vous des questions sur l'architecture de base de données proposée ou souhaitez-vous des ajustements ?
