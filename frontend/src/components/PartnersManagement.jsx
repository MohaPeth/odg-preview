import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Users,
  Search,
  Eye,
  Mail,
  Building2,
  Calendar,
  TrendingUp,
  RefreshCw,
  UserCheck,
  UserX,
  Clock,
  UserPlus,
} from "lucide-react";

import { getUsers, createUser } from "../services/usersApi";
import { fetchOperators } from "../services/operatorsApi";

const PartnersManagement = () => {
  const [partners, setPartners] = useState([]);
  const [operators, setOperators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [selectedPartner, setSelectedPartner] = useState(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newPartner, setNewPartner] = useState({
    name: "",
    email: "",
    status: "active",
    operatorId: "",
  });

  // Charger les partenaires et opérateurs au montage
  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      try {
        setLoading(true);
        setError("");

        const [usersData, operatorsData] = await Promise.all([
          getUsers(),
          fetchOperators(),
        ]);

        if (!isMounted) return;

        // Filtrer uniquement les partenaires
        const partnersOnly = (Array.isArray(usersData) ? usersData : []).filter(
          (user) => user.role === "partner"
        );

        // Mapper les opérateurs par ID pour un accès rapide
        const operatorsMap = {};
        (Array.isArray(operatorsData) ? operatorsData : []).forEach((op) => {
          operatorsMap[op.id] = op;
        });

        // Enrichir les partenaires avec les infos opérateur
        const enrichedPartners = partnersOnly.map((partner) => ({
          ...partner,
          operator: partner.operator_id
            ? operatorsMap[partner.operator_id]
            : null,
        }));

        setPartners(enrichedPartners);
        setOperators(Array.isArray(operatorsData) ? operatorsData : []);
      } catch (err) {
        console.error("Erreur chargement partenaires:", err);
        if (isMounted) {
          setError("Erreur lors du chargement des partenaires");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, []);

  const reloadPartners = async () => {
    try {
      setLoading(true);
      setError("");

      const [usersData, operatorsData] = await Promise.all([
        getUsers(),
        fetchOperators(),
      ]);

      const partnersOnly = (Array.isArray(usersData) ? usersData : []).filter(
        (user) => user.role === "partner"
      );

      const operatorsMap = {};
      (Array.isArray(operatorsData) ? operatorsData : []).forEach((op) => {
        operatorsMap[op.id] = op;
      });

      const enrichedPartners = partnersOnly.map((partner) => ({
        ...partner,
        operator: partner.operator_id ? operatorsMap[partner.operator_id] : null,
      }));

      setPartners(enrichedPartners);
      setOperators(Array.isArray(operatorsData) ? operatorsData : []);
    } catch (err) {
      console.error("Erreur rechargement partenaires:", err);
      setError("Erreur lors du rechargement des partenaires");
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePartner = async () => {
    if (!newPartner.name || !newPartner.email) {
      return;
    }
    try {
      setCreating(true);
      setError("");

      const payload = {
        name: newPartner.name,
        email: newPartner.email,
        role: "partner",
        status: newPartner.status || "active",
      };

      if (newPartner.operatorId) {
        payload.operator_id = parseInt(newPartner.operatorId, 10);
      }

      await createUser(payload);
      await reloadPartners();

      setNewPartner({ name: "", email: "", status: "active", operatorId: "" });
      setIsCreateOpen(false);
    } catch (err) {
      console.error("Erreur création partenaire:", err);
      setError("Erreur lors de la création du partenaire");
    } finally {
      setCreating(false);
    }
  };

  const statusLabels = {
    active: { label: "Actif", color: "bg-green-100 text-green-800", icon: UserCheck },
    pending: { label: "En attente", color: "bg-yellow-100 text-yellow-800", icon: Clock },
    suspended: { label: "Suspendu", color: "bg-red-100 text-red-800", icon: UserX },
  };

  // Filtrage des partenaires
  const filteredPartners = partners.filter((partner) => {
    const name = partner.name || partner.username || "";
    const email = partner.email || "";
    const operatorName = partner.operator?.name || "";

    const matchesSearch =
      name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      operatorName.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || partner.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  // Statistiques
  const stats = {
    total: partners.length,
    active: partners.filter((p) => p.status === "active").length,
    pending: partners.filter((p) => p.status === "pending").length,
    withOperator: partners.filter((p) => p.operator_id).length,
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "—";
    try {
      return new Date(dateStr).toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2 text-gray-600">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <span>Chargement des partenaires...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* En-tête */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <span className="flex items-center justify-center h-10 w-10 rounded-full bg-purple-100 text-purple-600">
            <Users className="h-5 w-5" />
          </span>
          <div>
            <h1 className="text-2xl font-bold">Gestion des Partenaires</h1>
            <p className="text-sm text-gray-600">
              Suivez vos partenaires et leurs investissements
            </p>
          </div>
        </div>
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button className="bg-purple-600 hover:bg-purple-700">
              <UserPlus className="h-4 w-4 mr-2" />
              Créer un partenaire
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Nouveau partenaire</DialogTitle>
              <DialogDescription>
                Créez un compte de type partenaire qui pourra consulter ses investissements.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Nom du partenaire</label>
                  <Input
                    value={newPartner.name}
                    onChange={(e) => setNewPartner({ ...newPartner, name: e.target.value })}
                    placeholder="Nom / Raison sociale"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Email</label>
                  <Input
                    type="email"
                    value={newPartner.email}
                    onChange={(e) => setNewPartner({ ...newPartner, email: e.target.value })}
                    placeholder="contact@partenaire.com"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Statut</label>
                  <Select
                    value={newPartner.status}
                    onValueChange={(value) => setNewPartner({ ...newPartner, status: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Actif</SelectItem>
                      <SelectItem value="pending">En attente</SelectItem>
                      <SelectItem value="suspended">Suspendu</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Opérateur associé (optionnel)</label>
                  <Select
                    value={newPartner.operatorId}
                    onValueChange={(value) => setNewPartner({ ...newPartner, operatorId: value })}
                    disabled={operators.length === 0}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={operators.length === 0 ? "Aucun opérateur" : "Sélectionner"} />
                    </SelectTrigger>
                    <SelectContent>
                      {operators.map((op) => (
                        <SelectItem key={op.id} value={String(op.id)}>
                          {op.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                Annuler
              </Button>
              <Button onClick={handleCreatePartner} disabled={creating || !newPartner.name || !newPartner.email}>
                {creating ? "Création..." : "Créer le partenaire"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-purple-600" />
              <span className="text-sm text-gray-600">Total partenaires</span>
            </div>
            <div className="text-2xl font-bold mt-1">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <UserCheck className="h-4 w-4 text-green-600" />
              <span className="text-sm text-gray-600">Actifs</span>
            </div>
            <div className="text-2xl font-bold mt-1 text-green-600">
              {stats.active}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-yellow-600" />
              <span className="text-sm text-gray-600">En attente</span>
            </div>
            <div className="text-2xl font-bold mt-1 text-yellow-600">
              {stats.pending}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Building2 className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-gray-600">Avec opérateur</span>
            </div>
            <div className="text-2xl font-bold mt-1 text-blue-600">
              {stats.withOperator}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtres */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Rechercher par nom, email ou opérateur..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrer par statut" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les statuts</SelectItem>
                <SelectItem value="active">Actifs</SelectItem>
                <SelectItem value="pending">En attente</SelectItem>
                <SelectItem value="suspended">Suspendus</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Message d'erreur */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4 text-red-700">{error}</CardContent>
        </Card>
      )}

      {/* Liste des partenaires */}
      <Card>
        <CardHeader>
          <CardTitle>Liste des partenaires</CardTitle>
          <CardDescription>
            {filteredPartners.length} partenaire(s) trouvé(s)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredPartners.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {partners.length === 0
                ? "Aucun partenaire enregistré pour le moment."
                : "Aucun partenaire ne correspond à vos critères de recherche."}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Partenaire</TableHead>
                  <TableHead>Opérateur associé</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Inscription</TableHead>
                  <TableHead>Dernière connexion</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredPartners.map((partner) => {
                  const StatusIcon =
                    statusLabels[partner.status]?.icon || Clock;
                  return (
                    <TableRow key={partner.id}>
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <div className="h-9 w-9 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 font-semibold">
                            {(partner.name || partner.username || "P")
                              .charAt(0)
                              .toUpperCase()}
                          </div>
                          <div>
                            <div className="font-medium">
                              {partner.name || partner.username}
                            </div>
                            <div className="text-sm text-gray-500 flex items-center">
                              <Mail className="h-3 w-3 mr-1" />
                              {partner.email}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {partner.operator ? (
                          <div className="flex items-center space-x-2">
                            <Building2 className="h-4 w-4 text-blue-600" />
                            <div>
                              <div className="font-medium text-sm">
                                {partner.operator.name}
                              </div>
                              <div className="text-xs text-gray-500">
                                {partner.operator.country || "—"}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <span className="text-gray-400 text-sm">
                            Non assigné
                          </span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={statusLabels[partner.status]?.color}
                        >
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {statusLabels[partner.status]?.label || partner.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="h-3 w-3 mr-1" />
                          {formatDate(partner.created_at || partner.createdAt)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm text-gray-600">
                          {partner.last_login_at || partner.lastLogin
                            ? formatDate(
                                partner.last_login_at || partner.lastLogin
                              )
                            : "Jamais connecté"}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedPartner(partner)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Dialog détails partenaire */}
      <Dialog
        open={!!selectedPartner}
        onOpenChange={() => setSelectedPartner(null)}
      >
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Détails du partenaire</DialogTitle>
            <DialogDescription>
              Informations complètes sur le partenaire
            </DialogDescription>
          </DialogHeader>
          {selectedPartner && (
            <div className="space-y-4 py-4">
              <div className="flex items-center space-x-4">
                <div className="h-16 w-16 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 text-2xl font-bold">
                  {(selectedPartner.name || selectedPartner.username || "P")
                    .charAt(0)
                    .toUpperCase()}
                </div>
                <div>
                  <h3 className="text-lg font-semibold">
                    {selectedPartner.name || selectedPartner.username}
                  </h3>
                  <p className="text-gray-500">{selectedPartner.email}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <div className="text-sm text-gray-500">Statut</div>
                  <Badge
                    className={statusLabels[selectedPartner.status]?.color}
                  >
                    {statusLabels[selectedPartner.status]?.label ||
                      selectedPartner.status}
                  </Badge>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Rôle</div>
                  <div className="font-medium capitalize">
                    {selectedPartner.role}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Date d'inscription</div>
                  <div className="font-medium">
                    {formatDate(
                      selectedPartner.created_at || selectedPartner.createdAt
                    )}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Dernière connexion</div>
                  <div className="font-medium">
                    {selectedPartner.last_login_at || selectedPartner.lastLogin
                      ? formatDate(
                          selectedPartner.last_login_at ||
                            selectedPartner.lastLogin
                        )
                      : "Jamais"}
                  </div>
                </div>
              </div>

              {selectedPartner.operator && (
                <div className="pt-4 border-t">
                  <div className="text-sm text-gray-500 mb-2">
                    Opérateur associé
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <Building2 className="h-8 w-8 text-blue-600" />
                    <div>
                      <div className="font-semibold">
                        {selectedPartner.operator.name}
                      </div>
                      <div className="text-sm text-gray-600">
                        {selectedPartner.operator.country || "Pays non renseigné"}{" "}
                        • {selectedPartner.operator.status || "Statut inconnu"}
                      </div>
                      {selectedPartner.operator.commodities?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {selectedPartner.operator.commodities.map((c, idx) => (
                            <span
                              key={idx}
                              className="inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700"
                            >
                              {c.label || c.code}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedPartner(null)}>
              Fermer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PartnersManagement;
