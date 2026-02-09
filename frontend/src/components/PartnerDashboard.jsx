import React, { useEffect, useMemo, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapContainer, TileLayer, Marker, Popup, LayersControl } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import {
  MapPin,
  TrendingUp,
  Calendar,
  DollarSign,
  BarChart3,
  Eye,
  RefreshCw,
} from "lucide-react";

const PartnerDashboard = ({ userProfile, onLogout }) => {
  const [deposits, setDeposits] = useState([]);
  const [loading, setLoading] = useState(true);

  // Données simulées des gisements avec parts partenaires
  const mockDeposits = [
    {
      id: 1,
      name: "Gisement Aurifère Estuaire Nord",
      coordinates: [0.3901, 9.4536],
      substance: "Or",
      status: "En exploitation",
      partnerShare: 15, // % de parts du partenaire
      estimatedValue: "2.5M €",
      extractionProgress: 35,
      lastUpdate: "2024-11-15",
      monthlyProduction: "125 kg",
      company: "ODG Mining Corp",
    },
    {
      id: 2,
      name: "Mine de Diamant Franceville",
      coordinates: [-1.6331, 13.5833],
      substance: "Diamant",
      status: "En développement",
      partnerShare: 25,
      estimatedValue: "4.8M €",
      extractionProgress: 12,
      lastUpdate: "2024-11-10",
      monthlyProduction: "En attente",
      company: "ODG Mining Corp",
    },
    {
      id: 3,
      name: "Gisement Manganèse Moanda",
      coordinates: [-1.5667, 13.2167],
      substance: "Manganèse",
      status: "En exploitation",
      partnerShare: 8,
      estimatedValue: "1.2M €",
      extractionProgress: 68,
      lastUpdate: "2024-11-12",
      monthlyProduction: "850 tonnes",
      company: "ODG Mining Corp",
    },
  ];

  useEffect(() => {
    // Simulation du chargement des données
    setTimeout(() => {
      setDeposits(mockDeposits);
      setLoading(false);
    }, 1000);
  }, []);

  const totalInvestment = useMemo(() => {
    return deposits.reduce((sum, deposit) => {
      const value = parseFloat(deposit.estimatedValue.replace(/[^\d.]/g, ""));
      return sum + (value * deposit.partnerShare) / 100;
    }, 0);
  }, [deposits]);

  const totalShares = useMemo(() => {
    return deposits.reduce((sum, deposit) => sum + deposit.partnerShare, 0);
  }, [deposits]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin" />
          <span>Chargement de votre portefeuille...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6 bg-gray-50 min-h-screen">
      {/* En-tête partenaire */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Tableau de bord partenaire
            </h1>
            <p className="text-gray-600 mt-1">
              Bienvenue {userProfile?.name || "Partenaire"} - Suivi de vos investissements miniers
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="bg-blue-50 text-blue-700">
              Accès partenaire
            </Badge>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Actualiser
            </Button>
            {onLogout && (
              <Button variant="outline" size="sm" onClick={onLogout}>
                Déconnexion
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Statistiques du portefeuille */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Gisements suivis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{deposits.length}</div>
            <p className="text-xs text-gray-500 mt-1">Projets actifs</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Parts totales
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{totalShares}%</div>
            <p className="text-xs text-gray-500 mt-1">Répartition globale</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Valeur estimée
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {totalInvestment.toFixed(1)}M €
            </div>
            <p className="text-xs text-gray-500 mt-1">Portefeuille total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Dernière MAJ
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">15/11</div>
            <p className="text-xs text-gray-500 mt-1">Données à jour</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Carte des gisements */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="h-5 w-5" />
              <span>Localisation des gisements</span>
            </CardTitle>
            <CardDescription>
              Visualisation géographique de vos investissements
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="h-[400px]">
              <MapContainer
                center={[0, 11.5]}
                zoom={6}
                style={{ height: "100%", width: "100%" }}
              >
                <LayersControl position="topright">
                  <LayersControl.BaseLayer checked name="OpenStreetMap">
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  </LayersControl.BaseLayer>
                  <LayersControl.BaseLayer name="Satellite">
                    <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" />
                  </LayersControl.BaseLayer>
                </LayersControl>

                {deposits.map((deposit) => (
                  <Marker key={deposit.id} position={deposit.coordinates}>
                    <Popup>
                      <div className="space-y-2">
                        <h3 className="font-semibold">{deposit.name}</h3>
                        <p><strong>Substance:</strong> {deposit.substance}</p>
                        <p><strong>Vos parts:</strong> {deposit.partnerShare}%</p>
                        <p><strong>Statut:</strong> {deposit.status}</p>
                        <p><strong>Progression:</strong> {deposit.extractionProgress}%</p>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
          </CardContent>
        </Card>

        {/* Liste détaillée des gisements */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Détail des investissements</span>
            </CardTitle>
            <CardDescription>
              Suivi de la progression et des rendements
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {deposits.map((deposit) => (
              <div
                key={deposit.id}
                className="border rounded-lg p-4 space-y-3 bg-white"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {deposit.name}
                    </h3>
                    <p className="text-sm text-gray-600">{deposit.substance}</p>
                  </div>
                  <Badge
                    variant={deposit.status === "En exploitation" ? "default" : "secondary"}
                  >
                    {deposit.status}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Vos parts:</span>
                    <div className="font-semibold text-blue-600">
                      {deposit.partnerShare}%
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Valeur estimée:</span>
                    <div className="font-semibold text-green-600">
                      {deposit.estimatedValue}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Progression:</span>
                    <div className="font-semibold">
                      {deposit.extractionProgress}%
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Production mensuelle:</span>
                    <div className="font-semibold">
                      {deposit.monthlyProduction}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center space-x-1">
                    <Calendar className="h-3 w-3" />
                    <span>MAJ: {deposit.lastUpdate}</span>
                  </span>
                  <Button variant="ghost" size="sm" className="h-6 px-2">
                    <Eye className="h-3 w-3 mr-1" />
                    Détails
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Informations légales */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <p className="text-sm text-blue-800">
            <strong>Information partenaire:</strong> Les données affichées correspondent à vos parts 
            d'investissement dans les projets miniers ODG. Les valeurs sont estimatives et peuvent 
            évoluer selon les conditions du marché et l'avancement des exploitations.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default PartnerDashboard;
