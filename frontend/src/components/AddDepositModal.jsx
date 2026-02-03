import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { MapPin, Save, X, Info, Loader2 } from "lucide-react";
import ApiService from "../services/api";
import "./modal-zindex.css";

// Statuts disponibles pour les gisements
const STATUS_OPTIONS = [
  "Exploration",
  "En développement",
  "Actif",
  "Suspendu",
  "Fermé",
];

const AddDepositModal = ({
  isOpen,
  onClose,
  onSave,
  initialCoordinates = null,
}) => {
  const [formData, setFormData] = useState({
    name: "",
    company: "",
    substanceId: "",
    latitude: "",
    longitude: "",
    status: "",
    estimatedQuantity: "",
    estimatedValue: "",
    description: "",
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [substances, setSubstances] = useState([]);
  const [isLoadingSubstances, setIsLoadingSubstances] = useState(false);

  // Charger les substances depuis l'API
  useEffect(() => {
    const loadSubstances = async () => {
      if (isOpen && substances.length === 0) {
        setIsLoadingSubstances(true);
        try {
          const response = await ApiService.getSubstances();
          if (response.success) {
            setSubstances(response.substances);
          }
        } catch (error) {
          // Erreur chargement substances
          setErrors((prev) => ({
            ...prev,
            substances: "Impossible de charger les substances",
          }));
        } finally {
          setIsLoadingSubstances(false);
        }
      }
    };

    loadSubstances();
  }, [isOpen, substances.length]);

  // Initialiser les coordonnées si elles sont fournies (clic sur la carte)
  useEffect(() => {
    if (initialCoordinates) {
      setFormData((prev) => ({
        ...prev,
        latitude: initialCoordinates.lat.toFixed(6),
        longitude: initialCoordinates.lng.toFixed(6),
      }));
    }
  }, [initialCoordinates]);

  // Réinitialiser le formulaire quand le modal se ferme
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        name: "",
        company: "",
        substanceId: "",
        latitude: "",
        longitude: "",
        status: "",
        estimatedQuantity: "",
        estimatedValue: "",
        description: "",
      });
      setErrors({});
      setIsSubmitting(false);
    }
  }, [isOpen]);

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Effacer l'erreur pour ce champ quand l'utilisateur commence à taper
    if (errors[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: null,
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Validation des champs obligatoires
    if (!formData.name.trim()) {
      newErrors.name = "Le nom du gisement est requis";
    }

    if (!formData.company.trim()) {
      newErrors.company = "Le nom de l'entreprise est requis";
    }

    if (!formData.substanceId) {
      newErrors.substanceId = "La substance minière est requise";
    }

    if (!formData.status) {
      newErrors.status = "Le statut est requis";
    }

    // Validation des coordonnées
    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);

    if (!formData.latitude || isNaN(lat) || lat < -90 || lat > 90) {
      newErrors.latitude = "Latitude invalide (doit être entre -90 et 90)";
    }

    if (!formData.longitude || isNaN(lng) || lng < -180 || lng > 180) {
      newErrors.longitude = "Longitude invalide (doit être entre -180 et 180)";
    }

    // Validation des valeurs numériques
    if (
      formData.estimatedQuantity &&
      isNaN(parseFloat(formData.estimatedQuantity))
    ) {
      newErrors.estimatedQuantity = "La quantité doit être un nombre";
    }

    if (formData.estimatedValue && isNaN(parseFloat(formData.estimatedValue))) {
      newErrors.estimatedValue = "La valeur doit être un nombre";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Préparer les données pour l'API en utilisant les données du formulaire
      const depositData = {
        name: formData.name,
        company: formData.company,
        substanceId: formData.substanceId,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        status: formData.status,
        estimatedQuantity: formData.estimatedQuantity
          ? parseFloat(formData.estimatedQuantity)
          : null,
        estimatedValue: formData.estimatedValue
          ? parseFloat(formData.estimatedValue)
          : null,
        description: formData.description || null,
        createdBy: "web_interface",
      };

      // Utiliser l'API pour créer le gisement
      const response = await ApiService.createDeposit(depositData);

      if (response.success) {
        // Appeler la fonction de callback du parent avec les données du gisement créé
        await onSave(response.deposit, response.geojson);

        // Fermer le modal après succès
        onClose();
      } else {
        throw new Error(response.error || "Erreur lors de la création");
      }
    } catch (error) {
      // Erreur lors de la sauvegarde
      setErrors({
        submit:
          error.message || "Erreur lors de la sauvegarde. Veuillez réessayer.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const selectedSubstance = substances.find(
    (s) => s.id === parseInt(formData.substanceId)
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="modal-content max-w-2xl max-h-[90vh] overflow-y-auto z-[9999] [&>*]:z-[9999]">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <MapPin className="mr-2 h-5 w-5" />
            Ajouter un nouveau gisement minier
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Informations générales */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nom du gisement *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Ex: Gisement Minkebe"
                className={errors.name ? "border-red-500" : ""}
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="company">Entreprise/Opérateur *</Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => handleInputChange("company", e.target.value)}
                placeholder="Ex: ODG"
                className={errors.company ? "border-red-500" : ""}
              />
              {errors.company && (
                <p className="text-sm text-red-500">{errors.company}</p>
              )}
            </div>
          </div>

          {/* Substance et statut */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="substance">Substance minière *</Label>
              <Select
                value={formData.substanceId}
                onValueChange={(value) =>
                  handleInputChange("substanceId", value)
                }
              >
                <SelectTrigger
                  className={errors.substanceId ? "border-red-500" : ""}
                >
                  <SelectValue placeholder="Sélectionner une substance" />
                </SelectTrigger>
                <SelectContent className="select-content-modal">
                  {isLoadingSubstances ? (
                    <div className="flex items-center justify-center p-4">
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      <span>Chargement...</span>
                    </div>
                  ) : substances.length === 0 ? (
                    <div className="p-4 text-center text-gray-500">
                      Aucune substance disponible
                    </div>
                  ) : (
                    substances.map((substance) => (
                      <SelectItem
                        key={substance.id}
                        value={substance.id.toString()}
                      >
                        <div className="flex items-center">
                          <div
                            className="w-3 h-3 rounded-full mr-2"
                            style={{ backgroundColor: substance.colorCode }}
                          />
                          {substance.name} ({substance.symbol})
                        </div>
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              {errors.substanceId && (
                <p className="text-sm text-red-500">{errors.substanceId}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Statut *</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => handleInputChange("status", value)}
              >
                <SelectTrigger
                  className={errors.status ? "border-red-500" : ""}
                >
                  <SelectValue placeholder="Sélectionner un statut" />
                </SelectTrigger>
                <SelectContent className="select-content-modal">
                  {STATUS_OPTIONS.map((status) => (
                    <SelectItem key={status} value={status}>
                      {status}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.status && (
                <p className="text-sm text-red-500">{errors.status}</p>
              )}
            </div>
          </div>

          {/* Coordonnées géographiques */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <MapPin className="h-4 w-4 text-blue-600" />
              <Label className="text-sm font-medium">Localisation *</Label>
              {initialCoordinates && (
                <span className="text-xs text-green-600">
                  (Coordonnées définies par clic sur la carte)
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="latitude">Latitude *</Label>
                <Input
                  id="latitude"
                  type="number"
                  step="any"
                  value={formData.latitude}
                  onChange={(e) =>
                    handleInputChange("latitude", e.target.value)
                  }
                  placeholder="-0.5000"
                  className={errors.latitude ? "border-red-500" : ""}
                />
                {errors.latitude && (
                  <p className="text-sm text-red-500">{errors.latitude}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="longitude">Longitude *</Label>
                <Input
                  id="longitude"
                  type="number"
                  step="any"
                  value={formData.longitude}
                  onChange={(e) =>
                    handleInputChange("longitude", e.target.value)
                  }
                  placeholder="12.0000"
                  className={errors.longitude ? "border-red-500" : ""}
                />
                {errors.longitude && (
                  <p className="text-sm text-red-500">{errors.longitude}</p>
                )}
              </div>
            </div>
          </div>

          {/* Données économiques */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="estimatedQuantity">
                Quantité estimée (tonnes)
              </Label>
              <Input
                id="estimatedQuantity"
                type="number"
                step="any"
                value={formData.estimatedQuantity}
                onChange={(e) =>
                  handleInputChange("estimatedQuantity", e.target.value)
                }
                placeholder="1000"
                className={errors.estimatedQuantity ? "border-red-500" : ""}
              />
              {errors.estimatedQuantity && (
                <p className="text-sm text-red-500">
                  {errors.estimatedQuantity}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="estimatedValue">Valeur estimée (EUR)</Label>
              <Input
                id="estimatedValue"
                type="number"
                step="any"
                value={formData.estimatedValue}
                onChange={(e) =>
                  handleInputChange("estimatedValue", e.target.value)
                }
                placeholder="1000000"
                className={errors.estimatedValue ? "border-red-500" : ""}
              />
              {errors.estimatedValue && (
                <p className="text-sm text-red-500">{errors.estimatedValue}</p>
              )}
            </div>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange("description", e.target.value)}
              placeholder="Description détaillée du gisement, localisation géographique, caractéristiques géologiques..."
              rows={3}
            />
          </div>

          {/* Aperçu de la substance sélectionnée */}
          {selectedSubstance && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <div className="flex items-center">
                  <div
                    className="w-4 h-4 rounded-full mr-2"
                    style={{ backgroundColor: selectedSubstance.colorCode }}
                  />
                  <strong>
                    {selectedSubstance.name} ({selectedSubstance.symbol})
                  </strong>{" "}
                  sélectionné pour ce gisement
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Erreur de chargement substances */}
          {errors.substances && (
            <Alert variant="destructive">
              <AlertDescription>{errors.substances}</AlertDescription>
            </Alert>
          )}

          {/* Erreur de soumission */}
          {errors.submit && (
            <Alert variant="destructive">
              <AlertDescription>{errors.submit}</AlertDescription>
            </Alert>
          )}
        </form>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isSubmitting}
          >
            <X className="mr-2 h-4 w-4" />
            Annuler
          </Button>
          <Button type="submit" onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Création en cours...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Enregistrer le gisement
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default AddDepositModal;
