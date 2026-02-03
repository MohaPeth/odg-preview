/**
 * Configuration centralisée pour l'application ODG Frontend
 * Charge les variables d'environnement depuis Vite
 */

const config = {
  // API Configuration
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  
  // Application
  appName: import.meta.env.VITE_APP_NAME || 'ODG WebGIS',
  appEnv: import.meta.env.VITE_APP_ENV || 'development',
  
  // Features
  features: {
    blockchain: import.meta.env.VITE_FEATURE_BLOCKCHAIN === 'true',
    debugMode: import.meta.env.VITE_DEBUG_MODE === 'true',
  },
  
  // Helper: Mode développement
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

// Log configuration en développement uniquement
if (config.isDevelopment && config.features.debugMode) {
  console.log('🔧 Configuration ODG:', config);
}

export default config;
