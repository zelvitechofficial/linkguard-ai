import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Setup an axios request interceptor to dynamically inject the Clerk token.
 */
export const setupInterceptors = (getToken) => {
  api.interceptors.request.use(async (config) => {
    try {
      const token = await getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (err) {
      console.error('Error fetching auth token for request:', err);
    }
    return config;
  }, (error) => {
    return Promise.reject(error);
  });
};

export const scanUrlAPI = async (url) => {
  const response = await api.post('/url/analyze', { url });
  return response.data;
};

export const scanHistoryAPI = async () => {
  const response = await api.get('/url/history');
  return response.data;
};

export default api;
