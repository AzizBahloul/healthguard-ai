import { useState, useEffect } from 'react'
import './App.css'

interface HealthStatus {
  status: string;
  version: string;
  timestamp: string;
}

interface BedAvailability {
  hospital_id: string;
  hospital_name: string;
  available_beds: number;
  total_beds: number;
  utilization_percentage: number;
}

function App() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [bedData, setBedData] = useState<BedAvailability[]>([]);

  useEffect(() => {
    // Fetch backend health status
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setHealthStatus(data))
      .catch(err => console.error('Failed to fetch health status:', err));

    // Fetch bed availability
    fetch('http://localhost:8000/api/v1/hospitals/beds')
      .then(res => res.json())
      .then(data => setBedData(data))
      .catch(err => console.error('Failed to fetch bed data:', err));
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent">
            🏥 HealthGuard AI
          </h1>
          <p className="text-slate-400">Command Center - Healthcare Intelligence Platform</p>
        </header>

        {/* System Status */}
        <div className="mb-8 p-6 bg-slate-800 rounded-lg border border-slate-700">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          {healthStatus ? (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-slate-400 text-sm">Status</p>
                <p className="text-lg font-semibold text-green-500">{healthStatus.status}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Version</p>
                <p className="text-lg font-semibold">{healthStatus.version}</p>
              </div>
              <div>
                <p className="text-slate-400 text-sm">Last Update</p>
                <p className="text-lg font-semibold">{new Date(healthStatus.timestamp).toLocaleTimeString()}</p>
              </div>
            </div>
          ) : (
            <p className="text-slate-400">Loading system status...</p>
          )}
        </div>

        {/* Real-time Bed Availability */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Real-time Bed Availability</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {bedData.length > 0 ? (
              bedData.map(hospital => (
                <div key={hospital.hospital_id} className="p-6 bg-slate-800 rounded-lg border border-slate-700">
                  <h3 className="text-lg font-semibold mb-3">{hospital.hospital_name}</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Available Beds</span>
                      <span className="font-semibold text-green-500">{hospital.available_beds}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Total Beds</span>
                      <span className="font-semibold">{hospital.total_beds}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Utilization</span>
                      <span className={`font-semibold ${
                        hospital.utilization_percentage > 90 ? 'text-red-500' : 
                        hospital.utilization_percentage > 80 ? 'text-yellow-500' : 
                        'text-green-500'
                      }`}>
                        {hospital.utilization_percentage.toFixed(1)}%
                      </span>
                    </div>
                    {/* Utilization bar */}
                    <div className="w-full bg-slate-700 rounded-full h-2 mt-3">
                      <div 
                        className={`h-2 rounded-full ${
                          hospital.utilization_percentage > 90 ? 'bg-red-500' : 
                          hospital.utilization_percentage > 80 ? 'bg-yellow-500' : 
                          'bg-green-500'
                        }`}
                        style={{ width: `${hospital.utilization_percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-400 col-span-2">Loading bed availability data...</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="p-4 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            <span className="text-2xl mb-2 block">🚑</span>
            <span className="text-sm">Ambulance Routing</span>
          </button>
          <button className="p-4 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors">
            <span className="text-2xl mb-2 block">🏥</span>
            <span className="text-sm">Hospital Status</span>
          </button>
          <button className="p-4 bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors">
            <span className="text-2xl mb-2 block">⚠️</span>
            <span className="text-sm">Active Alerts</span>
          </button>
          <button className="p-4 bg-green-600 hover:bg-green-700 rounded-lg transition-colors">
            <span className="text-2xl mb-2 block">📊</span>
            <span className="text-sm">Analytics</span>
          </button>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-slate-500 text-sm">
          <p>HealthGuard AI © 2024 | AI-Powered Healthcare Coordination</p>
          <p className="mt-1">Status: <span className="text-green-500">All Systems Operational</span></p>
        </footer>
      </div>
    </div>
  )
}

export default App
