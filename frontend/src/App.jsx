import React, { useState } from "react";
import MainApp from "./components/MainApp";
import PartnerDashboard from "./components/PartnerDashboard";
import Login from "./components/Login";
import "./App.css";

const STORAGE_KEY = "odg_user";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) ? true : false;
  });

  const [userProfile, setUserProfile] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  });

  const handleLogin = ({ user, rememberMe }) => {
    if (!user) return;

    const profile = {
      id: user.id,
      name: user.name || user.username,
      email: user.email,
      role: user.role,
      status: user.status,
      operatorId: user.operator_id ?? user.operatorId ?? null,
    };

    setUserProfile(profile);
    if (rememberMe) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    }
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEY);
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

