import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import TargetManagement from './components/TargetManagement';
import WorkflowMonitor from './components/WorkflowMonitor';
import ScanResults from './components/ScanResults';
import AdminPanel from './components/AdminPanel';
import ToolsManagement from './components/ToolsManagement';

function App() {
  const [activeScans, setActiveScans] = useState(0);
  const [toolStats, setToolStats] = useState({
    installed: 0,
    not_installed: 0,
    failed: 0,
    online: 0,
    busy: 0
  });
  const [recentScans, setRecentScans] = useState([]);

  useEffect(() => {
    fetchToolStats();
    fetchRecentScans();
  }, []);

  const fetchToolStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/tools/stats`);
      const data = await response.json();
      setToolStats(data);
    } catch (error) {
      console.error('Error fetching tool stats:', error);
    }
  };

  const fetchRecentScans = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/scan-results`);
      const data = await response.json();
      setRecentScans(data.slice(0, 5)); // Get latest 5 scans
    } catch (error) {
      console.error('Error fetching recent scans:', error);
      // Keep empty array as fallback
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white">
        {/* Sidebar Navigation */}
        <div className="flex">
          <nav className="w-64 bg-gray-800 min-h-screen p-4">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-cyan-400 mb-2">ReconFlow</h1>
              <p className="text-gray-400 text-sm">Automated Reconnaissance Platform</p>
            </div>
            
            <div className="space-y-2">
              <NavLink 
                to="/" 
                className={({ isActive }) => 
                  `block p-3 rounded-lg transition-colors ${isActive ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                <i className="fas fa-tachometer-alt mr-3"></i>
                Dashboard
              </NavLink>
              
              <NavLink 
                to="/targets" 
                className={({ isActive }) => 
                  `block p-3 rounded-lg transition-colors ${isActive ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                <i className="fas fa-bullseye mr-3"></i>
                Target Management
              </NavLink>
              
              <NavLink 
                to="/tools" 
                className={({ isActive }) => 
                  `block p-3 rounded-lg transition-colors ${isActive ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                <i className="fas fa-toolbox mr-3"></i>
                Tools Management
              </NavLink>
              
              <NavLink 
                to="/workflow" 
                className={({ isActive }) => 
                  `block p-3 rounded-lg transition-colors ${isActive ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                <i className="fas fa-project-diagram mr-3"></i>
                Workflow Monitor
              </NavLink>
              
              <NavLink 
                to="/results" 
                className={({ isActive }) => 
                  `block p-3 rounded-lg transition-colors ${isActive ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                <i className="fas fa-chart-bar mr-3"></i>
                Scan Results
              </NavLink>
              
              <NavLink 
                to="/admin" 
                className={({ isActive }) => 
                  `block p-3 rounded-lg transition-colors ${isActive ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                <i className="fas fa-cogs mr-3"></i>
                Admin Panel
              </NavLink>
            </div>

            {/* Active Scans Indicator */}
            <div className="mt-8 p-4 bg-gray-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-300">Active Scans</span>
                <span className="text-cyan-400 font-bold">{activeScans}</span>
              </div>
              <div className="w-full bg-gray-600 rounded-full h-2">
                <div className="bg-cyan-400 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="flex-1 p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/targets" element={<TargetManagement />} />
              <Route path="/tools" element={<ToolsManagement />} />
              <Route path="/workflow" element={<WorkflowMonitor />} />
              <Route path="/results" element={<ScanResults />} />
              <Route path="/admin" element={<AdminPanel />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;