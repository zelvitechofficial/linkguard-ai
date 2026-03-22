import { useEffect, useState, useCallback } from 'react';
import { Users, ScanLine, ShieldCheck, ShieldAlert, RefreshCw } from 'lucide-react';
import StatCard from '../components/StatCard';
import ThreatDonut from '../components/ThreatDonut';
import VolumeLineChart from '../components/VolumeLineChart';
import LoadingSpinner from '../components/LoadingSpinner';
import { getStats, getScanVolume } from '../api/adminApi';

function pivotVolume(raw) {
  const map = {};
  raw.forEach(({ date, verdict, count }) => {
    if (!map[date]) map[date] = { date, safe: 0, malicious: 0 };
    map[date][verdict] = count;
  });
  return Object.values(map).sort((a, b) => a.date.localeCompare(b.date));
}

export default function OverviewPage() {
  const [stats, setStats] = useState(null);
  const [volume, setVolume] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [s, v] = await Promise.all([getStats(), getScanVolume()]);
      setStats(s);
      setVolume(pivotVolume(v));
    } catch {
      // Fallback to empty state — backend may be offline
      setStats({ total_users: 0, total_scans: 0, safe_scans: 0, malicious_scans: 0 });
    } finally {
      setLoading(false);
      setLastRefresh(new Date().toLocaleTimeString());
    }
  }, []);

  useEffect(() => { load(); }, [load]);

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
    <div className="space-y-6">
      {/* Top bar */}
      <div className="flex items-center justify-between mt-2 mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">System Overview</h2>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Real-time stats from your database</p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="flex items-center gap-1.5 btn-outline dark:border-gray-700 dark:text-gray-400 dark:hover:border-indigo-500"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          {lastRefresh ? `Updated ${lastRefresh}` : 'Refresh'}
        </button>
      </div>

      {loading && !stats ? (
        <LoadingSpinner />
      ) : (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {cards.map(c => <StatCard key={c.label} {...c} />)}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <ThreatDonut safe={safe} malicious={mal} />
            <div className="lg:col-span-2">
              <VolumeLineChart volumeData={volume} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
