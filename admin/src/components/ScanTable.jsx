import { useState } from 'react';
import { Trash2 } from 'lucide-react';
import { deleteScan } from '../api/adminApi';

const PAGE_SIZE = 12;

export default function ScanTable({ scans = [], onRefresh, loading = false }) {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [deletingId, setDeletingId] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  const handleDelete = (id) => {
    if (confirmDeleteId === id) {
      performDelete(id);
    } else {
      setConfirmDeleteId(id);
      // Auto-reset after 5 seconds
      setTimeout(() => setConfirmDeleteId(null), 5000);
    }
  };

  const performDelete = async (id) => {
    setDeletingId(id);
    setConfirmDeleteId(null);
    try {
      await deleteScan(id);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Delete error:', err);
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = scans.filter(s =>
    (s.url || '').toLowerCase().includes(query.toLowerCase()) ||
    (s.email || '').toLowerCase().includes(query.toLowerCase())
  );

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const sliced = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="card overflow-hidden transition-all duration-500 relative">
      {/* Search bar */}
      <div className="card-header flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">Recent URL Scans</p>
        <input
          value={query}
          onChange={e => { setQuery(e.target.value); setPage(1); }}
          placeholder="Filter by URL or email…"
          className="text-sm border border-gray-200 dark:border-gray-700 dark:bg-gray-800 rounded-lg px-3 py-1.5 outline-none focus:ring-2 focus:ring-indigo-100 dark:focus:ring-indigo-900/40 focus:border-indigo-400 w-full sm:w-64 transition dark:text-gray-200"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-100 dark:border-gray-800">
            <tr>
              {['User Email', 'Analyzed URL', 'Verdict', 'Confidence', 'Scan Time', 'Actions'].map(h => (
                <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
            {sliced.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-10 text-center text-sm text-gray-400 dark:text-gray-600">
                  {loading ? 'Fetching scan records...' : 'No records found'}
                </td>
              </tr>
            ) : sliced.map((s, i) => (
              <tr key={s.id || i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td className="px-5 py-3 text-gray-600 dark:text-gray-400">{s.email || '—'}</td>
                <td className="px-5 py-3 text-gray-700 dark:text-gray-300 max-w-xs truncate font-mono text-xs">{s.url}</td>
                <td className="px-5 py-3">
                  <span className={s.verdict === 'malicious' ? 'badge badge-malicious' : 'badge badge-safe'}>
                    {s.verdict}
                  </span>
                </td>
                <td className="px-5 py-3 text-gray-600 dark:text-gray-400">{s.confidence != null ? `${(s.confidence * 100).toFixed(1)}%` : '—'}</td>
                <td className="px-5 py-3 text-gray-400 dark:text-gray-500 text-xs">{s.scanned_at ? new Date(s.scanned_at).toLocaleString() : '—'}</td>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-2">
                    {confirmDeleteId === s.id && (
                      <span className="text-[10px] font-bold text-red-500 uppercase animate-pulse">Confirm?</span>
                    )}
                    <button 
                      onClick={() => handleDelete(s.id)}
                      disabled={deletingId === s.id}
                      className={`p-1.5 rounded-lg transition-all ${
                        confirmDeleteId === s.id 
                          ? 'bg-red-500 text-white shadow-sm ring-4 ring-red-500/20' 
                          : 'text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
                      }`}
                      title={confirmDeleteId === s.id ? "Click again to confirm delete" : "Delete Record"}
                    >
                      <Trash2 size={16} className={deletingId === s.id ? 'animate-spin' : ''} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-5 py-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
        <span>{filtered.length} records</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-40 hover:border-indigo-300 dark:hover:border-indigo-500 transition"
          >Prev</button>
          <span>Page {page} / {totalPages}</span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1 rounded-lg border border-gray-200 dark:border-gray-700 disabled:opacity-40 hover:border-indigo-300 dark:hover:border-indigo-500 transition"
          >Next</button>
        </div>
      </div>
    </div>
  );
}
