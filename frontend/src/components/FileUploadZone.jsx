import React, { useState, useCallback, useRef } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Upload, 
  File, 
  FileText, 
  Map, 
  Database, 
  Image, 
  AlertCircle, 
  CheckCircle, 
  X,
  Folder
} from 'lucide-react';

const FileUploadZone = ({ 
  onFileSelect, 
  selectedFile, 
  supportedFormats,
  maxFileSize = 100 * 1024 * 1024, // 100MB par défaut
  className = ""
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const fileInputRef = useRef(null);

  // Icônes par type de fichier
  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'kml':
      case 'kmz':
        return <Map className="h-8 w-8 text-red-500" />;
      case 'shp':
        return <Database className="h-8 w-8 text-blue-500" />;
      case 'geojson':
      case 'json':
        return <FileText className="h-8 w-8 text-green-500" />;
      case 'csv':
        return <FileText className="h-8 w-8 text-orange-500" />;
      case 'txt':
        return <File className="h-8 w-8 text-gray-500" />;
      case 'tiff':
      case 'tif':
        return <Image className="h-8 w-8 text-purple-500" />;
      default:
        return <File className="h-8 w-8 text-gray-400" />;
    }
  };

  // Couleur du badge par format
  const getBadgeColor = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'kml':
      case 'kmz':
        return 'bg-red-100 text-red-800';
      case 'shp':
        return 'bg-blue-100 text-blue-800';
      case 'geojson':
      case 'json':
        return 'bg-green-100 text-green-800';
      case 'csv':
        return 'bg-orange-100 text-orange-800';
      case 'txt':
        return 'bg-gray-100 text-gray-800';
      case 'tiff':
      case 'tif':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Validation du fichier
  const validateFile = useCallback((file) => {
    setError('');
    setIsValidating(true);

    // Vérification de la taille
    if (file.size > maxFileSize) {
      const maxSizeMB = maxFileSize / (1024 * 1024);
      setError(`Fichier trop volumineux. Taille maximum : ${maxSizeMB}MB`);
      setIsValidating(false);
      return false;
    }

    // Vérification de l'extension
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!supportedFormats.extensions.includes(fileExt)) {
      setError(`Format non supporté. Formats acceptés : ${supportedFormats.extensions.join(', ')}`);
      setIsValidating(false);
      return false;
    }

    // Vérification du nom de fichier
    if (file.name.length > 255) {
      setError('Nom de fichier trop long (maximum 255 caractères)');
      setIsValidating(false);
      return false;
    }

    // Vérification des caractères spéciaux
    const invalidChars = /[<>:"/\\|?*]/;
    if (invalidChars.test(file.name)) {
      setError('Le nom de fichier contient des caractères non autorisés');
      setIsValidating(false);
      return false;
    }

    setIsValidating(false);
    return true;
  }, [maxFileSize, supportedFormats]);

  // Gestion de la sélection de fichier
  const handleFileSelection = useCallback((file) => {
    if (validateFile(file)) {
      onFileSelect(file);
    }
  }, [validateFile, onFileSelect]);

  // Gestion du drag & drop
  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelection(files[0]); // Prendre seulement le premier fichier
    }
  }, [handleFileSelection]);

  // Gestion du clic sur la zone
  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // Gestion de la sélection via input
  const handleInputChange = useCallback((e) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  }, [handleFileSelection]);

  // Suppression du fichier sélectionné
  const handleRemoveFile = useCallback((e) => {
    e.stopPropagation();
    onFileSelect(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [onFileSelect]);

  // Formatage de la taille de fichier
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Zone de drop */}
      <Card 
        className={`
          relative cursor-pointer transition-all duration-200 border-2 border-dashed
          ${isDragOver 
            ? 'border-blue-400 bg-blue-50' 
            : selectedFile 
              ? 'border-green-400 bg-green-50' 
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }
        `}
        onClick={handleClick}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <CardContent className="p-8">
          {selectedFile ? (
            // Fichier sélectionné
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center">
                {getFileIcon(selectedFile.name)}
              </div>
              
              <div className="space-y-2">
                <h3 className="font-medium text-green-800">{selectedFile.name}</h3>
                <p className="text-sm text-green-600">
                  {formatFileSize(selectedFile.size)}
                </p>
                <Badge className={getBadgeColor(selectedFile.name)}>
                  {selectedFile.name.split('.').pop()?.toUpperCase()}
                </Badge>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={handleRemoveFile}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <X className="h-4 w-4 mr-1" />
                Supprimer
              </Button>
            </div>
          ) : (
            // Zone d'upload vide
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center">
                {isDragOver ? (
                  <Upload className="h-12 w-12 text-blue-500 animate-bounce" />
                ) : (
                  <Folder className="h-12 w-12 text-gray-400" />
                )}
              </div>
              
              <div className="space-y-2">
                <h3 className="text-lg font-medium text-gray-900">
                  {isDragOver ? 'Déposez votre fichier ici' : 'Glissez-déposez votre fichier'}
                </h3>
                <p className="text-sm text-gray-500">
                  ou <span className="text-blue-600 font-medium">cliquez pour parcourir</span>
                </p>
              </div>

              <div className="text-xs text-gray-400 space-y-1">
                <p>Formats supportés : {supportedFormats.extensions.join(', ')}</p>
                <p>Taille maximum : {Math.round(maxFileSize / (1024 * 1024))}MB</p>
              </div>
            </div>
          )}

          {/* Indicateur de validation */}
          {isValidating && (
            <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
              <div className="text-center space-y-2">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-sm text-gray-600">Validation du fichier...</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Input file caché */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept={supportedFormats.extensions.join(',')}
        onChange={handleInputChange}
      />

      {/* Message d'erreur */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Informations sur les formats */}
      {!selectedFile && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="p-4">
            <h4 className="font-medium text-blue-900 mb-3 flex items-center">
              <FileText className="h-4 w-4 mr-2" />
              Formats supportés
            </h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <Map className="h-4 w-4 text-red-500" />
                  <span><strong>KML/KMZ</strong> - Google Earth</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Database className="h-4 w-4 text-blue-500" />
                  <span><strong>Shapefile</strong> - ESRI (.shp)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-green-500" />
                  <span><strong>GeoJSON</strong> - Standard web</span>
                </div>
              </div>
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-orange-500" />
                  <span><strong>CSV</strong> - Coordonnées tabulaires</span>
                </div>
                <div className="flex items-center space-x-2">
                  <File className="h-4 w-4 text-gray-500" />
                  <span><strong>TXT</strong> - Coordonnées brutes</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Image className="h-4 w-4 text-purple-500" />
                  <span><strong>TIFF</strong> - Images géoréférencées</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Conseils d'utilisation */}
      {!selectedFile && (
        <Card className="bg-gray-50 border-gray-200">
          <CardContent className="p-4">
            <h4 className="font-medium text-gray-900 mb-3 flex items-center">
              <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
              Conseils pour un import réussi
            </h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Assurez-vous que vos données utilisent le système WGS84 (EPSG:4326)</li>
              <li>• Pour les CSV, incluez des colonnes 'latitude' et 'longitude'</li>
              <li>• Les fichiers Shapefile doivent inclure les fichiers .shx et .dbf</li>
              <li>• Évitez les caractères spéciaux dans les noms de fichiers</li>
              <li>• Maximum {supportedFormats.max_features?.toLocaleString() || '10,000'} features par fichier</li>
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FileUploadZone;
