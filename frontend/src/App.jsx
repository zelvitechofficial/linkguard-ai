import { lazy, Suspense, useEffect } from 'react'
import { Routes, Route, BrowserRouter } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import { Toaster } from 'react-hot-toast'
import ErrorBoundary from './components/ErrorBoundary'
import { setupInterceptors as setupFrontendInterceptors } from './services/api'
import { setupInterceptors as setupAdminInterceptors } from './services/adminApi'
import './App.css'

const Home = lazy(() => import('./pages/Home'))
const AdminLayout = lazy(() => import('./pages/admin/AdminLayout'))

export default function App() {
  const { isLoaded, isSignedIn, getToken } = useAuth()

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      setupFrontendInterceptors(getToken)
      setupAdminInterceptors(getToken)
    }
  }, [isLoaded, isSignedIn, getToken])

  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Toaster position="top-center" reverseOrder={false} />
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-950"><div className="w-8 h-8 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin"></div></div>}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin/*" element={<AdminLayout />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </BrowserRouter>
  );
}
