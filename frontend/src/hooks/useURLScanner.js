import { useState, useEffect, useCallback } from 'react'
import { useAuth, useUser, useClerk } from '@clerk/clerk-react'
import { scanUrlAPI } from '../services/api'
import { useUsage } from '../context/UsageContext'

export const useURLScanner = () => {
  const [inputValue, setInputValue] = useState('')
  const [scanResult, setScanResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const { getToken } = useAuth()
  const { user } = useUser()
  const clerk = useClerk()
  const { checkScanLimit, incrementScanUsage, refreshUsage } = useUsage()

  const handleScan = useCallback(async (url) => {
    const targetUrl = url || inputValue
    if (!targetUrl) return

    if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
      setError('Invalid URL. Must start with http:// or https://')
      return
    }

    if (!checkScanLimit()) return

    setIsLoading(true)
    setError(null)
    setScanResult(null)

    try {
      if (!user) {
        localStorage.setItem('pendingScanUrl', targetUrl)
        clerk.openSignIn({ afterSignInUrl: window.location.href, afterSignUpUrl: window.location.href })
        return
      }

      // Token is now managed globally by axios instances set in App.jsx
      const data = await scanUrlAPI(targetUrl)
      setScanResult(data)
      setInputValue('')
      incrementScanUsage()
      // Refresh to sync authoritative count
      refreshUsage()
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setIsLoading(false)
    }
  }, [inputValue, user, clerk, getToken, checkScanLimit, incrementScanUsage])

  useEffect(() => {
    const savedUrl = localStorage.getItem('pendingScanUrl')
    if (user && savedUrl) {
      setInputValue(savedUrl)
      localStorage.removeItem('pendingScanUrl')
      // Small delay ensures auth token is fully available
      setTimeout(() => handleScan(savedUrl), 100)
    }
  }, [user, handleScan])

  return { inputValue, setInputValue, scanResult, isLoading, error, handleScan }
}
