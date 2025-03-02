import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Login from './components/Login/Login.js';
import Signup from './components/Signup/Signup.js';
import MainView from './components/MainView/MainView.js';
import { Routes, Route, useNavigate } from 'react-router-dom';
import React, { useEffect, useState } from 'react';


const App = () => {
  const navigate = useNavigate();
  const [logoutWarning, setLogoutWarning] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const expiresAt = localStorage.getItem('access_token_expires_at');
  
    if (token && expiresAt) {
      const expirationTime = parseInt(expiresAt, 10);
  
      if (Date.now() > expirationTime) {
        // Token already expired: clear session and redirect.
        localStorage.clear();
        navigate('/login');
      } else {
        const timeout = expirationTime - Date.now();
        const warningTime = 5000; // 5 seconds in milliseconds
        
        // Set a warning timer if there's enough time left
        let warningTimer;
        if (timeout > warningTime) {
          warningTimer = setTimeout(() => {
            setLogoutWarning(true);
          }, timeout - warningTime);
        } else {
          // If there's less than 5 seconds left, show warning immediately.
          setLogoutWarning(true);
        }
        
        // Set the logout timer
        const logoutTimer = setTimeout(() => {
          // Clear the notification before logging out
          setLogoutWarning(false);
          localStorage.clear();
          navigate('/login');
        }, timeout);
  
        // Cleanup both timers on unmount
        return () => {
          if (warningTimer) clearTimeout(warningTimer);
          clearTimeout(logoutTimer);
        };
      }
    }
  }, [navigate]);

  return (
    <>
      {logoutWarning && (
        <div className="logout-warning">
          <p>
            Your session is about to expire. Please log in again to continue your work.
          </p>
        </div>
      )}
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<MainView />} />
      </Routes>
    </>
  );
};

export default App;