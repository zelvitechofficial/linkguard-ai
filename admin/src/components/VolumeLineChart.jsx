import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts';

/**
 * volumeData: [{ date, safe, malicious }]  (pre-pivoted)
 */
export default function VolumeLineChart({ volumeData = [] }) {
  return (
    <div className="card p-5">
      <p className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">Scan Volume Over Time</p>
      {volumeData.length === 0 ? (
        <div className="flex items-center justify-center h-48 text-sm text-gray-400 dark:text-gray-600">No time-series data</div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={volumeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#9ca3af' }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip />
            <Legend iconType="circle" iconSize={8} />
            <Line type="monotone" dataKey="safe" stroke="#10b981" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="malicious" stroke="#ef4444" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
