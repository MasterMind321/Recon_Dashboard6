import React, { useState, useEffect } from 'react';

const WorkflowMonitor = () => {
  const [tools, setTools] = useState([]);
  const [toolStats, setToolStats] = useState({
    installation: { installed: 0, not_installed: 0, failed: 0, outdated: 0 },
    status: { online: 0, busy: 0 },
    categories: {}
  });
  const [activeWorkflows, setActiveWorkflows] = useState([]);

  useEffect(() => {
    fetchTools();
    fetchToolStats();
    fetchActiveWorkflows();
  }, []);

  const fetchTools = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/tools`);
      const data = await response.json();
      setTools(data);
    } catch (error) {
      console.error('Error fetching tools:', error);
    }
  };

  const fetchToolStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/tools/stats`);
      const data = await response.json();
      setToolStats(data);
    } catch (error) {
      console.error('Error fetching tool stats:', error);
    }
  };

  const fetchActiveWorkflows = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/scan-results`);
      const data = await response.json();
      const runningScans = data.filter(scan => scan.status === 'running').slice(0, 3);
      setActiveWorkflows(runningScans);
    } catch (error) {
      console.error('Error fetching active workflows:', error);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      subdomain_enumeration: '#3b82f6',
      liveness_fingerprinting: '#10b981',
      javascript_endpoint: '#f59e0b',
      vulnerability_scanning: '#ef4444',
      historical_data: '#8b5cf6',
      directory_fuzzing: '#f97316',
      port_scanning: '#a16207',
      cloud_recon: '#0ea5e9',
      reporting_notification: '#eab308',
      utility_misc: '#6b7280'
    };
    return colors[category] || '#6b7280';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      subdomain_enumeration: 'fas fa-sitemap',
      liveness_fingerprinting: 'fas fa-heartbeat',
      javascript_endpoint: 'fab fa-js',
      vulnerability_scanning: 'fas fa-bug',
      historical_data: 'fas fa-history',
      directory_fuzzing: 'fas fa-folder',
      port_scanning: 'fas fa-network-wired',
      cloud_recon: 'fas fa-cloud',
      reporting_notification: 'fas fa-bell',
      utility_misc: 'fas fa-tools'
    };
    return icons[category] || 'fas fa-tools';
  };

  const getPhaseStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'running': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'pending': return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
      case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getPhaseIcon = (status) => {
    switch (status) {
      case 'completed': return 'fas fa-check-circle';
      case 'running': return 'fas fa-spinner fa-spin';
      case 'pending': return 'fas fa-clock';
      case 'failed': return 'fas fa-exclamation-triangle';
      default: return 'fas fa-question-circle';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Workflow Monitor</h1>
          <p className="text-gray-400">Monitor reconnaissance workflow execution in real-time</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-sm text-gray-400">Active Workflows</div>
            <div className="text-2xl font-bold text-cyan-400">{activeWorkflows.length}</div>
          </div>
        </div>
      </div>

      {/* Tool Categories Overview */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <i className="fas fa-layer-group mr-2 text-cyan-400"></i>
          Reconnaissance Tool Categories ({Object.values(toolStats.categories).reduce((sum, count) => sum + count, 0)} Tools)
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {Object.entries(toolStats.categories).map(([category, count]) => (
            <div 
              key={category} 
              className="border rounded-lg p-4 bg-gray-700 border-gray-600"
              style={{ borderLeftColor: getCategoryColor(category), borderLeftWidth: '4px' }}
            >
              <div className="flex items-center justify-between mb-2">
                <i 
                  className={`${getCategoryIcon(category)} text-lg`}
                  style={{ color: getCategoryColor(category) }}
                ></i>
                <span className="text-sm font-medium text-white">{count}</span>
              </div>
              
              <h4 className="font-semibold text-sm mb-1 text-white capitalize">
                {category.replace(/_/g, ' ')}
              </h4>
              
              <div className="text-xs text-gray-400">
                Tools available
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Workflows */}
      {activeWorkflows.length > 0 ? (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white flex items-center">
            <i className="fas fa-play mr-2 text-cyan-400"></i>
            Active Workflows ({activeWorkflows.length})
          </h2>
          
          {activeWorkflows.map((workflow) => (
            <div key={workflow.id} className="bg-gray-800 rounded-lg border border-gray-700">
              {/* Workflow Header */}
              <div className="p-6 border-b border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <i className="fas fa-globe mr-3 text-cyan-400 text-xl"></i>
                    <div>
                      <h3 className="text-xl font-semibold text-white">{workflow.target}</h3>
                      <p className="text-gray-400 text-sm">
                        Started: {new Date(workflow.start_time).toLocaleString()} • Tool: {workflow.tool_name}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-cyan-400">{workflow.status}</div>
                    <div className="text-sm text-gray-400">{workflow.category}</div>
                  </div>
                </div>
              </div>

              {/* Workflow Details */}
              <div className="p-6">
                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="text-white font-semibold mb-2">Results Preview</h4>
                  <pre className="text-sm text-gray-300 overflow-x-auto">
                    {JSON.stringify(workflow.results, null, 2).slice(0, 300)}...
                  </pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
          <i className="fas fa-play-circle text-6xl text-gray-600 mb-4"></i>
          <h3 className="text-xl font-semibold text-white mb-2">No Active Workflows</h3>
          <p className="text-gray-400">Start a new reconnaissance scan to see workflow progress here.</p>
        </div>
      )}

      {/* Workflow Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Tools</p>
              <p className="text-2xl font-bold text-white">
                {Object.values(toolStats.categories).reduce((sum, count) => sum + count, 0)}
              </p>
            </div>
            <i className="fas fa-tools text-2xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Installed Tools</p>
              <p className="text-2xl font-bold text-green-400">{toolStats.installation.installed}</p>
            </div>
            <i className="fas fa-download text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Online Tools</p>
              <p className="text-2xl font-bold text-blue-400">{toolStats.status.online}</p>
            </div>
            <i className="fas fa-check-circle text-2xl text-blue-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Workflows</p>
              <p className="text-2xl font-bold text-yellow-400">{activeWorkflows.length}</p>
            </div>
            <i className="fas fa-play text-2xl text-yellow-400"></i>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowMonitor;