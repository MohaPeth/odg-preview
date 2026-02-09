import React, { useState, useEffect } from "react";
import MainApp from "./components/MainApp";
import PartnerDashboard from "./components/PartnerDashboard";
import Login from "./components/Login";
import { getToken, setToken, clearAuth } from "./services/authUtils";
import "./App.css";

// Mode démo : afficher le frontend sans backend (pas de login requis). Remettre à false pour exiger la connexion.
const DEMO_NO_AUTH = true;

const STORAGE_KEY = "odg_user";

const MOCK_PROFILE = {
  id: 1,
  name: "Admin (démo)",
  email: "admin@odg.ga",
  role: "admin",
  status: "active",
  operatorId: null,
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    if (DEMO_NO_AUTH) return true;
    const hasProfile = localStorage.getItem(STORAGE_KEY) || sessionStorage.getItem(STORAGE_KEY);
    return !!(getToken() && hasProfile);
  });

  const [userProfile, setUserProfile] = useState(() => {
    if (DEMO_NO_AUTH) return MOCK_PROFILE;
    const stored = localStorage.getItem(STORAGE_KEY) || sessionStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    const onUnauthorized = () => {
      setUserProfile(null);
      setIsAuthenticated(false);
    };
    window.addEventListener("odg-unauthorized", onUnauthorized);
    return () => window.removeEventListener("odg-unauthorized", onUnauthorized);
  }, []);

  const handleLogin = ({ user, token, rememberMe }) => {
    if (!user || !token) return;

    const profile = {
      id: user.id,
      name: user.name || user.username,
      email: user.email,
      role: user.role,
      status: user.status,
      operatorId: user.operator_id ?? user.operatorId ?? null,
    };

    setUserProfile(profile);
    setToken(token);
    if (rememberMe) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    } else {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    }
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem(STORAGE_KEY);
    setUserProfile(null);
    setIsAuthenticated(false);
  };

  return (
    <div className="App">
      {isAuthenticated ? (
        userProfile?.role === "partner" ? (
          <PartnerDashboard userProfile={userProfile} onLogout={handleLogout} />
        ) : (
          <MainApp userProfile={userProfile} onLogout={handleLogout} />
        )
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;

