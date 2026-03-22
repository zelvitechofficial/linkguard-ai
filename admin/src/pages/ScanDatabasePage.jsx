import { useEffect, useState, useCallback } from 'react';
import { RefreshCw } from 'lucide-react';
import ScanTable from '../components/ScanTable';
import LoadingSpinner from '../components/LoadingSpinner';
import { getScans } from '../api/adminApi';

export default function ScanDatabasePage() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getScans(200);
      setScans(data);
    } catch {
      setScans([]);
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
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">Scan Database</h2>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Full URL scan history with verdict and confidence</p>
        </div>
        <button onClick={load} disabled={loading} className="flex items-center gap-1.5 btn-outline dark:border-gray-700 dark:text-gray-400 dark:hover:border-indigo-500">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          {lastRefresh ? `Updated ${lastRefresh}` : 'Refresh'}
        </button>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <ScanTable scans={scans} onRefresh={load} />
      )}
    </div>
  );
}
