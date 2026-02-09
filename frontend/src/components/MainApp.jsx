import React, { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Map, Shield, Home, BarChart3, Settings, Menu, X, ChevronLeft, ChevronRight, Layers, Users, Handshake, Building2, UserCheck, Clock } from "lucide-react";
import { fetchOperators } from "../services/operatorsApi";
import { getUsers } from "../services/usersApi";
import WebGISMap from "./WebGISMap";
import BlockchainDashboard from "./BlockchainDashboard";
import LayersWorkspace from "./LayersWorkspace";
import AnalyticsWorkspace from "./AnalyticsWorkspace";
import SettingsWorkspace from "./SettingsWorkspace";
import UserManagement from "./UserManagement";
import PartnersManagement from "./PartnersManagement";

const MainApp = ({ userProfile, onLogout }) => {
  const [activeTab, setActiveTab] = useState("home");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Données opérateurs pour l'onboarding
  const [operators, setOperators] = useState([]);
  const [operatorsLoading, setOperatorsLoading] = useState(true);
  const [operatorsError, setOperatorsError] = useState("");

  // Données partenaires pour l'onboarding
  const [partners, setPartners] = useState([]);
  const [partnersLoading, setPartnersLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadOperators = async () => {
      try {
        setOperatorsLoading(true);
        setOperatorsError("");
        const data = await fetchOperators();
        if (isMounted) {
          setOperators(data);
        }
      } catch (error) {
        if (isMounted) {
          console.error("Erreur chargement opérateurs:", error);
          setOperatorsError(error.message || "Erreur lors du chargement des opérateurs");
        }
      } finally {
        if (isMounted) {
          setOperatorsLoading(false);
        }
      }
    };

    const loadPartners = async () => {
      try {
        setPartnersLoading(true);
        const usersData = await getUsers();
        if (isMounted) {
          // Filtrer uniquement les partenaires
          const partnersOnly = (Array.isArray(usersData) ? usersData : []).filter(
            (user) => user.role === "partner"
          );
          setPartners(partnersOnly);
        }
      } catch (error) {
        if (isMounted) {
          console.error("Erreur chargement partenaires:", error);
        }
      } finally {
        if (isMounted) {
          setPartnersLoading(false);
        }
      }
    };

    loadOperators();
    loadPartners();

    return () => {
      isMounted = false;
    };
  }, []);

  const navigation = [
    { id: "home", name: "Accueil", icon: Home },
    { id: "webgis", name: "Géoportail", icon: Map },
    { id: "layers", name: "Couches", icon: Layers },
    { id: "blockchain", name: "Blockchain", icon: Shield },
    { id: "analytics", name: "Analyses", icon: BarChart3 },
    { id: "partners", name: "Partenaires", icon: Handshake },
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

      {/* Opérateurs - aperçu onboarding */}
      <Card>
        <CardHeader>
          <CardTitle>Opérateurs miniers</CardTitle>
        </CardHeader>
        <CardContent>
          {operatorsLoading ? (
            <div className="text-sm text-gray-600">Chargement des opérateurs...</div>
          ) : operatorsError ? (
            <div className="text-sm text-red-600">{operatorsError}</div>
          ) : operators.length === 0 ? (
            <div className="text-sm text-gray-600">
              Aucun opérateur n'est encore configuré. Vous pourrez en ajouter dès que la base sera alimentée.
            </div>
          ) : (
            <div className="space-y-3">
              {operators.slice(0, 3).map((op) => (
                <div key={op.id} className="flex items-center justify-between border rounded-md px-3 py-2">
                  <div className="flex items-center space-x-3">
                    {op.logoUrl ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={op.logoUrl}
                        alt={op.name}
                        className="h-8 w-8 rounded-full object-cover"
                      />
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-xs font-semibold text-blue-600">
                        {op.name?.charAt(0) || "O"}
                      </div>
                    )}
                    <div>
                      <div className="text-sm font-semibold text-gray-900">{op.name}</div>
                      <div className="text-xs text-gray-500">
                        {op.country || "Pays non renseigné"}  b7 {op.status || "Statut inconnu"}
                      </div>
                      {op.commodities && op.commodities.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {op.commodities.slice(0, 3).map((c, idx) => (
                            <span
                              key={idx}
                              className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-medium text-blue-700"
                            >
                              {c.label || c.code}
                            </span>
                          ))}
                          {op.commodities.length > 3 && (
                            <span className="text-[10px] text-gray-500">+{op.commodities.length - 3} autres</span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">Permis</div>
                    <div className="text-sm font-semibold text-gray-900">{op.permitsCount ?? 0}</div>
                  </div>
                </div>
              ))}
              {operators.length > 3 && (
                <div className="text-xs text-gray-500">
                  Et {operators.length - 3} autres opérateurs configurés.
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Section Partenaires - Résumé */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Handshake className="h-5 w-5 text-purple-600" />
            <span>Partenaires</span>
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setActiveTab("partners")}
          >
            Voir tout
          </Button>
        </CardHeader>
        <CardContent>
          {partnersLoading ? (
            <div className="text-sm text-gray-600">Chargement des partenaires...</div>
          ) : partners.length === 0 ? (
            <div className="text-sm text-gray-600">
              Aucun partenaire enregistré pour le moment.
            </div>
          ) : (
            <div className="space-y-4">
              {/* Stats rapides partenaires */}
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{partners.length}</div>
                  <div className="text-xs text-gray-600">Total</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {partners.filter(p => p.status === "active").length}
                  </div>
                  <div className="text-xs text-gray-600">Actifs</div>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {partners.filter(p => p.status === "pending").length}
                  </div>
                  <div className="text-xs text-gray-600">En attente</div>
                </div>
              </div>

              {/* Liste des 3 derniers partenaires */}
              <div className="space-y-2">
                {partners.slice(0, 3).map((partner) => (
                  <div
                    key={partner.id}
                    className="flex items-center justify-between border rounded-md px-3 py-2 hover:bg-gray-50"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center text-sm font-semibold text-purple-600">
                        {(partner.name || partner.username || "P").charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="text-sm font-medium">{partner.name || partner.username}</div>
                        <div className="text-xs text-gray-500">{partner.email}</div>
                      </div>
                    </div>
                    <Badge
                      className={
                        partner.status === "active"
                          ? "bg-green-100 text-green-800"
                          : partner.status === "pending"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-gray-100 text-gray-800"
                      }
                    >
                      {partner.status === "active" && <UserCheck className="h-3 w-3 mr-1" />}
                      {partner.status === "pending" && <Clock className="h-3 w-3 mr-1" />}
                      {partner.status === "active" ? "Actif" : partner.status === "pending" ? "En attente" : partner.status}
                    </Badge>
                  </div>
                ))}
                {partners.length > 3 && (
                  <div className="text-xs text-gray-500 text-center pt-2">
                    Et {partners.length - 3} autre(s) partenaire(s)
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Statistiques globales (à connecter aux données réelles) */}
      <Card>
        <CardHeader>
          <CardTitle>Statistiques globales</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">
            Les indicateurs chiffrés (gisements actifs, transactions confirmées, volumes tracés,
            taux de transparence, etc.) seront connectés prochainement aux données réelles de la
            base et de la blockchain. Cette section sert pour l’instant de placeholder.
          </p>
        </CardContent>
      </Card>

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

          <div className="flex items-center justify-between flex-1">
            <span className="text-sm text-gray-600">
              {navigation.find((item) => item.id === activeTab)?.name}
            </span>
            <div className="flex items-center gap-2">
              {userProfile && (
                <span className="text-sm text-gray-700 hidden sm:inline" title={userProfile.email}>
                  {userProfile.name || userProfile.email}
                </span>
              )}
              {onLogout && (
                <Button variant="outline" size="sm" onClick={onLogout}>
                  Déconnexion
                </Button>
              )}
            </div>
          </div>
        </header>

        {/* Contenu – padding responsif */}
        <main className="flex-1 overflow-auto overflow-x-hidden">
          {activeTab === "home" && (
            <div className="p-4 sm:p-6">
              <HomeContent />
            </div>
          )}
          {activeTab === "webgis" && <WebGISMap />}
          {activeTab === "layers" && <LayersWorkspace />}
          {activeTab === "blockchain" && <BlockchainDashboard />}
          {activeTab === "analytics" && <AnalyticsWorkspace />}
          {activeTab === "users" && <UserManagement />}
          {activeTab === "partners" && <PartnersManagement />}
          {activeTab === "settings" && <SettingsWorkspace onNavigateToUsers={() => setActiveTab("users")} />}
        </main>
      </div>
    </div>
  );
};

export default MainApp;
