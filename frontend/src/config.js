/**
 * Application Configuration
 * Centralized source for all external URLs and environment-specific settings.
 */

const isProd = import.meta.env.PROD;

export const config = {
  // Backend API URL
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',

  // Admin Panel URL (Internal Route)
  adminUrl: '/admin',
  
  // Frontend Home URL
  homeUrl: '/',

  // Admin Email for Authorization
  adminEmail: import.meta.env.VITE_ADMIN_EMAIL || 'linkguardai@gmail.com',
};

export default config;
