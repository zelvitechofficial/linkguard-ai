import { useState } from 'react';
import { Trash2, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { deleteScan } from '../api/adminApi';

const PAGE_SIZE = 20;

export default function ScanTable({ scans = [], onRefresh }) {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = (id) => {
    toast((t) => (
      <div className="flex flex-col gap-3 min-w-[200px]">
        <div className="flex items-center gap-2 text-amber-600 dark:text-amber-500 font-semibold">
          <AlertTriangle size={18} />
          <span>Confirm Deletion</span>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-300">Are you sure you want to delete this scan record? This action cannot be undone.</p>
        <div className="flex justify-end gap-2 mt-1">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              toast.dismiss(t.id);
              performDelete(id);
            }}
            className="px-3 py-1.5 text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg shadow-sm transition"
          >
            Delete
          </button>
        </div>
      </div>
    ), { 
      duration: 5000, 
      position: 'top-center',
      className: 'dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow-xl'
    });
  };

  const performDelete = async (id) => {
    setDeletingId(id);
    try {
      await toast.promise(
        deleteScan(id),
        {
          loading: 'Deleting scan record...',
          success: 'Scan deleted successfully!',
          error: 'Could not delete scan. Please try again.',
        },
        {
          style: {
            borderRadius: '10px',
            background: '#333',
            color: '#fff',
          },
        }
      );
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
    <div className="card overflow-hidden">
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
                <td colSpan={6} className="py-10 text-center text-sm text-gray-400 dark:text-gray-600">No records found</td>
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
                  <button 
                    onClick={() => handleDelete(s.id)}
                    disabled={deletingId === s.id}
                    className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50"
                    title="Delete Record"
                  >
                    <Trash2 size={16} className={deletingId === s.id ? 'animate-pulse' : ''} />
                  </button>
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
