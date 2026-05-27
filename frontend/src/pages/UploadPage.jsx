import { useState } from 'react';
import api from '../api/client';

const SOURCES = [
  { value: 'sap_fuel', label: 'SAP Fuel / Procurement', desc: 'IDoc flat-file export from SAP MM' },
  { value: 'utility', label: 'Utility Electricity', desc: 'Portal CSV from utility provider' },
  { value: 'travel', label: 'Corporate Travel', desc: 'Concur/Navan booking export' },
];

export default function UploadPage() {
  const [sourceType, setSourceType] = useState('sap_fuel');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setResult(null);
    setError(null);

    const fd = new FormData();
    fd.append('file', file);

    try {
      const res = await api.post(`uploads/${sourceType}/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
      setFile(null);
      e.target.reset();
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Check file format.');
    } finally {
      setUploading(false);
    }
  };

  const selectedSource = SOURCES.find(s => s.value === sourceType);

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-900 mb-1">Upload Data Source</h1>
      <p className="text-sm text-gray-500 mb-6">Select a source type and upload a CSV file for ingestion.</p>

      <form onSubmit={handleUpload} className="bg-white border border-gray-200 rounded-lg p-6 max-w-lg">
        <div className="mb-5">
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Source Type</label>
          <select
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            {SOURCES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
          {selectedSource && <p className="text-xs text-gray-400 mt-1">{selectedSource.desc}</p>}
        </div>

        <div className="mb-5">
          <label className="block text-sm font-medium text-gray-700 mb-1.5">CSV File</label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:bg-green-600 file:text-white file:text-xs file:font-medium file:cursor-pointer hover:file:bg-green-700"
          />
        </div>

        <button
          type="submit"
          disabled={!file || uploading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white text-sm font-medium py-2 rounded-md transition-colors"
        >
          {uploading ? 'Processing...' : 'Upload & Process'}
        </button>
      </form>

      {result && (
        <div className="mt-5 bg-green-50 border border-green-200 rounded-lg p-4 max-w-lg">
          <p className="text-green-800 font-medium text-sm mb-2">Upload complete</p>
          <div className="grid grid-cols-2 gap-y-1 text-sm">
            <span className="text-gray-500">File</span><span className="text-gray-900">{result.file_name}</span>
            <span className="text-gray-500">Rows</span><span className="text-gray-900">{result.rows_processed}</span>
            <span className="text-gray-500">Flagged</span>
            <span className={result.suspicious_count > 0 ? 'text-orange-600 font-medium' : 'text-green-700'}>{result.suspicious_count}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-5 bg-red-50 border border-red-200 rounded-lg p-4 max-w-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}
