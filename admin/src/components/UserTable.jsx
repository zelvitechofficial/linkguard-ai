import { useState } from 'react';

const PAGE_SIZE = 10;

export default function UserTable({ users = [], loading = false }) {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);

  const filtered = users.filter(u =>
    (u.email || '').toLowerCase().includes(query.toLowerCase()) ||
    (u.first_name || '').toLowerCase().includes(query.toLowerCase()) ||
    (u.last_name || '').toLowerCase().includes(query.toLowerCase())
  );

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const sliced = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="card overflow-hidden transition-all duration-500 relative">
      {/* Search bar */}
      <div className="card-header flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">Registered Users</p>
        <input
          value={query}
          onChange={e => { setQuery(e.target.value); setPage(1); }}
          placeholder="Filter by name or email…"
          className="text-sm border border-gray-200 dark:border-gray-700 dark:bg-gray-800 rounded-lg px-3 py-1.5 outline-none focus:ring-2 focus:ring-indigo-100 dark:focus:ring-indigo-900/40 focus:border-indigo-400 w-full sm:w-64 transition dark:text-gray-200"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-100 dark:border-gray-800">
            <tr>
              {['User', 'Last Sign-in', 'Created At'].map(h => (
                <th key={h} className="text-left px-5 py-3 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
            {sliced.length === 0 ? (
              <tr>
                <td colSpan={3} className="py-10 text-center text-sm text-gray-400 dark:text-gray-600">
                  {loading ? 'Updating user data...' : 'No users found'}
                </td>
              </tr>
            ) : sliced.map((u, i) => (
              <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td className="px-5 py-3 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-indigo-700 dark:text-indigo-400">
                     {u.image_url ? <img src={u.image_url} alt="" className="w-8 h-8 rounded-full" /> : (u.first_name?.[0] || u.email?.[0] || '?').toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-700 dark:text-gray-200">{u.first_name} {u.last_name}</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">{u.email}</p>
                  </div>
                </td>
                <td className="px-5 py-3 text-gray-600 dark:text-gray-400">
                  {u.last_sign_in_at ? new Date(u.last_sign_in_at).toLocaleString() : 'Never'}
                </td>
                <td className="px-5 py-3 text-gray-400 dark:text-gray-500 text-xs">
                  {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-5 py-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
        <span>{filtered.length} users</span>
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
