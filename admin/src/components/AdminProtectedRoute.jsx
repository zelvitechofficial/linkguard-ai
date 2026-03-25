import { useUser, SignIn } from '@clerk/clerk-react';
import { useEffect } from 'react';
import config from '../config';

const AdminProtectedRoute = ({ children }) => {
  const { isLoaded, isSignedIn, user } = useUser();

  const email = (user?.primaryEmailAddress?.emailAddress || "").toLowerCase();
  const adminEmail = (config.adminEmail || "").toLowerCase();

    if (isLoaded && isSignedIn && email && email !== adminEmail) {
      const timer = setTimeout(() => {
        window.location.href = config.homeUrl;
      }, 3000); 
      return () => clearTimeout(timer);
    }

  if (!isLoaded) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-950">
        <div className="relative">
          <div className="w-12 h-12 border-4 border-indigo-100 dark:border-indigo-900/30 rounded-full"></div>
          <div className="absolute top-0 left-0 w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <p className="mt-4 text-sm font-medium text-gray-500 dark:text-gray-400 animate-pulse">
          Initializing secure session...
        </p>
      </div>
    );
  }

  // 1. If not signed in at all: Show the focused SignIn card
  if (!isSignedIn) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950 p-4">
        <div className="w-full max-w-md">
          <SignIn 
            routing="hash"
            afterSignInUrl={window.location.href}
          />
          <div className="mt-8 text-center">
            <a 
              href={config.homeUrl} 
              className="text-sm text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 transition-colors"
            >
              &larr; Back to Home
            </a>
          </div>
        </div>
      </div>
    );
  }

  // 2. If signed in but NOT as the admin: Don't render children while redirecting
  if (email && email !== adminEmail) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-950 p-6 text-center">
        <div className="w-16 h-16 bg-red-50 dark:bg-red-900/20 rounded-full flex items-center justify-center text-red-600 dark:text-red-400 mb-4">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        </div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Access Denied</h2>
        <p className="text-gray-500 dark:text-gray-400 max-w-sm">
          The account <strong>{email}</strong> does not have administrator privileges.
        </p>
        <p className="mt-8 text-sm text-gray-400 animate-pulse">Redirecting to Home...</p>
      </div>
    ); 
  }

  // 3. Authorized admin: Render the dashboard
  return children;
};

export default AdminProtectedRoute;
