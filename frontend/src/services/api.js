import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Setup an axios request interceptor to dynamically inject the Clerk token.
 * This ensures every request has a fresh, valid token, avoiding race conditions.
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
