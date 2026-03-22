import { lazy, Suspense } from 'react'
import ErrorBoundary from './components/ErrorBoundary'
import './App.css'

const Home = lazy(() => import('./pages/Home'))

export default function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-950"><div className="w-8 h-8 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin"></div></div>}>
        <Home />
      </Suspense>
    </ErrorBoundary>
  );
}
