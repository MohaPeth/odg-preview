import React, { useState } from "react";
import MainApp from "./components/MainApp";
import PartnerDashboard from "./components/PartnerDashboard";
import Login from "./components/Login";
import "./App.css";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem("odg_mock_user") ? true : false;
  });

  const [userProfile, setUserProfile] = useState(() => {
    const stored = localStorage.getItem("odg_mock_user");
    return stored ? JSON.parse(stored) : null;
  });

  const handleLogin = (credentials) => {
    // Simulation de différents types d'utilisateurs
    let profile = { ...credentials };
    
    // Détection du type d'utilisateur basé sur l'email
    if (credentials.email.includes("partenaire") || credentials.email.includes("partner")) {
      profile.role = "partner";
      profile.name = "Partenaire Minier SA";
    } else {
      profile.role = "admin";
      profile.name = "Administrateur ODG";
    }

    setUserProfile(profile);
    if (credentials.rememberMe) {
      localStorage.setItem("odg_mock_user", JSON.stringify(profile));
    }
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("odg_mock_user");
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

