import React, { useState, useCallback } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Upload, FileText, MapPin, AlertCircle, CheckCircle, Loader2, Plus } from 'lucide-react';
import FileUploadZone from './FileUploadZone';

const AddGeospatialLayerModal = ({ onLayerAdded, trigger }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [previewData, setPreviewData] = useState(null);

  // Configuration de la couche
  const [layerConfig, setLayerConfig] = useState({
    name: '',
    description: '',
    layer_type: 'custom',
    status: 'actif'
  });

  // Fichier sélectionné
  const [selectedFile, setSelectedFile] = useState(null);

  // Types de couches disponibles
  const layerTypes = [
    { value: 'deposit', label: 'Gisement Minier', icon: '⛏️' },
    { value: 'infrastructure', label: 'Infrastructure', icon: '🏗️' },
    { value: 'zone', label: 'Zone Administrative', icon: '🗺️' },
    { value: 'custom', label: 'Personnalisé', icon: '📍' }
  ];

  // Statuts disponibles
  const statusOptions = [
    { value: 'actif', label: 'Actif', color: 'bg-green-500' },
    { value: 'en_développement', label: 'En Développement', color: 'bg-yellow-500' },
    { value: 'exploration', label: 'Exploration', color: 'bg-blue-500' },
    { value: 'terminé', label: 'Terminé', color: 'bg-gray-500' }
  ];

  // Formats supportés (récupérés du backend)
  const [supportedFormats, setSupportedFormats] = useState({
    extensions: ['.kml', '.kmz', '.shp', '.geojson', '.json', '.csv', '.txt', '.tiff', '.tif'],
    max_file_size_mb: 100,
    max_features: 10000
  });

  // Réinitialiser le modal
  const resetModal = useCallback(() => {
    setCurrentStep(1);
    setIsUploading(false);
    setUploadProgress(0);
    setError('');
    setSuccess('');
    setPreviewData(null);
    setSelectedFile(null);
    setLayerConfig({
      name: '',
      description: '',
      layer_type: 'custom',
      status: 'actif'
    });
  }, []);

  // Gestion de la fermeture du modal
  const handleClose = useCallback(() => {
    setIsOpen(false);
    setTimeout(resetModal, 300); // Délai pour l'animation
  }, [resetModal]);

  // Gestion de la sélection de fichier
  const handleFileSelect = useCallback((file) => {
    setSelectedFile(file);
    setError('');
    
    // Auto-remplissage du nom si vide
    if (!layerConfig.name && file) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
      setLayerConfig(prev => ({
        ...prev,
        name: nameWithoutExt.replace(/[_-]/g, ' ')
      }));
    }
  }, [layerConfig.name]);

  // Validation de l'étape 1 (fichier)
  const validateStep1 = useCallback(() => {
    if (!selectedFile) {
      setError('Veuillez sélectionner un fichier');
      return false;
    }
    return true;
  }, [selectedFile]);

  // Validation de l'étape 2 (configuration)
  const validateStep2 = useCallback(() => {
    if (!layerConfig.name.trim()) {
      setError('Le nom de la couche est obligatoire');
      return false;
    }
    if (layerConfig.name.length < 3) {
      setError('Le nom doit contenir au moins 3 caractères');
      return false;
    }
    return true;
  }, [layerConfig]);

  // Passage à l'étape suivante
  const handleNextStep = useCallback(() => {
    setError('');
    
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2);
    } else if (currentStep === 2 && validateStep2()) {
      setCurrentStep(3);
    }
  }, [currentStep, validateStep1, validateStep2]);

  // Retour à l'étape précédente
  const handlePrevStep = useCallback(() => {
    setError('');
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  }, [currentStep]);

  // Upload du fichier
  const handleUpload = useCallback(async () => {
    if (!selectedFile || !validateStep2()) return;

    setIsUploading(true);
    setUploadProgress(0);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('name', layerConfig.name.trim());
      formData.append('description', layerConfig.description.trim());
      formData.append('layer_type', layerConfig.layer_type);
      formData.append('status', layerConfig.status);

      // Simulation du progrès
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await fetch('/api/geospatial/upload', {
        method: 'POST',
        body: formData
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      const result = await response.json();

      if (result.success) {
        setSuccess(`Couche "${layerConfig.name}" importée avec succès !`);
        setPreviewData(result.data);
        
        // Notifier le parent
        if (onLayerAdded) {
          onLayerAdded(result.data.layer);
        }

        // Fermer le modal après 2 secondes
        setTimeout(() => {
          handleClose();
        }, 2000);
      } else {
        throw new Error(result.error || 'Erreur lors de l\'upload');
      }
    } catch (err) {
      setError(err.message || 'Erreur lors de l\'upload du fichier');
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  }, [selectedFile, layerConfig, validateStep2, onLayerAdded, handleClose]);

  // Rendu du contenu selon l'étape
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium mb-2">Sélectionner un fichier géospatial</h3>
              <p className="text-sm text-gray-500 mb-4">
                Formats supportés : {supportedFormats.extensions.join(', ')}
              </p>
            </div>

            <FileUploadZone
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              supportedFormats={supportedFormats}
            />

            {selectedFile && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Fichier sélectionné</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-3">
                    <FileText className="h-8 w-8 text-blue-500" />
                    <div className="flex-1">
                      <p className="font-medium">{selectedFile.name}</p>
                      <p className="text-sm text-gray-500">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <Badge variant="outline">
                      {selectedFile.name.split('.').pop().toUpperCase()}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <MapPin className="mx-auto h-12 w-12 text-blue-500 mb-4" />
              <h3 className="text-lg font-medium mb-2">Configuration de la couche</h3>
              <p className="text-sm text-gray-500">
                Définissez les propriétés de votre nouvelle couche géospatiale
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="layer-name">Nom de la couche *</Label>
                <Input
                  id="layer-name"
                  value={layerConfig.name}
                  onChange={(e) => setLayerConfig(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Ex: Gisements aurifères de la région"
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="layer-description">Description</Label>
                <Textarea
                  id="layer-description"
                  value={layerConfig.description}
                  onChange={(e) => setLayerConfig(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Description détaillée de la couche géospatiale..."
                  className="mt-1"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="layer-type">Type de couche</Label>
                  <Select
                    value={layerConfig.layer_type}
                    onValueChange={(value) => setLayerConfig(prev => ({ ...prev, layer_type: value }))}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {layerTypes.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          <span className="flex items-center space-x-2">
                            <span>{type.icon}</span>
                            <span>{type.label}</span>
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="layer-status">Statut</Label>
                  <Select
                    value={layerConfig.status}
                    onValueChange={(value) => setLayerConfig(prev => ({ ...prev, status: value }))}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.map(status => (
                        <SelectItem key={status.value} value={status.value}>
                          <span className="flex items-center space-x-2">
                            <span className={`w-2 h-2 rounded-full ${status.color}`}></span>
                            <span>{status.label}</span>
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              {isUploading ? (
                <Loader2 className="mx-auto h-12 w-12 text-blue-500 animate-spin mb-4" />
              ) : success ? (
                <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
              ) : (
                <Upload className="mx-auto h-12 w-12 text-blue-500 mb-4" />
              )}
              
              <h3 className="text-lg font-medium mb-2">
                {isUploading ? 'Import en cours...' : success ? 'Import réussi !' : 'Confirmer l\'import'}
              </h3>
              
              {!isUploading && !success && (
                <p className="text-sm text-gray-500">
                  Vérifiez les informations ci-dessous avant de lancer l'import
                </p>
              )}
            </div>

            {/* Résumé de la configuration */}
            {!success && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Résumé de l'import</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Fichier :</span>
                    <span className="text-sm font-medium">{selectedFile?.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Nom :</span>
                    <span className="text-sm font-medium">{layerConfig.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Type :</span>
                    <span className="text-sm font-medium">
                      {layerTypes.find(t => t.value === layerConfig.layer_type)?.label}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Statut :</span>
                    <Badge variant="outline">
                      {statusOptions.find(s => s.value === layerConfig.status)?.label}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Barre de progression */}
            {isUploading && (
              <div className="space-y-2">
                <Progress value={uploadProgress} className="w-full" />
                <p className="text-sm text-center text-gray-500">
                  {uploadProgress}% - Traitement du fichier...
                </p>
              </div>
            )}

            {/* Données de preview */}
            {previewData && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm text-green-600">Import terminé</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-sm">
                      <strong>Couche créée :</strong> {previewData.layer.name}
                    </p>
                    <p className="text-sm">
                      <strong>Type de géométrie :</strong> {previewData.layer.geometry_type}
                    </p>
                    {previewData.layer.area_km2 && (
                      <p className="text-sm">
                        <strong>Superficie :</strong> {previewData.layer.area_km2} km²
                      </p>
                    )}
                    {previewData.layer.length_km && (
                      <p className="text-sm">
                        <strong>Longueur :</strong> {previewData.layer.length_km} km
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button className="flex items-center space-x-2">
            <Plus className="h-4 w-4" />
            <span>Ajouter une couche</span>
          </Button>
        )}
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <MapPin className="h-5 w-5 text-blue-500" />
            <span>Ajouter une couche géospatiale</span>
          </DialogTitle>
        </DialogHeader>

        {/* Indicateur d'étapes */}
        <div className="flex items-center justify-center space-x-4 py-4">
          {[1, 2, 3].map((step) => (
            <div key={step} className="flex items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                ${currentStep >= step 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-500'
                }
              `}>
                {step}
              </div>
              {step < 3 && (
                <div className={`
                  w-12 h-0.5 mx-2
                  ${currentStep > step ? 'bg-blue-500' : 'bg-gray-200'}
                `} />
              )}
            </div>
          ))}
        </div>

        {/* Messages d'erreur et de succès */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        {/* Contenu de l'étape */}
        <div className="py-4">
          {renderStepContent()}
        </div>

        {/* Boutons de navigation */}
        <div className="flex justify-between pt-4 border-t">
          <div>
            {currentStep > 1 && !isUploading && !success && (
              <Button variant="outline" onClick={handlePrevStep}>
                Précédent
              </Button>
            )}
          </div>
          
          <div className="flex space-x-2">
            {!success && (
              <Button variant="outline" onClick={handleClose} disabled={isUploading}>
                Annuler
              </Button>
            )}
            
            {currentStep < 3 && !isUploading && (
              <Button onClick={handleNextStep}>
                Suivant
              </Button>
            )}
            
            {currentStep === 3 && !isUploading && !success && (
              <Button onClick={handleUpload} className="bg-blue-500 hover:bg-blue-600">
                <Upload className="h-4 w-4 mr-2" />
                Importer
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AddGeospatialLayerModal;
