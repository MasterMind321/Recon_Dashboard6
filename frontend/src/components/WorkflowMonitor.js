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

      {/* Workflow Orchestration Diagram */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <i className="fas fa-project-diagram mr-2 text-cyan-400"></i>
          Orchestration Flow
        </h2>
        
        <div className="relative">
          <img 
            src="https://images.pexels.com/photos/1054397/pexels-photo-1054397.jpeg" 
            alt="Network Infrastructure" 
            className="w-full h-32 object-cover rounded-lg opacity-20"
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-gray-900/80 rounded-lg p-4 text-center">
              <h3 className="text-white font-semibold mb-2">Recon Orchestration Pipeline</h3>
              <p className="text-gray-300 text-sm">
                Target → Subdomain Enum → ASN Expansion → DNS Resolution → Liveness → 
                Web Analysis → JS Extraction → Port Scan → Vulnerability Scan → Aggregation
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Active Workflows */}
      <div className="space-y-6">
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
                      Started: {workflow.startTime} • Current: {workflow.currentPhase}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-cyan-400">{workflow.progress}%</div>
                  <div className="text-sm text-gray-400">Complete</div>
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="mt-4">
                <div className="w-full bg-gray-600 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-cyan-400 to-blue-500 h-3 rounded-full transition-all duration-500"
                    style={{width: `${workflow.progress}%`}}
                  ></div>
                </div>
              </div>
            </div>

            {/* Workflow Phases */}
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {workflow.phases.map((phase, index) => (
                  <div key={index} className={`border rounded-lg p-4 ${getPhaseStatusColor(phase.status)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <i className={`${getPhaseIcon(phase.status)} text-lg`}></i>
                      <span className="text-sm font-medium">{phase.results}</span>
                    </div>
                    
                    <h4 className="font-semibold text-sm mb-2">{phase.name}</h4>
                    
                    <div className="space-y-1">
                      {phase.tools.map((tool, toolIndex) => (
                        <div key={toolIndex} className="flex items-center text-xs">
                          <div className={`w-2 h-2 rounded-full mr-2 ${
                            phase.status === 'completed' ? 'bg-green-400' :
                            phase.status === 'running' ? 'bg-yellow-400' : 'bg-gray-500'
                          }`}></div>
                          <span className="opacity-75">{tool}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Real-time Logs */}
            <div className="p-6 border-t border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                <i className="fas fa-terminal mr-2 text-cyan-400"></i>
                Real-time Logs
              </h4>
              <div className="bg-black rounded-lg p-4 font-mono text-sm max-h-32 overflow-y-auto">
                <div className="text-green-400">[2025-03-15 15:42:31] HTTPx: Checking liveness for 127 subdomains...</div>
                <div className="text-yellow-400">[2025-03-15 15:42:32] HTTPx: Found 89 live subdomains</div>
                <div className="text-cyan-400">[2025-03-15 15:42:33] Dalfox: Starting XSS scan on 45 parameters...</div>
                <div className="text-green-400">[2025-03-15 15:42:34] Dalfox: Found potential XSS in /search?q=</div>
                <div className="text-yellow-400">[2025-03-15 15:42:35] SQLMap: Testing 23 injection points...</div>
                <div className="text-red-400">[2025-03-15 15:42:36] SQLMap: SQL injection detected in /login.php</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Workflow Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Tools</p>
              <p className="text-2xl font-bold text-white">12</p>
            </div>
            <i className="fas fa-tools text-2xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Avg. Completion</p>
              <p className="text-2xl font-bold text-green-400">8.5h</p>
            </div>
            <i className="fas fa-clock text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Success Rate</p>
              <p className="text-2xl font-bold text-blue-400">94%</p>
            </div>
            <i className="fas fa-check-circle text-2xl text-blue-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Queue Length</p>
              <p className="text-2xl font-bold text-yellow-400">7</p>
            </div>
            <i className="fas fa-list text-2xl text-yellow-400"></i>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowMonitor;