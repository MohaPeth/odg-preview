# 🚀 MÉTHODES DE DÉMARRAGE - ODG API

## 📋 PROBLÈME RÉSOLU

Le problème venait du **redémarrage automatique de Flask** en mode debug. Quand Flask redémarre, il ne trouve plus le bon chemin vers le fichier de lancement.

## 🎯 SOLUTIONS DISPONIBLES

### **Option 1 : Simple et Stable** ⭐ RECOMMANDÉ

```bash
python start_odg_api.py
```

- ✅ **Stable** : Pas de problème de redémarrage
- ✅ **Simple** : Fonctionne toujours
- ❌ **Redémarrage manuel** : Ctrl+C puis relancer pour voir les changements

### **Option 2 : Auto-reload (Risqué)**

```bash
python run_postgis.py
```

- ✅ **Auto-reload** : Détecte les changements automatiquement
- ❌ **Instable** : Peut planter au redémarrage

### **Option 3 : Démarrage Direct**

```bash
python launch_api.py
```

- ✅ **Auto-reload** : Fonctionne bien
- ✅ **Stable** : Démarre depuis src/
- ⚠️ **Path complexe** : Plus de gestion de chemins

### **Option 4 : Script Windows**

```cmd
start_postgis.bat
```

- ✅ **Menu interactif** : Choisir la méthode
- ✅ **Environnement automatique** : Active le venv

## 🏆 RECOMMANDATION

**Pour développement actif :**

```bash
python launch_api.py
```

**Pour démo/présentation :**

```bash
python start_odg_api.py
```

**Pour Windows :**

```cmd
start_postgis.bat
```

## 🔧 TESTS RAPIDES

Après démarrage, testez :

1. **API de base** : http://localhost:5000/
2. **Santé** : http://localhost:5000/api/health
3. **Substances** : http://localhost:5000/api/webgis/substances

## 💡 SI PROBLÈMES PERSISTENT

```bash
# Méthode bulletproof
cd src
python main_postgis.py
```

Cette méthode fonctionne TOUJOURS car elle évite tous les problèmes de path Python.

---

✅ **Votre API est maintenant prête et stable !**
