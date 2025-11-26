import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  Users,
  UserPlus,
  Edit,
  Trash2,
  Shield,
  Eye,
  MoreHorizontal,
  Search,
  Filter,
} from "lucide-react";

const UserManagement = () => {
  const [users, setUsers] = useState([
    {
      id: 1,
      name: "Jean Dupont",
      email: "j.dupont@odg.ga",
      role: "admin",
      status: "active",
      deposits: ["Gisement Aurifère Estuaire Nord"],
      shares: { "Gisement Aurifère Estuaire Nord": 0 },
      createdAt: "2024-10-15",
      lastLogin: "2024-11-15",
    },
    {
      id: 2,
      name: "Marie Martin",
      email: "m.martin@odg.ga",
      role: "analyst",
      status: "active",
      deposits: [],
      shares: {},
      createdAt: "2024-10-20",
      lastLogin: "2024-11-14",
    },
    {
      id: 3,
      name: "Partenaire Minier SA",
      email: "contact@partenaire-minier.com",
      role: "partner",
      status: "active",
      deposits: ["Gisement Aurifère Estuaire Nord", "Mine de Diamant Franceville"],
      shares: {
        "Gisement Aurifère Estuaire Nord": 15,
        "Mine de Diamant Franceville": 25,
      },
      createdAt: "2024-11-01",
      lastLogin: "2024-11-15",
    },
    {
      id: 4,
      name: "Investisseur International",
      email: "invest@global-mining.com",
      role: "partner",
      status: "pending",
      deposits: ["Gisement Manganèse Moanda"],
      shares: { "Gisement Manganèse Moanda": 8 },
      createdAt: "2024-11-10",
      lastLogin: "Jamais connecté",
    },
  ]);

  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [isAddUserOpen, setIsAddUserOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    role: "partner",
    deposits: [],
    shares: {},
  });

  const availableDeposits = [
    "Gisement Aurifère Estuaire Nord",
    "Mine de Diamant Franceville",
    "Gisement Manganèse Moanda",
  ];

  const roleLabels = {
    admin: { label: "Administrateur", color: "bg-red-100 text-red-800" },
    analyst: { label: "Analyste", color: "bg-blue-100 text-blue-800" },
    operator: { label: "Opérateur", color: "bg-green-100 text-green-800" },
    partner: { label: "Partenaire", color: "bg-purple-100 text-purple-800" },
  };

  const statusLabels = {
    active: { label: "Actif", color: "bg-green-100 text-green-800" },
    pending: { label: "En attente", color: "bg-yellow-100 text-yellow-800" },
    suspended: { label: "Suspendu", color: "bg-red-100 text-red-800" },
  };

  const filteredUsers = users.filter((user) => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === "all" || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const handleAddUser = () => {
    const user = {
      id: Date.now(),
      ...newUser,
      status: "pending",
      createdAt: new Date().toISOString().split("T")[0],
      lastLogin: "Jamais connecté",
    };
    setUsers([...users, user]);
    setNewUser({ name: "", email: "", role: "partner", deposits: [], shares: {} });
    setIsAddUserOpen(false);
  };

  const handleEditUser = (user) => {
    setEditingUser({ ...user });
  };

  const handleSaveEdit = () => {
    setUsers(users.map(u => u.id === editingUser.id ? editingUser : u));
    setEditingUser(null);
  };

  const handleDeleteUser = (userId) => {
    setUsers(users.filter(u => u.id !== userId));
  };

  const handleDepositShareChange = (deposit, share) => {
    if (editingUser) {
      const newShares = { ...editingUser.shares };
      if (share > 0) {
        newShares[deposit] = parseInt(share);
        if (!editingUser.deposits.includes(deposit)) {
          setEditingUser({
            ...editingUser,
            deposits: [...editingUser.deposits, deposit],
            shares: newShares,
          });
        } else {
          setEditingUser({ ...editingUser, shares: newShares });
        }
      } else {
        delete newShares[deposit];
        setEditingUser({
          ...editingUser,
          deposits: editingUser.deposits.filter(d => d !== deposit),
          shares: newShares,
        });
      }
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <span className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-100 text-blue-600">
            <Users className="h-5 w-5" />
          </span>
          <div>
            <h1 className="text-2xl font-bold">Gestion des utilisateurs</h1>
            <p className="text-sm text-gray-600">
              Gérez les accès et les parts des partenaires sur les gisements
            </p>
          </div>
        </div>
        <Dialog open={isAddUserOpen} onOpenChange={setIsAddUserOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <UserPlus className="h-4 w-4 mr-2" />
              Ajouter un utilisateur
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Nouvel utilisateur</DialogTitle>
              <DialogDescription>
                Créez un compte pour un nouveau partenaire ou collaborateur
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Nom complet</Label>
                  <Input
                    id="name"
                    value={newUser.name}
                    onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                    placeholder="Nom de l'utilisateur"
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    placeholder="email@exemple.com"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="role">Rôle</Label>
                <Select value={newUser.role} onValueChange={(value) => setNewUser({ ...newUser, role: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Administrateur</SelectItem>
                    <SelectItem value="analyst">Analyste</SelectItem>
                    <SelectItem value="operator">Opérateur</SelectItem>
                    <SelectItem value="partner">Partenaire</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddUserOpen(false)}>
                Annuler
              </Button>
              <Button onClick={handleAddUser}>Créer l'utilisateur</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-gray-600">Total utilisateurs</span>
            </div>
            <div className="text-2xl font-bold mt-1">{users.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Shield className="h-4 w-4 text-purple-600" />
              <span className="text-sm text-gray-600">Partenaires</span>
            </div>
            <div className="text-2xl font-bold mt-1">
              {users.filter(u => u.role === "partner").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Eye className="h-4 w-4 text-green-600" />
              <span className="text-sm text-gray-600">Actifs</span>
            </div>
            <div className="text-2xl font-bold mt-1">
              {users.filter(u => u.status === "active").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <MoreHorizontal className="h-4 w-4 text-yellow-600" />
              <span className="text-sm text-gray-600">En attente</span>
            </div>
            <div className="text-2xl font-bold mt-1">
              {users.filter(u => u.status === "pending").length}
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
                  placeholder="Rechercher par nom ou email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrer par rôle" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les rôles</SelectItem>
                <SelectItem value="admin">Administrateur</SelectItem>
                <SelectItem value="analyst">Analyste</SelectItem>
                <SelectItem value="operator">Opérateur</SelectItem>
                <SelectItem value="partner">Partenaire</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tableau des utilisateurs */}
      <Card>
        <CardHeader>
          <CardTitle>Liste des utilisateurs</CardTitle>
          <CardDescription>
            Gérez les accès et les parts des utilisateurs sur les gisements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Utilisateur</TableHead>
                <TableHead>Rôle</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Gisements</TableHead>
                <TableHead>Parts totales</TableHead>
                <TableHead>Dernière connexion</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{user.name}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={roleLabels[user.role]?.color}>
                      {roleLabels[user.role]?.label}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={statusLabels[user.status]?.color}>
                      {statusLabels[user.status]?.label}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {user.deposits.length > 0 ? (
                        <span>{user.deposits.length} gisement(s)</span>
                      ) : (
                        <span className="text-gray-400">Aucun</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm font-medium">
                      {Object.values(user.shares).reduce((sum, share) => sum + share, 0)}%
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-gray-600">{user.lastLogin}</div>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditUser(user)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteUser(user.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dialog d'édition */}
      <Dialog open={!!editingUser} onOpenChange={() => setEditingUser(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Modifier l'utilisateur</DialogTitle>
            <DialogDescription>
              Ajustez les informations et les parts sur les gisements
            </DialogDescription>
          </DialogHeader>
          {editingUser && (
            <div className="grid gap-6 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Nom</Label>
                  <Input
                    value={editingUser.name}
                    onChange={(e) => setEditingUser({ ...editingUser, name: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Email</Label>
                  <Input
                    value={editingUser.email}
                    onChange={(e) => setEditingUser({ ...editingUser, email: e.target.value })}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Rôle</Label>
                  <Select 
                    value={editingUser.role} 
                    onValueChange={(value) => setEditingUser({ ...editingUser, role: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Administrateur</SelectItem>
                      <SelectItem value="analyst">Analyste</SelectItem>
                      <SelectItem value="operator">Opérateur</SelectItem>
                      <SelectItem value="partner">Partenaire</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Statut</Label>
                  <Select 
                    value={editingUser.status} 
                    onValueChange={(value) => setEditingUser({ ...editingUser, status: value })}
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
              </div>

              {editingUser.role === "partner" && (
                <div>
                  <Label className="text-base font-medium">Parts sur les gisements</Label>
                  <div className="mt-3 space-y-3">
                    {availableDeposits.map((deposit) => (
                      <div key={deposit} className="flex items-center justify-between p-3 border rounded-lg">
                        <span className="font-medium">{deposit}</span>
                        <div className="flex items-center space-x-2">
                          <Input
                            type="number"
                            min="0"
                            max="100"
                            value={editingUser.shares[deposit] || 0}
                            onChange={(e) => handleDepositShareChange(deposit, e.target.value)}
                            className="w-20"
                          />
                          <span className="text-sm text-gray-500">%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingUser(null)}>
              Annuler
            </Button>
            <Button onClick={handleSaveEdit}>Sauvegarder</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserManagement;
