import axios from "axios";

const api = axios.create({
  baseURL: "http://35.226.3.30:8080",
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach the token to every request if available.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercept responses to catch unauthorized errors.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
