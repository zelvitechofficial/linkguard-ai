export default function StatCard({ label, value, sub, subColor = 'text-gray-400', icon: Icon, iconBg = 'bg-indigo-50', iconColor = 'text-indigo-600' }) {
  return (
    <div className="stat-card transition-colors">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">{label}</p>
        <div className={`${iconBg} dark:bg-opacity-10 p-2 rounded-xl`}>
          <Icon size={16} className={iconColor} />
        </div>
      </div>
      <p className="text-3xl font-bold text-gray-800 dark:text-gray-100 leading-none tracking-tight">{value}</p>
      {sub && <p className={`text-xs font-medium ${subColor} dark:opacity-80`}>{sub}</p>}
    </div>
  );
}
