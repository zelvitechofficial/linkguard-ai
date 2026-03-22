import { useUser, SignIn } from '@clerk/clerk-react';
import { useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

const ADMIN_EMAIL = import.meta.env.VITE_ADMIN_EMAIL;

const UnauthorizedView = ({ email }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      window.location.href = "http://localhost:5173";
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950 p-4">
      <div className="w-full max-w-md p-8 bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-red-100 dark:border-red-900/30 text-center">
        <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Unauthorized Access</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6 font-medium">
          The following account does not have administrative privileges:
        </p>
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg py-2 px-4 mb-6 inline-block">
          <code className="text-indigo-600 dark:text-indigo-400 text-sm font-bold">{email}</code>
        </div>
        <p className="text-sm text-gray-500 mb-4 animate-pulse">
          Redirecting to home page in 3 seconds...
        </p>
      </div>
    </div>
  );
};

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
              href="http://localhost:5173" 
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
  if (user?.primaryEmailAddress?.emailAddress !== ADMIN_EMAIL) {
    return <UnauthorizedView email={user?.primaryEmailAddress?.emailAddress} />;
  }

  // 3. Authorized admin: Render the dashboard
  return children;
};

export default AdminProtectedRoute;
