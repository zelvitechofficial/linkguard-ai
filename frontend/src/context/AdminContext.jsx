import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AdminContext = createContext();

export const AdminProvider = ({ children }) => {
  // Initialize from sessionStorage to persist across page reloads/navigation away
  const [data, setData] = useState(() => {
    const saved = sessionStorage.getItem('admin_data');
    return saved ? JSON.parse(saved) : {
      overview: null,
      ml: null,
      users: null,
      scans: null,
    };
  });

  const [visitedPages, setVisitedPages] = useState(() => {
    const saved = sessionStorage.getItem('admin_visited');
    return saved ? new Set(JSON.parse(saved)) : new Set();
  });

  // Sync to sessionStorage on changes
  useEffect(() => {
    sessionStorage.setItem('admin_data', JSON.stringify(data));
  }, [data]);

  useEffect(() => {
    sessionStorage.setItem('admin_visited', JSON.stringify(Array.from(visitedPages)));
  }, [visitedPages]);

  const updatePageData = useCallback((page, pageData) => {
    setData(prev => {
      const existing = prev[page];
      // Merge if both are objects and not arrays
      const shouldMerge = existing && 
                          typeof existing === 'object' && !Array.isArray(existing) &&
                          typeof pageData === 'object' && !Array.isArray(pageData);
      
      return {
        ...prev,
        [page]: shouldMerge ? { ...existing, ...pageData } : pageData
      };
    });
    setVisitedPages(prev => {
      if (prev.has(page)) return prev;
      const next = new Set(prev);
      next.add(page);
      return next;
    });
  }, []);

  const value = {
    data,
    visitedPages,
    updatePageData,
  };

  return <AdminContext.Provider value={value}>{children}</AdminContext.Provider>;
};

export const useAdmin = () => {
  const context = useContext(AdminContext);
  if (!context) {
    throw new Error('useAdmin must be used within an AdminProvider');
  }
  return context;
};
