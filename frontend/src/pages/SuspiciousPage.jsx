import { useState, useEffect } from 'react';
import api from '../api/client';

export default function SuspiciousPage() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewingId, setReviewingId] = useState(null);
  const [reviewerName, setReviewerName] = useState('');
  const [notes, setNotes] = useState('');
  const [nameSet, setNameSet] = useState(false);

  const fetchRecords = () => {
    setLoading(true);
    api.get('emissions/', { params: { is_suspicious: 'true' } })
      .then(r => setRecords(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchRecords(); }, []);

  const handleReview = async (recordId, decision) => {
    if (!reviewerName.trim()) return;
    try {
      await api.post('reviews/', {
        emission_record: recordId,
        decision,
        reviewer_name: reviewerName,
        notes,
      });
      setReviewingId(null);
      setNotes('');
      fetchRecords();
    } catch (err) {
      alert('Review failed: ' + (err.response?.data?.error || 'Unknown error'));
    }
  };

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;

  const pending = records.filter(r => r.status === 'pending');
  const reviewed = records.filter(r => r.status !== 'pending');

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-900 mb-1">Analyst Review</h1>
      <p className="text-sm text-gray-500 mb-6">Review flagged records before they go to audit.</p>

      {!nameSet && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6 max-w-sm">
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Your name</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={reviewerName}
              onChange={e => setReviewerName(e.target.value)}
              placeholder="e.g. Priya Sharma"
              className="flex-1 border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              onClick={() => { if (reviewerName.trim()) setNameSet(true); }}
              className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:bg-gray-300"
              disabled={!reviewerName.trim()}
            >Set</button>
          </div>
        </div>
      )}

      {nameSet && <p className="text-xs text-gray-400 mb-4">Reviewing as <span className="font-medium text-gray-700">{reviewerName}</span></p>}

      {pending.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center text-gray-500 text-sm">
          No records pending review.
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden mb-8">
          <div className="px-4 py-3 border-b border-gray-200 bg-orange-50">
            <span className="text-sm font-medium text-orange-700">{pending.length} records need review</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
                <tr>
                  <th className="text-left px-3 py-2">ID</th>
                  <th className="text-left px-3 py-2">Scope</th>
                  <th className="text-left px-3 py-2">Source</th>
                  <th className="text-left px-3 py-2">Category</th>
                  <th className="text-left px-3 py-2">Value</th>
                  <th className="text-left px-3 py-2">CO₂ (kg)</th>
                  <th className="text-left px-3 py-2">Date</th>
                  <th className="text-left px-3 py-2">Reason</th>
                  <th className="text-left px-3 py-2">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {pending.map(r => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-3 py-2 text-gray-900 font-mono text-xs">{r.id}</td>
                    <td className="px-3 py-2 text-gray-600">{r.scope}</td>
                    <td className="px-3 py-2 text-gray-600">{r.source_type}</td>
                    <td className="px-3 py-2 text-gray-900 max-w-[180px] truncate" title={r.category}>{r.category}</td>
                    <td className="px-3 py-2 text-gray-600">{r.raw_value} {r.raw_unit}</td>
                    <td className="px-3 py-2 text-gray-600">{r.co2_kg ?? '—'}</td>
                    <td className="px-3 py-2 text-gray-500 text-xs">{r.reporting_date}</td>
                    <td className="px-3 py-2 text-orange-600 text-xs max-w-[200px]">{r.suspicious_reason}</td>
                    <td className="px-3 py-2">
                      {reviewingId === r.id ? (
                        <div className="flex flex-col gap-1.5 min-w-[160px]">
                          <textarea
                            value={notes}
                            onChange={e => setNotes(e.target.value)}
                            placeholder="Notes"
                            rows={2}
                            className="border border-gray-300 rounded text-xs px-2 py-1 focus:outline-none"
                          />
                          <div className="flex gap-1">
                            <button onClick={() => handleReview(r.id, 'approved')} className="px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700">Approve</button>
                            <button onClick={() => handleReview(r.id, 'rejected')} className="px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700">Reject</button>
                            <button onClick={() => { setReviewingId(null); setNotes(''); }} className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300">Cancel</button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => setReviewingId(r.id)}
                          disabled={!nameSet}
                          className="px-2.5 py-1 bg-white border border-gray-300 text-gray-700 text-xs rounded hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                        >Review</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {reviewed.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-200">
            <span className="text-sm font-medium text-gray-700">{reviewed.length} reviewed</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
                <tr>
                  <th className="text-left px-3 py-2">ID</th>
                  <th className="text-left px-3 py-2">Source</th>
                  <th className="text-left px-3 py-2">Category</th>
                  <th className="text-left px-3 py-2">Reason</th>
                  <th className="text-left px-3 py-2">Decision</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {reviewed.map(r => (
                  <tr key={r.id}>
                    <td className="px-3 py-2 font-mono text-xs">{r.id}</td>
                    <td className="px-3 py-2 text-gray-600">{r.source_type}</td>
                    <td className="px-3 py-2 text-gray-900 max-w-[180px] truncate">{r.category}</td>
                    <td className="px-3 py-2 text-xs text-gray-500">{r.suspicious_reason}</td>
                    <td className="px-3 py-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        r.status === 'approved' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>{r.status}</span>
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
