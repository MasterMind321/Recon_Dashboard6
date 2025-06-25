import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalTargets: 15,
    activeScans: 3,
    subdomainsFound: 1247,
    vulnerabilities: 23,
    completedScans: 156,
    liveSubdomains: 892
  });

  const [recentScans, setRecentScans] = useState([
    {
      id: 1,
      target: 'example.com',
      status: 'completed',
      progress: 100,
      subdomains: 234,
      vulnerabilities: 7,
      startTime: '2025-03-15 10:30:00',
      endTime: '2025-03-15 12:45:00'
    },
    {
      id: 2,
      target: 'target.com',
      status: 'running',
      progress: 65,
      subdomains: 127,
      vulnerabilities: 3,
      startTime: '2025-03-15 14:15:00',
      currentPhase: 'Vulnerability Scanning'
    },
    {
      id: 3,
      target: 'testsite.org',
      status: 'running',
      progress: 30,
      subdomains: 89,
      vulnerabilities: 1,
      startTime: '2025-03-15 15:45:00',
      currentPhase: 'Port Scanning'
    }
  ]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-400';
      case 'running': return 'text-yellow-400';
      case 'failed': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return 'fas fa-check-circle';
      case 'running': return 'fas fa-spinner fa-spin';
      case 'failed': return 'fas fa-exclamation-triangle';
      default: return 'fas fa-clock';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Recon Dashboard</h1>
          <p className="text-gray-400">Monitor your reconnaissance operations in real-time</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-400">Last Updated</div>
          <div className="text-cyan-400 font-mono">{new Date().toLocaleString()}</div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Targets</p>
              <p className="text-2xl font-bold text-white">{stats.totalTargets}</p>
            </div>
            <i className="fas fa-bullseye text-2xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Scans</p>
              <p className="text-2xl font-bold text-yellow-400">{stats.activeScans}</p>
            </div>
            <i className="fas fa-spinner fa-spin text-2xl text-yellow-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Subdomains Found</p>
              <p className="text-2xl font-bold text-green-400">{stats.subdomainsFound}</p>
            </div>
            <i className="fas fa-sitemap text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Live Subdomains</p>
              <p className="text-2xl font-bold text-blue-400">{stats.liveSubdomains}</p>
            </div>
            <i className="fas fa-globe text-2xl text-blue-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Vulnerabilities</p>
              <p className="text-2xl font-bold text-red-400">{stats.vulnerabilities}</p>
            </div>
            <i className="fas fa-shield-alt text-2xl text-red-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Completed</p>
              <p className="text-2xl font-bold text-purple-400">{stats.completedScans}</p>
            </div>
            <i className="fas fa-check-circle text-2xl text-purple-400"></i>
          </div>
        </div>
      </div>

      {/* Recent Scans */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white flex items-center">
              <i className="fas fa-history mr-2 text-cyan-400"></i>
              Recent Scans
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentScans.map((scan) => (
                <div key={scan.id} className="bg-gray-700 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <i className={`${getStatusIcon(scan.status)} mr-2 ${getStatusColor(scan.status)}`}></i>
                      <span className="font-semibold text-white">{scan.target}</span>
                    </div>
                    <span className="text-sm text-gray-400">{scan.progress}%</span>
                  </div>
                  
                  <div className="w-full bg-gray-600 rounded-full h-2 mb-3">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        scan.status === 'completed' ? 'bg-green-400' : 
                        scan.status === 'running' ? 'bg-yellow-400' : 'bg-red-400'
                      }`}
                      style={{width: `${scan.progress}%`}}
                    ></div>
                  </div>
                  
                  <div className="flex justify-between text-sm text-gray-400">
                    <div>
                      <span className="text-cyan-400">{scan.subdomains}</span> subdomains
                      <span className="mx-2">•</span>
                      <span className="text-red-400">{scan.vulnerabilities}</span> vulns
                    </div>
                    {scan.currentPhase && (
                      <span className="text-yellow-400">{scan.currentPhase}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white flex items-center">
              <i className="fas fa-server mr-2 text-cyan-400"></i>
              System Status
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {[
                { tool: 'Subfinder', status: 'online', usage: 85 },
                { tool: 'Amass', status: 'online', usage: 92 },
                { tool: 'HTTPx', status: 'online', usage: 67 },
                { tool: 'Nuclei', status: 'online', usage: 74 },
                { tool: 'Nmap', status: 'busy', usage: 100 },
                { tool: 'FFUF', status: 'online', usage: 45 }
              ].map((tool, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      tool.status === 'online' ? 'bg-green-400' :
                      tool.status === 'busy' ? 'bg-yellow-400' : 'bg-red-400'
                    }`}></div>
                    <span className="text-white">{tool.tool}</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-20 bg-gray-600 rounded-full h-2 mr-2">
                      <div 
                        className="bg-cyan-400 h-2 rounded-full" 
                        style={{width: `${tool.usage}%`}}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-400 w-10">{tool.usage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Hero Image */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="relative h-64">
          <img 
            src="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5" 
            alt="Cybersecurity Matrix" 
            className="w-full h-full object-cover opacity-30"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-gray-900 to-transparent flex items-center">
            <div className="p-8">
              <h3 className="text-2xl font-bold text-white mb-2">Advanced Reconnaissance Platform</h3>
              <p className="text-gray-300 max-w-md">
                Automated vulnerability discovery and asset enumeration with 
                intelligent workflow orchestration and real-time monitoring.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;