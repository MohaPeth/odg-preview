import React, { useState, useEffect, useMemo } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  BarChart3,
  MapPin,
  Layers,
  Shield,
  TrendingUp,
  Building2,
  RefreshCw,
  Database,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { getAnalyticsData } from "../services/analyticsApi";

const CHART_COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#6366f1"];

const AnalyticsWorkspace = () => {
  const [data, setData] = useState({
    summary: null,
    blockchain: null,
    webgis: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");
      const result = await getAnalyticsData();
      setData(result);
    } catch (err) {
      setError(err?.message || "Impossible de charger les données d'analyse");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Données pour les graphiques
  const transactionStatusData = useMemo(() => {
    const b = data.blockchain;
    if (!b?.transactions) return [];
    const { confirmed = 0, pending = 0, total = 0 } = b.transactions;
    const items = [];
    if (confirmed > 0) items.push({ name: "Confirmées", value: confirmed, color: CHART_COLORS[2] });
    if (pending > 0) items.push({ name: "En attente", value: pending, color: CHART_COLORS[4] });
    if (total === 0) items.push({ name: "Aucune", value: 1, color: "#94a3b8" });
    return items;
  }, [data.blockchain]);

  const materialsChartData = useMemo(() => {
    const b = data.blockchain;
    if (!b?.materials?.length) return [];
    return b.materials.map((m, i) => ({
      type: m.type || "N/A",
      transactions: m.transactions ?? 0,
      volume: Number(m.totalQuantity) || 0,
      fill: CHART_COLORS[i % CHART_COLORS.length],
    }));
  }, [data.blockchain]);

  const depositsByTypeData = useMemo(() => {
    const w = data.webgis?.deposits;
    if (!w) return [];
    const { byType = {}, total = 0, active = 0 } = w;
    const items = [
      { name: "Or", count: byType.gold ?? 0, fill: CHART_COLORS[4] },
      { name: "Diamant", count: byType.diamond ?? 0, fill: CHART_COLORS[0] },
      { name: "Total", count: total, fill: CHART_COLORS[1] },
      { name: "Actifs", count: active, fill: CHART_COLORS[2] },
    ].filter((d) => d.count > 0);
    if (items.length === 0) items.push({ name: "Aucun gisement", count: 0, fill: "#94a3b8" });
    return items;
  }, [data.webgis]);

  const companiesChartData = useMemo(() => {
    const w = data.webgis?.companies;
    if (!Array.isArray(w) || w.length === 0) return [];
    return w.slice(0, 8).map((c, i) => ({
      name: (c.name || "Sans nom").slice(0, 12),
      deposits: c.deposits ?? 0,
      fill: CHART_COLORS[i % CHART_COLORS.length],
    }));
  }, [data.webgis]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 p-6">
        <RefreshCw className="h-10 w-10 animate-spin text-blue-600" />
        <p className="text-gray-600">Chargement des analyses...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 sm:p-6">
      {/* En-tête */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <span className="flex items-center justify-center h-10 w-10 rounded-full bg-purple-100 text-purple-600">
            <BarChart3 className="h-5 w-5" />
          </span>
          <div>
            <h1 className="text-2xl font-bold">Analyses et Rapports</h1>
            <p className="text-sm text-gray-600">
              Vue d&apos;ensemble des indicateurs et statistiques de la plateforme
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={fetchData}
          className="inline-flex items-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          <RefreshCw className="h-4 w-4" />
          Actualiser
        </button>
      </div>

      {error && (
        <Card className="border-amber-200 bg-amber-50">
          <CardContent className="p-4 text-amber-800">
            {error}
            <span className="ml-2 text-sm">
              Certaines données peuvent être partielles (mode démo ou backend indisponible).
            </span>
          </CardContent>
        </Card>
      )}

      {/* KPI */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Gisements actifs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.summary?.deposits?.active ?? data.webgis?.deposits?.active ?? 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">Sur la plateforme</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Transactions confirmées
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.summary?.blockchain?.transactions?.confirmed ??
                data.blockchain?.transactions?.confirmed ??
                0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Total : {data.blockchain?.transactions?.total ?? 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Volume tracé
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Number(
                data.summary?.blockchain?.volumes?.total ?? data.blockchain?.totalVolume ?? 0
              ).toLocaleString("fr-FR", { maximumFractionDigits: 0 })}
            </div>
            <p className="text-xs text-gray-500 mt-1">Unité (tous matériaux)</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Layers className="h-4 w-4" />
              Couches actives
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.summary?.geospatial?.activeLayers ?? 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">Géospatiales visibles</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Building2 className="h-4 w-4" />
              Opérateurs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.summary?.operators?.total ?? 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">Enregistrés</p>
          </CardContent>
        </Card>
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Statut des transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Statut des transactions blockchain</CardTitle>
            <CardDescription>Confirmées vs en attente</CardDescription>
          </CardHeader>
          <CardContent>
            {transactionStatusData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={transactionStatusData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {transactionStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[280px] text-gray-500 text-sm">
                Aucune donnée de transaction disponible
              </div>
            )}
          </CardContent>
        </Card>

        {/* Matériaux */}
        <Card>
          <CardHeader>
            <CardTitle>Transactions par type de matériau</CardTitle>
            <CardDescription>Nombre de transactions et volume par matériau</CardDescription>
          </CardHeader>
          <CardContent>
            {materialsChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={materialsChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="transactions" name="Transactions" radius={[4, 4, 0, 0]} fill={CHART_COLORS[0]} />
                  <Bar dataKey="volume" name="Volume" radius={[4, 4, 0, 0]} fill={CHART_COLORS[2]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[280px] text-gray-500 text-sm">
                Aucune donnée de matériau disponible
              </div>
            )}
          </CardContent>
        </Card>

        {/* Gisements par type */}
        <Card>
          <CardHeader>
            <CardTitle>Gisements (WebGIS)</CardTitle>
            <CardDescription>Répartition par type et statut</CardDescription>
          </CardHeader>
          <CardContent>
            {depositsByTypeData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={depositsByTypeData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" name="Nombre" radius={[4, 4, 0, 0]} fill={CHART_COLORS[1]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[280px] text-gray-500 text-sm">
                Aucun gisement enregistré
              </div>
            )}
          </CardContent>
        </Card>

        {/* Entreprises */}
        <Card>
          <CardHeader>
            <CardTitle>Gisements par entreprise</CardTitle>
            <CardDescription>Nombre de gisements par société</CardDescription>
          </CardHeader>
          <CardContent>
            {companiesChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={companiesChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="deposits" name="Gisements" radius={[4, 4, 0, 0]} fill={CHART_COLORS[3]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[280px] text-gray-500 text-sm">
                Aucune donnée entreprise disponible
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Résumé texte */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Synthèse
          </CardTitle>
          <CardDescription>
            Indicateurs clés pour le pilotage de la plateforme ODG
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-gray-600 space-y-2">
          <p>
            • <strong>Gisements actifs</strong> : nombre de dépôts miniers au statut &quot;Actif&quot;.
          </p>
          <p>
            • <strong>Transactions confirmées</strong> : enregistrements blockchain validés ; le volume tracé correspond à la somme des quantités confirmées.
          </p>
          <p>
            • <strong>Couches actives</strong> : couches géospatiales visibles et au statut actif.
          </p>
          <p>
            • Les graphiques ci-dessus sont alimentés par les APIs Dashboard, Blockchain et WebGIS. En mode démo ou sans backend, certaines valeurs peuvent être à zéro.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsWorkspace;
