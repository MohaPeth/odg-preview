import React from "react";
import config from "@/config";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import {
  Settings,
  Database,
  ShieldCheck,
  Server,
  RefreshCw,
  FileText,
  AlertCircle,
  UploadCloud,
  Users,
} from "lucide-react";

const SettingsWorkspace = ({ onNavigateToUsers }) => {
  const mockEnv = [
    { key: "FLASK_ENV", value: "development", description: "Mode d'exécution actuel" },
    { key: "DATABASE_URL", value: "postgresql://odg:***@localhost:5432/odg_dev", description: "Instance de développement" },
    { key: "API_BASE_URL", value: "/api", description: "Préfixe des routes API" },
  ];

  const mockTables = [
    { name: "users", description: "Utilisateurs de la plateforme", status: "SYNC" },
    { name: "geospatial_layers", description: "Couches géospatiales importées", status: "SYNC" },
    { name: "layer_upload_history", description: "Historique des imports de couches", status: "SYNC" },
    { name: "deposits", description: "Gisements miniers référencés", status: "PENDING" },
    { name: "sensor_readings", description: "Capture des capteurs terrain", status: "PLANNED" },
  ];

  // Rôles alignés sur le backend (admin, operator, partner) – données illustratives
  const mockUserRoles = [
    { name: "Admin", count: 2, permissions: "Gestion complète" },
    { name: "Operator", count: 6, permissions: "Ajout de couches / gisements" },
    { name: "Partner", count: 4, permissions: "Lecture seule" },
  ];

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6">
      <p className="text-xs text-gray-500 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
        Données illustratives : les blocs Environnement, Base de données et Rôles ne sont pas connectés à l&apos;API.
      </p>
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <span className="flex items-center justify-center h-12 w-12 rounded-full bg-slate-100 text-slate-700">
            <Settings className="h-6 w-6" />
          </span>
          <div>
            <h1 className="text-2xl font-bold">Paramètres de la plateforme</h1>
            <p className="text-sm text-gray-600">
              Configurez l'environnement, la base de données et les accès utilisateurs avant la mise en production.
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="flex items-center">
            <FileText className="h-4 w-4 mr-2" />
            Exporter la configuration
          </Button>
          <Button className="bg-blue-600 hover:bg-blue-700 flex items-center">
            <UploadCloud className="h-4 w-4 mr-2" />
            Publier vers la recette
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Server className="h-5 w-5" />
              <span>Environnement</span>
            </CardTitle>
            <CardDescription>Résumé d'exécution actuel</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Mode</span>
              <Badge variant="outline">{config.appEnv}</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>API</span>
              <span className="font-mono text-xs">{config.apiBaseUrl}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Front</span>
              <span className="font-mono text-xs">{window.location.origin}</span>
            </div>
            <Separator className="my-3" />
            <div className="flex items-center justify-between text-sm">
              <span>Mode maintenance</span>
              <Switch defaultChecked={false} disabled />
            </div>
            <p className="text-xs text-gray-500">
              Activez le mode maintenance avant une mise à jour critique pour bloquer l'accès utilisateur.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <ShieldCheck className="h-5 w-5" />
              <span>Sécurité & audits</span>
            </CardTitle>
            <CardDescription>État des contrôles clés</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span>HTTPS activé</span>
              <Badge variant="outline" className="bg-green-50 text-green-600 border-green-200">OK</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Journalisation des accès</span>
              <Badge variant="outline" className="bg-yellow-50 text-yellow-600 border-yellow-200">À configurer</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Backup base de données</span>
              <Badge variant="outline" className="bg-red-50 text-red-600 border-red-200">Absent</Badge>
            </div>
            <Separator className="my-2" />
            <Button variant="outline" size="sm" className="w-full flex items-center justify-center">
              <RefreshCw className="h-4 w-4 mr-2" />
              Lancer un audit rapide
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5" />
              <span>Rôles & accès</span>
            </CardTitle>
            <CardDescription>Répartition des profils actifs</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockUserRoles.map((role) => (
              <div key={role.name} className="flex items-start justify-between text-sm">
                <div>
                  <p className="font-medium text-gray-900">{role.name}</p>
                  <p className="text-xs text-gray-500">{role.permissions}</p>
                </div>
                <Badge variant="secondary">{role.count} utilisateurs</Badge>
              </div>
            ))}
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full"
              onClick={() => onNavigateToUsers?.()}
            >
              Gérer les utilisateurs
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>Base de données & tables</span>
          </CardTitle>
          <CardDescription>
            Suivi des structures clés (PostgreSQL + PostGIS) et état des migrations.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mockTables.map((table) => (
              <div
                key={table.name}
                className="border rounded-lg p-4 space-y-2 bg-slate-50"
              >
                <div className="flex items-center justify-between">
                  <p className="font-semibold text-gray-900">{table.name}</p>
                  <Badge
                    variant={table.status === "SYNC" ? "secondary" : "outline"}
                    className={
                      table.status === "SYNC"
                        ? "bg-green-100 text-green-700"
                        : table.status === "PENDING"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-slate-200 text-slate-600"
                    }
                  >
                    {table.status}
                  </Badge>
                </div>
                <p className="text-xs text-gray-600">{table.description}</p>
              </div>
            ))}
          </div>
          <Button variant="outline" className="flex items-center">
            <RefreshCw className="h-4 w-4 mr-2" />
            Vérifier les migrations appliquées
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Variables d'environnement critiques</CardTitle>
          <CardDescription>Vérifiez que les valeurs sensibles sont définies avant la production.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {mockEnv.map((item) => (
            <div key={item.key} className="border rounded-lg p-3 bg-white">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-gray-800">{item.key}</span>
                <Badge variant="outline">{item.value}</Badge>
              </div>
              <p className="text-xs text-gray-500 mt-1">{item.description}</p>
            </div>
          ))}
          <Button variant="outline" size="sm" className="flex items-center">
            <FileText className="h-4 w-4 mr-2" />
            Télécharger le .env exemple
          </Button>
        </CardContent>
      </Card>

      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="h-5 w-5" />
            <span>Checklist avant production</span>
          </CardTitle>
          <CardDescription className="text-red-600">
            Points critiques à valider avant la mise en ligne officielle.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-red-700 space-y-2">
          <p>• Configurer les sauvegardes automatiques PostgreSQL et vérifier les restaurations.</p>
          <p>• Activer l'envoi de logs applicatifs (API & frontend) vers un stockage centralisé.</p>
          <p>• Réaliser un test de charge sur l'import massif de couches (SHP + GeoJSON).</p>
          <p>• Configurer le monitoring des capteurs pour le tableau `sensor_readings`.</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsWorkspace;
