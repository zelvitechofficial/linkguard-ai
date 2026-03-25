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
    setData(prev => ({ ...prev, [page]: pageData }));
    setVisitedPages(prev => {
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
