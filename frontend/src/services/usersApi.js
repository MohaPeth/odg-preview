import { getAuthHeaders, checkUnauthorized } from "./authUtils";

const API_BASE_URL = "/api/users";
const AUTH_LOGIN_URL = "/api/auth/login";

async function handleResponse(response) {
  checkUnauthorized(response);
  let data;
  try {
    data = await response.json();
  } catch (e) {
    throw new Error("Réponse invalide du serveur utilisateurs");
  }

  if (!response.ok) {
    const message = data && data.error ? data.error : "Erreur lors de l'appel à l'API utilisateurs";
    throw new Error(message);
  }

  return data;
}

function authHeaders() {
  return { "Content-Type": "application/json", ...getAuthHeaders() };
}

export async function getUsers() {
  const response = await fetch(API_BASE_URL, { headers: getAuthHeaders() });
  return handleResponse(response);
}

export async function createUser(payload) {
  const response = await fetch(API_BASE_URL, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function updateUser(id, payload) {
  const response = await fetch(`${API_BASE_URL}/${id}`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

export async function deleteUser(id) {
  const response = await fetch(`${API_BASE_URL}/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  checkUnauthorized(response);
  if (!response.ok) {
    let message = "Erreur lors de la suppression de l'utilisateur";
    try {
      const data = await response.json();
      if (data && data.error) {
        message = data.error;
      }
    } catch (e) {
      // ignore
    }
    throw new Error(message);
  }
  return true;
}

export async function loginUser(payload) {
  const response = await fetch(AUTH_LOGIN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}
