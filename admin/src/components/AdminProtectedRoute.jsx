import { useUser, SignIn } from '@clerk/clerk-react';
import { useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';
import config from '../config';
import { toast } from 'react-hot-toast';

// UnauthorizedView removed in favor of slick toast notifications

const AdminProtectedRoute = ({ children }) => {
  const { isLoaded, isSignedIn, user } = useUser();

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
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

  // 2. If signed in but NOT as the admin: Show error and redirect automatically
  const email = (user?.primaryEmailAddress?.emailAddress || "").toLowerCase();
  const adminEmail = (config.adminEmail || "").toLowerCase();

  if (email !== adminEmail) {
    // Use toast for a slick demo experience instead of a full error page
    toast.error(`Access Denied: ${email} is not an authorized administrator.`, {
      id: 'admin-denied',
      duration: 5000,
      position: 'top-center'
    });

    // Immediate redirect back to home
    setTimeout(() => {
      window.location.href = config.homeUrl;
    }, 500);
    
    return null;
  }

  // 3. Authorized admin: Render the dashboard
  return children;
};

export default AdminProtectedRoute;
