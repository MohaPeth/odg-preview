import React, { useState, useEffect, useRef } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polygon,
  Polyline,
  LayersControl,
  FeatureGroup,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ApiService from "../services/api";
import { Input } from "@/components/ui/input";
import {
  Search,
  MapPin,
  Mountain,
  Factory,
  Route,
  Info,
  Plus,
  Target,
  Layers,
  Upload,
  Database,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import AddDepositModal from "./AddDepositModal";
import AddGeospatialLayerModalV2 from "./AddGeospatialLayerModalV2";
import LayersManagementTable from "./LayersManagementTable";
import DynamicLayerRenderer from "./DynamicLayerRenderer";
import ErrorBoundary from "./ErrorBoundary";
import { useGeospatialLayers } from "../services/geospatialApi";

// Configuration des icônes Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// Icônes personnalisées pour différents types de gisements
const goldIcon = new L.Icon({
  iconUrl:
    "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIGZpbGw9IiNGRkQ3MDAiIHN0cm9rZT0iI0Y1OTUwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CjwvdXZnPgo=",
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -10],
});

const diamondIcon = new L.Icon({
  iconUrl:
    "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIGZpbGw9IiM2MEE1RkEiIHN0cm9rZT0iIzI1NjNFQiIgc3Ryb2tlLXdpZHRoPSIyIi8+CjwvdXZnPgo=",
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -10],
});

// Données simulées basées sur les informations du projet
const miningDeposits = [
  {
    id: 1,
    name: "Gisement Minkebe",
    type: "Or",
    coordinates: [-0.5, 12.0],
    company: "ODG",
    estimatedQuantity: "755 Km²",
    status: "Actif",
    description: "Gisement aurifère dans la province de Woleu-Ntem",
  },
  {
    id: 2,
    name: "Gisement Myaning",
    type: "Or",
    coordinates: [-1.2, 10.8],
    company: "ODG",
    estimatedQuantity: "150 Km²",
    status: "En développement",
    description: "Gisement aurifère à 70 Km de Lambaréné",
  },
  {
    id: 3,
    name: "Gisement Eteke",
    type: "Or",
    coordinates: [-2.1, 11.5],
    company: "ODG",
    estimatedQuantity: "765 Km²",
    status: "Exploration",
    description: "Gisement dans le sud-est du Gabon, province de la Ngounié",
  },
];

const exploitationAreas = [
  {
    id: 1,
    name: "Zone AFM",
    company: "AFM",
    status: "En cours",
    coordinates: [
      [-0.4, 11.9],
      [-0.6, 11.9],
      [-0.6, 12.1],
      [-0.4, 12.1],
    ],
    area: "50 Km²",
    extractedVolume: "1,200 tonnes",
  },
  {
    id: 2,
    name: "Zone BDM",
    company: "BDM",
    status: "Terminé",
    coordinates: [
      [-1.1, 10.7],
      [-1.3, 10.7],
      [-1.3, 10.9],
      [-1.1, 10.9],
    ],
    area: "30 Km²",
    extractedVolume: "800 tonnes",
  },
];

const infrastructure = [
  {
    id: 1,
    name: "Route Libreville-Lambaréné",
    type: "Route",
    coordinates: [
      [0.4, 9.4],
      [-0.7, 10.2],
      [-1.2, 10.8],
    ],
    length: "250 km",
    status: "Bon état",
  },
];

