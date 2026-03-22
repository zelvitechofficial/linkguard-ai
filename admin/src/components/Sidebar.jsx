import { NavLink } from 'react-router-dom';
import { LayoutDashboard, BarChart2, Database, Zap, X, Home, Users } from 'lucide-react';

const nav = [
  { to: '/',            label: 'Overview',       icon: LayoutDashboard },
  { to: '/users',       label: 'Users',          icon: Users },
  { to: '/ml',          label: 'ML Monitoring',  icon: BarChart2 },
  { to: '/scans',       label: 'Scan Database',  icon: Database },
];

export default function Sidebar({ isOpen, onClose }) {
  return (
    <aside className={`
      fixed left-0 top-0 h-screen w-56 bg-white dark:bg-gray-900 border-r border-gray-100 dark:border-gray-800 flex flex-col z-20 transition-transform duration-300
      ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
    `}>
      {/* Brand */}
      <div className="flex items-center justify-between px-5 py-5 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <div className="bg-indigo-600 rounded-lg p-1.5">
            <Zap size={16} className="text-white" />
          </div>
          <span className="font-bold text-indigo-700 dark:text-indigo-400 text-base tracking-tight">LinkGuard AI</span>
        </div>
        <button className="lg:hidden p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" onClick={onClose}>
          <X size={20} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-0.5 mt-2">
        <p className="text-[10px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-widest px-4 mb-2">Main</p>
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={() => onClose && onClose()}
            className={({ isActive }) =>
              `sidebar-link transition-all ${isActive ? 'active' : ''}`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}

        {/* External Links Section */}
        <div className="pt-4 mt-4 border-t border-gray-100 dark:border-gray-800">
          <p className="text-[10px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-widest px-4 mb-2">Platform</p>
          <a
            href={import.meta.env.VITE_FRONTEND_URL || "http://localhost:5173"}
            className="sidebar-link flex items-center gap-3 px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-all"
          >
            <Home size={16} />
            Back to Home
          </a>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-100 dark:border-gray-800">
        <p className="text-[10px] text-gray-400 dark:text-gray-500 text-center">Admin Panel v2.0</p>
      </div>
    </aside>
  );
}
