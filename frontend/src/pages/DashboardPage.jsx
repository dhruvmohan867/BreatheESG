import { useState, useEffect } from 'react';
import api from '../api/client';

const SCOPE_LABELS = { 1: 'Scope 1', 2: 'Scope 2', 3: 'Scope 3' };
const SOURCE_LABELS = { sap_fuel: 'SAP Fuel', utility: 'Utility', travel: 'Travel' };

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('emissions/dashboard/')
      .then(r => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;
  if (!stats) return <p className="text-red-600 text-sm">Could not load dashboard.</p>;

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-8">
        {[
          { label: 'Total Records', val: stats.total_records, bg: 'bg-white' },
          { label: 'Pending', val: stats.pending_count, bg: 'bg-yellow-50', text: 'text-yellow-700' },
          { label: 'Suspicious', val: stats.suspicious_count, bg: 'bg-orange-50', text: 'text-orange-700' },
          { label: 'Approved', val: stats.approved_count, bg: 'bg-green-50', text: 'text-green-700' },
          { label: 'Rejected', val: stats.rejected_count, bg: 'bg-red-50', text: 'text-red-700' },
        ].map(c => (
          <div key={c.label} className={`${c.bg} border border-gray-200 rounded-lg p-4`}>
            <p className={`text-2xl font-bold ${c.text || 'text-gray-900'}`}>{c.val}</p>
            <p className="text-xs text-gray-500 mt-1">{c.label}</p>
          </div>
        ))}
      </div>

      {stats.by_source_type.length > 0 && (
        <div className="mb-8">
          <h2 className="text-sm font-medium text-gray-700 mb-3">By Source</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {stats.by_source_type.map(s => (
              <div key={s.source_type} className="bg-white border border-gray-200 rounded-lg p-4">
                <p className="text-xs text-gray-500 uppercase tracking-wide">{SOURCE_LABELS[s.source_type] || s.source_type}</p>
                <p className="text-lg font-semibold text-gray-900 mt-1">{s.total} records</p>
                {s.suspicious > 0 && <p className="text-xs text-orange-600 mt-0.5">{s.suspicious} suspicious</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {stats.recent_uploads?.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-700 mb-3">Recent Uploads</h2>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
                <tr>
                  <th className="text-left px-4 py-2.5">File</th>
                  <th className="text-left px-4 py-2.5">Source</th>
                  <th className="text-left px-4 py-2.5">Rows</th>
                  <th className="text-left px-4 py-2.5">Flagged</th>
                  <th className="text-left px-4 py-2.5">Status</th>
                  <th className="text-left px-4 py-2.5">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {stats.recent_uploads.map(u => (
                  <tr key={u.id}>
                    <td className="px-4 py-2.5 text-gray-900 font-medium">{u.file_name}</td>
                    <td className="px-4 py-2.5 text-gray-600">{SOURCE_LABELS[u.source_type] || u.source_type}</td>
                    <td className="px-4 py-2.5 text-gray-600">{u.row_count}</td>
                    <td className="px-4 py-2.5">
                      <span className={u.suspicious_count > 0 ? 'text-orange-600 font-medium' : 'text-gray-400'}>{u.suspicious_count}</span>
                    </td>
                    <td className="px-4 py-2.5">
                      <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                        u.status === 'completed' ? 'bg-green-100 text-green-700' :
                        u.status === 'failed' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>{u.status}</span>
                    </td>
                    <td className="px-4 py-2.5 text-gray-500 text-xs">{new Date(u.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