const WebGISMap = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDeposit, setSelectedDeposit] = useState(null);
  const [filteredDeposits, setFilteredDeposits] = useState(miningDeposits);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isAddingMode, setIsAddingMode] = useState(false);
  const [pendingCoordinates, setPendingCoordinates] = useState(null);
  const [deposits, setDeposits] = useState(miningDeposits);
  const [activeTab, setActiveTab] = useState("deposits");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const mapRef = useRef();

  // Hook pour les couches géospatiales
  const {
    layers: geospatialLayers,
    loading: layersLoading,
    error: layersError,
    fetchLayers,
    addLayer,
    updateLayer,
    removeLayer,
    toggleLayerVisibility
  } = useGeospatialLayers();

  // Composant pour gérer les clics sur la carte
  const MapClickHandler = () => {
    useMapEvents({
      click: (e) => {
        if (isAddingMode) {
          const { lat, lng } = e.latlng;
          setPendingCoordinates({ lat, lng });
          setIsAddModalOpen(true);
          setIsAddingMode(false);
        }
      },
    });
    return null;
  };

  useEffect(() => {
    // Charger les données initiales depuis l'API au démarrage
    loadDepositsFromAPI();
    // Charger les couches géospatiales
    fetchLayers();
  }, []); // Le tableau vide signifie que cela ne s'exécute qu'au montage du composant

  useEffect(() => {
    const filtered = deposits.filter(
      (deposit) =>
        deposit.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        deposit.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        deposit.company.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredDeposits(filtered);
  }, [searchTerm, deposits]);

  // Fonction pour sauvegarder un nouveau gis<|1000000|>ement
  const handleSaveDeposit = async (depositData, geojsonFeature) => {
    try {
      // Si nous avons des données géographiques et un ID
      if (depositData && depositData.id) {
        // Extraire les coordonnées depuis les données reçues
        const coordinates = depositData.coordinates || [
          depositData.longitude,
          depositData.latitude,
        ];

        // Créer un objet de gisement formaté pour notre interface
        const newDeposit = {
          id: depositData.id,
          name: depositData.name,
          type: depositData.substance?.name || "Inconnu",
          coordinates: [depositData.latitude, depositData.longitude],
          company: depositData.company,
          estimatedQuantity: depositData.estimatedQuantity
            ? `${depositData.estimatedQuantity} ${
                depositData.quantityUnit || "tonnes"
              }`
            : "Non spécifiée",
          status: depositData.status,
          description:
            depositData.description ||
            "Nouveau gisement ajouté via l'interface",
        };

        // Ajouter le nouveau gisement à la liste
        setDeposits((prev) => [...prev, newDeposit]);

        // Sélectionner automatiquement le nouveau gisement
        setSelectedDeposit(newDeposit);

        // Notifier l'utilisateur
        alert(`Le gisement "${depositData.name}" a été ajouté avec succès!`);
      }

      // Effacer les coordonnées en attente
      setPendingCoordinates(null);

      // Rafraîchir la liste des gisements depuis l'API
      loadDepositsFromAPI();
    } catch (error) {
      alert(
        "Une erreur est survenue lors de l'ajout du gisement. Veuillez réessayer."
      );
      throw error;
    }
  };

  // Chargement des gisements depuis l'API (mode démo si backend indisponible)
  const loadDepositsFromAPI = async () => {
    try {
      const apiDeposits = await ApiService.getDeposits();
      if (apiDeposits && apiDeposits.length > 0) {
        setDeposits(apiDeposits);
      }
    } catch (error) {
      // En cas d'erreur, on garde les données simulées
      setDeposits(miningDeposits);
    }
  };

  // Fonction pour activer le mode d'ajout
  const handleAddDepositClick = () => {
    setIsAddingMode(true);
    setSelectedDeposit(null);
  };

  // Fonction pour annuler le mode d'ajout
  const handleCancelAddMode = () => {
    setIsAddingMode(false);
    setPendingCoordinates(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "Actif":
      case "En cours":
        return "bg-green-500";
      case "En développement":
        return "bg-yellow-500";
      case "Exploration":
        return "bg-blue-500";
      case "Terminé":
        return "bg-gray-500";
      default:
        return "bg-gray-400";
    }
  };

  const getPolygonColor = (status) => {
    switch (status) {
      case "En cours":
        return "#22c55e";
      case "Terminé":
        return "#6b7280";
      case "Permis en attente":
        return "#eab308";
      default:
        return "#3b82f6";
    }
  };

  // Logs de debug pour les couches
  useEffect(() => {
    // Rafraîchir la carte après chargement des couches
    if (mapRef.current && geospatialLayers.length > 0) {
      setTimeout(() => {
        const map = mapRef.current;
        if (map && map.invalidateSize) {
          map.invalidateSize();
        }
      }, 100);
    }
  }, [geospatialLayers]);

  // Gestionnaires d'événements pour les couches géospatiales
  const handleLayerAdded = (newLayer) => {
    addLayer(newLayer);
    // Rafraîchir la liste des couches
    fetchLayers();
    
    // Rafraîchir la carte
    if (mapRef.current) {
      setTimeout(() => {
        const map = mapRef.current;
        if (map && map.invalidateSize) {
          map.invalidateSize();
        }
      }, 200);
    }
  };

  const handleLayerToggle = (layerId, isVisible) => {
    toggleLayerVisibility(layerId);
    
    // Rafraîchir la carte
    if (mapRef.current) {
      setTimeout(() => {
        const map = mapRef.current;
        if (map && map.invalidateSize) {
          map.invalidateSize();
        }
      }, 100);
    }
  };

  const handleLayerEdit = (layer) => {
    // TODO: Implémenter l'édition des couches
  };

  const handleLayerDelete = (layerId) => {
    removeLayer(layerId);
  };

  const handleLayerClick = (layer, feature, event) => {
    // Gestion du clic sur une couche
  };

  const handleLayerLoad = (layer, leafletLayer) => {
    // Couche chargée avec succès
  };

  const handleLayerError = (layer, error) => {
    // Erreur lors du chargement de la couche
  };

  return (
    <div className="h-screen flex relative overflow-hidden min-w-0">
      {/* Bouton toggle mobile */}
      <Button
        variant="outline"
        size="sm"
        className="fixed top-4 left-4 z-50 lg:hidden bg-white shadow-md"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
      </Button>

      {/* Overlay mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Panneau latéral – max-w-full et min-w-0 pour éviter débordement horizontal */}
      <div className={`
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        ${sidebarCollapsed ? 'lg:w-16' : 'lg:w-80'}
        fixed lg:relative top-0 left-0 h-full w-80 max-w-[85vw] lg:max-w-none bg-white shadow-lg overflow-y-auto overflow-x-hidden z-40 shrink-0
        transition-all duration-300 ease-in-out
      `}>
        <div className="p-4 min-w-0">
          {/* En-tête avec bouton collapse desktop */}
          <div className="flex items-center justify-between mb-4">
            <h2 className={`text-xl font-bold flex items-center ${sidebarCollapsed ? 'lg:hidden' : ''}`}>
              <Mountain className="mr-2" />
              {!sidebarCollapsed && "Géoportail Minier ODG"}
            </h2>
            
            {/* Bouton collapse desktop */}
            <Button
              variant="ghost"
              size="sm"
              className="hidden lg:flex"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            >
              {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </Button>
          </div>

          {/* Onglets principaux */}
          {!sidebarCollapsed && (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-4">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="deposits" className="flex items-center space-x-1">
                  <Mountain className="h-4 w-4" />
                  <span>Gisements</span>
                </TabsTrigger>
                <TabsTrigger value="layers" className="flex items-center space-x-1">
                  <Layers className="h-4 w-4" />
                  <span>Couches</span>
                </TabsTrigger>
              </TabsList>

            <TabsContent value="deposits" className="space-y-4">
              {/* Boutons d'action pour gisements */}
              <div className="flex space-x-2">
                <Button
                  onClick={handleAddDepositClick}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                  disabled={isAddingMode}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  {isAddingMode ? "Cliquez sur la carte" : "Ajouter un gisement"}
                </Button>
                {isAddingMode && (
                  <Button onClick={handleCancelAddMode} variant="outline" size="sm">
                    Annuler
                  </Button>
                )}
              </div>

              {/* Barre de recherche pour gisements */}
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Rechercher gisements, entreprises..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Légende */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Légende</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
                    <span className="text-sm">Gisements d'or</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                    <span className="text-sm">Gisements de diamant</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-green-500 rounded"></div>
                    <span className="text-sm">Zone en exploitation</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-gray-500 rounded"></div>
                    <span className="text-sm">Zone terminée</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Route className="w-4 h-4 text-blue-600" />
                    <span className="text-sm">Infrastructure</span>
                  </div>
                </CardContent>
              </Card>

              {/* Liste des gisements */}
              <div className="space-y-2">
                <h3 className="font-semibold text-sm text-gray-600">
                  Gisements Miniers
                </h3>
                {filteredDeposits.map((deposit) => (
                  <Card
                    key={deposit.id}
                    className={`cursor-pointer transition-all hover:shadow-md ${
                      selectedDeposit?.id === deposit.id
                        ? "ring-2 ring-blue-500"
                        : ""
                    }`}
                    onClick={() => setSelectedDeposit(deposit)}
                  >
                    <CardContent className="p-3">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-sm">{deposit.name}</h4>
                        <Badge
                          className={`text-xs ${getStatusColor(
                            deposit.status
                          )} text-white`}
                        >
                          {deposit.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 mb-1">
                        {deposit.type} - {deposit.company}
                      </p>
                      <p className="text-xs text-gray-500">
                        {deposit.estimatedQuantity}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="layers" className="space-y-4 min-w-0">
              {/* Boutons d'action pour couches géospatiales */}
              <div className="flex flex-wrap gap-2">
                <AddGeospatialLayerModalV2 
                  onLayerAdded={handleLayerAdded}
                  trigger={
                    <Button className="flex-1 min-w-0 bg-blue-600 hover:bg-blue-700">
                      <Upload className="mr-2 h-4 w-4 shrink-0" />
                      <span className="truncate">Importer une couche</span>
                    </Button>
                  }
                />
              </div>

              {/* Tableau de gestion des couches géospatiales – scroll horizontal si besoin */}
              <div className="min-w-0 overflow-x-auto">
              <ErrorBoundary onReset={() => window.location.reload()}>
                <LayersManagementTable
                  onLayerToggle={handleLayerToggle}
                  onLayerEdit={handleLayerEdit}
                  onLayerDelete={handleLayerDelete}
                  selectedLayers={geospatialLayers.filter(layer => layer.is_visible).map(layer => layer.id)}
                  className="max-h-96 overflow-y-auto min-w-0"
                />
              </ErrorBoundary>
              </div>
            </TabsContent>
            </Tabs>
          )}

          {/* Boutons rapides en mode collapsé */}
          {sidebarCollapsed && (
            <div className="hidden lg:flex flex-col space-y-2">
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-center"
                onClick={() => {
                  setSidebarCollapsed(false);
                  setActiveTab('deposits');
                }}
                title="Gisements"
              >
                <Mountain className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-center"
                onClick={() => {
                  setSidebarCollapsed(false);
                  setActiveTab('layers');
                }}
                title="Couches géospatiales"
              >
                <Layers className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* Mode d'ajout actif */}
          {!sidebarCollapsed && isAddingMode && (
            <Card className="mb-4 border-green-500 bg-green-50">
              <CardContent className="p-3">
                <div className="flex items-center text-green-700">
                  <Target className="mr-2 h-4 w-4" />
                  <span className="text-sm font-medium">
                    Mode ajout activé - Cliquez sur la carte pour définir la
                    localisation
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Carte principale – min-w-0 pour que flex ne déborde pas */}
      <div className="flex-1 min-w-0 relative">
        <MapContainer
          center={[0, 11.5]}
          zoom={7}
          style={{ height: "100%", width: "100%" }}
          ref={mapRef}
        >
          <MapClickHandler />
          
          {/* Rendu dynamique des couches géospatiales */}
          <DynamicLayerRenderer
            layers={geospatialLayers}
            onLayerClick={handleLayerClick}
            onLayerLoad={handleLayerLoad}
            onLayerError={handleLayerError}
          />
          
          <LayersControl position="topright">
            <LayersControl.BaseLayer checked name="OpenStreetMap">
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
            </LayersControl.BaseLayer>

            <LayersControl.BaseLayer name="Satellite">
              <TileLayer
                attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              />
            </LayersControl.BaseLayer>

            <LayersControl.Overlay checked name="Gisements Miniers">
              <FeatureGroup>
                {deposits.map((deposit) => {
                  // Déterminer l'icône en fonction du type
                  let icon;
                  if (
                    deposit.type &&
                    deposit.type.toLowerCase().includes("or")
                  ) {
                    icon = goldIcon;
                  } else if (
                    deposit.type &&
                    deposit.type.toLowerCase().includes("diamant")
                  ) {
                    icon = diamondIcon;
                  } else {
                    // Icône par défaut pour les autres types
                    icon = new L.Icon({
                      iconUrl:
                        "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIGZpbGw9IiM4NEMxRkYiIHN0cm9rZT0iIzAwMDAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CjwvdXZnPgo=",
                      iconSize: [20, 20],
                      iconAnchor: [10, 10],
                      popupAnchor: [0, -10],
                    });
                  }

                  return (
                    <Marker
                      key={deposit.id}
                      position={deposit.coordinates}
                      icon={icon}
                    >
                      <Popup>
                        <div className="p-2">
                          <h3 className="font-bold">{deposit.name}</h3>
                          <p>
                            <strong>Type:</strong> {deposit.type}
                          </p>
                          <p>
                            <strong>Entreprise:</strong> {deposit.company}
                          </p>
                          <p>
                            <strong>Superficie:</strong>{" "}
                            {deposit.estimatedQuantity}
                          </p>
                          <p>
                            <strong>Statut:</strong> {deposit.status}
                          </p>
                          <p className="text-sm text-gray-600 mt-2">
                            {deposit.description}
                          </p>
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </FeatureGroup>
            </LayersControl.Overlay>

            <LayersControl.Overlay checked name="Zones d'Exploitation">
              <FeatureGroup>
                {exploitationAreas.map((area) => (
                  <Polygon
                    key={area.id}
                    positions={area.coordinates}
                    pathOptions={{
                      color: getPolygonColor(area.status),
                      fillColor: getPolygonColor(area.status),
                      fillOpacity: 0.3,
                      weight: 2,
                    }}
                  >
                    <Popup>
                      <div className="p-2">
                        <h3 className="font-bold">{area.name}</h3>
                        <p>
                          <strong>Entreprise:</strong> {area.company}
                        </p>
                        <p>
                          <strong>Statut:</strong> {area.status}
                        </p>
                        <p>
                          <strong>Superficie:</strong> {area.area}
                        </p>
                        <p>
                          <strong>Volume extrait:</strong>{" "}
                          {area.extractedVolume}
                        </p>
                      </div>
                    </Popup>
                  </Polygon>
                ))}
              </FeatureGroup>
            </LayersControl.Overlay>

            <LayersControl.Overlay name="Infrastructure">
              <FeatureGroup>
                {infrastructure.map((infra) => (
                  <Polyline
                    key={infra.id}
                    positions={infra.coordinates}
                    pathOptions={{
                      color: "#2563eb",
                      weight: 4,
                      opacity: 0.8,
                    }}
                  >
                    <Popup>
                      <div className="p-2">
                        <h3 className="font-bold">{infra.name}</h3>
                        <p>
                          <strong>Type:</strong> {infra.type}
                        </p>
                        <p>
                          <strong>Longueur:</strong> {infra.length}
                        </p>
                        <p>
                          <strong>État:</strong> {infra.status}
                        </p>
                      </div>
                    </Popup>
                  </Polyline>
                ))}
              </FeatureGroup>
            </LayersControl.Overlay>
          </LayersControl>
        </MapContainer>

        {/* Panneau d'information flottant */}
        {selectedDeposit && (
          <Card className="absolute top-4 right-4 w-80 z-[1000] shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <Info className="mr-2 h-4 w-4" />
                  {selectedDeposit.name}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedDeposit(null)}
                >
                  ×
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="font-medium">Type:</span>
                  <span>{selectedDeposit.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Entreprise:</span>
                  <span>{selectedDeposit.company}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Superficie:</span>
                  <span>{selectedDeposit.estimatedQuantity}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Statut:</span>
                  <Badge
                    className={`${getStatusColor(
                      selectedDeposit.status
                    )} text-white`}
                  >
                    {selectedDeposit.status}
                  </Badge>
                </div>
                <div className="mt-3">
                  <span className="font-medium">Description:</span>
                  <p className="text-sm text-gray-600 mt-1">
                    {selectedDeposit.description}
                  </p>
                </div>
                <div className="mt-3">
                  <span className="font-medium">Coordonnées:</span>
                  <p className="text-sm text-gray-600">
                    {selectedDeposit.coordinates[0].toFixed(4)},{" "}
                    {selectedDeposit.coordinates[1].toFixed(4)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Modal d'ajout de gisement */}
      <AddDepositModal
        isOpen={isAddModalOpen}
        onClose={() => {
          setIsAddModalOpen(false);
          setPendingCoordinates(null);
        }}
        onSave={handleSaveDeposit}
        initialCoordinates={pendingCoordinates}
      />
    </div>
  );
};

export default WebGISMap;
