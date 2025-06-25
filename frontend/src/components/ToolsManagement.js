import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ToolsManagement = () => {
  const [tools, setTools] = useState([]);
  const [toolStats, setToolStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  const categoryMap = {
    'all': 'All Tools',
    'subdomain_enumeration': '🟦 Subdomain Enumeration',
    'liveness_fingerprinting': '🟩 Liveness & Fingerprinting',
    'javascript_endpoint': '🟨 JavaScript/Endpoint Discovery',
    'vulnerability_scanning': '🟥 Vulnerability Scanning',
    'historical_data': '🟪 Historical Data & Archive',
    'directory_fuzzing': '🟧 Directory & File Fuzzing',
    'port_scanning': '🟫 Port Scanning & Network',
    'cloud_recon': '🟦 Cloud & S3 Recon',
    'reporting_notification': '🟨 Reporting & Notification',
    'utility_misc': '⚙️ Utility & Miscellaneous'
  };

  useEffect(() => {
    fetchTools();
    fetchToolStats();
  }, []);

  const fetchTools = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/tools`);
      setTools(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching tools:', error);
      setLoading(false);
    }
  };

  const fetchToolStats = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/tools/stats`);
      setToolStats(response.data);
    } catch (error) {
      console.error('Error fetching tool stats:', error);
    }
  };

  const installTool = async (toolId) => {
    try {
      await axios.post(`${BACKEND_URL}/api/tools/${toolId}/install`);
      // Update tool status in local state
      setTools(tools.map(tool => 
        tool.id === toolId 
          ? { ...tool, installation_status: 'updating' }
          : tool
      ));
      // Simulate installation completion after 3 seconds
      setTimeout(() => {
        setTools(tools.map(tool => 
          tool.id === toolId 
            ? { ...tool, installation_status: 'installed', tool_status: 'online' }
            : tool
        ));
        fetchToolStats(); // Refresh stats
      }, 3000);
    } catch (error) {
      console.error('Error installing tool:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'installed': return 'text-green-400 bg-green-400/10';
      case 'not_installed': return 'text-gray-400 bg-gray-400/10';
      case 'updating': return 'text-yellow-400 bg-yellow-400/10';
      case 'failed': return 'text-red-400 bg-red-400/10';
      case 'outdated': return 'text-orange-400 bg-orange-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const getToolStatusColor = (status) => {
    switch (status) {
      case 'online': return 'text-green-400';
      case 'busy': return 'text-yellow-400';
      case 'offline': return 'text-gray-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'installed': return 'fas fa-check-circle';
      case 'not_installed': return 'fas fa-download';
      case 'updating': return 'fas fa-spinner fa-spin';
      case 'failed': return 'fas fa-exclamation-triangle';
      case 'outdated': return 'fas fa-arrow-up';
      default: return 'fas fa-question-circle';
    }
  };

  const getToolStatusIcon = (status) => {
    switch (status) {
      case 'online': return 'fas fa-circle';
      case 'busy': return 'fas fa-spinner fa-spin';
      case 'offline': return 'fas fa-times-circle';
      case 'error': return 'fas fa-exclamation-triangle';
      default: return 'fas fa-question-circle';
    }
  };

  const filteredTools = tools.filter(tool => {
    const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory;
    const matchesSearch = tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tool.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const openConfigModal = (tool) => {
    setSelectedTool(tool);
    setShowConfigModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <i className="fas fa-spinner fa-spin text-4xl text-cyan-400"></i>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Tools Management</h1>
          <p className="text-gray-400">Install, configure, and manage reconnaissance tools</p>
        </div>
        <div className="flex items-center space-x-4">
          <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center">
            <i className="fas fa-sync mr-2"></i>
            Check Updates
          </button>
          <button className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg flex items-center">
            <i className="fas fa-download mr-2"></i>
            Install All
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Installed Tools</p>
              <p className="text-2xl font-bold text-green-400">{toolStats.installation?.installed || 0}</p>
            </div>
            <i className="fas fa-check-circle text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Not Installed</p>
              <p className="text-2xl font-bold text-gray-400">{toolStats.installation?.not_installed || 0}</p>
            </div>
            <i className="fas fa-download text-2xl text-gray-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Online Tools</p>
              <p className="text-2xl font-bold text-cyan-400">{toolStats.status?.online || 0}</p>
            </div>
            <i className="fas fa-circle text-2xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Updates Available</p>
              <p className="text-2xl font-bold text-orange-400">{toolStats.installation?.outdated || 0}</p>
            </div>
            <i className="fas fa-arrow-up text-2xl text-orange-400"></i>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Category Filter */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-400"
            >
              {Object.entries(categoryMap).map(([key, label]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
          </div>
          
          {/* Search */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-2">Search Tools</label>
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name or description..."
                className="w-full px-3 py-2 pl-10 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400"
              />
              <i className="fas fa-search absolute left-3 top-3 text-gray-400"></i>
            </div>
          </div>
        </div>
      </div>

      {/* Tools Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTools.map((tool) => (
          <div key={tool.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-cyan-400/50 transition-colors">
            {/* Tool Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div 
                  className="w-3 h-3 rounded-full mr-3"
                  style={{ backgroundColor: tool.icon_color }}
                ></div>
                <h3 className="text-lg font-semibold text-white">{tool.name}</h3>
              </div>
              <div className="flex items-center space-x-2">
                <i className={`${getToolStatusIcon(tool.tool_status)} text-sm ${getToolStatusColor(tool.tool_status)}`}></i>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(tool.installation_status)}`}>
                  <i className={`${getStatusIcon(tool.installation_status)} mr-1`}></i>
                  {tool.installation_status.replace('_', ' ')}
                </span>
              </div>
            </div>

            {/* Tool Description */}
            <p className="text-gray-400 text-sm mb-4">{tool.description}</p>
            <p className="text-gray-300 text-xs mb-4">{tool.usage_description}</p>

            {/* Install Command */}
            <div className="bg-gray-900 rounded p-3 mb-4">
              <code className="text-green-400 text-xs break-all">{tool.install_command}</code>
            </div>

            {/* Actions */}
            <div className="flex space-x-2">
              {tool.installation_status === 'not_installed' && (
                <button
                  onClick={() => installTool(tool.id)}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700 text-white py-2 px-3 rounded text-sm font-medium transition-colors"
                >
                  <i className="fas fa-download mr-1"></i>
                  Install
                </button>
              )}
              
              {tool.installation_status === 'installed' && (
                <>
                  <button
                    onClick={() => openConfigModal(tool)}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 rounded text-sm font-medium transition-colors"
                  >
                    <i className="fas fa-cog mr-1"></i>
                    Configure
                  </button>
                  <button className="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded text-sm transition-colors">
                    <i className="fas fa-sync"></i>
                  </button>
                </>
              )}
              
              {tool.installation_status === 'updating' && (
                <button disabled className="flex-1 bg-gray-600 text-white py-2 px-3 rounded text-sm font-medium">
                  <i className="fas fa-spinner fa-spin mr-1"></i>
                  Installing...
                </button>
              )}
              
              {tool.installation_status === 'outdated' && (
                <button
                  onClick={() => installTool(tool.id)}
                  className="flex-1 bg-orange-600 hover:bg-orange-700 text-white py-2 px-3 rounded text-sm font-medium transition-colors"
                >
                  <i className="fas fa-arrow-up mr-1"></i>
                  Update
                </button>
              )}
            </div>

            {/* Resource Usage (if installed) */}
            {tool.installation_status === 'installed' && (
              <div className="mt-4 pt-4 border-t border-gray-700">
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>CPU: {tool.cpu_usage}%</span>
                  <span>Memory: {tool.memory_usage}%</span>
                </div>
                <div className="flex space-x-2">
                  <div className="flex-1 bg-gray-600 rounded-full h-1">
                    <div 
                      className="bg-cyan-400 h-1 rounded-full transition-all duration-300"
                      style={{width: `${tool.cpu_usage}%`}}
                    ></div>
                  </div>
                  <div className="flex-1 bg-gray-600 rounded-full h-1">
                    <div 
                      className="bg-yellow-400 h-1 rounded-full transition-all duration-300"
                      style={{width: `${tool.memory_usage}%`}}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredTools.length === 0 && (
        <div className="text-center py-12">
          <i className="fas fa-search text-4xl text-gray-400 mb-4"></i>
          <p className="text-gray-400">No tools found matching your criteria</p>
        </div>
      )}

      {/* Configuration Modal */}
      {showConfigModal && selectedTool && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">Configure {selectedTool.name}</h3>
              <button
                onClick={() => setShowConfigModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Configuration File Path
                </label>
                <input
                  type="text"
                  defaultValue={`/etc/${selectedTool.name}/${selectedTool.name}.conf`}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-400"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Custom Parameters
                </label>
                <textarea
                  rows="4"
                  placeholder="Enter custom command line parameters..."
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400"
                ></textarea>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button className="flex-1 bg-cyan-600 hover:bg-cyan-700 text-white py-2 rounded-lg font-semibold transition-colors">
                  Save Configuration
                </button>
                <button
                  onClick={() => setShowConfigModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-lg font-semibold transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolsManagement;