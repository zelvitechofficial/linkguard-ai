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

export const fetchStats = () => api.get('/admin/stats').then(r => r.data);
export const fetchScans = (limit = 200) => api.get(`/admin/scans?limit=${limit}`).then(r => r.data);
export const fetchMlMetrics = () => api.get('/admin/ml-metrics').then(r => r.data);
export const fetchScanVolume = () => api.get('/admin/scan-volume').then(r => r.data);
export const fetchUsers = () => api.get('/admin/users').then(r => r.data);
export const executeDeleteScan = (id) => api.delete(`/admin/scans/${id}`).then(r => r.data);

export default api;
