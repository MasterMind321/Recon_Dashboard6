import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const DomainResultsOverview = () => {
  const [targets, setTargets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({});
  const navigate = useNavigate();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchTargetsWithResults();
  }, []);

  const fetchTargetsWithResults = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch targets and their basic stats
      const [targetsResponse, statsResponse] = await Promise.all([
        fetch(`${BACKEND_URL}/api/targets`),
        fetch(`${BACKEND_URL}/api/targets/stats`)
      ]);

      if (!targetsResponse.ok || !statsResponse.ok) {
        throw new Error('Failed to fetch data');
      }

      const targetsData = await targetsResponse.json();
      const statsData = await statsResponse.json();

      // For each target, fetch additional scan results
      const targetsWithResults = await Promise.all(
        targetsData.map(async (target) => {
          try {
            const [subdomainsResponse, livenessResponse, jsResponse, vulnResponse] = await Promise.all([
              fetch(`${BACKEND_URL}/api/targets/${target.id}/subdomains`).catch(() => ({ ok: false })),
              fetch(`${BACKEND_URL}/api/targets/${target.id}/liveness-results`).catch(() => ({ ok: false })),
              fetch(`${BACKEND_URL}/api/targets/${target.id}/javascript-results`).catch(() => ({ ok: false })),
              fetch(`${BACKEND_URL}/api/vulnerability/stats`).catch(() => ({ ok: false }))
            ]);

            let subdomains = [];
            let livenessResults = [];
            let jsResults = [];
            let vulnStats = { total_vulnerabilities: 0 };

            if (subdomainsResponse.ok) {
              subdomains = await subdomainsResponse.json();
            }
            if (livenessResponse.ok) {
              livenessResults = await livenessResponse.json();
            }
            if (jsResponse.ok) {
              jsResults = await jsResponse.json();
            }
            if (vulnResponse.ok) {
              vulnStats = await vulnResponse.json();
            }

            const liveSubdomains = livenessResults.filter(result => result.is_alive).length;
            const totalTechnologies = [...new Set(livenessResults.flatMap(result => result.technologies || []))].length;
            const jsFiles = jsResults.length;

            return {
              ...target,
              scanResults: {
                totalSubdomains: subdomains.length,
                liveSubdomains: liveSubdomains,
                technologies: totalTechnologies,
                jsFiles: jsFiles,
                vulnerabilities: vulnStats.total_vulnerabilities || 0,
                lastScanTime: target.last_scan || target.updated_at
              }
            };
          } catch (err) {
            console.error(`Error fetching results for target ${target.id}:`, err);
            return {
              ...target,
              scanResults: {
                totalSubdomains: target.subdomains || 0,
                liveSubdomains: 0,
                technologies: 0,
                jsFiles: 0,
                vulnerabilities: target.vulnerabilities || 0,
                lastScanTime: target.last_scan || target.updated_at
              }
            };
          }
        })
      );

      setTargets(targetsWithResults);
      setStats(statsData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching targets:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'scanning': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'pending': return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
      case 'completed': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'failed': return 'text-red-400 bg-red-400/10 border-red-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
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

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const handleViewDomain = (target) => {
    navigate(`/scan-results/domain/${target.id}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <i className="fas fa-spinner fa-spin text-4xl text-cyan-400"></i>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-600/10 border border-red-400/20 rounded-lg p-6">
        <div className="flex items-center">
          <i className="fas fa-exclamation-triangle text-red-400 mr-3"></i>
          <span className="text-red-400">Error loading targets: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Domain Reconnaissance Results</h1>
          <p className="text-gray-400">Hierarchical view of all target domains and their comprehensive scan results</p>
        </div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={fetchTargetsWithResults}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fas fa-sync mr-2"></i>
            Refresh All
          </button>
        </div>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-cyan-600/10 to-blue-600/10 border border-cyan-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Domains</p>
              <p className="text-2xl font-bold text-white">{targets.length}</p>
            </div>
            <i className="fas fa-globe text-2xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-600/10 to-emerald-600/10 border border-green-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Scans</p>
              <p className="text-2xl font-bold text-green-400">{stats.active_scans || 0}</p>
            </div>
            <i className="fas fa-search text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-purple-600/10 to-pink-600/10 border border-purple-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Subdomains</p>
              <p className="text-2xl font-bold text-purple-400">{stats.total_subdomains || 0}</p>
            </div>
            <i className="fas fa-sitemap text-2xl text-purple-400"></i>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-red-600/10 to-orange-600/10 border border-red-400/20 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Vulnerabilities</p>
              <p className="text-2xl font-bold text-red-400">{stats.total_vulnerabilities || 0}</p>
            </div>
            <i className="fas fa-shield-alt text-2xl text-red-400"></i>
          </div>
        </div>
      </div>

      {/* Domain Cards */}
      <div className="space-y-4">
        {targets.length === 0 ? (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
            <i className="fas fa-search text-4xl text-gray-400 mb-4"></i>
            <h3 className="text-xl font-semibold text-white mb-2">No Domains Found</h3>
            <p className="text-gray-400">Add some targets to start reconnaissance scanning.</p>
          </div>
        ) : (
          targets.map((target) => (
            <div key={target.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-cyan-400/50 transition-colors">
              {/* Domain Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <i className="fas fa-globe text-2xl text-cyan-400 mr-4"></i>
                  <div>
                    <h2 className="text-xl font-bold text-white">{target.domain}</h2>
                    <div className="flex items-center space-x-3 mt-1">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(target.status)}`}>
                        {target.status}
                      </span>
                      <span className="text-gray-400 text-sm">{target.type}</span>
                      <span className="text-gray-400 text-sm">•</span>
                      <span className="text-gray-400 text-sm">Last scan: {formatDate(target.scanResults.lastScanTime)}</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleViewDomain(target)}
                  className="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-2 rounded-lg flex items-center transition-colors"
                >
                  <i className="fas fa-eye mr-2"></i>
                  View Details
                </button>
              </div>

              {/* Quick Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-cyan-400">{target.scanResults.totalSubdomains}</div>
                  <div className="text-gray-400 text-sm">Subdomains</div>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">{target.scanResults.liveSubdomains}</div>
                  <div className="text-gray-400 text-sm">Live</div>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-400">{target.scanResults.technologies}</div>
                  <div className="text-gray-400 text-sm">Technologies</div>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-400">{target.scanResults.jsFiles}</div>
                  <div className="text-gray-400 text-sm">JS Files</div>
                </div>
                
                <div className="bg-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-red-400">{target.scanResults.vulnerabilities}</div>
                  <div className="text-gray-400 text-sm">Vulnerabilities</div>
                </div>
              </div>

              {/* Workflow Status Indicator */}
              <div className="mt-4 pt-4 border-t border-gray-700">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-sm">Reconnaissance Workflow:</span>
                  <span className="text-cyan-400 text-sm font-medium">{target.workflow || 'full-recon'}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DomainResultsOverview;