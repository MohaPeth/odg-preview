import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Map, Shield, Home, BarChart3, Settings, Menu, X, ChevronLeft, ChevronRight, Layers, Users } from "lucide-react";
import WebGISMap from "./WebGISMap";
import BlockchainDashboard from "./BlockchainDashboard";
import LayersWorkspace from "./LayersWorkspace";
import SettingsWorkspace from "./SettingsWorkspace";
import UserManagement from "./UserManagement";

const MainApp = () => {
  const [activeTab, setActiveTab] = useState("home");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const navigation = [
    { id: "home", name: "Accueil", icon: Home },
    { id: "webgis", name: "Géoportail", icon: Map },
    { id: "layers", name: "Couches", icon: Layers },
    { id: "blockchain", name: "Blockchain", icon: Shield },
    { id: "analytics", name: "Analyses", icon: BarChart3 },
    { id: "users", name: "Utilisateurs", icon: Users },
    { id: "settings", name: "Paramètres", icon: Settings },
  ];

  const HomeContent = () => (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8">
        <h1 className="text-4xl font-bold mb-4">
          Plateforme ODG - Ogooué Digital Gold
        </h1>
        <p className="text-xl mb-6">
          Système intégré de géoportail WebGIS et de traçabilité blockchain pour
          l'industrie minière gabonaise
        </p>
        <div className="flex space-x-4">
          <Button
            onClick={() => setActiveTab("webgis")}
            className="bg-white text-blue-600 hover:bg-gray-100"
          >
            <Map className="mr-2 h-4 w-4" />
            Explorer le Géoportail
          </Button>
          <Button
            onClick={() => setActiveTab("blockchain")}
            variant="outline"
            className="border-white  hover:bg-white text-blue-600 hover:text-blue-600"
          >
            <Shield className="mr-2 h-4 w-4" />
            Voir la Blockchain
          </Button>
        </div>
      </div>

      {/* Fonctionnalités principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card
          className="hover:shadow-lg transition-shadow cursor-pointer"
          onClick={() => setActiveTab("webgis")}
        >
          <CardHeader>
            <CardTitle className="flex items-center">
              <Map className="mr-2 h-5 w-5 text-blue-600" />
              Géoportail WebGIS
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Visualisez les gisements miniers, zones d'exploitation et
              infrastructures du Gabon sur une carte interactive.
            </p>
            <ul className="text-sm text-gray-500 space-y-1">
              <li>• Cartographie des gisements d'or et de diamant</li>
              <li>• Zones d'exploitation en temps réel</li>
              <li>• Infrastructure minière</li>
              <li>• Recherche et filtrage avancés</li>
            </ul>
          </CardContent>
        </Card>

        <Card
          className="hover:shadow-lg transition-shadow cursor-pointer"
          onClick={() => setActiveTab("blockchain")}
        >
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="mr-2 h-5 w-5 text-green-600" />
              Traçabilité Blockchain
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Suivez la chaîne d'approvisionnement des matériaux miniers avec
              une transparence totale.
            </p>
            <ul className="text-sm text-gray-500 space-y-1">
              <li>• Transactions sécurisées et immuables</li>
              <li>• Certificats de traçabilité</li>
              <li>• Chaîne d'approvisionnement complète</li>
              <li>• Vérification en temps réel</li>
            </ul>
          </CardContent>
        </Card>

        <Card
          className="hover:shadow-lg transition-shadow cursor-pointer"
          onClick={() => setActiveTab("analytics")}
        >
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="mr-2 h-5 w-5 text-purple-600" />
              Analyses & Rapports
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Analysez les données minières et générez des rapports détaillés
              pour la prise de décision.
            </p>
            <ul className="text-sm text-gray-500 space-y-1">
              <li>• Tableaux de bord interactifs</li>
              <li>• Rapports de production</li>
              <li>• Analyses environnementales</li>
              <li>• Exportation de données</li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Statistiques rapides */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-blue-600 mb-2">3</div>
            <div className="text-sm text-gray-600">Gisements Actifs</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-green-600 mb-2">2</div>
            <div className="text-sm text-gray-600">Transactions Confirmées</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-purple-600 mb-2">
              15.7 kg
            </div>
            <div className="text-sm text-gray-600">Or Tracé</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-2xl font-bold text-orange-600 mb-2">100%</div>
            <div className="text-sm text-gray-600">Transparence</div>
          </CardContent>
        </Card>
      </div>

      {/* À propos d'ODG */}
      <Card>
        <CardHeader>
          <CardTitle>À propos d'Ogooué Digital Gold</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 leading-relaxed">
            ODG est une entreprise gabonaise spécialisée dans le marketing
            minier, le développement de projets géologiques et la digitalisation
            des activités minières. Notre plateforme intègre des technologies
            avancées comme le WebGIS et la Blockchain pour répondre aux enjeux
            de visibilité, de traçabilité, de transparence et de valorisation
            des projets numériques dans le secteur minier du Gabon.
          </p>
        </CardContent>
      </Card>
    </div>
  );

  const AnalyticsContent = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Analyses et Rapports</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Fonctionnalité en Développement</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">
              Les modules d'analyse avancée et de génération de rapports sont en
              cours de développement. Cette section permettra de visualiser des
              statistiques détaillées, des tendances de production et des
              analyses environnementales.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Prochaines Fonctionnalités</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-gray-600">
              <li>• Rapports de production automatisés</li>
              <li>• Analyses d'impact environnemental</li>
              <li>• Prévisions de rendement</li>
              <li>• Tableaux de bord personnalisables</li>
              <li>• Exportation multi-formats</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } ${
          sidebarCollapsed ? "lg:w-16" : "lg:w-64"
        } fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-all duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
      >
        <div className="flex items-center justify-between h-16 px-4 sm:px-6 border-b">
          <h1 className={`text-lg sm:text-xl font-bold text-gray-900 ${sidebarCollapsed ? 'lg:hidden' : ''}`}>
            ODG Platform
          </h1>
          
          <div className="flex items-center space-x-2">
            {/* Bouton collapse desktop */}
            <Button
              variant="ghost"
              size="sm"
              className="hidden lg:flex"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            >
              {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </Button>
            
            {/* Bouton fermer mobile */}
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <nav className="mt-6">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  setSidebarOpen(false);
                }}
                className={`w-full flex items-center px-4 sm:px-6 py-3 text-left hover:bg-gray-50 transition-colors ${
                  activeTab === item.id
                    ? "bg-blue-50 text-blue-600 border-r-2 border-blue-600"
                    : "text-gray-700"
                } ${sidebarCollapsed ? 'lg:justify-center lg:px-2' : ''}`}
                title={sidebarCollapsed ? item.name : ''}
              >
                <Icon className={`h-5 w-5 ${sidebarCollapsed ? 'lg:mr-0' : 'mr-3'}`} />
                <span className={sidebarCollapsed ? 'lg:hidden' : ''}>{item.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Overlay pour mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Contenu principal */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b h-16 flex items-center justify-between px-4 sm:px-6">
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-4 w-4" />
          </Button>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {navigation.find((item) => item.id === activeTab)?.name}
            </span>
          </div>
        </header>

        {/* Contenu */}
        <main className="flex-1 overflow-auto">
          {activeTab === "home" && (
            <div className="p-6">
              <HomeContent />
            </div>
          )}
          {activeTab === "webgis" && <WebGISMap />}
          {activeTab === "layers" && <LayersWorkspace />}
          {activeTab === "blockchain" && <BlockchainDashboard />}
          {activeTab === "analytics" && (
            <div className="p-6">
              <AnalyticsContent />
            </div>
          )}
          {activeTab === "users" && <UserManagement />}
          {activeTab === "settings" && <SettingsWorkspace />}
        </main>
      </div>
    </div>
  );
};

export default MainApp;
