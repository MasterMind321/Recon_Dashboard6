import React, { useState, useEffect } from 'react';

const TargetManagement = () => {
  const [targets, setTargets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    total_targets: 0,
    active_scans: 0,
    total_subdomains: 0,
    total_vulnerabilities: 0,
    by_status: {},
    by_type: {},
    by_severity: {}
  });
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTarget, setNewTarget] = useState({
    domain: '',
    type: 'domain',
    workflow: 'full-recon',
    notes: ''
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Fetch targets and stats
  const fetchTargets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [targetsResponse, statsResponse] = await Promise.all([
        fetch(`${backendUrl}/api/targets`),
        fetch(`${backendUrl}/api/targets/stats`)
      ]);

      if (!targetsResponse.ok || !statsResponse.ok) {
        throw new Error('Failed to fetch data');
      }

      const targetsData = await targetsResponse.json();
      const statsData = await statsResponse.json();

      setTargets(targetsData);
      setStats(statsData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching targets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTargets();
  }, []);

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-400/10';
      case 'scanning': return 'text-yellow-400 bg-yellow-400/10';
      case 'pending': return 'text-gray-400 bg-gray-400/10';
      case 'completed': return 'text-blue-400 bg-blue-400/10';
      case 'failed': return 'text-red-400 bg-red-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-400/10';
      case 'high': return 'text-orange-400 bg-orange-400/10';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10';
      case 'low': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const handleAddTarget = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${backendUrl}/api/targets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          domain: newTarget.domain,
          type: newTarget.type,
          workflow: newTarget.workflow,
          notes: newTarget.notes || null
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create target');
      }

      // Refresh targets and stats
      await fetchTargets();
      
      // Reset form and close modal
      setNewTarget({ domain: '', type: 'domain', workflow: 'full-recon', notes: '' });
      setShowAddModal(false);
    } catch (err) {
      setError(err.message);
      console.error('Error creating target:', err);
    }
  };

  const startScan = async (targetId) => {
    try {
      const response = await fetch(`${backendUrl}/api/targets/${targetId}/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to start scan');
      }

      // Refresh targets to get updated status
      await fetchTargets();
    } catch (err) {
      setError(err.message);
      console.error('Error starting scan:', err);
    }
  };

  const deleteTarget = async (targetId) => {
    if (!window.confirm('Are you sure you want to delete this target?')) {
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/targets/${targetId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete target');
      }

      // Refresh targets and stats
      await fetchTargets();
    } catch (err) {
      setError(err.message);
      console.error('Error deleting target:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-300 px-4 py-3 rounded-lg">
          <div className="flex items-center">
            <i className="fas fa-exclamation-triangle mr-2"></i>
            <span>{error}</span>
            <button 
              onClick={() => setError(null)}
              className="ml-auto text-red-300 hover:text-white"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Target Management</h1>
          <p className="text-gray-400">Manage your reconnaissance targets and initiate scans</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center transition-colors"
        >
          <i className="fas fa-plus mr-2"></i>
          Add Target
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Targets</p>
              <p className="text-xl font-bold text-white">{stats.total_targets}</p>
            </div>
            <i className="fas fa-bullseye text-xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Scans</p>
              <p className="text-xl font-bold text-yellow-400">{stats.active_scans}</p>
            </div>
            <i className="fas fa-spinner fa-spin text-xl text-yellow-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Subdomains</p>
              <p className="text-xl font-bold text-green-400">{stats.total_subdomains}</p>
            </div>
            <i className="fas fa-sitemap text-xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Vulnerabilities</p>
              <p className="text-xl font-bold text-red-400">{stats.total_vulnerabilities}</p>
            </div>
            <i className="fas fa-shield-alt text-xl text-red-400"></i>
          </div>
        </div>
      </div>

      {/* Targets Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white flex items-center">
            <i className="fas fa-list mr-2 text-cyan-400"></i>
            Target List
          </h2>
        </div>
        
        {loading ? (
          <div className="p-6 text-center">
            <i className="fas fa-spinner fa-spin text-2xl text-cyan-400 mb-4"></i>
            <p className="text-gray-400">Loading targets...</p>
          </div>
        ) : targets.length === 0 ? (
          <div className="p-6 text-center">
            <i className="fas fa-bullseye text-4xl text-gray-600 mb-4"></i>
            <h3 className="text-lg font-semibold text-gray-400 mb-2">No Targets Found</h3>
            <p className="text-gray-500 mb-4">Get started by adding your first reconnaissance target.</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              <i className="fas fa-plus mr-2"></i>
              Add Target
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Target
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Subdomains
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Vulnerabilities
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Last Scan
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {targets.map((target) => (
                  <tr key={target.id} className="hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <i className={`fas ${target.type === 'domain' ? 'fa-globe' : target.type === 'ip' ? 'fa-server' : 'fa-network-wired'} mr-3 text-cyan-400`}></i>
                        <span className="text-white font-medium">{target.domain}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-gray-300 capitalize">{target.type}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(target.status)}`}>
                        {target.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-white">
                      {target.subdomains}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-white mr-2">{target.vulnerabilities}</span>
                        {target.severity !== 'none' && (
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(target.severity)}`}>
                            {target.severity}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-400 text-sm">
                      {formatDate(target.last_scan)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => startScan(target.id)}
                          disabled={target.status === 'scanning'}
                          className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors"
                        >
                          {target.status === 'scanning' ? 'Scanning...' : 'Scan'}
                        </button>
                        <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors">
                          View
                        </button>
                        <button 
                          onClick={() => deleteTarget(target.id)}
                          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Target Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white">Add New Target</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <form onSubmit={handleAddTarget} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Target
                </label>
                <input
                  type="text"
                  value={newTarget.domain}
                  onChange={(e) => setNewTarget({...newTarget, domain: e.target.value})}
                  placeholder="example.com or 192.168.1.0/24"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Type
                </label>
                <select
                  value={newTarget.type}
                  onChange={(e) => setNewTarget({...newTarget, type: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-400"
                >
                  <option value="domain">Domain</option>
                  <option value="ip">IP Address</option>
                  <option value="cidr">CIDR Range</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Workflow
                </label>
                <select
                  value={newTarget.workflow}
                  onChange={(e) => setNewTarget({...newTarget, workflow: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-400"
                >
                  <option value="full-recon">Full Reconnaissance</option>
                  <option value="subdomain-only">Subdomain Enumeration Only</option>
                  <option value="vuln-scan">Vulnerability Scanning</option>
                  <option value="port-scan">Port Scanning</option>
                </select>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700 text-white py-2 rounded-lg font-semibold transition-colors"
                >
                  Add Target
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-lg font-semibold transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TargetManagement;