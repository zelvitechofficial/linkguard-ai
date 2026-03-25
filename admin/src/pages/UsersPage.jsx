import { useEffect, useState, useCallback } from 'react';
import { RefreshCw } from 'lucide-react';
import UserTable from '../components/UserTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { getUsers } from '../api/adminApi';
import { useAdmin } from '../context/AdminContext';

export default function UsersPage() {
  const { data, updatePageData, visitedPages } = useAdmin();
  const users = data.users;
  
  const [loading, setLoading] = useState(users === null);
  const [lastRefresh, setLastRefresh] = useState(data.users_lastRefresh || null);

  const load = useCallback(async (isManual = false) => {
    setLoading(true);
    try {
      const resp = await getUsers();
      const timestamp = new Date().toLocaleTimeString();
      updatePageData('users', resp);
      setLastRefresh(timestamp);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    } finally {
      setLoading(false);
    }
  }, [updatePageData]);

  useEffect(() => { 
    if (!visitedPages.has('users')) {
      load(); 
    }
  }, [load, visitedPages]);

  if (!users && (loading || !visitedPages.has('users'))) {
    return <LoadingSpinner message="Fetching registered users..." />;
  }

  return (
    <div className="relative">
      <div className="space-y-6">
      <div className="flex items-center justify-between mt-2 mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">User Management</h2>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Real-time user data fetched from Clerk</p>
        </div>
        <button onClick={() => load(true)} disabled={loading} className="flex items-center gap-1.5 btn-outline dark:border-gray-700 dark:text-gray-400 dark:hover:border-indigo-500 group overflow-hidden">
          <RefreshCw size={13} className={`${loading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
          {lastRefresh ? `Updated ${lastRefresh}` : 'Refresh'}
        </button>
      </div>

      {loading && users && (
         <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/10 dark:bg-gray-950/20 backdrop-blur-[1px]">
            <div className="bg-white dark:bg-gray-900 px-6 py-4 rounded-2xl shadow-xl flex items-center gap-3 border border-gray-100 dark:border-gray-800">
               <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
               <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Syncing users...</span>
            </div>
         </div>
      )}

      <UserTable users={users || []} loading={false} />
    </div>
    </div>
  );
}
