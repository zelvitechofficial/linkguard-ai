import { useState, useEffect, useCallback } from 'react'
import { useAuth, useUser, useClerk } from '@clerk/clerk-react'
import { scanUrlAPI } from '../services/api'
import { toast } from 'react-hot-toast'
export const useURLScanner = () => {
  const [inputValue, setInputValue] = useState('')
  const [scanResult, setScanResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const { getToken } = useAuth()
  const { user } = useUser()
  const clerk = useClerk()

  const handleScan = useCallback(async (url) => {
    const targetUrl = url || inputValue
    if (!targetUrl) return

    if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
      const msg = 'Protocol required. Please ensure your URL starts with http:// or https://'
      setError(msg)
      toast.error(msg)
      return
    }

    setIsLoading(true)
    setScanResult(null)
    setError(null)

    try {
      if (!user) {
        localStorage.setItem('pendingScanUrl', targetUrl)
        clerk.openSignIn({ afterSignInUrl: window.location.href, afterSignUpUrl: window.location.href })
        setIsLoading(false)
        return
      }

      const data = await scanUrlAPI(targetUrl)
      setScanResult(data)
      setInputValue('')
    } catch (err) {
      console.error('Scan error:', err)
      const msg = err.response?.data?.detail || err.message || 'Failed to analyze URL'
      setError(msg)
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }, [inputValue, user, clerk])

  useEffect(() => {
    const savedUrl = localStorage.getItem('pendingScanUrl')
    if (user && savedUrl) {
      setInputValue(savedUrl)
      localStorage.removeItem('pendingScanUrl')
      // Small delay ensures auth token is fully available
      setTimeout(() => handleScan(savedUrl), 100)
    }
  }, [user, handleScan])

  return { inputValue, setInputValue, scanResult, isLoading, handleScan, error }
}
