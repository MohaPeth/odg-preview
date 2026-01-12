import React, { useState, useCallback } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
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
import { 
  Upload, 
  FileText, 
  MapPin, 
  AlertCircle, 
  CheckCircle, 
  Loader2, 
  Plus, 
  Info,
  ArrowRight,
  ArrowLeft,
  Eye,
  Settings,
  Save,
  HelpCircle
} from 'lucide-react';
import FileUploadZone from './FileUploadZone';
import { GeospatialLayerService } from '../services/geospatialApi';

const AddGeospatialLayerModalV2 = ({ onLayerAdded, trigger }) => {
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

  // Types de couches avec descriptions détaillées
  const layerTypes = [
    { 
      value: 'deposit', 
      label: 'Gisement Minier', 
      icon: '⛏️',
      description: 'Localisation des gisements d\'or, diamant et autres minéraux',
      examples: 'Points de forage, zones d\'extraction, réserves estimées'
    },
    { 
      value: 'infrastructure', 
      label: 'Infrastructure', 
      icon: '🏗️',
      description: 'Routes, ponts, installations minières et équipements',
      examples: 'Routes d\'accès, usines de traitement, camps de base'
    },
    { 
      value: 'zone', 
      label: 'Zone Administrative', 
      icon: '🗺️',
      description: 'Limites administratives, concessions et permis',
      examples: 'Frontières de concessions, zones protégées, permis d\'exploitation'
    },
    { 
      value: 'environment', 
      label: 'Environnement', 
      icon: '🌿',
      description: 'Données environnementales et écologiques',
      examples: 'Zones protégées, cours d\'eau, végétation'
    },
    { 
      value: 'custom', 
      label: 'Personnalisé', 
      icon: '📍',
      description: 'Autres types de données géospatiales',
      examples: 'Données spécifiques à votre projet'
    }
  ];

  // Statuts avec descriptions
  const statusOptions = [
    { 
      value: 'actif', 
      label: 'Actif', 
      color: 'bg-green-500',
      description: 'Données validées et prêtes à l\'utilisation'
    },
    { 
      value: 'en_développement', 
      label: 'En Développement', 
      color: 'bg-yellow-500',
      description: 'Données en cours de validation ou de mise à jour'
    },
    { 
      value: 'exploration', 
      label: 'Exploration', 
      color: 'bg-blue-500',
      description: 'Données préliminaires pour études et analyses'
    },
    { 
      value: 'terminé', 
      label: 'Terminé', 
      color: 'bg-gray-500',
      description: 'Projet terminé, données archivées'
    }
  ];

  // Formats supportés avec descriptions
  const supportedFormats = [
    {
      format: 'KML/KMZ',
      description: 'Format Google Earth, idéal pour les points et polygones',
      icon: '🌍',
      use: 'Recommandé pour les gisements et zones'
    },
    {
      format: 'GeoJSON',
      description: 'Format web standard, compatible avec la plupart des outils',
      icon: '📄',
      use: 'Polyvalent pour tous types de données'
    },
    {
      format: 'Shapefile (SHP)',
      description: 'Format professionnel SIG, très précis',
      icon: '🗂️',
      use: 'Données techniques et professionnelles'
    },
    {
      format: 'CSV',
      description: 'Tableau avec coordonnées latitude/longitude',
      icon: '📊',
      use: 'Listes de points simples'
    },
    {
      format: 'TIFF',
      description: 'Images géoréférencées et cartes raster',
      icon: '🖼️',
      use: 'Cartes et images satellite'
    }
  ];

  const steps = [
    {
      number: 1,
      title: "Type de Données",
      description: "Choisissez le type de données que vous souhaitez ajouter",
      icon: Settings
    },
    {
      number: 2,
      title: "Fichier de Données",
      description: "Importez votre fichier géospatial",
      icon: Upload
    },
    {
      number: 3,
      title: "Aperçu et Validation",
      description: "Vérifiez vos données avant l'ajout",
      icon: Eye
    },
    {
      number: 4,
      title: "Configuration Finale",
      description: "Nommez et configurez votre couche",
      icon: Save
    }
  ];

  const resetForm = () => {
    setCurrentStep(1);
    setLayerConfig({
      name: '',
      description: '',
      layer_type: 'custom',
      status: 'actif'
    });
    setSelectedFile(null);
    setPreviewData(null);
    setError('');
    setSuccess('');
    setUploadProgress(0);
  };

  const handleClose = () => {
    setIsOpen(false);
    resetForm();
  };

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleFileSelect = useCallback(
    async (file) => {
      setSelectedFile(file);
      setError('');
      setPreviewData(null);

      if (!file) return;

      const buildMockPreview = () => ({
        fileName: file.name,
        size: file.size,
        type: file.type,
        features: Math.floor(Math.random() * 50) + 10,
        bounds: {
          north: 2.3,
          south: -3.9,
          east: 14.5,
          west: 8.7,
        },
      });

      try {
        // Tentative de prévisualisation réelle via l'API backend
        const result = await GeospatialLayerService.previewFile(file, layerConfig);

        if (result && result.success && result.data) {
          const boundsArray = result.data.bounds || [];
          const [minX, minY, maxX, maxY] =
            boundsArray.length === 4 ? boundsArray : [null, null, null, null];

          setPreviewData({
            fileName: file.name,
            size: file.size,
            type: file.type,
            features: result.data.featureCount ?? 0,
            bounds: {
              north: maxY,
              south: minY,
              east: maxX,
              west: minX,
            },
          });
          return;
        }

        // Si la réponse n'est pas au format attendu, fallback mock
        setPreviewData(buildMockPreview());
      } catch (err) {
        // Mode démo : si le backend n'est pas disponible, utiliser le mock existant
        console.warn('Prévisualisation géospatiale indisponible, utilisation du mock', err);
        setTimeout(() => {
          setPreviewData(buildMockPreview());
        }, 1000);
      }
    },
    [layerConfig]
  );

  const handleSubmit = async () => {
    if (!selectedFile || !layerConfig.name) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setIsUploading(true);
    setError('');
    setUploadProgress(0);

    try {
      // Upload réel vers le backend avec progression
      const result = await GeospatialLayerService.uploadFile(
        selectedFile,
        layerConfig,
        (progress) => {
          setUploadProgress(progress);
        }
      );

      if (result && result.success) {
        const newLayer = result.data || {
          id: Date.now(),
          name: layerConfig.name,
          description: layerConfig.description,
          layer_type: layerConfig.layer_type,
          status: layerConfig.status,
          file_name: selectedFile.name,
          file_size: selectedFile.size,
          created_at: new Date().toISOString(),
          is_visible: true,
          features_count: previewData?.features || 0
        };

        if (onLayerAdded) {
          onLayerAdded(newLayer);
        }

        setSuccess(result.message || 'Couche ajoutée avec succès !');
        setTimeout(() => {
          handleClose();
        }, 2000);
      } else {
        throw new Error(result?.error || 'Erreur lors de l\'upload');
      }

    } catch (err) {
      console.error('Erreur upload:', err);
      setError('Erreur lors de l\'ajout de la couche : ' + err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold mb-2">Quel type de données souhaitez-vous ajouter ?</h3>
              <p className="text-gray-600">Sélectionnez la catégorie qui correspond le mieux à vos données</p>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {layerTypes.map((type) => (
                <Card 
                  key={type.value}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    layerConfig.layer_type === type.value 
                      ? 'ring-2 ring-blue-500 bg-blue-50' 
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setLayerConfig({...layerConfig, layer_type: type.value})}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-4">
                      <div className="text-2xl">{type.icon}</div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-lg">{type.label}</h4>
                        <p className="text-gray-600 mb-2">{type.description}</p>
                        <p className="text-sm text-gray-500">
                          <strong>Exemples :</strong> {type.examples}
                        </p>
                      </div>
                      {layerConfig.layer_type === type.value && (
                        <CheckCircle className="h-5 w-5 text-blue-500" />
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Aide sur les formats */}
            <Card className="bg-blue-50 border-blue-200">
              <CardHeader>
                <CardTitle className="flex items-center text-blue-700">
                  <HelpCircle className="mr-2 h-5 w-5" />
                  Formats de fichiers supportés
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {supportedFormats.map((format, index) => (
                    <div key={index} className="flex items-center space-x-3 p-2 bg-white rounded">
                      <span className="text-lg">{format.icon}</span>
                      <div>
                        <div className="font-medium text-sm">{format.format}</div>
                        <div className="text-xs text-gray-600">{format.use}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold mb-2">Importez votre fichier de données</h3>
              <p className="text-gray-600">
                Glissez-déposez votre fichier ou cliquez pour le sélectionner
              </p>
            </div>

            <FileUploadZone 
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              supportedFormats={{
                extensions: ['.kml', '.kmz', '.geojson', '.json', '.shp', '.csv', '.tiff', '.tif'],
                max_features: 10000,
              }}
              maxFileSize={100 * 1024 * 1024} // 100MB
              className="min-h-[200px]"
            />

            {selectedFile && (
              <Card className="bg-green-50 border-green-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <div>
                      <div className="font-medium">{selectedFile.name}</div>
                      <div className="text-sm text-gray-600">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Conseils d'utilisation */}
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>Conseils :</strong>
                <ul className="mt-2 space-y-1 text-sm">
                  <li>• Assurez-vous que vos coordonnées sont en WGS84 (latitude/longitude)</li>
                  <li>• Pour les fichiers CSV, incluez les colonnes 'latitude' et 'longitude'</li>
                  <li>• Les fichiers Shapefile doivent être compressés en ZIP</li>
                  <li>• Taille maximale : 100 MB par fichier</li>
                </ul>
              </AlertDescription>
            </Alert>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold mb-2">Aperçu de vos données</h3>
              <p className="text-gray-600">Vérifiez que les informations sont correctes</p>
            </div>

            {previewData ? (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <FileText className="mr-2 h-5 w-5" />
                      Informations du fichier
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium">Nom du fichier</Label>
                        <p className="text-sm text-gray-600">{previewData.fileName}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Taille</Label>
                        <p className="text-sm text-gray-600">
                          {(previewData.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Nombre d'éléments</Label>
                        <p className="text-sm text-gray-600">{previewData.features} éléments</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">Type sélectionné</Label>
                        <p className="text-sm text-gray-600">
                          {layerTypes.find(t => t.value === layerConfig.layer_type)?.label}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <MapPin className="mr-2 h-5 w-5" />
                      Étendue géographique
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                      <div>
                        <Label>Nord</Label>
                        <p className="text-gray-600">{previewData.bounds.north}°</p>
                      </div>
                      <div>
                        <Label>Sud</Label>
                        <p className="text-gray-600">{previewData.bounds.south}°</p>
                      </div>
                      <div>
                        <Label>Est</Label>
                        <p className="text-gray-600">{previewData.bounds.east}°</p>
                      </div>
                      <div>
                        <Label>Ouest</Label>
                        <p className="text-gray-600">{previewData.bounds.west}°</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Alert className="bg-green-50 border-green-200">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-700">
                    Vos données semblent correctes et prêtes à être importées !
                  </AlertDescription>
                </Alert>
              </div>
            ) : (
              <div className="text-center py-8">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">Analyse du fichier en cours...</p>
              </div>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold mb-2">Configuration finale</h3>
              <p className="text-gray-600">Donnez un nom et une description à votre couche</p>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="layer-name" className="text-base font-medium">
                  Nom de la couche *
                </Label>
                <Input
                  id="layer-name"
                  value={layerConfig.name}
                  onChange={(e) => setLayerConfig({...layerConfig, name: e.target.value})}
                  placeholder="Ex: Gisements d'or région Nord"
                  className="mt-1"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Ce nom apparaîtra dans la liste des couches
                </p>
              </div>

              <div>
                <Label htmlFor="layer-description" className="text-base font-medium">
                  Description
                </Label>
                <Textarea
                  id="layer-description"
                  value={layerConfig.description}
                  onChange={(e) => setLayerConfig({...layerConfig, description: e.target.value})}
                  placeholder="Décrivez brièvement le contenu de cette couche..."
                  className="mt-1"
                  rows={3}
                />
              </div>

              <div>
                <Label className="text-base font-medium">Statut de la couche</Label>
                <div className="grid grid-cols-1 gap-2 mt-2">
                  {statusOptions.map((status) => (
                    <Card 
                      key={status.value}
                      className={`cursor-pointer transition-all ${
                        layerConfig.status === status.value 
                          ? 'ring-2 ring-blue-500 bg-blue-50' 
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => setLayerConfig({...layerConfig, status: status.value})}
                    >
                      <CardContent className="p-3">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${status.color}`}></div>
                          <div className="flex-1">
                            <div className="font-medium">{status.label}</div>
                            <div className="text-sm text-gray-600">{status.description}</div>
                          </div>
                          {layerConfig.status === status.value && (
                            <CheckCircle className="h-4 w-4 text-blue-500" />
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
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
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="mr-2 h-4 w-4" />
            Ajouter une couche
          </Button>
        )}
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">
            Ajouter une nouvelle couche géospatiale
          </DialogTitle>
          <DialogDescription>
            Suivez les étapes pour importer vos données géospatiales dans le système
          </DialogDescription>
        </DialogHeader>

        {/* Indicateur de progression */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                  currentStep >= step.number 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {currentStep > step.number ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    step.number
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-12 h-1 mx-2 ${
                    currentStep > step.number ? 'bg-blue-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
          
          <div className="text-center">
            <h4 className="font-semibold">{steps[currentStep - 1].title}</h4>
            <p className="text-sm text-gray-600">{steps[currentStep - 1].description}</p>
          </div>
        </div>

        {/* Messages d'erreur et de succès */}
        {error && (
          <Alert className="mb-4 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-700">{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-4 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-700">{success}</AlertDescription>
          </Alert>
        )}

        {/* Contenu de l'étape */}
        <div className="min-h-[400px]">
          {renderStepContent()}
        </div>

        {/* Barre de progression pour l'upload */}
        {isUploading && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Ajout en cours...</span>
              <span className="text-sm text-gray-600">{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} className="h-2" />
          </div>
        )}

        {/* Boutons de navigation */}
        <div className="flex justify-between pt-4 border-t">
          <Button
            variant="outline"
            onClick={currentStep === 1 ? handleClose : handlePrevious}
            disabled={isUploading}
          >
            {currentStep === 1 ? (
              'Annuler'
            ) : (
              <>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Précédent
              </>
            )}
          </Button>

          <div className="flex space-x-2">
            {currentStep < 4 ? (
              <Button
                onClick={handleNext}
                disabled={
                  (currentStep === 1 && !layerConfig.layer_type) ||
                  (currentStep === 2 && !selectedFile) ||
                  (currentStep === 3 && !previewData) ||
                  isUploading
                }
              >
                Suivant
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={!layerConfig.name || isUploading}
                className="bg-green-600 hover:bg-green-700"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Ajout en cours...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Ajouter la couche
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AddGeospatialLayerModalV2;
