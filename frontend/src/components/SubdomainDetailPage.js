import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const SubdomainDetailPage = () => {
  const { domainId, subdomain } = useParams();
  const navigate = useNavigate();
  const [target, setTarget] = useState(null);
  const [subdomainData, setSubdomainData] = useState(null);
  const [livenessResult, setLivenessResult] = useState(null);
  const [jsResults, setJsResults] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const decodedSubdomain = decodeURIComponent(subdomain);

  useEffect(() => {
    if (domainId && subdomain) {
      fetchSubdomainDetails();
    }
  }, [domainId, subdomain]);

  const fetchSubdomainDetails = async () => {
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

      // Fetch subdomain data
      const subdomainsResponse = await fetch(`${BACKEND_URL}/api/targets/${domainId}/subdomains`);
      if (subdomainsResponse.ok) {
        const subdomainsData = await subdomainsResponse.json();
        const foundSubdomain = subdomainsData.find(s => s.subdomain === decodedSubdomain);
        setSubdomainData(foundSubdomain);
      }

      // Fetch liveness results for this specific subdomain
      const livenessResponse = await fetch(`${BACKEND_URL}/api/targets/${domainId}/liveness-results`);
      if (livenessResponse.ok) {
        const livenessData = await livenessResponse.json();
        const subdomainLiveness = livenessData.find(l => l.subdomain === decodedSubdomain);
        setLivenessResult(subdomainLiveness);
      }

      // Fetch JavaScript results for this subdomain
      const jsResponse = await fetch(`${BACKEND_URL}/api/targets/${domainId}/javascript-results`);
      if (jsResponse.ok) {
        const jsData = await jsResponse.json();
        const subdomainJs = jsData.filter(js => js.subdomain === decodedSubdomain);
        setJsResults(subdomainJs);
      }

      // TODO: Fetch vulnerability results when available
      // For now using mock data
      setVulnerabilities([]);

    } catch (err) {
      setError(err.message);
      console.error('Error fetching subdomain details:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'live': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'dead': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 200: return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 403: return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 404: return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 500: return 'text-red-400 bg-red-400/10 border-red-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const handleStartScan = async (scanType) => {
    try {
      let endpoint = '';
      switch (scanType) {
        case 'liveness':
          endpoint = `/api/targets/${domainId}/check-liveness`;
          break;
        case 'javascript':
          endpoint = `/api/targets/${domainId}/analyze-javascript`;
          break;
        case 'vulnerability':
          endpoint = `/api/targets/${domainId}/scan-vulnerabilities`;
          break;
        default:
          return;
      }

      const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subdomain_filter: decodedSubdomain }),
      });

      if (response.ok) {
        // Refresh data after starting scan
        setTimeout(() => fetchSubdomainDetails(), 2000);
      }
    } catch (err) {
      console.error(`Error starting ${scanType} scan:`, err);
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
          <span className="text-red-400">Error: {error || 'Subdomain not found'}</span>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: 'fas fa-chart-pie' },
    { id: 'liveness', name: 'Liveness & Technologies', icon: 'fas fa-globe', count: livenessResult ? 1 : 0 },
    { id: 'ports', name: 'Ports & Services', icon: 'fas fa-network-wired', count: livenessResult?.open_ports?.length || 0 },
    { id: 'javascript', name: 'JavaScript Analysis', icon: 'fab fa-js-square', count: jsResults.length },
    { id: 'directories', name: 'Directories', icon: 'fas fa-folder', count: 0 },
    { id: 'vulnerabilities', name: 'Vulnerabilities', icon: 'fas fa-shield-alt', count: vulnerabilities.length }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <button
            onClick={() => navigate(`/scan-results/domain/${domainId}`)}
            className="bg-gray-700 hover:bg-gray-600 text-white p-2 rounded-lg mr-4 transition-colors"
          >
            <i className="fas fa-arrow-left"></i>
          </button>
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">{decodedSubdomain}</h1>
            <div className="flex items-center space-x-4">
              <span className="text-gray-400">Parent Domain: {target.domain}</span>
              <span className="text-gray-400">•</span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(livenessResult?.is_alive ? 'live' : 'dead')}`}>
                {livenessResult?.is_alive ? 'Live' : livenessResult ? 'Dead' : 'Unknown'}
              </span>
              {livenessResult?.status_code && (
                <>
                  <span className="text-gray-400">•</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(livenessResult.status_code)}`}>
                    {livenessResult.status_code}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => handleStartScan('liveness')}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fas fa-globe mr-2"></i>
            Check Liveness
          </button>
          <button 
            onClick={() => handleStartScan('javascript')}
            className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fab fa-js-square mr-2"></i>
            Analyze JS
          </button>
          <button 
            onClick={() => handleStartScan('vulnerability')}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fas fa-shield-alt mr-2"></i>
            Vuln Scan
          </button>
          <button 
            onClick={fetchSubdomainDetails}
            className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fas fa-sync mr-2"></i>
            Refresh
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <div className="bg-gradient-to-r from-green-600/10 to-emerald-600/10 border border-green-400/20 rounded-lg p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">{livenessResult?.is_alive ? 'Live' : 'Dead'}</div>
            <div className="text-gray-400 text-sm">Status</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-blue-600/10 to-cyan-600/10 border border-blue-400/20 rounded-lg p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">{livenessResult?.status_code || 'N/A'}</div>
            <div className="text-gray-400 text-sm">Status Code</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-purple-600/10 to-pink-600/10 border border-purple-400/20 rounded-lg p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">{livenessResult?.technologies?.length || 0}</div>
            <div className="text-gray-400 text-sm">Technologies</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-orange-600/10 to-red-600/10 border border-orange-400/20 rounded-lg p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-400">{livenessResult?.open_ports?.length || 0}</div>
            <div className="text-gray-400 text-sm">Open Ports</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-yellow-600/10 to-orange-600/10 border border-yellow-400/20 rounded-lg p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">{jsResults.length}</div>
            <div className="text-gray-400 text-sm">JS Files</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-red-600/10 to-pink-600/10 border border-red-400/20 rounded-lg p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">{vulnerabilities.length}</div>
            <div className="text-gray-400 text-sm">Vulnerabilities</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="border-b border-gray-700">
          <nav className="flex overflow-x-auto px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-6 border-b-2 font-medium text-sm flex items-center whitespace-nowrap ${
                  activeTab === tab.id
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
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Basic Information */}
              <div className="bg-gray-700 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Subdomain Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Subdomain:</span>
                      <span className="text-white font-mono">{decodedSubdomain}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Parent Domain:</span>
                      <span className="text-white">{target.domain}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Discovery Method:</span>
                      <span className="text-cyan-400">{subdomainData?.discovered_by?.join(', ') || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">First Seen:</span>
                      <span className="text-white">{formatDate(subdomainData?.first_seen)}</span>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Status:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(livenessResult?.is_alive ? 'live' : 'dead')}`}>
                        {livenessResult?.is_alive ? 'Live' : livenessResult ? 'Dead' : 'Unknown'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">IP Address:</span>
                      <span className="text-white font-mono">{livenessResult?.ip_addresses?.[0] || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Response Time:</span>
                      <span className="text-white">{livenessResult?.response_time || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Last Checked:</span>
                      <span className="text-white">{formatDate(livenessResult?.last_checked)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Screenshot */}
              {livenessResult?.screenshot && (
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Screenshot</h3>
                  <div className="bg-gray-800 rounded border border-gray-600 p-4">
                    <img 
                      src={livenessResult.screenshot} 
                      alt={`Screenshot of ${decodedSubdomain}`}
                      className="w-full max-w-2xl rounded border border-gray-600"
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'liveness' && (
            <div className="space-y-6">
              {livenessResult ? (
                <>
                  {/* Liveness Status */}
                  <div className="bg-gray-700 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Liveness Check Results</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Status:</span>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(livenessResult.is_alive ? 'live' : 'dead')}`}>
                            {livenessResult.is_alive ? 'Live' : 'Dead'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Status Code:</span>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(livenessResult.status_code)}`}>
                            {livenessResult.status_code}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Response Time:</span>
                          <span className="text-white">{livenessResult.response_time}</span>
                        </div>
                      </div>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Content Length:</span>
                          <span className="text-white">{livenessResult.content_length || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Server:</span>
                          <span className="text-white">{livenessResult.server || 'Unknown'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Title:</span>
                          <span className="text-white">{livenessResult.title || 'No title'}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Technologies */}
                  {livenessResult.technologies && livenessResult.technologies.length > 0 && (
                    <div className="bg-gray-700 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-white mb-4">Detected Technologies</h3>
                      <div className="flex flex-wrap gap-2">
                        {livenessResult.technologies.map((tech, index) => (
                          <span key={index} className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-sm">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* CDN/WAF Detection */}
                  {(livenessResult.cdn_name || livenessResult.waf_name) && (
                    <div className="bg-gray-700 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-white mb-4">Security & CDN</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {livenessResult.cdn_name && (
                          <div>
                            <span className="text-gray-400">CDN:</span>
                            <span className="text-cyan-400 ml-2">{livenessResult.cdn_name}</span>
                          </div>
                        )}
                        {livenessResult.waf_name && (
                          <div>
                            <span className="text-gray-400">WAF:</span>
                            <span className="text-red-400 ml-2">{livenessResult.waf_name}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="bg-gray-700 rounded-lg p-12 text-center">
                  <i className="fas fa-globe text-4xl text-gray-400 mb-4"></i>
                  <h3 className="text-xl font-semibold text-white mb-2">No Liveness Data</h3>
                  <p className="text-gray-400 mb-4">Run a liveness check to gather information about this subdomain.</p>
                  <button 
                    onClick={() => handleStartScan('liveness')}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg"
                  >
                    Start Liveness Check
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'ports' && (
            <div className="space-y-6">
              {livenessResult?.open_ports && livenessResult.open_ports.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {livenessResult.open_ports.map((port, index) => (
                    <div key={index} className="bg-gray-700 p-6 rounded-lg border border-gray-600">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-white">Port {port.port}</h3>
                          <p className="text-gray-400">{port.service} ({port.protocol})</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor('live')}`}>
                          Open
                        </span>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Service:</span>
                          <span className="text-white">{port.service}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Protocol:</span>
                          <span className="text-white">{port.protocol}</span>
                        </div>
                        {port.version && (
                          <div className="flex justify-between">
                            <span className="text-gray-400">Version:</span>
                            <span className="text-white">{port.version}</span>
                          </div>
                        )}
                      </div>
                      
                      {port.banner && (
                        <div className="mt-4 p-3 bg-gray-800 rounded">
                          <span className="text-gray-400 text-xs">Banner:</span>
                          <div className="text-green-400 text-xs font-mono mt-1">{port.banner}</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-gray-700 rounded-lg p-12 text-center">
                  <i className="fas fa-network-wired text-4xl text-gray-400 mb-4"></i>
                  <h3 className="text-xl font-semibold text-white mb-2">No Port Data</h3>
                  <p className="text-gray-400 mb-4">Port information will be available after liveness check.</p>
                  <button 
                    onClick={() => handleStartScan('liveness')}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg"
                  >
                    Start Liveness Check
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'javascript' && (
            <div className="space-y-6">
              {jsResults.length > 0 ? (
                <div className="space-y-4">
                  {jsResults.map((jsResult, index) => (
                    <div key={index} className="bg-gray-700 p-6 rounded-lg border border-gray-600">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-white font-medium">{jsResult.js_url}</h3>
                          <p className="text-gray-400 text-sm">Found by: {jsResult.discovered_by}</p>
                        </div>
                        <span className="text-cyan-400 font-mono">{jsResult.file_size || 'Unknown size'}</span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Endpoints:</span>
                            <span className="text-green-400">{jsResult.endpoints?.length || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Parameters:</span>
                            <span className="text-blue-400">{jsResult.parameters?.length || 0}</span>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Keywords:</span>
                            <span className="text-yellow-400">{jsResult.keywords?.length || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Secrets:</span>
                            <span className="text-red-400">{jsResult.secrets?.length || 0}</span>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Last Modified:</span>
                            <span className="text-white">{formatDate(jsResult.last_modified)}</span>
                          </div>
                        </div>
                      </div>
                      
                      {jsResult.secrets && jsResult.secrets.length > 0 && (
                        <div>
                          <span className="text-gray-400 text-sm">Potential Secrets:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {jsResult.secrets.map((secret, secretIndex) => (
                              <span key={secretIndex} className="px-2 py-1 bg-red-600/20 text-red-400 rounded text-xs">
                                {secret}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-gray-700 rounded-lg p-12 text-center">
                  <i className="fab fa-js-square text-4xl text-gray-400 mb-4"></i>
                  <h3 className="text-xl font-semibold text-white mb-2">No JavaScript Data</h3>
                  <p className="text-gray-400 mb-4">Run JavaScript analysis to discover JS files and extract endpoints.</p>
                  <button 
                    onClick={() => handleStartScan('javascript')}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-2 rounded-lg"
                  >
                    Start JS Analysis
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'directories' && (
            <div className="bg-gray-700 rounded-lg p-12 text-center">
              <i className="fas fa-folder text-4xl text-gray-400 mb-4"></i>
              <h3 className="text-xl font-semibold text-white mb-2">Directory Fuzzing</h3>
              <p className="text-gray-400 mb-4">Directory fuzzing results will be displayed here once implemented.</p>
              <button 
                className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg"
                disabled
              >
                Coming Soon
              </button>
            </div>
          )}

          {activeTab === 'vulnerabilities' && (
            <div className="bg-gray-700 rounded-lg p-12 text-center">
              <i className="fas fa-shield-alt text-4xl text-gray-400 mb-4"></i>
              <h3 className="text-xl font-semibold text-white mb-2">No Vulnerabilities Found</h3>
              <p className="text-gray-400 mb-4">Run vulnerability scans to discover potential security issues.</p>
              <button 
                onClick={() => handleStartScan('vulnerability')}
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg"
              >
                Start Vulnerability Scan
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SubdomainDetailPage;