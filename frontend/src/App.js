import React, { useState, useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import TargetManagement from './components/TargetManagement';
import WorkflowMonitor from './components/WorkflowMonitor';
import ScanResults from './components/ScanResults';
import VulnerabilityResults from './components/VulnerabilityResults';
import AdminPanel from './components/AdminPanel';
import NotificationCenter from './components/NotificationCenter';
import ToolsManagement from './components/ToolsManagement';

function App() {
  const [activeScans, setActiveScans] = useState(3);
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'success',
      message: 'Subdomain enumeration completed for example.com',
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      type: 'warning',
      message: 'High-severity XSS vulnerability found in api.target.com',
      timestamp: new Date().toISOString()
    },
    {
      id: 3,
      type: 'info',
      message: 'Port scan initiated for 127 live subdomains',
      timestamp: new Date().toISOString()
    }
  ]);

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
                to="/vulnerabilities" 
                className={({ isActive }) => 
                  `block p-3 rounded-lg transition-colors ${isActive ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                <i className="fas fa-shield-alt mr-3"></i>
                Vulnerabilities
              </NavLink>
              
              <NavLink 
                to="/notifications" 
                className={({ isActive }) => 
                  `block p-3 rounded-lg transition-colors relative ${isActive ? 'bg-cyan-600 text-white' : 'text-gray-300 hover:bg-gray-700'}`
                }
              >
                <i className="fas fa-bell mr-3"></i>
                Notifications
                {notifications.length > 0 && (
                  <span className="absolute right-2 top-2 bg-red-500 text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {notifications.length}
                  </span>
                )}
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
              <Route path="/vulnerabilities" element={<VulnerabilityResults />} />
              <Route path="/notifications" element={<NotificationCenter notifications={notifications} />} />
              <Route path="/admin" element={<AdminPanel />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;