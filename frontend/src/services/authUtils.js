/**
 * Utilitaires d'authentification : token JWT, en-têtes, déconnexion sur 401.
 */
const TOKEN_KEY = "odg_token";
const USER_KEY = "odg_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  window.dispatchEvent(new CustomEvent("odg-unauthorized"));
}

export function getAuthHeaders() {
  const token = getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

/**
 * À appeler après réception d'une réponse fetch.
 * Si status === 401, efface auth et dispatch l'événement pour rediriger vers login.
 */
export function checkUnauthorized(response) {
  if (response.status === 401) {
    clearAuth();
  }
}
