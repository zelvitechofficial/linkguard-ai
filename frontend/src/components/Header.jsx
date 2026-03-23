import { SignedIn, SignedOut, SignInButton, UserButton, useUser, useClerk } from '@clerk/clerk-react'
import { Zap } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import config from '../config'
import { toast } from 'react-hot-toast'

const SunIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="5" />
    <line x1="12" y1="1" x2="12" y2="3" />
    <line x1="12" y1="21" x2="12" y2="23" />
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
    <line x1="1" y1="12" x2="3" y2="12" />
    <line x1="21" y1="12" x2="23" y2="12" />
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
  </svg>
)

const MoonIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
)

export const Header = () => {
  const { isDark, toggle } = useTheme()
  const { user, isLoaded } = useUser()
  const { openSignIn } = useClerk()

  const handleAdminClick = (e) => {
    e.preventDefault();
    
    if (!isLoaded) return;

    if (!user) {
      toast.error("Please sign in to access the admin panel.", {
        icon: '🔒',
        style: { borderRadius: '10px', background: '#333', color: '#fff' }
      });
      return;
    }

    const email = user.primaryEmailAddress?.emailAddress;
    if (email !== config.adminEmail) {
      toast.error("Access Denied: This account does not have administrative privileges.", {
        duration: 4000,
        position: 'top-center',
        style: { border: '1px solid #ef4444', padding: '16px', color: '#ef4444' }
      });
      return;
    }

    // Authorized - redirect
    window.location.href = config.adminUrl;
  };

  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-white/80 dark:bg-gray-950/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800 z-50 px-4 md:px-10 flex items-center justify-between transition-colors duration-300">
      <div className="flex items-center gap-1.5 sm:gap-2 md:ml-4">
        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shrink-0">
          <Zap size={18} className="text-white fill-current" />
        </div>
        <span className="font-bold text-lg md:text-xl xl:text-2xl tracking-tighter md:tracking-tight text-[#1a1a1a] dark:text-white whitespace-nowrap">LinkGuard AI</span>
      </div>

      <div className="flex items-center gap-3 md:mr-4">
        {/* Admin Link (as button for check) */}
        <button
          onClick={handleAdminClick}
          className="text-sm font-semibold text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors mr-1 cursor-pointer"
        >
          Admin
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggle}
          aria-label="Toggle dark mode"
          className="w-9 h-9 flex items-center justify-center rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200"
        >
          {isDark ? <SunIcon /> : <MoonIcon />}
        </button>

        <SignedIn>
          <UserButton afterSignOutUrl="/" showMultiSessions={true} />
        </SignedIn>
        <SignedOut>
          <SignInButton mode="modal">
            <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold px-5 py-2 rounded-full transition-all shadow-md hover:shadow-lg">Sign In</button>
          </SignInButton>
        </SignedOut>
      </div>
    </header>
  )
}
