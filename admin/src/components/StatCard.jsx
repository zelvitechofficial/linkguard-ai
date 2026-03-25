export default function StatCard({ label, value, sub, subColor = 'text-gray-400', icon: Icon, iconBg = 'bg-indigo-50', iconColor = 'text-indigo-600', loading = false }) {
  return (
    <div className="stat-card relative overflow-hidden transition-all duration-300">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">{label}</p>
        <div className={`${iconBg} dark:bg-opacity-10 p-2 rounded-xl transition-transform duration-500`}>
          <Icon size={16} className={iconColor} />
        </div>
      </div>
      <div>
        <p className="text-3xl font-bold text-gray-800 dark:text-gray-100 leading-none tracking-tight">
          {value || '—'}
        </p>
        {sub && <p className={`text-xs font-medium ${subColor} dark:opacity-80 mt-1`}>{sub}</p>}
      </div>
    </div>
  );
}
