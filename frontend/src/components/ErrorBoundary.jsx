import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Frontend Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-white dark:bg-gray-950 flex items-center justify-center p-6 transition-colors duration-300">
          <div className="max-w-md w-full bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border border-gray-100 dark:border-gray-800 p-8 text-center animate-in fade-in zoom-in duration-300">
            <div className="w-20 h-20 bg-amber-50 dark:bg-amber-900/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertTriangle size={40} className="text-amber-500" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">Something went wrong</h1>
            <p className="text-gray-500 dark:text-gray-400 mb-8 leading-relaxed">
              The application encountered an unexpected error. We've been notified and are working on it.
            </p>

            <div className="flex flex-col gap-3">
              <button 
                onClick={() => window.location.reload()}
                className="btn-primary w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-2xl flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-indigo-500/25"
              >
                <RefreshCw size={18} />
                Refresh Page
              </button>
              
              <button 
                onClick={() => window.location.href = '/'}
                className="w-full py-3 px-6 text-gray-600 dark:text-gray-400 font-semibold hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors flex items-center justify-center gap-2"
              >
                <Home size={18} />
                Back to Home
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && (
              <div className="mt-8 p-4 bg-red-50 dark:bg-red-900/10 rounded-xl text-left overflow-auto max-h-40">
                <p className="text-xs font-mono text-red-600 dark:text-red-400 whitespace-pre">
                  {this.state.error?.toString()}
                </p>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
