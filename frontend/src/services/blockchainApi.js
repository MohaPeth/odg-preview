const BASE_URL = "/api/blockchain-integration";

async function handleResponse(response) {
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("Réponse invalide du serveur blockchain");
  }

  if (!response.ok || !data.success) {
    const message =
      (data && data.error) ||
      "Erreur lors de l'appel à l'API blockchain";
    throw new Error(message);
  }

  return data.data;
}

export async function fetchBlockchainStatus() {
  const response = await fetch(`${BASE_URL}/status`);
  return handleResponse(response);
}
