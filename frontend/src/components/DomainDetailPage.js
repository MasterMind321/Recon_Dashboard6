import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const DomainDetailPage = () => {
  const { domainId } = useParams();
  const navigate = useNavigate();
  const [target, setTarget] = useState(null);
  const [subdomains, setSubdomains] = useState([]);
  const [livenessResults, setLivenessResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('overview');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (domainId) {
      fetchDomainDetails();
    }
  }, [domainId]);

  const fetchDomainDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch target details
      const targetResponse = await fetch(`${BACKEND_URL}/api/targets/${domainId}`);
      if (!targetResponse.ok) {
        throw new Error('Target not found');
      }
      const targetData = await targetResponse.json();
      setTarget(targetData);

      // Fetch all scan results for this domain
      const [subdomainsResponse, livenessResponse] = await Promise.all([
        fetch(`${BACKEND_URL}/api/targets/${domainId}/subdomains`).catch(() => ({ ok: false })),
        fetch(`${BACKEND_URL}/api/targets/${domainId}/liveness-results`).catch(() => ({ ok: false }))
      ]);

      if (subdomainsResponse.ok) {
        const subdomainsData = await subdomainsResponse.json();
        setSubdomains(subdomainsData);
      }

      if (livenessResponse.ok) {
        const livenessData = await livenessResponse.json();
        setLivenessResults(livenessData);
      }

    } catch (err) {
      setError(err.message);
      console.error('Error fetching domain details:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'live': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'dead': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'active': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'scanning': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'pending': return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
      case 'completed': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const handleViewSubdomain = (subdomain) => {
    navigate(`/scan-results/domain/${domainId}/subdomain/${encodeURIComponent(subdomain.subdomain)}`);
  };

  const handleStartScan = async (scanType = 'full') => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/targets/${domainId}/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ scan_type: scanType }),
      });

      if (response.ok) {
        // Refresh data after starting scan
        await fetchDomainDetails();
        // Show success message or update UI
      }
    } catch (err) {
      console.error('Error starting scan:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <i className="fas fa-spinner fa-spin text-4xl text-cyan-400"></i>
      </div>
    );
  }

  if (error || !target) {
    return (
      <div className="bg-red-600/10 border border-red-400/20 rounded-lg p-6">
        <div className="flex items-center">
          <i className="fas fa-exclamation-triangle text-red-400 mr-3"></i>
          <span className="text-red-400">Error: {error || 'Domain not found'}</span>
        </div>
      </div>
    );
  }

  const liveSubdomains = livenessResults.filter(result => result.is_alive);
  const deadSubdomains = livenessResults.filter(result => !result.is_alive);
  const uniqueTechnologies = [...new Set(livenessResults.flatMap(result => result.technologies || []))];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <button
            onClick={() => navigate('/scan-results')}
            className="bg-gray-700 hover:bg-gray-600 text-white p-2 rounded-lg mr-4 transition-colors"
          >
            <i className="fas fa-arrow-left"></i>
          </button>
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">{target.domain}</h1>
            <div className="flex items-center space-x-4">
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(target.status)}`}>
                {target.status}
              </span>
              <span className="text-gray-400">{target.type}</span>
              <span className="text-gray-400">•</span>
              <span className="text-gray-400">Last scan: {formatDate(target.last_scan)}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => handleStartScan('subdomain')}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fas fa-sitemap mr-2"></i>
            Enumerate Subdomains
          </button>
          <button 
            onClick={() => handleStartScan('full')}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fas fa-play mr-2"></i>
            Start Full Scan
          </button>
          <button 
            onClick={fetchDomainDetails}
            className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fas fa-sync mr-2"></i>
            Refresh
          </button>
        </div>
      </div>

      {/* Domain Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-gradient-to-r from-cyan-600/10 to-blue-600/10 border border-cyan-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Subdomains</p>
              <p className="text-2xl font-bold text-cyan-400">{subdomains.length}</p>
            </div>
            <i className="fas fa-sitemap text-2xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-600/10 to-emerald-600/10 border border-green-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Live Subdomains</p>
              <p className="text-2xl font-bold text-green-400">{liveSubdomains.length}</p>
            </div>
            <i className="fas fa-globe text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-red-600/10 to-orange-600/10 border border-red-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Dead Subdomains</p>
              <p className="text-2xl font-bold text-red-400">{deadSubdomains.length}</p>
            </div>
            <i className="fas fa-times-circle text-2xl text-red-400"></i>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-purple-600/10 to-pink-600/10 border border-purple-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Technologies</p>
              <p className="text-2xl font-bold text-purple-400">{uniqueTechnologies.length}</p>
            </div>
            <i className="fas fa-cogs text-2xl text-purple-400"></i>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-yellow-600/10 to-orange-600/10 border border-yellow-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Vulnerabilities</p>
              <p className="text-2xl font-bold text-yellow-400">{target.vulnerabilities || 0}</p>
            </div>
            <i className="fas fa-shield-alt text-2xl text-yellow-400"></i>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="border-b border-gray-700">
          <nav className="flex overflow-x-auto px-6" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Overview', icon: 'fas fa-chart-pie' },
              { id: 'subdomains', name: 'Subdomains', icon: 'fas fa-sitemap', count: subdomains.length },
              { id: 'workflow', name: 'Recon Workflow', icon: 'fas fa-project-diagram' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id)}
                className={`py-4 px-6 border-b-2 font-medium text-sm flex items-center whitespace-nowrap ${
                  activeView === tab.id
                    ? 'border-cyan-400 text-cyan-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                <i className={`${tab.icon} mr-2`}></i>
                {tab.name}
                {tab.count !== undefined && (
                  <span className="ml-2 bg-gray-700 text-gray-300 py-0.5 px-2 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeView === 'overview' && (
            <div className="space-y-6">
              {/* Domain Information */}
              <div className="bg-gray-700 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Domain Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Domain:</span>
                        <span className="text-white font-mono">{target.domain}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Type:</span>
                        <span className="text-white">{target.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Workflow:</span>
                        <span className="text-cyan-400">{target.workflow || 'full-recon'}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Created:</span>
                        <span className="text-white">{formatDate(target.created_at)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Last Updated:</span>
                        <span className="text-white">{formatDate(target.updated_at)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Last Scan:</span>
                        <span className="text-white">{formatDate(target.last_scan)}</span>
                      </div>
                    </div>
                  </div>
                </div>
                {target.notes && (
                  <div className="mt-4 pt-4 border-t border-gray-600">
                    <span className="text-gray-400 text-sm">Notes:</span>
                    <p className="text-white mt-1">{target.notes}</p>
                  </div>
                )}
              </div>

              {/* Quick Technology Overview */}
              {uniqueTechnologies.length > 0 && (
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Detected Technologies</h3>
                  <div className="flex flex-wrap gap-2">
                    {uniqueTechnologies.slice(0, 20).map((tech, index) => (
                      <span key={index} className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-sm">
                        {tech}
                      </span>
                    ))}
                    {uniqueTechnologies.length > 20 && (
                      <span className="px-3 py-1 bg-gray-600 text-gray-400 rounded-full text-sm">
                        +{uniqueTechnologies.length - 20} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeView === 'subdomains' && (
            <div className="space-y-4">
              {/* Subdomain Filters */}
              <div className="flex space-x-4 mb-6">
                <button className="bg-green-600/20 text-green-400 px-4 py-2 rounded-lg border border-green-400/20">
                  Live ({liveSubdomains.length})
                </button>
                <button className="bg-red-600/20 text-red-400 px-4 py-2 rounded-lg border border-red-400/20">
                  Dead ({deadSubdomains.length})
                </button>
                <button className="bg-gray-600/20 text-gray-400 px-4 py-2 rounded-lg border border-gray-400/20">
                  All ({subdomains.length})
                </button>
              </div>

              {/* Subdomain List */}
              {subdomains.length === 0 ? (
                <div className="bg-gray-700 rounded-lg p-12 text-center">
                  <i className="fas fa-sitemap text-4xl text-gray-400 mb-4"></i>
                  <h3 className="text-xl font-semibold text-white mb-2">No Subdomains Found</h3>
                  <p className="text-gray-400 mb-4">Start subdomain enumeration to discover subdomains for this domain.</p>
                  <button 
                    onClick={() => handleStartScan('subdomain')}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg"
                  >
                    Start Subdomain Enumeration
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-4">
                  {subdomains.map((subdomain, index) => {
                    const livenessResult = livenessResults.find(lr => lr.subdomain === subdomain.subdomain);
                    return (
                      <div key={index} className="bg-gray-700 rounded-lg border border-gray-600 p-6 hover:border-cyan-400/50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <i className="fas fa-globe mr-3 text-cyan-400"></i>
                            <div>
                              <h4 className="text-lg font-semibold text-white">{subdomain.subdomain}</h4>
                              <div className="flex items-center space-x-3 mt-1">
                                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(livenessResult?.is_alive ? 'live' : 'dead')}`}>
                                  {livenessResult?.is_alive ? 'Live' : 'Dead'}
                                </span>
                                {livenessResult?.ip_addresses?.length > 0 && (
                                  <span className="text-gray-400 text-sm font-mono">{livenessResult.ip_addresses[0]}</span>
                                )}
                                <span className="text-gray-400 text-sm">
                                  Found by: {subdomain.discovered_by?.join(', ') || 'Unknown'}
                                </span>
                              </div>
                            </div>
                          </div>
                          <button
                            onClick={() => handleViewSubdomain(subdomain)}
                            className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
                          >
                            <i className="fas fa-eye mr-2"></i>
                            View Details
                          </button>
                        </div>
                        
                        {livenessResult?.technologies?.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-600">
                            <div className="flex flex-wrap gap-2">
                              {livenessResult.technologies.slice(0, 5).map((tech, techIndex) => (
                                <span key={techIndex} className="px-2 py-1 bg-purple-600/20 text-purple-400 rounded text-xs">
                                  {tech}
                                </span>
                              ))}
                              {livenessResult.technologies.length > 5 && (
                                <span className="px-2 py-1 bg-gray-600 text-gray-400 rounded text-xs">
                                  +{livenessResult.technologies.length - 5} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {activeView === 'workflow' && (
            <div className="space-y-6">
              <div className="bg-gray-700 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Reconnaissance Workflow Status</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-800 rounded">
                    <div className="flex items-center">
                      <i className="fas fa-sitemap text-cyan-400 mr-3"></i>
                      <span className="text-white">Subdomain Enumeration</span>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(subdomains.length > 0 ? 'completed' : 'pending')}`}>
                      {subdomains.length > 0 ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-800 rounded">
                    <div className="flex items-center">
                      <i className="fas fa-globe text-green-400 mr-3"></i>
                      <span className="text-white">Liveness Check</span>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(livenessResults.length > 0 ? 'completed' : 'pending')}`}>
                      {livenessResults.length > 0 ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-800 rounded">
                    <div className="flex items-center">
                      <i className="fas fa-camera text-purple-400 mr-3"></i>
                      <span className="text-white">Screenshots</span>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor('pending')}`}>
                      Pending
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-800 rounded">
                    <div className="flex items-center">
                      <i className="fas fa-code text-yellow-400 mr-3"></i>
                      <span className="text-white">JavaScript Analysis</span>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor('pending')}`}>
                      Pending
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-gray-800 rounded">
                    <div className="flex items-center">
                      <i className="fas fa-shield-alt text-red-400 mr-3"></i>
                      <span className="text-white">Vulnerability Scanning</span>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor('pending')}`}>
                      Pending
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DomainDetailPage;