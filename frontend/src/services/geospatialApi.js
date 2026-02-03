/**
 * Service API pour les fonctionnalités géospatiales ODG
 * Gère les appels vers le backend Flask
 */

import React from 'react';

const API_BASE_URL = '/api/geospatial';

/**
 * Classe utilitaire pour les appels API
 */
class ApiClient {
  static async request(url, options = {}) {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    // Ne pas définir Content-Type pour FormData
    if (options.body instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    try {
      const response = await fetch(url, config);
      
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Erreur HTTP: ${response.status}`);
      }

      return data;
    } catch (error) {
      throw error;
    }
  }

  static async get(endpoint, params = {}) {
    const url = new URL(endpoint, window.location.origin);
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null) {
        url.searchParams.append(key, params[key]);
      }
    });

    return this.request(url.toString());
  }

  static async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data)
    });
  }

  static async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  static async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }
}

/**
 * Service principal pour les couches géospatiales
 */
export class GeospatialLayerService {
  /**
   * Upload d'un fichier géospatial
   * @param {File} file - Fichier à uploader
   * @param {Object} config - Configuration de la couche
   * @param {Function} onProgress - Callback de progression (optionnel)
   * @returns {Promise<Object>} Résultat de l'upload
   */
  static async uploadFile(file, config, onProgress = null) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', config.name);
    formData.append('description', config.description || '');
    formData.append('layer_type', config.layer_type);
    formData.append('status', config.status);

    // Si on a un callback de progression, utiliser XMLHttpRequest
    if (onProgress) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            onProgress(percentComplete);
          }
        });

        xhr.addEventListener('load', () => {
          try {
            const response = JSON.parse(xhr.responseText);
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve(response);
            } else {
              reject(new Error(response.error || `Erreur HTTP: ${xhr.status}`));
            }
          } catch (error) {
            reject(new Error('Erreur de parsing de la réponse'));
          }
        });

        xhr.addEventListener('error', () => {
          reject(new Error('Erreur réseau lors de l\'upload'));
        });

        xhr.open('POST', `${API_BASE_URL}/upload`);
        xhr.send(formData);
      });
    }

    // Sinon utiliser fetch classique
    return ApiClient.post(`${API_BASE_URL}/upload`, formData);
  }

  /**
   * Prévisualise un fichier géospatial sans créer de couche en base.
   * Utilisé pour l'étape "Aperçu et Validation" côté frontend.
   */
  static async previewFile(file, config = {}) {
    const formData = new FormData();
    formData.append('file', file);

    if (config.name) formData.append('name', config.name);
    if (config.description) formData.append('description', config.description);
    if (config.layer_type) formData.append('layer_type', config.layer_type);
    if (config.status) formData.append('status', config.status);

    return ApiClient.post(`${API_BASE_URL}/preview`, formData);
  }

  /**
   * Récupère la liste des couches géospatiales
   * @param {Object} filters - Filtres de recherche
   * @returns {Promise<Object>} Liste des couches avec pagination
   */
  static async getLayers(filters = {}) {
    const params = {
      page: filters.page || 1,
      per_page: filters.per_page || 20,
      include_geojson: filters.include_geojson || false,
      ...filters
    };

    return ApiClient.get(`${API_BASE_URL}/layers`, params);
  }

  /**
   * Récupère une couche spécifique
   * @param {number} layerId - ID de la couche
   * @param {boolean} includeGeojson - Inclure les données GeoJSON
   * @returns {Promise<Object>} Données de la couche
   */
  static async getLayer(layerId, includeGeojson = false) {
    const params = includeGeojson ? { include_geojson: true } : {};
    return ApiClient.get(`${API_BASE_URL}/layers/${layerId}`, params);
  }

  /**
   * Met à jour une couche géospatiale
   * @param {number} layerId - ID de la couche
   * @param {Object} updates - Données à mettre à jour
   * @returns {Promise<Object>} Couche mise à jour
   */
  static async updateLayer(layerId, updates) {
    return ApiClient.put(`${API_BASE_URL}/layers/${layerId}`, updates);
  }

  /**
   * Supprime une couche géospatiale
   * @param {number} layerId - ID de la couche
   * @returns {Promise<Object>} Confirmation de suppression
   */
  static async deleteLayer(layerId) {
    return ApiClient.delete(`${API_BASE_URL}/layers/${layerId}`);
  }

  /**
   * Exporte une couche dans un format spécifique
   * @param {number} layerId - ID de la couche
   * @param {string} format - Format d'export (geojson, kml, csv)
   * @returns {Promise<Object>} Données exportées
   */
  static async exportLayer(layerId, format) {
    return ApiClient.get(`${API_BASE_URL}/layers/${layerId}/export/${format}`);
  }

  /**
   * Télécharge une couche exportée
   * @param {number} layerId - ID de la couche
   * @param {string} format - Format d'export
   * @param {string} filename - Nom du fichier (optionnel)
   */
  static async downloadLayer(layerId, format, filename = null) {
    try {
      const data = await this.exportLayer(layerId, format);
      
      // Créer le blob selon le format
      let blob, mimeType, extension;
      
      switch (format.toLowerCase()) {
        case 'geojson':
          blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          mimeType = 'application/json';
          extension = 'geojson';
          break;
        case 'kml':
          blob = new Blob([data], { type: 'application/vnd.google-earth.kml+xml' });
          mimeType = 'application/vnd.google-earth.kml+xml';
          extension = 'kml';
          break;
        case 'csv':
          blob = new Blob([data], { type: 'text/csv' });
          mimeType = 'text/csv';
          extension = 'csv';
          break;
        default:
          throw new Error(`Format non supporté: ${format}`);
      }

      // Télécharger le fichier
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `layer_${layerId}.${extension}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      return { success: true, message: 'Téléchargement démarré' };
    } catch (error) {
      throw new Error(`Erreur lors du téléchargement: ${error.message}`);
    }
  }
}

/**
 * Service pour les statistiques géospatiales
 */
export class GeospatialStatsService {
  /**
   * Récupère les statistiques générales
   * @returns {Promise<Object>} Statistiques des couches
   */
  static async getStatistics() {
    return ApiClient.get(`${API_BASE_URL}/statistics`);
  }

  /**
   * Récupère l'historique des uploads
   * @param {Object} filters - Filtres de pagination
   * @returns {Promise<Object>} Historique avec pagination
   */
  static async getUploadHistory(filters = {}) {
    const params = {
      page: filters.page || 1,
      per_page: filters.per_page || 20
    };

    return ApiClient.get(`${API_BASE_URL}/upload-history`, params);
  }

  /**
   * Récupère les formats supportés
   * @returns {Promise<Object>} Formats et limites
   */
  static async getSupportedFormats() {
    return ApiClient.get(`${API_BASE_URL}/supported-formats`);
  }
}

/**
 * Service pour la validation des fichiers
 */
export class FileValidationService {
  /**
   * Valide un fichier avant upload
   * @param {File} file - Fichier à valider
   * @param {Object} supportedFormats - Formats supportés
   * @returns {Object} Résultat de validation
   */
  static validateFile(file, supportedFormats) {
    const errors = [];
    const warnings = [];

    // Vérification de la taille
    if (file.size > supportedFormats.max_file_size_mb * 1024 * 1024) {
      errors.push(`Fichier trop volumineux (max: ${supportedFormats.max_file_size_mb}MB)`);
    }

    // Vérification de l'extension
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!supportedFormats.extensions.includes(fileExt)) {
      errors.push(`Format non supporté. Formats acceptés: ${supportedFormats.extensions.join(', ')}`);
    }

    // Vérification du nom de fichier
    if (file.name.length > 255) {
      errors.push('Nom de fichier trop long (maximum 255 caractères)');
    }

    // Caractères spéciaux
    const invalidChars = /[<>:"/\\|?*]/;
    if (invalidChars.test(file.name)) {
      errors.push('Le nom de fichier contient des caractères non autorisés');
    }

    // Avertissements
    if (file.size > 10 * 1024 * 1024) { // 10MB
      warnings.push('Fichier volumineux - le traitement peut prendre du temps');
    }

    if (file.name.includes(' ')) {
      warnings.push('Le nom de fichier contient des espaces');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Détecte le type de fichier géospatial
   * @param {File} file - Fichier à analyser
   * @returns {Object} Informations sur le type
   */
  static detectFileType(file) {
    const ext = file.name.split('.').pop()?.toLowerCase();
    
    const typeMap = {
      'kml': { type: 'KML', description: 'Google Earth KML', category: 'vector' },
      'kmz': { type: 'KMZ', description: 'Google Earth KMZ (compressé)', category: 'vector' },
      'shp': { type: 'Shapefile', description: 'ESRI Shapefile', category: 'vector' },
      'geojson': { type: 'GeoJSON', description: 'GeoJSON standard', category: 'vector' },
      'json': { type: 'JSON', description: 'JSON (possiblement GeoJSON)', category: 'vector' },
      'csv': { type: 'CSV', description: 'Données tabulaires avec coordonnées', category: 'tabular' },
      'txt': { type: 'TXT', description: 'Coordonnées en texte brut', category: 'tabular' },
      'tiff': { type: 'TIFF', description: 'Image géoréférencée', category: 'raster' },
      'tif': { type: 'TIFF', description: 'Image géoréférencée', category: 'raster' }
    };

    return typeMap[ext] || { type: 'Inconnu', description: 'Format non reconnu', category: 'unknown' };
  }
}

/**
 * Hook React pour gérer les couches géospatiales
 */
export const useGeospatialLayers = () => {
  const [layers, setLayers] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const fetchLayers = React.useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);

    try {
      console.log('🔄 [fetchLayers] Appel API avec filtres:', filters);
      const result = await GeospatialLayerService.getLayers(filters);
      console.log('✅ [fetchLayers] Réponse API reçue:', result);
      console.log('✅ [fetchLayers] Données extraites:', result.data);
      console.log('✅ [fetchLayers] Nombre de couches:', result.data?.length);
      setLayers(result.data || []);
      return result;
    } catch (err) {
      console.error('❌ [fetchLayers] Erreur API:', err);
      console.warn('⚠️ Backend indisponible, utilisation des données de démonstration');
      // Mode démo avec plusieurs couches d'exemple cohérentes avec la section Couches
      const nowIso = new Date().toISOString();
      const demoLayers = [
        {
          id: 1,
          name: "Gisements d'or - Estuaire Nord",
          description: 'Principaux gisements aurifères suivis par ODG dans la région nord.',
          layer_type: 'deposit',
          status: 'actif',
          file_name: 'gisements_or_estuaire.geojson',
          created_at: nowIso,
          is_visible: true,
          features_count: 24,
        },
        {
          id: 2,
          name: 'Mines de diamant - Franceville',
          description: 'Localisation des sites diamantifères autour de Franceville.',
          layer_type: 'deposit',
          status: 'exploration',
          file_name: 'mines_diamant_franceville.kml',
          created_at: nowIso,
          is_visible: false,
          features_count: 9,
        },
        {
          id: 3,
          name: "Réseau routier minier",
          description: "Routes d'accès stratégiques aux principaux sites miniers.",
          layer_type: 'infrastructure',
          status: 'actif',
          file_name: 'reseau_routier_miner.shp',
          created_at: nowIso,
          is_visible: true,
          features_count: 48,
        },
        {
          id: 4,
          name: 'Concessions minières ODG',
          description: 'Limites administratives des concessions et permis.',
          layer_type: 'zone',
          status: 'en_développement',
          file_name: 'concessions_mineres_odg.geojson',
          created_at: nowIso,
          is_visible: false,
          features_count: 6,
        },
      ];
      setLayers(demoLayers);
      setError(null);
      return { data: demoLayers };
    } finally {
      setLoading(false);
    }
  }, []);

  const addLayer = React.useCallback((newLayer) => {
    setLayers(prev => [newLayer, ...prev]);
  }, []);

  const updateLayer = React.useCallback((layerId, updates) => {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId ? { ...layer, ...updates } : layer
    ));
  }, []);

  const removeLayer = React.useCallback((layerId) => {
    setLayers(prev => prev.filter(layer => layer.id !== layerId));
  }, []);

  const toggleLayerVisibility = React.useCallback((layerId) => {
    setLayers(prev => prev.map(layer => 
      layer.id === layerId ? { ...layer, is_visible: !layer.is_visible } : layer
    ));
  }, []);

  return {
    layers,
    loading,
    error,
    fetchLayers,
    addLayer,
    updateLayer,
    removeLayer,
    toggleLayerVisibility
  };
};

/**
 * Hook pour les statistiques géospatiales
 */
export const useGeospatialStats = () => {
  const [stats, setStats] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const fetchStats = React.useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await GeospatialStatsService.getStatistics();
      setStats(result.data);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats
  };
};

/**
 * Utilitaires pour les formats de fichiers
 */
export const FileUtils = {
  /**
   * Formate la taille d'un fichier
   * @param {number} bytes - Taille en bytes
   * @returns {string} Taille formatée
   */
  formatFileSize: (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  /**
   * Obtient l'icône pour un type de fichier
   * @param {string} filename - Nom du fichier
   * @returns {string} Classe d'icône
   */
  getFileIcon: (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    const iconMap = {
      'kml': '🗺️',
      'kmz': '🗺️',
      'shp': '🗃️',
      'geojson': '📄',
      'json': '📄',
      'csv': '📊',
      'txt': '📝',
      'tiff': '🖼️',
      'tif': '🖼️'
    };
    return iconMap[ext] || '📁';
  },

  /**
   * Génère un nom de fichier sûr
   * @param {string} filename - Nom original
   * @returns {string} Nom sécurisé
   */
  sanitizeFilename: (filename) => {
    return filename
      .replace(/[<>:"/\\|?*]/g, '_')
      .replace(/\s+/g, '_')
      .toLowerCase();
  }
};

// Export par défaut
export default {
  GeospatialLayerService,
  GeospatialStatsService,
  FileValidationService,
  FileUtils
};
