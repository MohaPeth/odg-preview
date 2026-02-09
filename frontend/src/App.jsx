import React, { useState, useEffect } from "react";
import MainApp from "./components/MainApp";
import PartnerDashboard from "./components/PartnerDashboard";
import Login from "./components/Login";
import { getToken, setToken, clearAuth } from "./services/authUtils";
import "./App.css";

const STORAGE_KEY = "odg_user";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const hasProfile = localStorage.getItem(STORAGE_KEY) || sessionStorage.getItem(STORAGE_KEY);
    return !!(getToken() && hasProfile);
  });

  const [userProfile, setUserProfile] = useState(() => {
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

