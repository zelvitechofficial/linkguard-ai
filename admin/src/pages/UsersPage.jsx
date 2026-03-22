import { useEffect, useState, useCallback } from 'react';
import { RefreshCw } from 'lucide-react';
import UserTable from '../components/UserTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { getUsers } from '../api/adminApi';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getUsers();
      setUsers(data);
    } catch {
      setUsers([]);
    } finally {
      setLoading(false);
      setLastRefresh(new Date().toLocaleTimeString());
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mt-2 mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">User Management</h2>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Real-time user data fetched from Clerk</p>
        </div>
        <button onClick={load} disabled={loading} className="flex items-center gap-1.5 btn-outline dark:border-gray-700 dark:text-gray-400 dark:hover:border-indigo-500">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          {lastRefresh ? `Updated ${lastRefresh}` : 'Refresh'}
        </button>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <UserTable users={users} />
      )}
    </div>
  );
}
