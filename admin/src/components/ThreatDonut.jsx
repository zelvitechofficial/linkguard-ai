import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const COLORS = ['#10b981', '#ef4444'];

export default function ThreatDonut({ safe = 0, malicious = 0 }) {
  const data = [
    { name: 'Safe', value: safe },
    { name: 'Malicious', value: malicious },
  ];
  const total = safe + malicious;

  return (
    <div className="card p-5 h-full">
      <p className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">Threat Distribution</p>
      {total === 0 ? (
        <div className="flex items-center justify-center h-48 text-sm text-gray-400 dark:text-gray-600">No data available</div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={88}
              dataKey="value"
              paddingAngle={3}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={COLORS[i]} />
              ))}
            </Pie>
            <Tooltip formatter={(v) => [v.toLocaleString(), '']} />
            <Legend iconType="circle" iconSize={8} />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
