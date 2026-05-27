import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import SuspiciousPage from './pages/SuspiciousPage';
import AuditLogPage from './pages/AuditLogPage';

const NAV = [
  { to: '/', label: 'Dashboard' },
  { to: '/upload', label: 'Upload' },
  { to: '/review', label: 'Review' },
  { to: '/audit', label: 'Audit Trail' },
];

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-14">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-md bg-green-600 flex items-center justify-center">
                <span className="text-white text-xs font-bold">B</span>
              </div>
              <span className="font-semibold text-gray-900 text-sm">BreatheESG</span>
            </div>
            <nav className="flex gap-1">
              {NAV.map(n => (
                <NavLink
                  key={n.to}
                  to={n.to}
                  end={n.to === '/'}
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-green-50 text-green-700'
                        : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'
                    }`
                  }
                >
                  {n.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/review" element={<SuspiciousPage />} />
            <Route path="/audit" element={<AuditLogPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
