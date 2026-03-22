import { useAuth } from '@clerk/clerk-react'
import { useURLScanner } from '../hooks/useURLScanner'
import { Header } from '../components/Header'
import { Hero } from '../components/Hero'
import { URLScanner } from '../components/URLScanner'
import { ScanResult } from '../components/ScanResult'
import { Footer } from '../components/Footer'
import { lazy, Suspense } from 'react'

const ChatAssistant = lazy(() => import('../components/ChatAssistant'));

export default function Home() {
  const { getToken, isLoaded } = useAuth()
  
  const {
    inputValue,
    setInputValue,
    scanResult,
    isLoading: isScanLoading,
    error,
    handleScan
  } = useURLScanner()

  return (
    <div className="min-h-screen flex flex-col dot-grid glow-indigo bg-white dark:bg-gray-950 transition-colors duration-300">
      <Header />
      <main className="flex-1 flex flex-col items-center justify-center px-6">
        <Hero />
        <URLScanner 
          inputValue={inputValue} 
          setInputValue={setInputValue} 
          isLoading={isScanLoading} 
          handleScan={handleScan}
        />
        {error && (
          <div className="mb-8 p-4 bg-red-50 dark:bg-red-950/40 border border-red-100 dark:border-red-900 rounded-xl text-red-600 dark:text-red-400 text-sm max-w-2xl w-full text-center">
            {error}
          </div>
        )}
        <ScanResult scanResult={scanResult} />
      </main>
      <Footer />
      <Suspense fallback={null}>
        <ChatAssistant />
      </Suspense>
    </div>
  )
}
