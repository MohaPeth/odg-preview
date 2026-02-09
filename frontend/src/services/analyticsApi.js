/**
 * Service API pour la section Analyses et Rapports
 * Agrège dashboard summary, blockchain stats et webgis stats
 */

import { getAuthHeaders, checkUnauthorized } from "./authUtils";

async function fetchJson(url) {
  const response = await fetch(url, { headers: getAuthHeaders() });
  checkUnauthorized(response);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error || `Erreur HTTP ${response.status}`);
  }
  return data;
}

/**
 * Résumé global du dashboard (gisements, blockchain, couches, opérateurs)
 */
export async function getDashboardSummary() {
  const data = await fetchJson("/api/dashboard/summary");
  return data.success ? data.data : null;
}

/**
 * Statistiques blockchain (transactions, matériaux, volumes)
 */
export async function getBlockchainStats() {
  const data = await fetchJson("/api/blockchain/stats");
  return data.success ? data.data : null;
}

/**
 * Statistiques WebGIS (gisements, zones, infrastructures, entreprises)
 */
export async function getWebgisStats() {
  const data = await fetchJson("/api/webgis/stats");
  return data.success ? data.data : null;
}

/**
 * Charge toutes les données nécessaires pour la section Analyses
 */
export async function getAnalyticsData() {
  const [summary, blockchain, webgis] = await Promise.allSettled([
    getDashboardSummary(),
    getBlockchainStats(),
    getWebgisStats(),
  ]);

  return {
    summary: summary.status === "fulfilled" ? summary.value : null,
    blockchain: blockchain.status === "fulfilled" ? blockchain.value : null,
    webgis: webgis.status === "fulfilled" ? webgis.value : null,
  };
}
