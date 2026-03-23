/**
 * Application Configuration
 * Centralized source for all external URLs and environment-specific settings.
 */

const isProd = import.meta.env.PROD;

export const config = {
  // Backend API URL
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',

  // Admin Panel URL
  // Priority: 
  // 1. Environment Variable (VITE_ADMIN_URL)
  // 2. Production Fallback (if on Netlify)
  // 3. Local Development (Port 5174)
  adminUrl: import.meta.env.VITE_ADMIN_URL || (
    isProd 
      ? 'https://linkguardaiadmin.netlify.app/' 
      : `http://${window.location.hostname}:5174`
  ),
  
  // Frontend Home URL (useful for redirects back from admin)
  homeUrl: isProd ? 'https://linkguardaihome.netlify.app/' : `http://${window.location.hostname}:5173`,
};

export default config;
