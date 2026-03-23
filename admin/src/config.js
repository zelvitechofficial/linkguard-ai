/**
 * Application Configuration for Admin Panel
 */

const isProd = import.meta.env.PROD;

export const config = {
  // Backend API URL
  apiUrl: import.meta.env.VITE_API_BASE_URL || 'https://linkguard-backend-q6cu.onrender.com',

  // Admin Email
  adminEmail: import.meta.env.VITE_ADMIN_EMAIL || 'nithyaganeshm@gmail.com',

  // Frontend Home URL (for redirects)
  homeUrl: isProd ? 'https://linkguardaihome.netlify.app/' : 'http://localhost:5173',
};

export default config;
