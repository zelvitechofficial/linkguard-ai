import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';

export default function MLMetricsCard({ metrics = {}, loading = false }) {
  const rf = metrics.random_forest || {};
  const dt = metrics.decision_tree || {};

  const featureData = Object.entries(metrics.feature_importance || {})
    .map(([name, value]) => ({ name, value: +(value * 100).toFixed(1) }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);

  const modelRows = [
    { label: 'Accuracy',  rf: rf.accuracy, dt: dt.accuracy },
    { label: 'Precision', rf: rf.precision, dt: dt.precision },
    { label: 'Recall',    rf: rf.recall,    dt: dt.recall },
    { label: 'F1-Score',  rf: rf.f1_score,  dt: dt.f1_score },
  ];

  const pct = v => v != null ? `${(v * 100).toFixed(1)}%` : '—';

  return (
    <div className="relative space-y-5">
      <div className="space-y-5">
      {/* Feature Importance */}
      <div className="card p-5">
        <p className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">Feature Importance</p>
        {featureData.length === 0 ? (
          <div className="text-sm text-gray-400 dark:text-gray-600 py-4 text-center">No metrics available — train the model first.</div>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={featureData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" className="dark:opacity-5" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: '#9ca3af' }} tickLine={false} axisLine={false} unit="%" />
              <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 11, fill: '#6b7280' }} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                itemStyle={{ fontSize: '12px' }}
                cursor={{ fill: 'rgba(0,0,0,0.03)' }}
                formatter={(v) => [`${v}%`, 'Importance']} 
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {featureData.map((_, i) => (
                  <Cell key={i} fill={`hsl(${230 + i * 8}, 70%, ${60 - i * 3}%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Model Performance Table */}
      <div className="card p-5">
        <p className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">Model Performance</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 dark:border-gray-800">
                <th className="text-left py-2 text-xs text-gray-400 dark:text-gray-500 font-medium whitespace-nowrap">Metric</th>
                <th className="text-center py-2 text-xs text-gray-400 dark:text-gray-500 font-medium whitespace-nowrap px-4">Random Forest</th>
                <th className="text-center py-2 text-xs text-gray-400 dark:text-gray-500 font-medium whitespace-nowrap px-4">Decision Tree</th>
              </tr>
            </thead>
            <tbody>
              {modelRows.map(({ label, rf: r, dt: d }) => (
                <tr key={label} className="border-b border-gray-50 dark:border-gray-800/50 last:border-0">
                  <td className="py-2.5 text-gray-600 dark:text-gray-400 font-medium whitespace-nowrap">{label}</td>
                  <td className="py-2.5 text-center px-4">
                    <span className="bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 text-xs font-semibold px-2 py-0.5 rounded-full">{pct(r)}</span>
                  </td>
                  <td className="py-2.5 text-center px-4">
                    <span className="bg-violet-50 dark:bg-violet-900/30 text-violet-700 dark:text-violet-400 text-xs font-semibold px-2 py-0.5 rounded-full">{pct(d)}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    </div>
  );
}
