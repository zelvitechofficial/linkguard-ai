import { lazy, Suspense, useEffect } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { Toaster } from 'react-hot-toast'
import ErrorBoundary from './components/ErrorBoundary'
import { setupInterceptors } from './services/api'
import './App.css'

const Home = lazy(() => import('./pages/Home'))

export default function App() {
  const { isLoaded, isSignedIn, getToken } = useAuth()

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      setupInterceptors(getToken)
    }
  }, [isLoaded, isSignedIn, getToken])

  return (
    <ErrorBoundary>
      <Toaster position="top-center" reverseOrder={false} />
      <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-950"><div className="w-8 h-8 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin"></div></div>}>
        <Home />
      </Suspense>
    </ErrorBoundary>
  );
}
