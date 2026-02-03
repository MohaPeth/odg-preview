import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  RefreshCcw,
  Layers as LayersIcon,
  Upload,
  Eye,
  EyeOff,
  Database,
} from "lucide-react";
import AddGeospatialLayerModalV2 from "./AddGeospatialLayerModalV2";
import LayersManagementTable from "./LayersManagementTable";
import { useGeospatialLayers } from "../services/geospatialApi";

const LayersWorkspace = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const {
    layers,
    fetchLayers,
    addLayer,
    removeLayer,
    toggleLayerVisibility,
  } = useGeospatialLayers();

  useEffect(() => {
    fetchLayers();
  }, [fetchLayers]);

  const visibleLayers = useMemo(
    () => layers.filter((layer) => layer.is_visible),
    [layers]
  );

  const layerStats = useMemo(() => {
    const total = layers.length;
    const visible = layers.filter((layer) => layer.is_visible).length;
    const hidden = total - visible;
    return { total, visible, hidden };
  }, [layers]);

  const triggerRefresh = () => setRefreshTrigger((count) => count + 1);

  const handleLayerAdded = async (newLayer) => {
    addLayer(newLayer);
    await fetchLayers();
    triggerRefresh();
  };

  const handleLayerDelete = async (layerId) => {
    removeLayer(layerId);
    await fetchLayers();
    triggerRefresh();
  };

  const handleLayerToggle = async (layerId, isVisible) => {
    toggleLayerVisibility(layerId);
    await fetchLayers();
    triggerRefresh();
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <span className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-100 text-blue-600">
              <LayersIcon className="h-5 w-5" />
            </span>
            <div>
              <h1 className="text-2xl font-bold">Gestion des Couches</h1>
              <p className="text-sm text-gray-600">
                Importez, visualisez et gérez vos couches géospatiales en temps réel.
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => fetchLayers()}
            className="flex items-center"
          >
            <RefreshCcw className="h-4 w-4 mr-2" />
            Rafraîchir
          </Button>
          <AddGeospatialLayerModalV2
            onLayerAdded={handleLayerAdded}
            trigger={
              <Button className="flex items-center bg-blue-600 hover:bg-blue-700">
                <Upload className="h-4 w-4 mr-2" />
                Importer une couche
              </Button>
            }
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle>Total des couches</CardTitle>
            <CardDescription>Statistiques globales</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{layerStats.total}</div>
            <p className="text-sm text-gray-500 mt-1">
              {layerStats.visible} visibles • {layerStats.hidden} masquées
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle>Visibles</CardTitle>
            <CardDescription>Couches affichées sur la carte</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-3xl font-bold text-green-600">
              <Eye className="h-6 w-6 mr-2" />
              {layerStats.visible}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle>Masquées</CardTitle>
            <CardDescription>Couches en attente d'activation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-3xl font-bold text-gray-500">
              <EyeOff className="h-6 w-6 mr-2" />
              {layerStats.hidden}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Database className="h-5 w-5" />
              <span>Tableau des couches</span>
            </CardTitle>
            <CardDescription>
              Visualisez la totalité des libellés et métadonnées avant validation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LayersManagementTable
              onLayerToggle={handleLayerToggle}
              onLayerDelete={handleLayerDelete}
              onLayerEdit={() => {}}
              selectedLayers={visibleLayers.map((layer) => layer.id)}
              className=""
              refreshTrigger={refreshTrigger}
            />
          </CardContent>
        </Card>
      </div>

      <Separator />
      <Card>
        <CardHeader>
          <CardTitle>Conseils d'utilisation</CardTitle>
          <CardDescription>
            Workflow recommandé pour assurer la cohérence entre la carte et les
            données tabulaires.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-gray-600 space-y-2">
          <p>
            • Importez vos couches via le bouton « Importer une couche » pour les
            rendre immédiatement disponibles dans le tableau et sur la carte.
          </p>
          <p>
            • Utilisez le tableau pour gérer la visibilité et vérifier les métadonnées
            (format, nombre d'éléments, date de création, statut).
          </p>
          <p>
            • Chaque modification de visibilité ou import entraîne une mise à jour
            automatique du rendu cartographique.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default LayersWorkspace;
