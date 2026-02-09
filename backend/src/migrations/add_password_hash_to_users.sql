-- Migration : ajout de la colonne password_hash à la table users
-- Permet la migration des utilisateurs existants (password_hash nullable au départ)
-- À exécuter avant de déployer l'authentification par mot de passe

ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL;
