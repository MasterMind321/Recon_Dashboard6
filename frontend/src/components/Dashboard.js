import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalTargets: 0,
    activeScans: 0,
    totalTools: 0,
    installedTools: 0,
    onlineTools: 0,
    scanResults: 0
  });

  const [toolStats, setToolStats] = useState({
    installation: {
      installed: 0,
      not_installed: 0,
      failed: 0,
      outdated: 0
    },
    status: {
      online: 0,
      busy: 0
    },
    categories: {}
  });

  const [recentScans, setRecentScans] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch tool statistics
      const toolStatsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/tools/stats`);
      const toolStatsData = await toolStatsResponse.json();
      setToolStats(toolStatsData);

      // Fetch recent scan results
      const scansResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/scan-results`);
      const scansData = await scansResponse.json();
      setRecentScans(scansData.slice(0, 5));

      // Calculate total tools
      const totalTools = Object.values(toolStatsData.categories).reduce((sum, count) => sum + count, 0);

      // Update stats
      setStats({
        totalTargets: [...new Set(scansData.map(scan => scan.target))].length,
        activeScans: scansData.filter(scan => scan.status === 'running').length,
        totalTools: totalTools,
        installedTools: toolStatsData.installation.installed,
        onlineTools: toolStatsData.status.online,
        scanResults: scansData.length
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

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
              <p className="text-gray-400 text-sm">Total Tools</p>
              <p className="text-2xl font-bold text-green-400">{stats.totalTools}</p>
            </div>
            <i className="fas fa-tools text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Installed Tools</p>
              <p className="text-2xl font-bold text-blue-400">{stats.installedTools}</p>
            </div>
            <i className="fas fa-download text-2xl text-blue-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Online Tools</p>
              <p className="text-2xl font-bold text-green-400">{stats.onlineTools}</p>
            </div>
            <i className="fas fa-check-circle text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Scan Results</p>
              <p className="text-2xl font-bold text-purple-400">{stats.scanResults}</p>
            </div>
            <i className="fas fa-chart-bar text-2xl text-purple-400"></i>
          </div>
        </div>
      </div>

      {/* Recent Scans and Tool Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white flex items-center">
              <i className="fas fa-history mr-2 text-cyan-400"></i>
              Recent Scans
            </h2>
          </div>
          <div className="p-6">
            {recentScans.length > 0 ? (
              <div className="space-y-4">
                {recentScans.map((scan) => (
                  <div key={scan.id} className="bg-gray-700 p-4 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <i className={`${getStatusIcon(scan.status)} mr-2 ${getStatusColor(scan.status)}`}></i>
                        <span className="font-semibold text-white">{scan.target}</span>
                      </div>
                      <span className="text-sm text-gray-400">{scan.tool_name}</span>
                    </div>
                    
                    <div className="flex justify-between text-sm text-gray-400">
                      <div>
                        <span className="text-cyan-400">{scan.category}</span>
                        <span className="mx-2">•</span>
                        <span className="text-green-400">{scan.status}</span>
                      </div>
                      <span className="text-yellow-400">
                        {new Date(scan.start_time).toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <i className="fas fa-search text-4xl text-gray-600 mb-3"></i>
                <p className="text-gray-400">No recent scans available</p>
              </div>
            )}
          </div>
        </div>

        {/* Tool Categories Overview */}
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white flex items-center">
              <i className="fas fa-layer-group mr-2 text-cyan-400"></i>
              Tool Categories
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {Object.entries(toolStats.categories).map(([category, count]) => (
                <div key={category} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full mr-3 bg-cyan-400"></div>
                    <span className="text-white capitalize">
                      {category.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <span className="text-cyan-400 font-bold">{count}</span>
                </div>
              ))}
              {Object.keys(toolStats.categories).length === 0 && (
                <div className="text-center py-4">
                  <p className="text-gray-400">Loading tool categories...</p>
                </div>
              )}
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