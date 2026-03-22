import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { fetchUsageAPI, setupInterceptors } from '../services/api';
import toast from 'react-hot-toast';

const UsageContext = createContext();

export const useUsage = () => {
  const context = useContext(UsageContext);
  if (!context) {
    throw new Error('useUsage must be used within a UsageProvider');
  }
  return context;
};

export const UsageProvider = ({ children }) => {
  const { isLoaded, isSignedIn, getToken, userId } = useAuth();
  const [usage, setUsage] = useState({
    scans: { used: 0, limit: 10 },
    chatbot: { used: 0, limit: 10 }
  });
  const [loading, setLoading] = useState(true);

  const refreshUsage = useCallback(async () => {
    if (!isSignedIn) return;
    try {
      const data = await fetchUsageAPI();
      setUsage(data);
    } catch (err) {
      console.error('Failed to fetch usage:', err);
    } finally {
      setLoading(false);
    }
  }, [isSignedIn, getToken]);

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      setupInterceptors(getToken);
      refreshUsage();
      
      return () => {};
    } else if (isLoaded && !isSignedIn) {
      setLoading(false);
    }
  }, [isLoaded, isSignedIn, userId, refreshUsage, getToken]);

  const incrementScanUsage = () => {
    setUsage(prev => ({
      ...prev,
      scans: { ...prev.scans, used: prev.scans.used + 1 }
    }));
  };

  const incrementChatUsage = () => {
    setUsage(prev => ({
      ...prev,
      chatbot: { ...prev.chatbot, used: prev.chatbot.used + 1 }
    }));
  };

  const checkScanLimit = () => {
    if (usage.scans.used >= usage.scans.limit) {
      toast.error(`Daily scan limit reached (${usage.scans.limit}). Please try again tomorrow.`, {
        id: 'scan-limit-reached',
        duration: 4000,
        position: 'top-center',
      });
      return false;
    }
    return true;
  };

  const checkChatLimit = () => {
    if (usage.chatbot.used >= usage.chatbot.limit) {
      toast.error(`Daily chatbot limit reached (${usage.chatbot.limit}). Please try again tomorrow.`, {
        id: 'chat-limit-reached',
        duration: 4000,
        position: 'top-center',
      });
      return false;
    }
    return true;
  };

  return (
    <UsageContext.Provider value={{ 
      usage, 
      loading, 
      refreshUsage, 
      incrementScanUsage, 
      incrementChatUsage,
      checkScanLimit,
      checkChatLimit
    }}>
      {children}
    </UsageContext.Provider>
  );
};
