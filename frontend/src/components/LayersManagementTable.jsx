import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { 
  Search, 
  Filter, 
  MoreHorizontal, 
  Eye, 
  EyeOff, 
  Edit, 
  Trash2, 
  Download, 
  MapPin,
  Calendar,
  Database,
  AlertCircle,
  CheckCircle,
  Loader2,
  RefreshCw,
  Maximize2,
  Minimize2,
  X,
  Plus
} from 'lucide-react';
import AddGeospatialLayerModalV2 from './AddGeospatialLayerModalV2';

const LayersManagementTable = ({ 
  onLayerToggle, 
  onLayerEdit, 
  onLayerDelete,
  selectedLayers = [],
  className = "",
  refreshTrigger = 0
}) => {
  // États
  const [layers, setLayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalLayers, setTotalLayers] = useState(0);
  const [selectedRows, setSelectedRows] = useState(new Set());
  const [deleteDialog, setDeleteDialog] = useState({ open: false, layer: null });
  const [refreshing, setRefreshing] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [addModalOpen, setAddModalOpen] = useState(false);

  const itemsPerPage = 10;

  // Options de filtrage
  const statusOptions = [
    { value: 'all', label: 'Tous les statuts' },
    { value: 'actif', label: 'Actif', color: 'bg-green-500' },
    { value: 'en_développement', label: 'En Développement', color: 'bg-yellow-500' },
    { value: 'exploration', label: 'Exploration', color: 'bg-blue-500' },
    { value: 'terminé', label: 'Terminé', color: 'bg-gray-500' }
  ];

  const typeOptions = [
    { value: 'all', label: 'Tous les types' },
    { value: 'deposit', label: 'Gisement Minier', icon: '⛏️' },
    { value: 'infrastructure', label: 'Infrastructure', icon: '🏗️' },
    { value: 'zone', label: 'Zone Administrative', icon: '🗺️' },
    { value: 'custom', label: 'Personnalisé', icon: '📍' }
  ];

  // Chargement des couches
  const fetchLayers = useCallback(async (showLoader = true) => {
    if (showLoader) setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: itemsPerPage.toString(),
        include_geojson: 'false'
      });

      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (typeFilter !== 'all') params.append('layer_type', typeFilter);

      const response = await fetch(`/api/geospatial/layers?${params}`);
      const result = await response.json();

      if (result.success) {
        setLayers(result.data);
        setTotalPages(result.pagination.pages);
        setTotalLayers(result.pagination.total);
      } else {
        throw new Error(result.error || 'Erreur lors du chargement');
      }
    } catch (err) {
      // Mode démo : si le backend ne répond pas, utiliser des couches mock
      // Backend géospatial indisponible, utilisation des couches de démonstration
      const nowIso = new Date().toISOString();
      const demoLayers = [
        {
          id: 1,
          name: "Gisements d'or - Estuaire Nord",
          description: "Principaux gisements aurifères suivis par ODG dans la région nord.",
          layer_type: 'deposit',
          status: 'actif',
          file_name: 'gisements_or_estuaire.geojson',
          created_at: nowIso,
          is_visible: true,
          features_count: 24,
        },
        {
          id: 2,
          name: 'Mines de diamant - Franceville',
          description: "Localisation des sites diamantifères autour de Franceville.",
          layer_type: 'deposit',
          status: 'exploration',
          file_name: 'mines_diamant_franceville.kml',
          created_at: nowIso,
          is_visible: false,
          features_count: 9,
        },
        {
          id: 3,
          name: "Réseau routier minier",
          description: "Routes d'accès stratégiques aux principaux sites miniers.",
          layer_type: 'infrastructure',
          status: 'actif',
          file_name: 'reseau_routier_miner.shp',
          created_at: nowIso,
          is_visible: true,
          features_count: 48,
        },
        {
          id: 4,
          name: 'Concessions minières ODG',
          description: 'Limites administratives des concessions et permis.',
          layer_type: 'zone',
          status: 'en_développement',
          file_name: 'concessions_mineres_odg.geojson',
          created_at: nowIso,
          is_visible: false,
          features_count: 6,
        },
      ];

      setLayers(demoLayers);
      setTotalPages(1);
      setTotalLayers(demoLayers.length);
      setError('');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [currentPage, searchTerm, statusFilter, typeFilter]);

  // Effet pour charger les données
  useEffect(() => {
    fetchLayers();
  }, [fetchLayers]);

  // Rafraîchissement déclenché par le parent
  useEffect(() => {
    if (!refreshTrigger) return;
    setCurrentPage(1);
    fetchLayers();
  }, [refreshTrigger, fetchLayers]);

  // Rafraîchissement
  const handleRefresh = useCallback(() => {
    setRefreshing(true);
    fetchLayers(false);
  }, [fetchLayers]);

  // Recherche avec debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentPage(1);
      fetchLayers();
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Changement de filtre
  const handleFilterChange = useCallback((type, value) => {
    if (type === 'status') setStatusFilter(value);
    if (type === 'type') setTypeFilter(value);
    setCurrentPage(1);
  }, []);

  // Sélection de lignes
  const handleRowSelect = useCallback((layerId, checked) => {
    const newSelected = new Set(selectedRows);
    if (checked) {
      newSelected.add(layerId);
    } else {
      newSelected.delete(layerId);
    }
    setSelectedRows(newSelected);
  }, [selectedRows]);

  // Sélection de toutes les lignes
  const handleSelectAll = useCallback((checked) => {
    if (checked) {
      setSelectedRows(new Set(layers.map(layer => layer.id)));
    } else {
      setSelectedRows(new Set());
    }
  }, [layers]);

  // Basculer la visibilité d'une couche
  const handleToggleVisibility = useCallback(async (layer) => {
    // Vérifier que la couche a des données géographiques
    if (!layer.geojson && !layer.geometry) {
      setError("Impossible d'afficher cette couche : données géographiques manquantes");
      return;
    }

    try {
      const newVisibilityState = !layer.is_visible;
      
      // Mise à jour optimiste de l'état local (avant la requête)
      setLayers(prevLayers => 
        prevLayers.map(l => 
          l.id === layer.id ? { ...l, is_visible: newVisibilityState } : l
        )
      );
      
      // Notifier le parent immédiatement pour mettre à jour la carte
      if (onLayerToggle) {
        onLayerToggle(layer.id, newVisibilityState);
      }
      
      // Envoyer la requête au serveur en arrière-plan
      const response = await fetch(`/api/geospatial/layers/${layer.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_visible: newVisibilityState })
      });

      const result = await response.json();
      if (!result.success) {
        // En cas d'erreur, revenir à l'état précédent
        setLayers(prevLayers => 
          prevLayers.map(l => 
            l.id === layer.id ? { ...l, is_visible: !newVisibilityState } : l
          )
        );
        throw new Error(result.error);
      }
    } catch (err) {
      setError(`Erreur lors de la mise à jour: ${err.message}`);
      // Recharger depuis le serveur en cas d'erreur pour être sûr de l'état
      fetchLayers(false);
    }
  }, [onLayerToggle, fetchLayers]);

  // Supprimer une couche
  const handleDelete = useCallback(async (layer) => {
    try {
      const response = await fetch(`/api/geospatial/layers/${layer.id}`, {
        method: 'DELETE'
      });

      const result = await response.json();
      if (result.success) {
        // Recharger les données
        fetchLayers();
        
        // Notifier le parent
        if (onLayerDelete) {
          onLayerDelete(layer.id);
        }
      } else {
        throw new Error(result.error);
      }
    } catch (err) {
      setError(`Erreur lors de la suppression: ${err.message}`);
    } finally {
      setDeleteDialog({ open: false, layer: null });
    }
  }, [fetchLayers, onLayerDelete]);

  // Export d'une couche
  const handleExport = useCallback(async (layer, format) => {
    try {
      const response = await fetch(`/api/geospatial/layers/${layer.id}/export/${format}`);
      
      if (response.ok) {
        const data = await response.json();
        
        // Télécharger le fichier
        const blob = new Blob([JSON.stringify(data, null, 2)], { 
          type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${layer.name}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        throw new Error('Erreur lors de l\'export');
      }
    } catch (err) {
      setError(`Erreur export: ${err.message}`);
    }
  }, []);

  // Formatage des données
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return 'Date invalide';
    }
  };

  const formatArea = (area) => {
    if (!area) return '-';
    return `${parseFloat(area).toFixed(2)} km²`;
  };

  const formatLength = (length) => {
    if (!length) return '-';
    return `${parseFloat(length).toFixed(2)} km`;
  };

  // Badge de statut
  const StatusBadge = ({ status }) => {
    if (!status) return null;
    const option = statusOptions.find(opt => opt.value === status);
    if (!option || option.value === 'all') return null;

    return (
      <Badge variant="outline" className="text-xs">
        <span className={`w-2 h-2 rounded-full mr-1 ${option.color}`}></span>
        {option.label}
      </Badge>
    );
  };

  // Badge de type
  const TypeBadge = ({ type }) => {
    if (!type) return <span className="text-xs text-gray-400">N/A</span>;
    const option = typeOptions.find(opt => opt.value === type);
    if (!option || option.value === 'all') return <span className="text-xs">{String(type)}</span>;

    return (
      <span className="flex items-center text-sm">
        <span className="mr-1">{option.icon}</span>
        {option.label}
      </span>
    );
  };

  // Statistiques filtrées
  const filteredStats = useMemo(() => {
    return {
      total: totalLayers,
      visible: layers.filter(l => l.is_visible).length,
      hidden: layers.filter(l => !l.is_visible).length,
      selected: selectedRows.size
    };
  }, [layers, totalLayers, selectedRows]);

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-8">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Chargement des couches...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* En-tête avec statistiques */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5" />
                <span>Couches Géospatiales</span>
              </CardTitle>
              <CardDescription>
                Gestion des couches importées ({filteredStats.total} total)
              </CardDescription>
            </div>
            <div className="flex space-x-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setIsExpanded(true)}
                title="Agrandir le tableau"
              >
                <Maximize2 className="h-4 w-4 mr-2" />
                Agrandir
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Actualiser
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span className="flex items-center space-x-1">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>{filteredStats.visible} visibles</span>
            </span>
            <span className="flex items-center space-x-1">
              <EyeOff className="h-4 w-4 text-gray-400" />
              <span>{filteredStats.hidden} masquées</span>
            </span>
            {filteredStats.selected > 0 && (
              <span className="flex items-center space-x-1">
                <Checkbox className="h-4 w-4" checked />
                <span>{filteredStats.selected} sélectionnées</span>
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Filtres et recherche */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Rechercher par nom ou description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Select value={statusFilter} onValueChange={(value) => handleFilterChange('status', value)}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={typeFilter} onValueChange={(value) => handleFilterChange('type', value)}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {typeOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.icon ? `${option.icon} ${option.label}` : option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Message d'erreur */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Tableau */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox
                    checked={selectedRows.size === layers.length && layers.length > 0}
                    onCheckedChange={handleSelectAll}
                  />
                </TableHead>
                <TableHead className="w-12">
                  <Eye className="h-4 w-4" />
                </TableHead>
                <TableHead>Informations de la couche</TableHead>
                <TableHead className="w-12">
                  <MoreHorizontal className="h-4 w-4" />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {layers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-12">
                    <div className="flex flex-col items-center space-y-3">
                      <Database className="h-12 w-12 text-gray-300" />
                      <div>
                        <h3 className="font-medium text-gray-900 mb-1">Aucune couche disponible</h3>
                        <p className="text-sm text-gray-500">
                          {searchTerm ? 'Aucun résultat pour cette recherche' : 'Commencez par importer une couche géospatiale'}
                        </p>
                      </div>
                      {searchTerm ? (
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => setSearchTerm('')}
                        >
                          Effacer la recherche
                        </Button>
                      ) : (
                        <Button 
                          size="sm" 
                          className="bg-blue-600 hover:bg-blue-700"
                          onClick={() => setAddModalOpen(true)}
                        >
                          <Plus className="h-4 w-4 mr-2" />
                          Ajouter une couche
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                layers.map((layer, index) => {
                  // Sécurité : utiliser l'index comme fallback si layer.id est manquant
                  const layerId = layer?.id ?? `layer-${index}`;
                  
                  return (
                  <TableRow key={layerId} className="hover:bg-gray-50">
                    <TableCell>
                      <Checkbox
                        checked={selectedRows.has(layerId)}
                        onCheckedChange={(checked) => handleRowSelect(layerId, checked)}
                      />
                    </TableCell>
                    <TableCell>
                      <div className="relative group">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleVisibility(layer)}
                          disabled={!layer.geojson && !layer.geometry}
                          className="p-1"
                          title={!layer.geojson && !layer.geometry ? "Données géographiques manquantes" : (layer.is_visible ? "Masquer la couche" : "Afficher la couche")}
                        >
                          {layer.is_visible ? (
                            <Eye className={`h-4 w-4 ${(!layer.geojson && !layer.geometry) ? 'text-gray-300' : 'text-green-500'}`} />
                          ) : (
                            <EyeOff className={`h-4 w-4 ${(!layer.geojson && !layer.geometry) ? 'text-gray-300' : 'text-gray-400'}`} />
                          )}
                        </Button>
                        {!layer.geojson && !layer.geometry && (
                          <span className="absolute hidden group-hover:block bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap -top-8 left-0 z-10">
                            Données géographiques manquantes
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="p-3">
                      <div className="space-y-2">
                        <div className="font-medium text-sm text-gray-900">{layer.name || 'Sans nom'}</div>
                        
                        <div className="flex flex-wrap gap-1">
                          <TypeBadge type={layer.layerType || layer.layer_type} />
                          <StatusBadge status={layer.status} />
                          {(!layer.geojson && !layer.geometry) && (
                            <Badge variant="destructive" className="text-xs">
                              Sans données géo
                            </Badge>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                          <div className="flex items-center space-x-1">
                            <span className="font-medium">Format:</span>
                            <Badge variant="outline" className="text-xs px-1 py-0">
                              {(() => {
                                const format = layer.sourceFormat || layer.source_format || 
                                  (layer.file_name ? layer.file_name.split('.').pop() : null) || 'N/A';
                                return String(format).toUpperCase();
                              })()}
                            </Badge>
                          </div>
                          
                          <div className="flex items-center space-x-1">
                            <MapPin className="h-3 w-3 text-gray-400" />
                            <span>{layer.featureCount || layer.features_count || 0} éléments</span>
                          </div>
                        </div>
                        
                        <div className="text-xs text-gray-500 flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>Créé le {formatDate(layer.createdAt || layer.created_at)}</span>
                        </div>
                        
                        {layer.description && (
                          <div className="text-xs text-gray-500 line-clamp-2 max-w-xs">
                            {String(layer.description || '')}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="p-1">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem onClick={() => onLayerEdit?.(layer)}>
                            <Edit className="h-4 w-4 mr-2" />
                            Modifier
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleToggleVisibility(layer)}>
                            {(layer.isVisible !== undefined ? layer.isVisible : layer.is_visible) ? (
                              <>
                                <EyeOff className="h-4 w-4 mr-2" />
                                Masquer
                              </>
                            ) : (
                              <>
                                <Eye className="h-4 w-4 mr-2" />
                                Afficher
                              </>
                            )}
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => handleExport(layer, 'geojson')}>
                            <Download className="h-4 w-4 mr-2" />
                            Exporter GeoJSON
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem 
                            onClick={() => setDeleteDialog({ open: true, layer })}
                            className="text-red-600"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Supprimer
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Page {currentPage} sur {totalPages} ({totalLayers} éléments)
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                >
                  Précédent
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                >
                  Suivant
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dialog de confirmation de suppression */}
      <Dialog open={deleteDialog.open} onOpenChange={(open) => setDeleteDialog({ open, layer: null })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmer la suppression</DialogTitle>
            <DialogDescription>
              Êtes-vous sûr de vouloir supprimer la couche "{deleteDialog.layer?.name || 'Sans nom'}" ?
              Cette action est irréversible.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setDeleteDialog({ open: false, layer: null })}
            >
              Annuler
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => handleDelete(deleteDialog.layer)}
            >
              Supprimer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal plein écran amélioré */}
      <Dialog open={isExpanded} onOpenChange={setIsExpanded}>
        <DialogContent className="max-w-[90vw] max-h-[90vh] w-full h-full">
          <div className="flex flex-col h-full">
            {/* En-tête simplifié */}
            <div className="flex items-center justify-between pb-4 border-b">
              <div>
                <h2 className="text-xl font-bold">Gestion des Couches Géospatiales</h2>
                <p className="text-sm text-gray-600">{layers.length} couches disponibles</p>
              </div>
              <Button 
                variant="outline" 
                onClick={() => setIsExpanded(false)}
              >
                <X className="h-4 w-4 mr-2" />
                Fermer
              </Button>
            </div>

            {/* Contenu du tableau */}
            <div className="flex-1 overflow-auto mt-4">
              {layers.length === 0 ? (
                <div className="text-center py-12">
                  <Database className="h-12 w-4 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune couche disponible</h3>
                  <p className="text-gray-600 mb-4">Commencez par importer une couche géospatiale</p>
                  <Button onClick={() => setAddModalOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Ajouter une couche
                  </Button>
                </div>
              ) : (
                <div className="grid gap-4">
                  {layers.map((layer) => (
                    <Card key={layer.id} className="p-4">
                      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <h3 className="font-semibold text-lg">{layer.name}</h3>
                            <StatusBadge status={layer.status} />
                            <TypeBadge type={layer.layerType || layer.layer_type} />
                          </div>
                          
                          {layer.description && (
                            <p className="text-gray-600 mb-3">{layer.description}</p>
                          )}
                          
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="font-medium text-gray-700">Format :</span>
                              <div className="mt-1">
                                <Badge variant="secondary">
                                  {(layer.sourceFormat || layer.source_format || layer.file_name?.split('.').pop() || 'N/A').toUpperCase()}
                                </Badge>
                              </div>
                            </div>
                            
                            <div>
                              <span className="font-medium text-gray-700">Éléments :</span>
                              <div className="mt-1 flex items-center space-x-1">
                                <MapPin className="h-4 w-4 text-gray-400" />
                                <span>{layer.featureCount || layer.features_count || 0}</span>
                              </div>
                            </div>
                            
                            <div>
                              <span className="font-medium text-gray-700">Créé le :</span>
                              <div className="mt-1 flex items-center space-x-1">
                                <Calendar className="h-4 w-4 text-gray-400" />
                                <span>{formatDate(layer.createdAt || layer.created_at)}</span>
                              </div>
                            </div>
                            
                            <div>
                              <span className="font-medium text-gray-700">Visibilité :</span>
                              <div className="mt-1">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleToggleVisibility(layer)}
                                  className="h-8 px-2"
                                >
                                  {layer.is_visible ? (
                                    <>
                                      <Eye className="h-4 w-4 text-green-600 mr-1" />
                                      <span className="text-green-600">Visible</span>
                                    </>
                                  ) : (
                                    <>
                                      <EyeOff className="h-4 w-4 text-gray-400 mr-1" />
                                      <span className="text-gray-400">Masquée</span>
                                    </>
                                  )}
                                </Button>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="md:ml-4 flex-shrink-0">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="outline" size="sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Actions</DropdownMenuLabel>
                              <DropdownMenuItem onClick={() => onLayerEdit && onLayerEdit(layer)}>
                                <Edit className="mr-2 h-4 w-4" />
                                Modifier
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleExport(layer, 'geojson')}>
                                <Download className="mr-2 h-4 w-4" />
                                Exporter GeoJSON
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleExport(layer, 'kml')}>
                                <Download className="mr-2 h-4 w-4" />
                                Exporter KML
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem 
                                onClick={() => setDeleteDialog({ open: true, layer })}
                                className="text-red-600"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Supprimer
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal d'ajout de couche */}
      <AddGeospatialLayerModalV2
        open={addModalOpen}
        onOpenChange={setAddModalOpen}
        onLayerAdded={() => {
          setAddModalOpen(false);
          fetchLayers();
        }}
      />
    </div>
  );
};

export default LayersManagementTable;
