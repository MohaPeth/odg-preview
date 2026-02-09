# Tests manuels – ODG WebGIS

Checklist courte pour valider le bon fonctionnement de l’interface et des couches après correctifs ou déploiement.

---

## Prérequis

- **Backend** : http://localhost:5000 (serveur lancé)
- **Frontend** : http://localhost:5173 (serveur lancé)

---

## 1. Vérifier les serveurs

- Backend : ouvrir http://localhost:5000/api/health ou http://localhost:5000/api/dashboard/summary  
- Frontend : ouvrir http://localhost:5173  

---

## 2. Rechargement et console

1. Aller sur http://localhost:5173  
2. Rechargement forcé : **Ctrl + Shift + R**  
3. Ouvrir **F12** → onglet **Console**  

### Logs attendus (exemples)

- Appel API : `[ApiClient] Données reçues: { success: true, data: [...] }`  
- Couches : `[fetchLayers] Nombre de couches: X`  
- Carte : `[DEBUG] Couches géospatiales: Array(X)`  
- Renderer : `[DynamicLayerRenderer] Filtrage: { totalLayers: X, visibleLayers: Y }`  

---

## 3. Interface

- **Statistiques** : affichage cohérent (ex. « X couches totales », « Y visibles »)  
- **Carte** : marqueurs visibles pour les couches actives  
- **Toggle œil** : bascule correcte visible / masqué par couche  

---

## 4. Test de création

1. Onglet **Couches** → « Ajouter une couche »  
2. Importer un fichier GeoJSON (ou autre format supporté)  
3. Vérifier que la nouvelle couche apparaît dans la liste et sur la carte  

---

## 5. Problèmes connus résolus

- Leaflet CSS bloqué par Tracking Prevention → import local  
- Hauteur carte 0px → min-height appliqué  
- `.env` non chargé → dotenv ajouté  
- Réponse API vide → vérifier PostgreSQL et `DATABASE_URL`  

---

## En cas d’erreur

- **« Backend indisponible »** : vérifier que le backend tourne sur le port 5000  
- **« Nombre de couches: 0 »** : vérifier la base PostgreSQL et les données  
- **« data is undefined »** : vérifier le format de réponse de l’API  

Pour les **tests automatisés** (pytest, Vitest), voir [Lancer les tests](lancer-les-tests.md) et [Contribuer et lancer les tests](contribuer-et-tests.md).
