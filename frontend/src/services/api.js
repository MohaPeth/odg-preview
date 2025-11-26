/**
 * Services API pour le géoportail ODG
 * Phase 3 : Intégration frontend-backend
 */

import { useState } from "react";
import L from "leaflet";

const API_BASE_URL = "http://localhost:5000/api/webgis";

// Configuration par défaut pour les requêtes
const defaultHeaders = {
  "Content-Type": "application/json",
};

class ApiService {
  /**
   * Récupérer toutes les couches SIG
   */
  static async getLayers() {
    try {
      const response = await fetch(`${API_BASE_URL}/layers`, {
        method: "GET",
        headers: defaultHeaders,
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Erreur récupération couches:", error);
      throw error;
    }
  }

  /**
   * Récupérer tous les gisements au format GeoJSON
   */
  static async getDeposits(filters = {}) {
    try {
      const queryParams = new URLSearchParams();

      if (filters.substances?.length > 0) {
        filters.substances.forEach((id) =>
          queryParams.append("substances", id)
        );
      }

      if (filters.statuses?.length > 0) {
        filters.statuses.forEach((status) =>
          queryParams.append("statuses", status)
        );
      }

      if (filters.bbox) {
        queryParams.append("bbox", filters.bbox);
      }

      const url = `${API_BASE_URL}/deposits${
        queryParams.toString() ? `?${queryParams}` : ""
      }`;

      const response = await fetch(url, {
        method: "GET",
        headers: defaultHeaders,
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Erreur récupération gisements:", error);
      throw error;
    }
  }

  /**
   * Créer un nouveau gisement
   */
  static async createDeposit(depositData) {
    try {
      const response = await fetch(`${API_BASE_URL}/deposits`, {
        method: "POST",
        headers: defaultHeaders,
        body: JSON.stringify(depositData),
      });

      const data = await response.json();

      if (!response.ok) {
        // Construire un message d'erreur détaillé
        let errorMessage = data.error || "Erreur lors de la création";

        if (data.details && Array.isArray(data.details)) {
          errorMessage += ":\n" + data.details.join("\n");
        }

        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      console.error("Erreur création gisement:", error);
      throw error;
    }
  }

  /**
   * Récupérer les détails d'un gisement
   */
  static async getDepositDetails(depositId) {
    try {
      const response = await fetch(`${API_BASE_URL}/deposits/${depositId}`, {
        method: "GET",
        headers: defaultHeaders,
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Erreur récupération détails gisement:", error);
      throw error;
    }
  }

  /**
   * Récupérer toutes les communautés
   */
  static async getCommunities(filters = {}) {
    try {
      const queryParams = new URLSearchParams();

      if (filters.minPopulation) {
        queryParams.append("minPopulation", filters.minPopulation);
      }

      if (filters.affectedOnly) {
        queryParams.append("affectedOnly", filters.affectedOnly);
      }

      if (filters.bbox) {
        queryParams.append("bbox", filters.bbox);
      }

      const url = `${API_BASE_URL}/communities${
        queryParams.toString() ? `?${queryParams}` : ""
      }`;

      const response = await fetch(url, {
        method: "GET",
        headers: defaultHeaders,
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Erreur récupération communautés:", error);
      throw error;
    }
  }

  /**
   * Rechercher des locations
   */
  static async searchLocations(query, type = "all", limit = 20) {
    try {
      const queryParams = new URLSearchParams({
        q: query,
        type,
        limit: limit.toString(),
      });

      const response = await fetch(`${API_BASE_URL}/search?${queryParams}`, {
        method: "GET",
        headers: defaultHeaders,
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Erreur recherche:", error);
      throw error;
    }
  }

  /**
   * Récupérer les statistiques globales
   */
  static async getStatistics() {
    try {
      const response = await fetch(`${API_BASE_URL}/statistics`, {
        method: "GET",
        headers: defaultHeaders,
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Erreur récupération statistiques:", error);
      throw error;
    }
  }

  /**
   * Récupérer la liste des substances
   */
  static async getSubstances() {
    try {
      const response = await fetch(`${API_BASE_URL}/substances`, {
        method: "GET",
        headers: defaultHeaders,
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Erreur récupération substances:", error);
      throw error;
    }
  }
}

/**
 * Hook personnalisé pour gérer les notifications
 */
export function useNotifications() {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (message, type = "info") => {
    const id = Date.now();
    const notification = { id, message, type };

    setNotifications((prev) => [...prev, notification]);

    // Supprimer automatiquement après 5 secondes
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 5000);
  };

  const removeNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return {
    notifications,
    addNotification,
    removeNotification,
  };
}

/**
 * Utilitaires pour la gestion des données géospatiales
 */
export class GeoUtils {
  /**
   * Convertir des coordonnées en chaîne de caractères
   */
  static coordinatesToString(lat, lng, precision = 6) {
    return `${lat.toFixed(precision)}, ${lng.toFixed(precision)}`;
  }

  /**
   * Calculer la bounding box à partir d'une liste de coordonnées
   */
  static calculateBounds(coordinates) {
    if (!coordinates || coordinates.length === 0) return null;

    let minLat = coordinates[0][0];
    let maxLat = coordinates[0][0];
    let minLng = coordinates[0][1];
    let maxLng = coordinates[0][1];

    coordinates.forEach(([lat, lng]) => {
      minLat = Math.min(minLat, lat);
      maxLat = Math.max(maxLat, lat);
      minLng = Math.min(minLng, lng);
      maxLng = Math.max(maxLng, lng);
    });

    return {
      minLat,
      maxLat,
      minLng,
      maxLng,
      bbox: `${minLng},${minLat},${maxLng},${maxLat}`,
    };
  }

  /**
   * Générer une icône Leaflet dynamique basée sur la couleur
   */
  static createColoredIcon(color, size = 20) {
    const svgIcon = `
      <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="${color}" stroke="#000000" stroke-width="2"/>
      </svg>
    `;

    return new L.Icon({
      iconUrl: `data:image/svg+xml;base64,${btoa(svgIcon)}`,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
      popupAnchor: [0, -size / 2],
    });
  }
}

export default ApiService;
