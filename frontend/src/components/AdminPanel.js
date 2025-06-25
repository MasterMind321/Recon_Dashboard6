import React, { useState } from 'react';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data for admin panel
  const systemMetrics = {
    cpu: 67,
    memory: 78,
    disk: 45,
    network: 23
  };

  const queueStats = {
    pending: 7,
    running: 3,
    completed: 156,
    failed: 4
  };

  const toolStatus = [
    { name: 'Subfinder', status: 'online', cpu: 12, memory: 45, lastUsed: '2 mins ago' },
    { name: 'Amass', status: 'online', cpu: 8, memory: 67, lastUsed: '5 mins ago' },
    { name: 'HTTPx', status: 'busy', cpu: 45, memory: 23, lastUsed: 'Running' },
    { name: 'Nuclei', status: 'online', cpu: 23, memory: 34, lastUsed: '1 min ago' },
    { name: 'Nmap', status: 'busy', cpu: 78, memory: 89, lastUsed: 'Running' },
    { name: 'FFUF', status: 'offline', cpu: 0, memory: 0, lastUsed: '1 hour ago' },
    { name: 'Dalfox', status: 'online', cpu: 34, memory: 56, lastUsed: '3 mins ago' },
    { name: 'SQLMap', status: 'online', cpu: 15, memory: 28, lastUsed: '8 mins ago' }
  ];

  const recentJobs = [
    {
      id: 'job_001',
      target: 'example.com',
      workflow: 'Full Recon',
      status: 'completed',
      duration: '2h 34m',
      startTime: '2025-03-15 13:15:00',
      endTime: '2025-03-15 15:49:00'
    },
    {
      id: 'job_002',
      target: 'target.com',
      workflow: 'Subdomain Only',
      status: 'running',
      duration: '45m',
      startTime: '2025-03-15 14:30:00',
      endTime: null
    },
    {
      id: 'job_003',
      target: 'testsite.org',
      workflow: 'Vulnerability Scan',
      status: 'failed',
      duration: '12m',
      startTime: '2025-03-15 16:20:00',
      endTime: '2025-03-15 16:32:00'
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'text-green-400 bg-green-400/10';
      case 'busy': return 'text-yellow-400 bg-yellow-400/10';
      case 'offline': return 'text-red-400 bg-red-400/10';
      case 'completed': return 'text-green-400 bg-green-400/10';
      case 'running': return 'text-yellow-400 bg-yellow-400/10';
      case 'failed': return 'text-red-400 bg-red-400/10';
      case 'pending': return 'text-gray-400 bg-gray-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online': return 'fas fa-circle';
      case 'busy': return 'fas fa-spinner fa-spin';
      case 'offline': return 'fas fa-times-circle';
      case 'completed': return 'fas fa-check-circle';
      case 'running': return 'fas fa-spinner fa-spin';
      case 'failed': return 'fas fa-exclamation-triangle';
      case 'pending': return 'fas fa-clock';
      default: return 'fas fa-question-circle';
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">CPU Usage</span>
            <span className="text-white font-bold">{systemMetrics.cpu}%</span>
          </div>
          <div className="w-full bg-gray-600 rounded-full h-2">
            <div 
              className="bg-cyan-400 h-2 rounded-full transition-all duration-300"
              style={{width: `${systemMetrics.cpu}%`}}
            ></div>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Memory</span>
            <span className="text-white font-bold">{systemMetrics.memory}%</span>
          </div>
          <div className="w-full bg-gray-600 rounded-full h-2">
            <div 
              className="bg-yellow-400 h-2 rounded-full transition-all duration-300"
              style={{width: `${systemMetrics.memory}%`}}
            ></div>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Disk Usage</span>
            <span className="text-white font-bold">{systemMetrics.disk}%</span>
          </div>
          <div className="w-full bg-gray-600 rounded-full h-2">
            <div 
              className="bg-green-400 h-2 rounded-full transition-all duration-300"
              style={{width: `${systemMetrics.disk}%`}}
            ></div>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Network I/O</span>
            <span className="text-white font-bold">{systemMetrics.network}%</span>
          </div>
          <div className="w-full bg-gray-600 rounded-full h-2">
            <div 
              className="bg-purple-400 h-2 rounded-full transition-all duration-300"
              style={{width: `${systemMetrics.network}%`}}
            ></div>
          </div>
        </div>
      </div>
      
      {/* Queue Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Pending Jobs</p>
              <p className="text-2xl font-bold text-yellow-400">{queueStats.pending}</p>
            </div>
            <i className="fas fa-clock text-2xl text-yellow-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Running Jobs</p>
              <p className="text-2xl font-bold text-cyan-400">{queueStats.running}</p>
            </div>
            <i className="fas fa-spinner fa-spin text-2xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Completed</p>
              <p className="text-2xl font-bold text-green-400">{queueStats.completed}</p>
            </div>
            <i className="fas fa-check-circle text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Failed Jobs</p>
              <p className="text-2xl font-bold text-red-400">{queueStats.failed}</p>
            </div>
            <i className="fas fa-exclamation-triangle text-2xl text-red-400"></i>
          </div>
        </div>
      </div>
    </div>
  );

  const renderToolStatus = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {toolStatus.map((tool, index) => (
        <div key={index} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <i className={`${getStatusIcon(tool.status)} mr-3 text-lg`}></i>
              <h3 className="text-lg font-semibold text-white">{tool.name}</h3>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(tool.status)}`}>
              {tool.status}
            </span>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">CPU Usage</span>
              <span className="text-white">{tool.cpu}%</span>
            </div>
            <div className="w-full bg-gray-600 rounded-full h-2">
              <div 
                className="bg-cyan-400 h-2 rounded-full transition-all duration-300"
                style={{width: `${tool.cpu}%`}}
              ></div>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Memory Usage</span>
              <span className="text-white">{tool.memory}%</span>
            </div>
            <div className="w-full bg-gray-600 rounded-full h-2">
              <div 
                className="bg-yellow-400 h-2 rounded-full transition-all duration-300"
                style={{width: `${tool.memory}%`}}
              ></div>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Last Used</span>
              <span className="text-gray-300">{tool.lastUsed}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderJobQueue = () => (
    <div className="space-y-4">
      {recentJobs.map((job) => (
        <div key={job.id} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <i className={`${getStatusIcon(job.status)} text-lg`}></i>
              <div>
                <h3 className="text-lg font-semibold text-white">{job.id}</h3>
                <p className="text-gray-400">{job.target} • {job.workflow}</p>
              </div>
            </div>
            <div className="text-right">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                {job.status}
              </span>
              <p className="text-sm text-gray-400 mt-1">Duration: {job.duration}</p>
            </div>
          </div>
          
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Start Time:</span>
              <span className="text-white ml-2">{job.startTime}</span>
            </div>
            <div>
              <span className="text-gray-400">End Time:</span>
              <span className="text-white ml-2">{job.endTime || 'Running...'}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const tabs = [
    { id: 'overview', name: 'System Overview', icon: 'fas fa-tachometer-alt' },
    { id: 'queue', name: 'Job Queue', icon: 'fas fa-list' },
    { id: 'logs', name: 'System Logs', icon: 'fas fa-file-alt' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Admin Panel</h1>
          <p className="text-gray-400">Monitor system performance and manage reconnaissance tools</p>
        </div>
        <div className="flex items-center space-x-4">
          <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center">
            <i className="fas fa-power-off mr-2"></i>
            Emergency Stop
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center">
            <i className="fas fa-sync mr-2"></i>
            Restart Services
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="border-b border-gray-700">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-cyan-400 text-cyan-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                <i className={`${tab.icon} mr-2`}></i>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'queue' && renderJobQueue()}
          {activeTab === 'logs' && (
            <div className="bg-black rounded-lg p-4 font-mono text-sm max-h-96 overflow-y-auto">
              <div className="text-green-400">[2025-03-15 15:42:31] INFO: System startup completed</div>
              <div className="text-yellow-400">[2025-03-15 15:42:32] WARN: High memory usage detected</div>
              <div className="text-cyan-400">[2025-03-15 15:42:33] INFO: New scan job queued: example.com</div>
              <div className="text-green-400">[2025-03-15 15:42:34] INFO: Subfinder process started</div>
              <div className="text-red-400">[2025-03-15 15:42:35] ERROR: FFUF service connection failed</div>
              <div className="text-yellow-400">[2025-03-15 15:42:36] WARN: Queue length exceeded threshold</div>
              <div className="text-green-400">[2025-03-15 15:42:37] INFO: Subdomain enumeration completed</div>
              <div className="text-cyan-400">[2025-03-15 15:42:38] INFO: Starting vulnerability scan</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;