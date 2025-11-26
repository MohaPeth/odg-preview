"""
Test script pour l'endpoint d'ajout de gisement
Phase 2 : Backend API
"""

import requests
import json

# Configuration de l'API
API_BASE_URL = "http://localhost:5000/api/webgis"

def test_create_deposit():
    """Tester la création d'un nouveau gisement"""
    
    # Données de test pour un nouveau gisement
    test_deposit = {
        "name": "Gisement Test API",
        "company": "ODG Test",
        "substanceId": "1",  # Or
        "latitude": -0.5,
        "longitude": 12.0,
        "status": "Exploration",
        "estimatedQuantity": 500.0,
        "estimatedValue": 1000000.0,
        "description": "Gisement de test créé via l'API WebGIS ODG"
    }
    
    try:
        # Appel POST à l'endpoint de création
        response = requests.post(
            f"{API_BASE_URL}/deposits",
            json=test_deposit,
            headers={
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            # Succès
            data = response.json()
            print("✅ Gisement créé avec succès!")
            print(f"ID: {data['deposit']['id']}")
            print(f"Nom: {data['deposit']['name']}")
            print(f"Coordonnées: {data['deposit']['latitude']}, {data['deposit']['longitude']}")
            print(f"Statut d'approbation: {data['metadata']['approvalStatus']}")
            
        elif response.status_code == 400:
            # Erreurs de validation
            data = response.json()
            print("❌ Erreurs de validation:")
            for error in data.get('details', []):
                print(f"  - {error}")
                
        elif response.status_code == 409:
            # Conflit (doublon)
            data = response.json()
            print("⚠️ Gisement en doublon:")
            print(f"  {data.get('details', ['Doublon détecté'])[0]}")
            
        else:
            # Autres erreurs
            print(f"❌ Erreur: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Message: {error_data.get('error', 'Erreur inconnue')}")
            except:
                print(f"Réponse brute: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur API")
        print("Assurez-vous que le serveur Flask est démarré")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - Le serveur met trop de temps à répondre")
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def test_get_substances():
    """Tester la récupération des substances"""
    try:
        response = requests.get(f"{API_BASE_URL}/substances")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Substances récupérées:")
            for substance in data['substances']:
                print(f"  - {substance['name']} ({substance['symbol']}) - {substance['colorCode']}")
        else:
            print(f"❌ Erreur récupération substances: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur substances: {e}")

def test_invalid_data():
    """Tester avec des données invalides"""
    
    invalid_deposits = [
        {
            "name": "",  # Nom vide
            "company": "Test",
            "substanceId": "1",
            "latitude": -0.5,
            "longitude": 12.0,
            "status": "Exploration"
        },
        {
            "name": "Test Coordonnées",
            "company": "Test",
            "substanceId": "1",
            "latitude": 95,  # Latitude invalide
            "longitude": 12.0,
            "status": "Exploration"
        },
        {
            "name": "Test Substance",
            "company": "Test",
            "substanceId": "999",  # Substance inexistante
            "latitude": -0.5,
            "longitude": 12.0,
            "status": "Exploration"
        }
    ]
    
    for i, invalid_deposit in enumerate(invalid_deposits, 1):
        print(f"\n🧪 Test validation {i}:")
        try:
            response = requests.post(
                f"{API_BASE_URL}/deposits",
                json=invalid_deposit,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 400:
                data = response.json()
                print("✅ Validation fonctionnelle - Erreurs détectées:")
                for error in data.get('details', []):
                    print(f"  - {error}")
            else:
                print(f"❌ Validation échouée - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur test validation: {e}")

if __name__ == "__main__":
    print("=== Test de l'API ODG WebGIS - Phase 2 ===\n")
    
    print("1. Test récupération des substances:")
    test_get_substances()
    
    print("\n2. Test création d'un gisement valide:")
    test_create_deposit()
    
    print("\n3. Test avec données invalides:")
    test_invalid_data()
    
    print("\n=== Tests terminés ===")
