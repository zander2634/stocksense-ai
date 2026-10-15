import React, { createContext, useState, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

// Helper: basahin agad ang user mula localStorage
const getInitialUser = () => {
  const token = localStorage.getItem('access_token');
  const savedUser = localStorage.getItem('user');
  
  if (token && savedUser) {
    try {
      return JSON.parse(savedUser);
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      return null;
    }
  }
  return null;
};

export const AuthProvider = ({ children }) => {
  // Initialize user AGAD mula sa localStorage
  const [user, setUser] = useState(getInitialUser);
  const [loading] = useState(false);

  const login = async (username, password, captchaToken) => {
    try {
      // Gumawa ng form data para sa login
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      if (captchaToken) {
        formData.append('captcha_token', captchaToken);
      }
      
      // Mag-request sa backend
      const response = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      // Kunin ang access token
      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);
      
      // Kunin ang user info
      const userResponse = await api.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      // I-save ang user sa localStorage
      localStorage.setItem('user', JSON.stringify(userResponse.data));
      setUser(userResponse.data);
      
      return { success: true };
    } catch (error) {
      // I-handle ang rate limit error (429)
      let errorMessage = 'Login failed';
      
      if (error.response) {
        if (error.response.status === 429) {
  errorMessage = '⚠️ Maximum 3 login attempts per minute. Please wait 1 minute and try again.';
} else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data?.error) {
          errorMessage = error.response.data.error;
        }
      }
      
      return {
        success: false,
        error: errorMessage
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/api/auth/register', userData);
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;