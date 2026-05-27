import { useState, useEffect } from 'react';
import api from '../api/client';

const LABELS = { upload: 'Upload', review_approved: 'Approved', review_rejected: 'Rejected' };
const COLORS = {
  upload: 'bg-blue-100 text-blue-700',
  review_approved: 'bg-green-100 text-green-700',
  review_rejected: 'bg-red-100 text-red-700',
};

export default function AuditLogPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('audit-logs/')
      .then(r => setLogs(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-900 mb-1">Audit Trail</h1>
      <p className="text-sm text-gray-500 mb-6">Every upload and review decision is logged here.</p>

      {logs.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center text-gray-500 text-sm">
          No audit entries yet.
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
                <tr>
                  <th className="text-left px-4 py-2.5">Time</th>
                  <th className="text-left px-4 py-2.5">Action</th>
                  <th className="text-left px-4 py-2.5">Target</th>
                  <th className="text-left px-4 py-2.5">By</th>
                  <th className="text-left px-4 py-2.5">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {logs.map(log => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2.5 text-gray-500 text-xs whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2.5">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${COLORS[log.action] || 'bg-gray-100 text-gray-600'}`}>
                        {LABELS[log.action] || log.action}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-gray-600 font-mono text-xs">{log.target_type} #{log.target_id}</td>
                    <td className="px-4 py-2.5 text-gray-700">{log.performed_by}</td>
                    <td className="px-4 py-2.5 text-gray-500 text-xs max-w-xs truncate">
                      {log.details && typeof log.details === 'object'
                        ? Object.entries(log.details).map(([k, v]) => `${k}: ${v}`).join(', ')
                        : ''}
                    </td>
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
