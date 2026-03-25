import { useEffect, useState, useCallback } from 'react';
import { Users, ScanLine, ShieldCheck, ShieldAlert, RefreshCw } from 'lucide-react';
import StatCard from '../components/StatCard';
import ThreatDonut from '../components/ThreatDonut';
import VolumeLineChart from '../components/VolumeLineChart';
import LoadingSpinner from '../components/LoadingSpinner';
import { getStats, getScanVolume } from '../api/adminApi';
import { useAdmin } from '../context/AdminContext';

function pivotVolume(raw) {
  const map = {};
  raw.forEach(({ date, verdict, count }) => {
    if (!map[date]) map[date] = { date, safe: 0, malicious: 0 };
    map[date][verdict] = count;
  });
  return Object.values(map).sort((a, b) => a.date.localeCompare(b.date));
}

export default function OverviewPage() {
  const { data, updatePageData, visitedPages } = useAdmin();
  const stats = data.overview?.stats;
  const volume = data.overview?.volume || [];
  
  // Start loading as true if we don't have stats yet
  const [loading, setLoading] = useState(stats === null);
  const [lastRefresh, setLastRefresh] = useState(data.overview?.lastRefresh || null);

  const load = useCallback(async (isManual = false) => {
    setLoading(true);
    try {
      const [s, v] = await Promise.all([getStats(), getScanVolume()]);
      const timestamp = new Date().toLocaleTimeString();
      updatePageData('overview', { stats: s, volume: pivotVolume(v), lastRefresh: timestamp });
      setLastRefresh(timestamp);
    } catch (err) {
      console.error('Failed to fetch dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  }, [updatePageData]); 

  useEffect(() => { 
    // If not visited yet in this session storage, load data
    if (!visitedPages.has('overview')) {
      load(); 
    }
  }, [load, visitedPages]);

  // Sequential loading check: Only show spinner if stats are null and we are either loading or haven't visited
  if (!stats && (loading || !visitedPages.has('overview'))) {
    return <LoadingSpinner message="Fetching dashboard analytics..." />;
  }

  const total = stats?.total_scans || 0;
  const safe = stats?.safe_scans || 0;
  const mal = stats?.malicious_scans || 0;

  const cards = [
    { label: 'Total Users',      value: stats?.total_users?.toLocaleString() ?? '—', icon: Users,        iconBg: 'bg-indigo-50',  iconColor: 'text-indigo-600', sub: 'Registered accounts' },
    { label: 'Total Scans',      value: total.toLocaleString(),                       icon: ScanLine,     iconBg: 'bg-violet-50',  iconColor: 'text-violet-600', sub: 'All-time URL analyses' },
    { label: 'Safe URLs',        value: safe.toLocaleString(),                        icon: ShieldCheck,  iconBg: 'bg-emerald-50', iconColor: 'text-emerald-600', sub: total > 0 ? `${(safe/total*100).toFixed(1)}% of total` : '0%', subColor: 'text-emerald-500' },
    { label: 'Malicious URLs',   value: mal.toLocaleString(),                         icon: ShieldAlert,  iconBg: 'bg-red-50',     iconColor: 'text-red-500',    sub: total > 0 ? `${(mal/total*100).toFixed(1)}% of total` : '0%', subColor: 'text-red-500' },
  ];

  return (
    <div className="relative">
      <div className="space-y-6">
      <div className="flex items-center justify-between mt-2 mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">System Overview</h2>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Real-time stats from your database</p>
        </div>
        <button
          onClick={() => load(true)}
          disabled={loading}
          className="flex items-center gap-1.5 btn-outline dark:border-gray-700 dark:text-gray-400 dark:hover:border-indigo-500 overflow-hidden relative group"
        >
          <RefreshCw size={13} className={`${loading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
          {lastRefresh ? `Updated ${lastRefresh}` : 'Refresh'}
        </button>
      </div>

      {/* When refreshing manually, we can show a slight overlay or just the spinner over the content if we want */}
      {loading && stats && (
         <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/20 dark:bg-gray-950/20 backdrop-blur-[1px]">
            <div className="bg-white dark:bg-gray-900 px-6 py-4 rounded-2xl shadow-xl flex items-center gap-3 border border-gray-100 dark:border-gray-800">
               <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
               <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Synchronizing...</span>
            </div>
         </div>
      )}

      <>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {cards.map(c => <StatCard key={c.label} {...c} loading={false} />)}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <ThreatDonut safe={safe} malicious={mal} />
          <div className="lg:col-span-2">
            <VolumeLineChart volumeData={volume} />
          </div>
        </div>
      </>
    </div>
    </div>
  );
}
