import React, { useState } from 'react';

const ScanResults = () => {
  const [activeTab, setActiveTab] = useState('subdomains');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data for different result types
  const scanResults = {
    subdomains: [
      { id: 1, subdomain: 'api.example.com', ip: '192.168.1.10', status: 'live', ports: '80,443', technology: 'nginx', lastSeen: '2025-03-15 15:30:00' },
      { id: 2, subdomain: 'admin.example.com', ip: '192.168.1.11', status: 'live', ports: '80,443,8080', technology: 'apache', lastSeen: '2025-03-15 15:28:00' },
      { id: 3, subdomain: 'dev.example.com', ip: '192.168.1.12', status: 'live', ports: '80,443,3000', technology: 'nodejs', lastSeen: '2025-03-15 15:25:00' },
      { id: 4, subdomain: 'test.example.com', ip: '192.168.1.13', status: 'dead', ports: '-', technology: '-', lastSeen: '2025-03-15 14:45:00' },
      { id: 5, subdomain: 'staging.example.com', ip: '192.168.1.14', status: 'live', ports: '80,443', technology: 'nginx', lastSeen: '2025-03-15 15:32:00' }
    ],
    technologies: [
      { id: 1, technology: 'nginx', version: '1.18.0', count: 45, risk: 'medium', cves: 3 },
      { id: 2, technology: 'apache', version: '2.4.41', count: 23, risk: 'low', cves: 1 },
      { id: 3, technology: 'php', version: '7.4.3', count: 34, risk: 'high', cves: 7 },
      { id: 4, technology: 'mysql', version: '8.0.25', count: 12, risk: 'medium', cves: 2 },
      { id: 5, technology: 'wordpress', version: '5.8.1', count: 8, risk: 'critical', cves: 12 }
    ],
    ports: [
      { id: 1, port: 80, service: 'http', hosts: 89, status: 'open', banner: 'nginx/1.18.0' },
      { id: 2, port: 443, service: 'https', hosts: 87, status: 'open', banner: 'nginx/1.18.0 (SSL)' },
      { id: 3, port: 22, service: 'ssh', hosts: 45, status: 'open', banner: 'OpenSSH 7.6p1' },
      { id: 4, port: 3306, service: 'mysql', hosts: 12, status: 'open', banner: 'MySQL 8.0.25' },
      { id: 5, port: 8080, service: 'http-alt', hosts: 23, status: 'open', banner: 'Apache/2.4.41' }
    ],
    jsfiles: [
      { id: 1, url: 'https://api.example.com/assets/app.js', size: '245KB', endpoints: 23, params: 45, sensitive: 'API Keys' },
      { id: 2, url: 'https://admin.example.com/js/admin.js', size: '189KB', endpoints: 34, params: 67, sensitive: 'Admin Tokens' },
      { id: 3, url: 'https://dev.example.com/bundle.js', size: '567KB', endpoints: 12, params: 89, sensitive: 'Debug Info' },
      { id: 4, url: 'https://staging.example.com/main.js', size: '123KB', endpoints: 45, params: 23, sensitive: 'None' },
      { id: 5, url: 'https://test.example.com/script.js', size: '78KB', endpoints: 8, params: 12, sensitive: 'DB Credentials' }
    ],
    directories: [
      { id: 1, path: '/admin', status: 200, size: '2.3KB', server: 'nginx', lastChecked: '15:30:00' },
      { id: 2, path: '/api/v1', status: 200, size: '156B', server: 'nginx', lastChecked: '15:28:00' },
      { id: 3, path: '/backup', status: 403, size: '1.1KB', server: 'apache', lastChecked: '15:25:00' },
      { id: 4, path: '/config', status: 404, size: '578B', server: 'nginx', lastChecked: '15:22:00' },
      { id: 5, path: '/.git', status: 200, size: '4.5KB', server: 'nginx', lastChecked: '15:35:00' }
    ]
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'critical': return 'text-red-400 bg-red-400/10';
      case 'high': return 'text-orange-400 bg-orange-400/10';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10';
      case 'low': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'live': return 'text-green-400 bg-green-400/10';
      case 'dead': return 'text-red-400 bg-red-400/10';
      case 'open': return 'text-green-400 bg-green-400/10';
      case 'closed': return 'text-red-400 bg-red-400/10';
      case 200: return 'text-green-400 bg-green-400/10';
      case 403: return 'text-yellow-400 bg-yellow-400/10';
      case 404: return 'text-red-400 bg-red-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const tabs = [
    { id: 'subdomains', name: 'Subdomains', icon: 'fas fa-sitemap', count: scanResults.subdomains.length },
    { id: 'technologies', name: 'Technologies', icon: 'fas fa-cogs', count: scanResults.technologies.length },
    { id: 'ports', name: 'Ports & Services', icon: 'fas fa-network-wired', count: scanResults.ports.length },
    { id: 'jsfiles', name: 'JS Files', icon: 'fab fa-js-square', count: scanResults.jsfiles.length },
    { id: 'directories', name: 'Directories', icon: 'fas fa-folder', count: scanResults.directories.length }
  ];

  const renderSubdomains = () => (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-700">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Subdomain</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">IP Address</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Ports</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Technology</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Last Seen</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-700">
          {scanResults.subdomains.map((subdomain) => (
            <tr key={subdomain.id} className="hover:bg-gray-700/50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <i className="fas fa-globe mr-3 text-cyan-400"></i>
                  <span className="text-white font-medium">{subdomain.subdomain}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-300 font-mono">
                {subdomain.ip}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(subdomain.status)}`}>
                  {subdomain.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-300 font-mono">
                {subdomain.ports}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-300">
                {subdomain.technology}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-400 text-sm">
                {subdomain.lastSeen}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderTechnologies = () => (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-700">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Technology</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Version</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Count</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Risk Level</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">CVEs</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-700">
          {scanResults.technologies.map((tech) => (
            <tr key={tech.id} className="hover:bg-gray-700/50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <i className="fas fa-cog mr-3 text-cyan-400"></i>
                  <span className="text-white font-medium">{tech.technology}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-300 font-mono">
                {tech.version}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-white">
                {tech.count}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskColor(tech.risk)}`}>
                  {tech.risk}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="text-red-400 font-semibold">{tech.cves}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'subdomains': return renderSubdomains();
      case 'technologies': return renderTechnologies();
      case 'ports':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scanResults.ports.map((port) => (
              <div key={port.id} className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-semibold">Port {port.port}</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(port.status)}`}>
                    {port.status}
                  </span>
                </div>
                <div className="text-sm text-gray-300 mb-1">Service: {port.service}</div>
                <div className="text-sm text-gray-300 mb-1">Hosts: {port.hosts}</div>
                <div className="text-xs text-gray-400 font-mono">{port.banner}</div>
              </div>
            ))}
          </div>
        );
      case 'jsfiles':
        return (
          <div className="space-y-4">
            {scanResults.jsfiles.map((jsfile) => (
              <div key={jsfile.id} className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-medium truncate">{jsfile.url}</span>
                  <span className="text-cyan-400 text-sm">{jsfile.size}</span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Endpoints:</span>
                    <span className="text-green-400 ml-2">{jsfile.endpoints}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Parameters:</span>
                    <span className="text-blue-400 ml-2">{jsfile.params}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Sensitive:</span>
                    <span className={`ml-2 ${jsfile.sensitive === 'None' ? 'text-green-400' : 'text-red-400'}`}>
                      {jsfile.sensitive}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );
      case 'directories':
        return renderSubdomains(); // Similar structure
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
          <p className="text-gray-400">Comprehensive reconnaissance results and analysis</p>
        </div>
        <div className="flex items-center space-x-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center">
            <i className="fas fa-download mr-2"></i>
            Export Results
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center">
            <i className="fas fa-sync mr-2"></i>
            Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search results..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400"
            />
          </div>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-400"
          >
            <option value="all">All Severities</option>
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
                <span className="ml-2 bg-gray-700 text-gray-300 py-0.5 px-2 rounded-full text-xs">
                  {tab.count}
                </span>
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