# 🧪 GUIDE TEST RAPIDE - APRÈS CORRECTION DU CRASH

## ⚡ Test en 3 minutes

### 1️⃣ Rechargez l'application
```
1. Allez sur http://localhost:5173
2. Appuyez sur Ctrl+Shift+R (hard reload)
```

### 2️⃣ Ouvrez la console (F12)

**Ce que vous DEVEZ voir** :
```
📡 [ApiClient] GET /api/geospatial/layers?...
📡 [ApiClient] Réponse reçue - Status: 200
🔄 [fetchLayers] Nombre de couches: 3
🔄 [fetchLayers] Données extraites: Array(3)
🎯 [DynamicLayerRenderer] Filtrage: 3 couches visibles sur 3
```

**Ce que vous NE devez PAS voir** :
```
❌ Error: Cannot read properties of undefined (reading 'indexOf')
❌ Error: Cannot read properties of null (reading 'toUpperCase')
❌ An error occurred in the <Text> component
❌ Uncaught TypeError
```

### 3️⃣ Vérifiez l'interface

#### **Stats en haut de page** :
- ✅ "3 couches totales" (au lieu de "0")
- ✅ "3 visibles" 
- ✅ "0 masquées"

#### **Tableau des couches** :
- ✅ 3 lignes affichées
- ✅ Chaque ligne a :
  - Un nom (ex: "Couche Geojson", "Gisement or")
  - Un format en badge (ex: "GEOJSON", "CSV")
  - Un nombre d'éléments (ex: "24 éléments")
  - Une date de création
- ✅ Icône 👁️ (œil) verte pour chaque couche

#### **Carte** :
- ✅ Des marqueurs visibles sur la carte
- ✅ Popup au clic sur un marqueur

---

## 🔍 SI VOUS VOYEZ UN ÉCRAN BLANC

### Scénario A : ErrorBoundary s'affiche

Vous verrez une carte rouge avec :
```
⚠️ Une erreur s'est produite
[Bouton Réessayer] [Bouton Rafraîchir la page]
```

**Action** : Cliquez sur "Rafraîchir la page", puis copiez l'erreur de la console.

---

### Scénario B : Console affiche "Nombre de couches: 0"

**Problème** : L'API ne renvoie pas les données

**Solution** :
```powershell
# 1. Vérifiez que le backend tourne
Get-NetTCPConnection -LocalPort 5000 -State Listen

# 2. Testez l'API manuellement
curl http://localhost:5000/api/geospatial/layers?include_geojson=false

# 3. Si l'API renvoie 0 couches, relancez force_visibility.py
cd backend
python force_visibility.py
```

---

### Scénario C : Console affiche "Nombre de couches: 3" mais écran blanc

**Problème** : Crash durant le rendu

**Diagnostic** :
1. Cherchez une erreur rouge dans la console
2. Elle devrait commencer par `🔴 [ErrorBoundary] Erreur capturée:`
3. Copiez l'erreur complète et identifiez le champ problématique

**Exemple d'erreur à chercher** :
```
TypeError: layer.metadata.toUpperCase is not a function
```
→ Cela signifie qu'on essaie d'afficher un objet au lieu d'une string.

---

## ✅ TEST DE RÉGRESSION

Après avoir confirmé que l'affichage fonctionne, testez ces actions :

### 1. Toggle visibilité
```
1. Cliquez sur l'icône 👁️ d'une couche
2. Elle doit devenir grise (👁️ barré)
3. Le marqueur doit disparaître de la carte
4. Cliquez à nouveau → le marqueur réapparaît
```

### 2. Rafraîchissement
```
1. Appuyez sur F5
2. Les 3 couches doivent rester affichées
3. Le compteur doit toujours afficher "3 couches totales"
```

### 3. Menu actions
```
1. Cliquez sur ⋯ (menu à droite d'une couche)
2. Le menu doit s'ouvrir avec :
   - Modifier
   - Masquer/Afficher
   - Exporter GeoJSON
   - Supprimer
```

---

## 📊 RÉSULTAT ATTENDU

| Critère | Attendu | Où vérifier |
|---------|---------|-------------|
| Nombre de couches | 3 | Stats en haut + console |
| Couches visibles | 3 | Icônes 👁️ vertes |
| Markers sur carte | Oui | Carte principale |
| Aucune erreur console | ✅ | Console F12 |
| Écran blanc | Non | Interface complète visible |

---

## 🆘 EN CAS DE PROBLÈME

Copiez les informations suivantes :

```
=== INFORMATIONS DE DEBUG ===
1. URL testée: http://localhost:5173
2. Erreur console (copier toutes les lignes rouges)
3. Screenshot de l'écran
4. Résultat de cette commande PowerShell:
   Get-NetTCPConnection -LocalPort 5000,5173 -State Listen
```

Et demandez de l'aide avec ces détails.
