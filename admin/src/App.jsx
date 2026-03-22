import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuth } from '@clerk/clerk-react';
import { setupInterceptors } from './api/adminApi';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import OverviewPage from './pages/OverviewPage';
import MLMonitoringPage from './pages/MLMonitoringPage';
import ScanDatabasePage from './pages/ScanDatabasePage';
import UsersPage from './pages/UsersPage';
import AdminProtectedRoute from './components/AdminProtectedRoute';

function Layout() {
  const { getToken, isLoaded } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  // Setup API interceptor once Clerk is loaded
  useEffect(() => {
    if (isLoaded) {
      setupInterceptors(getToken);
    }
  }, [isLoaded, getToken]);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  return (
    <AdminProtectedRoute>
      <div className="flex min-h-screen transition-colors duration-300">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        {/* Overlay Backdrop */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-10 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <div className="flex-1 lg:ml-56 w-full min-w-0">
          <Header 
            onOpenSidebar={() => setSidebarOpen(true)} 
            theme={theme}
            toggleTheme={toggleTheme}
          />
          <main className="p-4 lg:p-6 lg:pt-2">
            <Routes>
              <Route path="/" element={<OverviewPage />} />
              <Route path="/ml" element={<MLMonitoringPage />} />
              <Route path="/users" element={<UsersPage />} />
              <Route path="/scans" element={<ScanDatabasePage />} />
            </Routes>
          </main>
        </div>
      </div>
    </AdminProtectedRoute>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
      <Toaster position="top-right" reverseOrder={false} />
    </BrowserRouter>
  );
}
