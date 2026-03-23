/**
 * Application Configuration
 * Centralized source for all external URLs and environment-specific settings.
 */

const isProd = import.meta.env.PROD;

export const config = {
  // Backend API URL
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',

  // Admin Panel URL
  adminUrl: import.meta.env.VITE_ADMIN_URL || (
    isProd 
      ? 'https://linkguardaiadmin.netlify.app/' 
      : `http://${window.location.hostname}:5174`
  ),
  
  // Admin Email
  adminEmail: import.meta.env.VITE_ADMIN_EMAIL || 'mrjeevajeeva1102@gmail.com',

  // Frontend Home URL
  homeUrl: isProd ? 'https://linkguardaihome.netlify.app/' : `http://${window.location.hostname}:5173`,
};

export default config;
