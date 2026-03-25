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
    handleScan,
    error
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
          error={error}
        />
        <ScanResult scanResult={scanResult} />
      </main>
      <Footer />
      <Suspense fallback={null}>
        <ChatAssistant />
      </Suspense>
    </div>
  )
}
