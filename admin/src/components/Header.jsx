import { Menu, Sun, Moon } from 'lucide-react';
import { UserButton, SignedIn, useUser } from '@clerk/clerk-react';

export default function Header({ onOpenSidebar, theme, toggleTheme }) {
  const { user } = useUser();
  const ADMIN_EMAIL = import.meta.env.VITE_ADMIN_EMAIL;
  const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL || "http://localhost:5173";

  // Security: If somehow someone bypasses the frontend, we still check here
  const isAuthorized = user?.primaryEmailAddress?.emailAddress === ADMIN_EMAIL;

  return (
    <header className="sticky top-0 h-14 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800 flex items-center justify-between lg:justify-end px-4 lg:px-6 z-10 transition-all">
      <button className="lg:hidden p-2 text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg" onClick={onOpenSidebar}>
        <Menu size={20} />
      </button>

      <div className="flex items-center gap-2 sm:gap-4">
        <span className="text-sm text-gray-500 dark:text-gray-400">Hi! <span className="font-semibold text-gray-700 dark:text-gray-200">Admin</span></span>
        
        <div className="border-l border-gray-100 dark:border-gray-800 pl-2 sm:pl-4 flex items-center">
          <button 
            onClick={toggleTheme}
            className="w-9 h-9 flex items-center justify-center rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
        </div>

        <SignedIn>
          <div className="flex items-center gap-2 border-l border-gray-100 dark:border-gray-800 pl-4">
            <UserButton 
              afterSignOutUrl={FRONTEND_URL} 
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8 rounded-lg"
                }
              }}
            />
          </div>
        </SignedIn>
      </div>
    </header>
  );
}
