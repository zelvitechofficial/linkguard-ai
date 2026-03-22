import axios from 'axios';

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE,
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

export const getStats = () => api.get('/api/v1/admin/stats').then(r => r.data);
export const getScans = (limit = 200) => api.get(`/api/v1/admin/scans?limit=${limit}`).then(r => r.data);
export const getMlMetrics = () => api.get('/api/v1/admin/ml-metrics').then(r => r.data);
export const getScanVolume = () => api.get('/api/v1/admin/scan-volume').then(r => r.data);
export const getUsers = () => api.get('/api/v1/admin/users').then(r => r.data);
export const deleteScan = (id) => api.delete(`/api/v1/admin/scans/${id}`).then(r => r.data);

export default api;
