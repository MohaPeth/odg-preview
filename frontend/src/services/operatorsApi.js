import { getAuthHeaders, checkUnauthorized } from './authUtils';

const API_BASE_URL = '/api/operators';

/**
 * Service API pour les opérateurs miniers.
 * Utilisé par l'onboarding du dashboard et, à terme, par le front public.
 */
export async function fetchOperators(search = '') {
  const params = new URLSearchParams();
  if (search) {
    params.append('search', search);
  }

  const url = params.toString() ? `${API_BASE_URL}/?${params.toString()}` : `${API_BASE_URL}/`;

  const response = await fetch(url, { headers: getAuthHeaders() });
  checkUnauthorized(response);
  let data;

  try {
    data = await response.json();
  } catch (e) {
    throw new Error('Réponse invalide du serveur opérateurs');
  }

  if (!response.ok || !data.success) {
    throw new Error(data?.error || 'Erreur lors du chargement des opérateurs');
  }

  return data.data || [];
}

export async function fetchOperatorById(id) {
  const response = await fetch(`${API_BASE_URL}/${id}`, { headers: getAuthHeaders() });
  checkUnauthorized(response);
  let data;

  try {
    data = await response.json();
  } catch (e) {
    throw new Error('Réponse invalide du serveur opérateurs');
  }

  if (!response.ok || !data.success) {
    throw new Error(data?.error || 'Erreur lors du chargement de l\'opérateur');
  }

  return data.data;
}
