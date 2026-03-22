import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import { ThemeProvider } from './context/ThemeContext'
import { UsageProvider } from './context/UsageContext'
import './index.css'
import App from './App.jsx'

import { Toaster } from 'react-hot-toast'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing Publishable Key")
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY} afterSignOutUrl="/">
      <ThemeProvider>
        <UsageProvider>
          <Toaster position="top-center" reverseOrder={false} />
          <App />
        </UsageProvider>
      </ThemeProvider>
    </ClerkProvider>
  </StrictMode>,
)

