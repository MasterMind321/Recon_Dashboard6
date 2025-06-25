import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ScanResults = () => {
  const [activeTab, setActiveTab] = useState('subdomains');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [scanResults, setScanResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTarget, setSelectedTarget] = useState('all');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  // Enhanced mock data with more comprehensive results
  const mockScanResults = {
    summary: {
      totalSubdomains: 127,
      liveSubdomains: 89,
      uniqueTechnologies: 23,
      openPorts: 345,
      jsFilesFound: 56,
      directoriesFound: 234,
      vulnerabilities: 18,
      lastScanTime: '2025-03-15 15:45:00'
    },
    subdomains: [
      { 
        id: 1, 
        subdomain: 'api.example.com', 
        ip: '192.168.1.10', 
        status: 'live', 
        ports: [80, 443, 8080], 
        technologies: ['nginx', 'nodejs', 'redis'], 
        lastSeen: '2025-03-15 15:30:00',
        responseTime: '245ms',
        statusCode: 200,
        title: 'API Gateway - Example Corp',
        screenshot: 'data:image/png;base64,placeholder'
      },
      { 
        id: 2, 
        subdomain: 'admin.example.com', 
        ip: '192.168.1.11', 
        status: 'live', 
        ports: [80, 443, 8080], 
        technologies: ['apache', 'php', 'mysql'], 
        lastSeen: '2025-03-15 15:28:00',
        responseTime: '567ms',
        statusCode: 200,
        title: 'Admin Panel - Restricted Access',
        screenshot: 'data:image/png;base64,placeholder'
      },
      { 
        id: 3, 
        subdomain: 'dev.example.com', 
        ip: '192.168.1.12', 
        status: 'live', 
        ports: [80, 443, 3000, 5000], 
        technologies: ['nginx', 'nodejs', 'mongodb'], 
        lastSeen: '2025-03-15 15:25:00',
        responseTime: '123ms',
        statusCode: 200,
        title: 'Development Server',
        screenshot: 'data:image/png;base64,placeholder'
      },
      { 
        id: 4, 
        subdomain: 'test.example.com', 
        ip: '192.168.1.13', 
        status: 'dead', 
        ports: [], 
        technologies: [], 
        lastSeen: '2025-03-15 14:45:00',
        responseTime: 'Timeout',
        statusCode: null,
        title: null,
        screenshot: null
      },
      { 
        id: 5, 
        subdomain: 'staging.example.com', 
        ip: '192.168.1.14', 
        status: 'live', 
        ports: [80, 443], 
        technologies: ['nginx', 'react'], 
        lastSeen: '2025-03-15 15:32:00',
        responseTime: '89ms',
        statusCode: 200,
        title: 'Staging Environment',
        screenshot: 'data:image/png;base64,placeholder'
      }
    ],
    technologies: [
      { id: 1, technology: 'nginx', version: '1.18.0', count: 45, risk: 'medium', cves: ['CVE-2021-23017'], subdomains: ['api.example.com', 'dev.example.com', 'staging.example.com'] },
      { id: 2, technology: 'apache', version: '2.4.41', count: 23, risk: 'low', cves: ['CVE-2021-44790'], subdomains: ['admin.example.com'] },
      { id: 3, technology: 'php', version: '7.4.3', count: 34, risk: 'high', cves: ['CVE-2021-21704', 'CVE-2021-21705'], subdomains: ['admin.example.com'] },
      { id: 4, technology: 'nodejs', version: '14.17.0', count: 12, risk: 'medium', cves: ['CVE-2021-22939'], subdomains: ['api.example.com', 'dev.example.com'] },
      { id: 5, technology: 'mysql', version: '8.0.25', count: 8, risk: 'medium', cves: ['CVE-2021-2342'], subdomains: ['admin.example.com'] }
    ],
    ports: [
      { id: 1, port: 80, service: 'http', protocol: 'tcp', hosts: 89, status: 'open', banner: 'nginx/1.18.0', version: '1.18.0', product: 'nginx' },
      { id: 2, port: 443, service: 'https', protocol: 'tcp', hosts: 87, status: 'open', banner: 'nginx/1.18.0 (SSL)', version: '1.18.0', product: 'nginx' },
      { id: 3, port: 22, service: 'ssh', protocol: 'tcp', hosts: 45, status: 'open', banner: 'OpenSSH 7.6p1 Ubuntu', version: '7.6p1', product: 'OpenSSH' },
      { id: 4, port: 3306, service: 'mysql', protocol: 'tcp', hosts: 12, status: 'open', banner: 'MySQL 8.0.25-0ubuntu0.20.04.1', version: '8.0.25', product: 'MySQL' },
      { id: 5, port: 8080, service: 'http-proxy', protocol: 'tcp', hosts: 23, status: 'open', banner: 'Apache/2.4.41 (Ubuntu)', version: '2.4.41', product: 'Apache httpd' }
    ],
    jsfiles: [
      { 
        id: 1, 
        url: 'https://api.example.com/assets/app.js', 
        size: '245KB', 
        endpoints: 23, 
        params: 45, 
        sensitiveData: ['API_KEY', 'AWS_SECRET'], 
        subdomain: 'api.example.com',
        lastModified: '2025-03-15 10:30:00',
        contentType: 'application/javascript'
      },
      { 
        id: 2, 
        url: 'https://admin.example.com/js/admin.js', 
        size: '189KB', 
        endpoints: 34, 
        params: 67, 
        sensitiveData: ['ADMIN_TOKEN', 'DB_PASSWORD'], 
        subdomain: 'admin.example.com',
        lastModified: '2025-03-14 16:45:00',
        contentType: 'application/javascript'
      },
      { 
        id: 3, 
        url: 'https://dev.example.com/bundle.js', 
        size: '567KB', 
        endpoints: 12, 
        params: 89, 
        sensitiveData: ['DEBUG_KEY'], 
        subdomain: 'dev.example.com',
        lastModified: '2025-03-15 14:20:00',
        contentType: 'application/javascript'
      }
    ],
    directories: [
      { id: 1, path: '/admin', status: 200, size: '2.3KB', server: 'nginx', lastChecked: '15:30:00', subdomain: 'example.com', authRequired: true, indexing: false },
      { id: 2, path: '/api/v1', status: 200, size: '156B', server: 'nginx', lastChecked: '15:28:00', subdomain: 'api.example.com', authRequired: false, indexing: false },
      { id: 3, path: '/backup', status: 403, size: '1.1KB', server: 'apache', lastChecked: '15:25:00', subdomain: 'admin.example.com', authRequired: true, indexing: false },
      { id: 4, path: '/.git', status: 200, size: '4.5KB', server: 'nginx', lastChecked: '15:35:00', subdomain: 'dev.example.com', authRequired: false, indexing: true },
      { id: 5, path: '/config', status: 404, size: '578B', server: 'nginx', lastChecked: '15:22:00', subdomain: 'staging.example.com', authRequired: false, indexing: false }
    ]
  };

  useEffect(() => {
    // Initialize with mock data for now
    setScanResults(mockScanResults);
    setLoading(false);
    
    // TODO: Replace with actual API call
    // fetchScanResults();
  }, []);

  const fetchScanResults = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/scan-results`);
      setScanResults(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching scan results:', error);
      setScanResults(mockScanResults);
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'critical': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'high': return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'low': return 'text-green-400 bg-green-400/10 border-green-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'live': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'dead': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'open': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'closed': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 200: return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 403: return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 404: return 'text-red-400 bg-red-400/10 border-red-400/20';
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const getResponseTimeColor = (responseTime) => {
    if (responseTime === 'Timeout') return 'text-red-400';
    const time = parseInt(responseTime);
    if (time < 100) return 'text-green-400';
    if (time < 500) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <i className="fas fa-spinner fa-spin text-4xl text-cyan-400"></i>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: 'fas fa-chart-pie', count: null },
    { id: 'subdomains', name: 'Subdomains', icon: 'fas fa-sitemap', count: scanResults?.subdomains?.length || 0 },
    { id: 'technologies', name: 'Technologies', icon: 'fas fa-cogs', count: scanResults?.technologies?.length || 0 },
    { id: 'ports', name: 'Ports & Services', icon: 'fas fa-network-wired', count: scanResults?.ports?.length || 0 },
    { id: 'jsfiles', name: 'JS Files', icon: 'fab fa-js-square', count: scanResults?.jsfiles?.length || 0 },
    { id: 'directories', name: 'Directories', icon: 'fas fa-folder', count: scanResults?.directories?.length || 0 }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div className="bg-gray-700 p-6 rounded-lg border border-gray-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Subdomains</p>
              <p className="text-2xl font-bold text-white">{scanResults.summary.totalSubdomains}</p>
            </div>
            <i className="fas fa-sitemap text-2xl text-cyan-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-700 p-6 rounded-lg border border-gray-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Live Subdomains</p>
              <p className="text-2xl font-bold text-green-400">{scanResults.summary.liveSubdomains}</p>
            </div>
            <i className="fas fa-globe text-2xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-700 p-6 rounded-lg border border-gray-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Open Ports</p>
              <p className="text-2xl font-bold text-blue-400">{scanResults.summary.openPorts}</p>
            </div>
            <i className="fas fa-network-wired text-2xl text-blue-400"></i>
          </div>
        </div>
        
        <div className="bg-gray-700 p-6 rounded-lg border border-gray-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Vulnerabilities</p>
              <p className="text-2xl font-bold text-red-400">{scanResults.summary.vulnerabilities}</p>
            </div>
            <i className="fas fa-exclamation-triangle text-2xl text-red-400"></i>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-gray-700 rounded-lg border border-gray-600 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Discoveries</h3>
        <div className="space-y-3">
          {scanResults.subdomains.slice(0, 5).map((subdomain, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-800 rounded">
              <div className="flex items-center">
                <i className={`fas fa-circle text-xs mr-3 ${subdomain.status === 'live' ? 'text-green-400' : 'text-red-400'}`}></i>
                <span className="text-white">{subdomain.subdomain}</span>
                <span className="text-gray-400 ml-2">({subdomain.ip})</span>
              </div>
              <div className="text-sm text-gray-400">{subdomain.lastSeen}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSubdomains = () => (
    <div className="space-y-4">
      {scanResults.subdomains.map((subdomain) => (
        <div key={subdomain.id} className="bg-gray-700 rounded-lg border border-gray-600 p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <i className="fas fa-globe mr-3 text-cyan-400"></i>
              <div>
                <h3 className="text-lg font-semibold text-white">{subdomain.subdomain}</h3>
                <p className="text-gray-400 text-sm">{subdomain.title || 'No title'}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(subdomain.status)}`}>
                {subdomain.status}
              </span>
              {subdomain.statusCode && (
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(subdomain.statusCode)}`}>
                  {subdomain.statusCode}
                </span>
              )}
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">IP Address:</span>
                <span className="text-white font-mono">{subdomain.ip}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Response Time:</span>
                <span className={`font-mono ${getResponseTimeColor(subdomain.responseTime)}`}>
                  {subdomain.responseTime}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Last Seen:</span>
                <span className="text-gray-300">{subdomain.lastSeen}</span>
              </div>
            </div>

            <div className="space-y-2">
              <div>
                <span className="text-gray-400">Open Ports:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {subdomain.ports.map((port, index) => (
                    <span key={index} className="px-2 py-1 bg-cyan-600/20 text-cyan-400 rounded text-xs">
                      {port}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <span className="text-gray-400">Technologies:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {subdomain.technologies.map((tech, index) => (
                    <span key={index} className="px-2 py-1 bg-purple-600/20 text-purple-400 rounded text-xs">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Screenshot placeholder */}
            <div className="bg-gray-800 rounded border-2 border-dashed border-gray-600 h-24 flex items-center justify-center">
              <span className="text-gray-400 text-sm">Screenshot</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-2">
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
              <i className="fas fa-external-link-alt mr-1"></i>
              Visit
            </button>
            <button className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm">
              <i className="fas fa-search mr-1"></i>
              Deep Scan
            </button>
            <button className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm">
              <i className="fas fa-bug mr-1"></i>
              Vuln Scan
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  const renderTechnologies = () => (
    <div className="space-y-4">
      {scanResults.technologies.map((tech) => (
        <div key={tech.id} className="bg-gray-700 rounded-lg border border-gray-600 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <i className="fas fa-cog mr-3 text-cyan-400"></i>
              <div>
                <h3 className="text-lg font-semibold text-white">{tech.technology}</h3>
                <p className="text-gray-400">Version {tech.version}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getRiskColor(tech.risk)}`}>
                {tech.risk} risk
              </span>
              <span className="text-gray-300">{tech.count} instances</span>
            </div>
          </div>

          {/* CVEs */}
          {tech.cves.length > 0 && (
            <div className="mb-4">
              <span className="text-gray-400 text-sm">Known CVEs:</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {tech.cves.map((cve, index) => (
                  <span key={index} className="px-2 py-1 bg-red-600/20 text-red-400 rounded text-xs font-mono">
                    {cve}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Affected Subdomains */}
          <div>
            <span className="text-gray-400 text-sm">Found on:</span>
            <div className="flex flex-wrap gap-2 mt-2">
              {tech.subdomains.map((subdomain, index) => (
                <span key={index} className="px-2 py-1 bg-blue-600/20 text-blue-400 rounded text-xs">
                  {subdomain}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'subdomains': return renderSubdomains();
      case 'technologies': return renderTechnologies();
      case 'ports':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scanResults.ports.map((port) => (
              <div key={port.id} className="bg-gray-700 p-6 rounded-lg border border-gray-600">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white">Port {port.port}</h3>
                    <p className="text-gray-400">{port.service} ({port.protocol})</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(port.status)}`}>
                    {port.status}
                  </span>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Hosts:</span>
                    <span className="text-white">{port.hosts}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Product:</span>
                    <span className="text-white">{port.product}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Version:</span>
                    <span className="text-white">{port.version}</span>
                  </div>
                </div>
                
                <div className="mt-4 p-3 bg-gray-800 rounded">
                  <span className="text-gray-400 text-xs">Banner:</span>
                  <div className="text-green-400 text-xs font-mono mt-1">{port.banner}</div>
                </div>
              </div>
            ))}
          </div>
        );
      case 'jsfiles':
        return (
          <div className="space-y-4">
            {scanResults.jsfiles.map((jsfile) => (
              <div key={jsfile.id} className="bg-gray-700 p-6 rounded-lg border border-gray-600">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-white font-medium">{jsfile.url}</h3>
                    <p className="text-gray-400 text-sm">{jsfile.subdomain}</p>
                  </div>
                  <span className="text-cyan-400 font-mono">{jsfile.size}</span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Endpoints:</span>
                      <span className="text-green-400">{jsfile.endpoints}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Parameters:</span>
                      <span className="text-blue-400">{jsfile.params}</span>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Content Type:</span>
                      <span className="text-white">{jsfile.contentType}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Last Modified:</span>
                      <span className="text-white">{jsfile.lastModified}</span>
                    </div>
                  </div>
                  
                  <div>
                    <span className="text-gray-400 text-sm">Sensitive Data:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {jsfile.sensitiveData.map((data, index) => (
                        <span key={index} className="px-2 py-1 bg-red-600/20 text-red-400 rounded text-xs">
                          {data}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
                    <i className="fas fa-eye mr-1"></i>
                    View Source
                  </button>
                  <button className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm">
                    <i className="fas fa-download mr-1"></i>
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        );
      case 'directories':
        return (
          <div className="space-y-4">
            {scanResults.directories.map((directory) => (
              <div key={directory.id} className="bg-gray-700 p-6 rounded-lg border border-gray-600">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <i className="fas fa-folder mr-3 text-yellow-400"></i>
                    <div>
                      <h3 className="text-white font-medium">{directory.path}</h3>
                      <p className="text-gray-400 text-sm">{directory.subdomain}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(directory.status)}`}>
                    {directory.status}
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Size:</span>
                      <span className="text-white">{directory.size}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Server:</span>
                      <span className="text-white">{directory.server}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Last Checked:</span>
                      <span className="text-white">{directory.lastChecked}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400 text-sm">Auth Required:</span>
                      <span className={`px-2 py-1 rounded text-xs ${directory.authRequired ? 'bg-red-600/20 text-red-400' : 'bg-green-600/20 text-green-400'}`}>
                        {directory.authRequired ? 'Yes' : 'No'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400 text-sm">Directory Indexing:</span>
                      <span className={`px-2 py-1 rounded text-xs ${directory.indexing ? 'bg-orange-600/20 text-orange-400' : 'bg-green-600/20 text-green-400'}`}>
                        {directory.indexing ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );
      default:
        return <div>Select a tab to view results</div>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Scan Results</h1>
          <p className="text-gray-400">Comprehensive reconnaissance results and detailed analysis</p>
        </div>
        <div className="flex items-center space-x-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors">
            <i className="fas fa-download mr-2"></i>
            Export Results
          </button>
          <button 
            onClick={fetchScanResults}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          >
            <i className="fas fa-sync mr-2"></i>
            Refresh
          </button>
        </div>
      </div>

      {/* Summary Card */}
      <div className="bg-gradient-to-r from-cyan-600/10 to-blue-600/10 border border-cyan-400/20 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white mb-2">Last Scan Summary</h2>
            <p className="text-gray-300">
              Completed on {scanResults?.summary.lastScanTime} • {scanResults?.summary.liveSubdomains} live subdomains discovered • {scanResults?.summary.vulnerabilities} potential vulnerabilities identified
            </p>
          </div>
          <i className="fas fa-chart-line text-3xl text-cyan-400"></i>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search results by subdomain, technology, or keyword..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400"
            />
          </div>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-400"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
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
                {tab.count !== null && (
                  <span className="ml-2 bg-gray-700 text-gray-300 py-0.5 px-2 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default ScanResults;