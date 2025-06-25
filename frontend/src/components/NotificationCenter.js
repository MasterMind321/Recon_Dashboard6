import React, { useState } from 'react';

const NotificationCenter = ({ notifications }) => {
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');

  // Mock notification data with more examples
  const allNotifications = [
    {
      id: 1,
      type: 'success',
      title: 'Scan Completed',
      message: 'Subdomain enumeration completed for example.com',
      details: 'Found 234 subdomains, 127 live hosts detected',
      timestamp: '2025-03-15 15:30:00',
      read: false,
      target: 'example.com',
      severity: 'info'
    },
    {
      id: 2,
      type: 'warning',
      title: 'High Severity Vulnerability',
      message: 'SQL injection vulnerability detected',
      details: 'Critical SQL injection found in admin.example.com/login.php',
      timestamp: '2025-03-15 14:23:15',
      read: false,
      target: 'admin.example.com',
      severity: 'critical'
    },
    {
      id: 3,
      type: 'info',
      title: 'Port Scan Initiated',
      message: 'Port scan started for 127 live subdomains',
      details: 'Scanning common ports using nmap and masscan',
      timestamp: '2025-03-15 13:45:22',
      read: true,
      target: 'target.com',
      severity: 'info'
    },
    {
      id: 4,
      type: 'error',
      title: 'Scan Failed',
      message: 'Subdomain enumeration failed for testsite.org',
      details: 'DNS resolution timeout, please check target accessibility',
      timestamp: '2025-03-15 12:15:33',
      read: true,
      target: 'testsite.org',
      severity: 'error'
    },
    {
      id: 5,
      type: 'success',
      title: 'New Technology Detected',
      message: 'WordPress installation found',
      details: 'WordPress 5.8.1 detected on staging.example.com',
      timestamp: '2025-03-15 11:30:45',
      read: true,
      target: 'staging.example.com',
      severity: 'medium'
    },
    {
      id: 6,
      type: 'warning',
      title: 'Sensitive File Exposed',
      message: 'Environment file accessible',
      details: '.env file found at https://dev.example.com/.env',
      timestamp: '2025-03-15 10:45:12',
      read: false,
      target: 'dev.example.com',
      severity: 'high'
    }
  ];

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success': return 'fas fa-check-circle text-green-400';
      case 'warning': return 'fas fa-exclamation-triangle text-yellow-400';
      case 'error': return 'fas fa-times-circle text-red-400';
      case 'info': return 'fas fa-info-circle text-blue-400';
      default: return 'fas fa-bell text-gray-400';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'border-l-red-500 bg-red-900/10';
      case 'high': return 'border-l-orange-500 bg-orange-900/10';
      case 'medium': return 'border-l-yellow-500 bg-yellow-900/10';
      case 'info': return 'border-l-blue-500 bg-blue-900/10';
      case 'error': return 'border-l-red-500 bg-red-900/10';
      default: return 'border-l-gray-500 bg-gray-900/10';
    }
  };

  const filteredNotifications = allNotifications.filter(notification => {
    if (filter === 'unread') return !notification.read;
    if (filter === 'critical') return notification.severity === 'critical';
    if (filter === 'warnings') return notification.type === 'warning';
    return true;
  });

  const sortedNotifications = filteredNotifications.sort((a, b) => {
    if (sortBy === 'newest') {
      return new Date(b.timestamp) - new Date(a.timestamp);
    } else {
      return new Date(a.timestamp) - new Date(b.timestamp);
    }
  });

  const unreadCount = allNotifications.filter(n => !n.read).length;
  const criticalCount = allNotifications.filter(n => n.severity === 'critical').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Notification Center</h1>
          <p className="text-gray-400">Stay updated with reconnaissance findings and system alerts</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-sm text-gray-400">Unread</div>
            <div className="text-2xl font-bold text-cyan-400">{unreadCount}</div>
          </div>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center">
            <i className="fas fa-cog mr-2"></i>
            Settings
          </button>
        </div>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-red-900/20 border border-red-500/30 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-400 text-sm font-medium">Critical Alerts</p>
              <p className="text-2xl font-bold text-red-400">{criticalCount}</p>
            </div>
            <i className="fas fa-exclamation-triangle text-xl text-red-400"></i>
          </div>
        </div>
        
        <div className="bg-yellow-900/20 border border-yellow-500/30 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-400 text-sm font-medium">Warnings</p>
              <p className="text-2xl font-bold text-yellow-400">
                {allNotifications.filter(n => n.type === 'warning').length}
              </p>
            </div>
            <i className="fas fa-exclamation text-xl text-yellow-400"></i>
          </div>
        </div>
        
        <div className="bg-green-900/20 border border-green-500/30 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-400 text-sm font-medium">Completed</p>
              <p className="text-2xl font-bold text-green-400">
                {allNotifications.filter(n => n.type === 'success').length}
              </p>
            </div>
            <i className="fas fa-check-circle text-xl text-green-400"></i>
          </div>
        </div>
        
        <div className="bg-blue-900/20 border border-blue-500/30 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-400 text-sm font-medium">Total</p>
              <p className="text-2xl font-bold text-blue-400">{allNotifications.length}</p>
            </div>
            <i className="fas fa-bell text-xl text-blue-400"></i>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Filter</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-400"
              >
                <option value="all">All Notifications</option>
                <option value="unread">Unread Only</option>
                <option value="critical">Critical Only</option>
                <option value="warnings">Warnings Only</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-cyan-400"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
              </select>
            </div>
          </div>
          <button className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center">
            <i className="fas fa-check mr-2"></i>
            Mark All Read
          </button>
        </div>
      </div>

      {/* Notifications List */}
      <div className="space-y-4">
        {sortedNotifications.map((notification) => (
          <div 
            key={notification.id} 
            className={`bg-gray-800 border-l-4 rounded-lg p-6 ${getSeverityColor(notification.severity)} ${
              !notification.read ? 'ring-1 ring-cyan-400/20' : ''
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <i className={`${getNotificationIcon(notification.type)} text-xl mt-1`}></i>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-lg font-semibold text-white">{notification.title}</h3>
                    {!notification.read && (
                      <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                    )}
                  </div>
                  <p className="text-gray-300 mb-2">{notification.message}</p>
                  <p className="text-sm text-gray-400 mb-3">{notification.details}</p>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <i className="fas fa-globe mr-1"></i>
                      <span>{notification.target}</span>
                    </div>
                    <div className="flex items-center">
                      <i className="fas fa-clock mr-1"></i>
                      <span>{notification.timestamp}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button className="text-gray-400 hover:text-white p-2 rounded">
                  <i className="fas fa-eye"></i>
                </button>
                <button className="text-gray-400 hover:text-white p-2 rounded">
                  <i className="fas fa-bookmark"></i>
                </button>
                <button className="text-gray-400 hover:text-white p-2 rounded">
                  <i className="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {sortedNotifications.length === 0 && (
        <div className="text-center py-12">
          <i className="fas fa-bell-slash text-6xl text-gray-600 mb-4"></i>
          <h3 className="text-xl font-semibold text-white mb-2">No Notifications</h3>
          <p className="text-gray-400">No notifications match your current filters.</p>
        </div>
      )}

      {/* Notification Settings */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <i className="fas fa-cog mr-2 text-cyan-400"></i>
          Notification Settings
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-medium text-white mb-3">Alert Channels</h3>
            <div className="space-y-3">
              {[
                { name: 'Email Notifications', enabled: true, icon: 'fas fa-envelope' },
                { name: 'Slack Integration', enabled: false, icon: 'fab fa-slack' },
                { name: 'Discord Webhook', enabled: true, icon: 'fab fa-discord' },
                { name: 'Browser Push', enabled: true, icon: 'fas fa-bell' }
              ].map((channel, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <i className={`${channel.icon} mr-3 text-cyan-400`}></i>
                    <span className="text-gray-300">{channel.name}</span>
                  </div>
                  <button 
                    className={`w-12 h-6 rounded-full transition-colors ${
                      channel.enabled ? 'bg-cyan-600' : 'bg-gray-600'
                    }`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      channel.enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}></div>
                  </button>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-white mb-3">Alert Triggers</h3>
            <div className="space-y-3">
              {[
                { name: 'Critical Vulnerabilities', enabled: true },
                { name: 'Scan Completion', enabled: true },
                { name: 'New Subdomains', enabled: false },
                { name: 'System Errors', enabled: true }
              ].map((trigger, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-gray-300">{trigger.name}</span>
                  <button 
                    className={`w-12 h-6 rounded-full transition-colors ${
                      trigger.enabled ? 'bg-cyan-600' : 'bg-gray-600'
                    }`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                      trigger.enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}></div>
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationCenter;