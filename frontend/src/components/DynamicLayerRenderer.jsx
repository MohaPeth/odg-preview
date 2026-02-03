import React, { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import './geospatial-layers.css';

const DynamicLayerRenderer = ({ 
  layers = [], 
  onLayerClick, 
  onLayerLoad,
  onLayerError 
}) => {
  const map = useMap();
  const layerGroupRef = useRef(null);
  const layersRef = useRef(new Map());

  // Styles par défaut selon le type de couche
  const getDefaultStyle = useCallback((layer) => {
    const baseStyle = {
      weight: 2,
      opacity: 0.8,
      fillOpacity: 0.6
    };

    // Styles selon le type de couche
    switch (layer.layer_type) {
      case 'deposit':
        return {
          ...baseStyle,
          color: '#f59e0b', // Orange pour les gisements
          fillColor: '#fbbf24'
        };
      case 'infrastructure':
        return {
          ...baseStyle,
          color: '#3b82f6', // Bleu pour l'infrastructure
          fillColor: '#60a5fa'
        };
      case 'zone':
        return {
          ...baseStyle,
          color: '#10b981', // Vert pour les zones
          fillColor: '#34d399'
        };
      case 'custom':
      default:
        return {
          ...baseStyle,
          color: '#8b5cf6', // Violet pour les couches personnalisées
          fillColor: '#a78bfa'
        };
    }
  }, []);

  // Styles selon le statut
  const getStatusStyle = useCallback((status) => {
    switch (status) {
      case 'actif':
        return { opacity: 0.8, fillOpacity: 0.6 };
      case 'en_développement':
        return { opacity: 0.6, fillOpacity: 0.4, dashArray: '5, 5' };
      case 'exploration':
        return { opacity: 0.5, fillOpacity: 0.3, dashArray: '10, 5' };
      case 'terminé':
        return { opacity: 0.4, fillOpacity: 0.2 };
      default:
        return { opacity: 0.8, fillOpacity: 0.6 };
    }
  }, []);

  // Création d'un marqueur personnalisé selon le type
  const createCustomMarker = useCallback((layer) => {
    const iconConfig = {
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -32]
    };

    // Icônes selon le type de couche
    switch (layer.layer_type) {
      case 'deposit':
        return L.divIcon({
          ...iconConfig,
          html: `<div class="custom-marker deposit-marker">⛏️</div>`,
          className: 'custom-div-icon'
        });
      case 'infrastructure':
        return L.divIcon({
          ...iconConfig,
          html: `<div class="custom-marker infrastructure-marker">🏗️</div>`,
          className: 'custom-div-icon'
        });
      case 'zone':
        return L.divIcon({
          ...iconConfig,
          html: `<div class="custom-marker zone-marker">🗺️</div>`,
          className: 'custom-div-icon'
        });
      case 'custom':
      default:
        return L.divIcon({
          ...iconConfig,
          html: `<div class="custom-marker custom-marker-icon">📍</div>`,
          className: 'custom-div-icon'
        });
    }
  }, []);

  // Création du contenu de popup
  const createPopupContent = useCallback((layer) => {
    const stats = [];
    const areaKm2 = layer.areaKm2 || layer.area_km2;
    const lengthKm = layer.lengthKm || layer.length_km;
    const pointCount = layer.pointCount || layer.point_count || layer.featureCount;
    
    if (areaKm2) stats.push(`Superficie: ${parseFloat(areaKm2).toFixed(2)} km²`);
    if (lengthKm) stats.push(`Longueur: ${parseFloat(lengthKm).toFixed(2)} km`);
    if (pointCount) stats.push(`Points: ${pointCount}`);

    // Sécuriser les propriétés avec fallback camelCase/snake_case
    const layerType = layer.layerType || layer.layer_type || 'Non spécifié';
    const sourceFormat = layer.sourceFormat || layer.source_format || 'Inconnu';
    const geometryType = layer.geometryType || layer.geometry_type || 'Non défini';
    const createdAt = layer.createdAt || layer.created_at;
    
    // Sécuriser la date
    let dateDisplay = 'Date inconnue';
    if (createdAt) {
      try {
        const date = new Date(createdAt);
        if (!isNaN(date.getTime())) {
          dateDisplay = date.toLocaleDateString('fr-FR');
        }
      } catch (e) {
        console.warn('Invalid date format:', createdAt);
      }
    }

    return `
      <div class="geospatial-popup">
        <h3 class="popup-title">${layer.name || 'Sans nom'}</h3>
        ${layer.description ? `<p class="popup-description">${layer.description}</p>` : ''}
        <div class="popup-details">
          <div class="popup-row">
            <strong>Type:</strong> ${layerType}
          </div>
          <div class="popup-row">
            <strong>Statut:</strong> <span class="status-${layer.status || 'inconnu'}">${layer.status || 'Non défini'}</span>
          </div>
          <div class="popup-row">
            <strong>Format:</strong> ${sourceFormat}
          </div>
          <div class="popup-row">
            <strong>Géométrie:</strong> ${geometryType}
          </div>
          ${stats.length > 0 ? `
            <div class="popup-stats">
              <strong>Statistiques:</strong><br>
              ${stats.join('<br>')}
            </div>
          ` : ''}
          <div class="popup-date">
            Créé le: ${dateDisplay}
          </div>
        </div>
      </div>
    `;
  }, []);

  // Création d'une couche Leaflet à partir des données GeoJSON
  const createLeafletLayer = useCallback(async (layer) => {
    try {
      // Création de la couche géospatiale
      
      // Récupérer les données GeoJSON de la couche
      const response = await fetch(`/api/geospatial/layers/${layer.id}?include_geojson=true`);
      const result = await response.json();
      

      if (!result.success || !result.data.geojson) {
        // GeoJSON manquant pour la couche
        throw new Error('Données GeoJSON non disponibles');
      }
      
      // GeoJSON récupéré avec succès

      const geojsonData = result.data.geojson;
      
      // Styles combinés
      const defaultStyle = getDefaultStyle(layer);
      const statusStyle = getStatusStyle(layer.status);
      const customStyle = layer.style_config || {};
      
      const finalStyle = {
        ...defaultStyle,
        ...statusStyle,
        ...customStyle
      };

      // Créer la couche GeoJSON
      const leafletLayer = L.geoJSON(geojsonData, {
        style: (feature) => finalStyle,
        
        pointToLayer: (feature, latlng) => {
          const marker = L.marker(latlng, {
            icon: createCustomMarker(layer)
          });
          return marker;
        },

        onEachFeature: (feature, leafletFeature) => {
          // Popup
          const popupContent = createPopupContent(layer);
          leafletFeature.bindPopup(popupContent, {
            maxWidth: 300,
            className: 'geospatial-popup-container'
          });

          // Tooltip
          leafletFeature.bindTooltip(layer.name, {
            permanent: false,
            direction: 'top',
            className: 'geospatial-tooltip'
          });

          // Événements
          leafletFeature.on({
            click: (e) => {
              if (onLayerClick) {
                onLayerClick(layer, feature, e);
              }
            },
            mouseover: (e) => {
              // Highlight au survol
              if (leafletFeature.setStyle) {
                leafletFeature.setStyle({
                  weight: finalStyle.weight + 2,
                  opacity: Math.min(1, finalStyle.opacity + 0.2)
                });
              }
            },
            mouseout: (e) => {
              // Retour au style normal
              if (leafletFeature.setStyle) {
                leafletFeature.setStyle(finalStyle);
              }
            }
          });
        }
      });

      // Métadonnées de la couche
      leafletLayer._geospatialLayer = layer;
      
      return leafletLayer;

    } catch (error) {
      // Erreur lors de la création de la couche
      if (onLayerError) {
        onLayerError(layer, error);
      }
      return null;
    }
  }, [getDefaultStyle, getStatusStyle, createCustomMarker, createPopupContent, onLayerClick, onLayerError]);

  // Mise à jour des couches
  const updateLayers = useCallback(async () => {
    if (!map || !layerGroupRef.current) return;

    // BUG FIX #2: Vérifier que layers existe et est un tableau
    if (!layers || !Array.isArray(layers) || layers.length === 0) {
      // Aucune couche à afficher ou layers invalide
      return;
    }

    // Couches actuellement affichées
    const currentLayerIds = new Set(layersRef.current.keys());
    
    // Couches qui devraient être affichées (visibles uniquement)
    // BUG FIX #3: Vérifier explicitement que is_visible === true (pas undefined, null, 0...)
    const visibleLayers = layers.filter(layer => layer.is_visible === true);
    const targetLayerIds = new Set(visibleLayers.map(layer => layer.id));
    

    // Supprimer les couches qui ne devraient plus être affichées
    for (const layerId of currentLayerIds) {
      if (!targetLayerIds.has(layerId)) {
        const leafletLayer = layersRef.current.get(layerId);
        if (leafletLayer) {
          layerGroupRef.current.removeLayer(leafletLayer);
          layersRef.current.delete(layerId);
        }
      }
    }

    // Ajouter ou mettre à jour les nouvelles couches
    for (const layer of visibleLayers) {
      if (!layersRef.current.has(layer.id)) {
        try {
          const leafletLayer = await createLeafletLayer(layer);
          if (leafletLayer) {
            layersRef.current.set(layer.id, leafletLayer);
            layerGroupRef.current.addLayer(leafletLayer);
            
            if (onLayerLoad) {
              onLayerLoad(layer, leafletLayer);
            }
          }
        } catch (error) {
          // Erreur lors du chargement de la couche
        }
      }
    }
  }, [map, layers, createLeafletLayer, onLayerLoad]);

  // Initialisation du groupe de couches
  useEffect(() => {
    if (!map) return;

    // Créer le groupe de couches s'il n'existe pas
    if (!layerGroupRef.current) {
      layerGroupRef.current = L.layerGroup().addTo(map);
    }

    // Ajouter les styles CSS personnalisés
    if (!document.getElementById('geospatial-styles')) {
      const style = document.createElement('style');
      style.id = 'geospatial-styles';
      style.textContent = `
        .custom-div-icon {
          background: none !important;
          border: none !important;
        }
        
        .custom-marker {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          background: white;
          border: 2px solid #333;
          border-radius: 50%;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .deposit-marker {
          border-color: #f59e0b;
          background: #fef3c7;
        }
        
        .infrastructure-marker {
          border-color: #3b82f6;
          background: #dbeafe;
        }
        
        .zone-marker {
          border-color: #10b981;
          background: #d1fae5;
        }
        
        .custom-marker-icon {
          border-color: #8b5cf6;
          background: #ede9fe;
        }
        
        .geospatial-popup-container .leaflet-popup-content {
          margin: 8px 12px;
          line-height: 1.4;
        }
        
        .geospatial-popup {
          font-family: system-ui, -apple-system, sans-serif;
        }
        
        .popup-title {
          font-size: 16px;
          font-weight: 600;
          margin: 0 0 8px 0;
          color: #1f2937;
        }
        
        .popup-description {
          font-size: 14px;
          color: #6b7280;
          margin: 0 0 12px 0;
        }
        
        .popup-details {
          font-size: 13px;
        }
        
        .popup-row {
          margin: 4px 0;
        }
        
        .popup-stats {
          margin: 8px 0;
          padding: 8px;
          background: #f9fafb;
          border-radius: 4px;
        }
        
        .popup-date {
          margin-top: 8px;
          font-size: 12px;
          color: #9ca3af;
        }
        
        .status-actif { color: #059669; font-weight: 500; }
        .status-en_développement { color: #d97706; font-weight: 500; }
        .status-exploration { color: #2563eb; font-weight: 500; }
        .status-terminé { color: #6b7280; font-weight: 500; }
        
        .geospatial-tooltip {
          background: rgba(0, 0, 0, 0.8) !important;
          border: none !important;
          border-radius: 4px !important;
          color: white !important;
          font-size: 12px !important;
          padding: 4px 8px !important;
        }
        
        .geospatial-tooltip::before {
          border-top-color: rgba(0, 0, 0, 0.8) !important;
        }
      `;
      document.head.appendChild(style);
    }

    return () => {
      // Nettoyage lors du démontage
      if (layerGroupRef.current) {
        map.removeLayer(layerGroupRef.current);
        layerGroupRef.current = null;
      }
      layersRef.current.clear();
    };
  }, [map]);

  // Mise à jour des couches quand les props changent
  useEffect(() => {
    updateLayers();
  }, [updateLayers]);

  // Méthodes exposées via ref (si nécessaire)
  const getLayerGroup = useCallback(() => layerGroupRef.current, []);
  const getLayer = useCallback((layerId) => layersRef.current.get(layerId), []);
  const getAllLayers = useCallback(() => Array.from(layersRef.current.values()), []);

  // Centrer la carte sur toutes les couches visibles
  const fitBounds = useCallback(() => {
    if (!layerGroupRef.current || layersRef.current.size === 0) return;

    try {
      const bounds = layerGroupRef.current.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [20, 20] });
      }
    } catch (error) {
      // Impossible de centrer sur les couches
    }
  }, [map]);

  // Les méthodes utiles sont disponibles via les callbacks

  // Ce composant ne rend rien directement (il manipule la carte)
  return null;
};

export default DynamicLayerRenderer;
