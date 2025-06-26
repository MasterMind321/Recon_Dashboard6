# ReconFlow - Automated Reconnaissance Platform

ReconFlow is a comprehensive automated reconnaissance platform designed for cybersecurity professionals and bug bounty hunters. It provides a full-stack web application for managing reconnaissance workflows, target monitoring, and vulnerability assessment across multiple domains and IP ranges.

## 🚀 Features

### 🎯 **Target Management**
- **Multi-type Target Support**: Domains, IP addresses, and CIDR ranges
- **Real-time Status Tracking**: Monitor scan progress and target status
- **Automated Workflows**: Full reconnaissance pipeline automation
- **Comprehensive Statistics**: Track discovered assets and vulnerabilities

### 🛠️ **58+ Integrated Security Tools**
ReconFlow integrates with 58+ popular cybersecurity tools across 10 categories:

#### 🟦 **Subdomain Enumeration (10 tools)**
- `subfinder` - Passive subdomain discovery
- `amass` - Active/passive subdomain enumeration
- `crt.sh parser` - Certificate Transparency search
- `puredns` - DNS resolution + wildcard detection
- `dnsx` - Fast DNS resolution
- `gotator` - Subdomain permutation
- `dnsgen` - Wordlist-based permutations
- `github-subdomains` - GitHub scraping for subdomains
- `mapcidr` - ASN to CIDR mapping
- `asnlookup` - ASN to IP/Subdomain correlation

#### 🟩 **Liveness, Fingerprinting & Screenshots (8 tools)**
- `httpx` - Liveness check with response info
- `cdncheck` - CDN and WAF fingerprinting
- `tlsx` - TLS certificate info gathering
- `gowitness` - Web screenshots of live hosts
- `wafw00f` - WAF detection
- `whatweb` - Web tech stack detection
- `wappalyzer` - Alternative to WhatWeb
- `CMSeeK` - CMS fingerprinting and CVE mapping

#### 🟨 **JavaScript/Endpoint Discovery (6 tools)**
- `subjs` - Extract JS URLs from HTML
- `xnLinkFinder` - Extract endpoints from JS
- `linkfinder` - Regex-based endpoint extractor
- `getjswords` - Parameter & keyword discovery
- `JSParser` - Static JS analysis
- `jsbeautifier` - JS beautification/minification

#### 🟥 **Vulnerability Scanning (7 tools)**
- `dalfox` - XSS scanner (param/context-aware)
- `XSStrike` - XSS detection via headless browser
- `sqlmap` - SQLi scanner (auto-detection)
- `crlfuzz` - CRLF Injection tester
- `qsreplace` - URL parameter replacement
- `nuclei` - Vulnerability templated scanner
- `nuclei-templates` - Template repository

#### 🟪 **Historical Data & Archive Recon (3 tools)**
- `gau` - Get all URLs from archives
- `waybackurls` - Wayback Machine URL extraction
- `urless` - Fast historical URL fetching

#### 🟧 **Directory & File Fuzzing (4 tools)**
- `ffuf` - Directory brute-forcing & fuzzing
- `feroxbuster` - Recursive fuzzing
- `dirsearch` - Python-based directory scanning
- `byp4xx` - 403 bypass techniques

#### 🟫 **Port Scanning & Network (5 tools)**
- `nmap` - Port scanning & service detection
- `smap` - Fast nmap-compatible scanner
- `naabu` - Lightweight port scanner
- `masscan` - Ultra-fast port scanning
- `brutespray` - Brute-force services

#### 🟦 **Cloud & S3 Recon (2 tools)**
- `s3scanner` - Public bucket enumeration
- `cloud_enum` - AWS/Azure/GCP asset recon

#### 🟨 **Reporting & Notification (4 tools)**
- `notify` - Send alerts (Slack, Email, etc.)
- `unfurl` - URL parsing
- `anew` - Deduplication utility
- `interactsh-client` - OOB detection

#### ⚙️ **Utility & Miscellaneous (9 tools)**
- `fav-up` - Favicon hashing
- `analyticsrelationships` - Google Analytics tracking
- `dsieve` - Domain filtering
- `cdnstake` - CNAME vulnerability scanner
- `inscope` - Scope filtering
- `enumerepo` - Git repository recon
- `gitleaks` - Git secret scanning
- `trufflehog` - Advanced git leak scanner
- `gitdorks_go` - GitHub dork scanner

### 📊 **Advanced UI Features**
- **Hierarchical Domain Results**: Organized domain → subdomain → vulnerability structure
- **Real-time Workflow Monitoring**: Track reconnaissance pipeline progress
- **Interactive Dashboard**: Comprehensive statistics and quick access
- **Tool Management Interface**: Install, configure, and monitor tools
- **Advanced Filtering**: Filter results by status, type, severity, and more

## 🏗️ Architecture

ReconFlow follows a modern microservices architecture:

- **Frontend**: React 19 + Tailwind CSS
- **Backend**: FastAPI (Python) with async/await
- **Database**: MongoDB for data persistence
- **Tool Integration**: Native integration with 58+ security tools
- **Background Processing**: Asynchronous task execution

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Yarn package manager**
- **MongoDB 5.0+**
- **Go 1.19+** (for Go-based tools)
- **Linux/macOS environment** (recommended)

## ⚡ Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd reconflow

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
yarn install
```

### 2. Configuration

#### Backend Configuration
Create `/app/backend/.env`:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="reconflow_db"
```

#### Frontend Configuration
Create `/app/frontend/.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3. Start Services

#### Option A: Using Supervisor (Recommended)
```bash
# Start all services
sudo supervisorctl start all

# Check status
sudo supervisorctl status
```

#### Option B: Manual Start
```bash
# Start MongoDB
sudo systemctl start mongodb

# Start Backend (Terminal 1)
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001

# Start Frontend (Terminal 2)
cd frontend
yarn start
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🔧 Installation & Setup

### MongoDB Setup
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mongodb

# macOS
brew install mongodb-community

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Go Installation (for Go-based tools)
```bash
# Ubuntu/Debian
sudo apt install golang-go

# macOS
brew install go

# Verify installation
go version
```

### Tool Installation
ReconFlow automatically handles tool installation through the web interface:

1. Navigate to **Tools Management** page
2. Select tools by category
3. Click **Install** for required tools
4. Monitor installation progress

## 📖 API Documentation

### Authentication
Currently, the API doesn't require authentication. This will be added in future versions.

### Base URL
```
http://localhost:8001/api
```

### Core Endpoints

#### Health Check
```http
GET /api/
```
Returns API health status.

#### Target Management

##### Get All Targets
```http
GET /api/targets
```
Query Parameters:
- `status` (optional): Filter by target status
- `type` (optional): Filter by target type

##### Create Target
```http
POST /api/targets
Content-Type: application/json

{
  "domain": "example.com",
  "type": "domain",
  "workflow": "full-recon",
  "notes": "Bug bounty target"
}
```

##### Get Target Details
```http
GET /api/targets/{target_id}
```

##### Update Target
```http
PUT /api/targets/{target_id}
Content-Type: application/json

{
  "status": "active",
  "notes": "Updated notes"
}
```

##### Delete Target
```http
DELETE /api/targets/{target_id}
```

##### Start Scan
```http
POST /api/targets/{target_id}/scan
```

##### Get Target Statistics
```http
GET /api/targets/stats
```

#### Tool Management

##### Get All Tools
```http
GET /api/tools
```

##### Get Tools by Category
```http
GET /api/tools/category/{category}
```
Categories: `subdomain_enumeration`, `liveness_fingerprinting`, `javascript_endpoint`, `vulnerability_scanning`, etc.

##### Install Tool
```http
POST /api/tools/{tool_id}/install
```

##### Get Tool Statistics
```http
GET /api/tools/stats
```

#### Subdomain Enumeration

##### Start Subdomain Enumeration
```http
POST /api/targets/{target_id}/enumerate-subdomains
Content-Type: application/json

{
  "tools": ["subfinder", "amass", "crt.sh"],
  "config": {
    "timeout": 300,
    "deep_scan": true
  }
}
```

##### Get Enumeration Job Status
```http
GET /api/enumeration-jobs/{job_id}
```

##### Get Target Subdomains
```http
GET /api/targets/{target_id}/subdomains
```

##### Get Subdomain Statistics
```http
GET /api/subdomains/stats
```

#### Liveness & Fingerprinting

##### Start Liveness Check
```http
POST /api/targets/{target_id}/check-liveness
Content-Type: application/json

{
  "tools": ["httpx", "gowitness", "wafw00f"],
  "config": {
    "timeout": 60,
    "screenshot": true
  }
}
```

##### Get Liveness Results
```http
GET /api/targets/{target_id}/liveness-results
```

##### Get Liveness Statistics
```http
GET /api/liveness/stats
```

#### JavaScript Analysis

##### Start JavaScript Analysis
```http
POST /api/targets/{target_id}/analyze-javascript
Content-Type: application/json

{
  "tools": ["subjs", "linkfinder", "jsbeautifier"],
  "config": {
    "deep_analysis": true
  }
}
```

##### Get JavaScript Results
```http
GET /api/targets/{target_id}/javascript-results
```

##### Get Discovered Endpoints
```http
GET /api/targets/{target_id}/endpoints
```

##### Get JavaScript Keywords
```http
GET /api/targets/{target_id}/keywords
```

#### Vulnerability Scanning

##### Start Vulnerability Scan
```http
POST /api/targets/{target_id}/scan-vulnerabilities
Content-Type: application/json

{
  "tools": ["nuclei", "dalfox", "sqlmap"],
  "config": {
    "severity": "medium",
    "templates": ["cves", "exposures"]
  }
}
```

##### Get Vulnerability Results
```http
GET /api/targets/{target_id}/vulnerabilities
```

##### Get Vulnerability Statistics
```http
GET /api/vulnerabilities/stats
```

#### Scan Results

##### Get All Scan Results
```http
GET /api/scan-results
```
Query Parameters:
- `target` (optional): Filter by target
- `tool_name` (optional): Filter by tool

##### Create Scan Result
```http
POST /api/scan-results
Content-Type: application/json

{
  "target": "example.com",
  "tool_name": "subfinder",
  "category": "subdomain_enumeration",
  "status": "completed",
  "results": {
    "subdomains": ["api.example.com", "www.example.com"],
    "count": 2
  },
  "start_time": "2024-01-01T00:00:00Z"
}
```

### Response Format

All API responses follow this format:

#### Success Response
```json
{
  "data": {
    // Response data
  },
  "status": "success",
  "message": "Operation completed successfully"
}
```

#### Error Response
```json
{
  "error": {
    "code": 400,
    "message": "Invalid request data",
    "details": "Domain field is required"
  },
  "status": "error"
}
```

### Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## 🛠️ Development

### Backend Development

#### Project Structure
```
backend/
├── models/           # Pydantic models
├── routes/           # FastAPI routes
├── services/         # Business logic
├── data/            # Static data
├── server.py        # Main application
└── requirements.txt # Dependencies
```

#### Adding New Tools
1. Update `RECON_TOOLS_DATA` in `server.py`
2. Create service in `services/`
3. Add routes in `routes/`
4. Update models if needed

#### Running Tests
```bash
cd backend
pytest
```

### Frontend Development

#### Project Structure
```
frontend/
├── src/
│   ├── components/   # React components
│   ├── App.js       # Main app component
│   └── index.js     # Entry point
├── public/          # Static assets
└── package.json     # Dependencies
```

#### Adding New Features
1. Create component in `src/components/`
2. Add routes in `App.js`
3. Update navigation as needed

#### Running Development Server
```bash
cd frontend
yarn start
```

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
tail -f /var/log/supervisor/backend.*.log

# Check MongoDB connection
mongo --eval "db.stats()"

# Verify dependencies
pip list | grep -E "(fastapi|motor|pymongo)"
```

#### Frontend Won't Connect
```bash
# Check environment variables
cat frontend/.env

# Verify backend is running
curl http://localhost:8001/api/

# Check CORS settings
```

#### Tool Installation Fails
```bash
# Check Go installation
go version

# Verify network connectivity
ping github.com

# Check disk space
df -h
```

### Performance Optimization

#### Backend Optimization
- Enable MongoDB indexing
- Use connection pooling
- Implement caching with Redis
- Optimize database queries

#### Frontend Optimization
- Implement lazy loading
- Use React.memo for components
- Optimize bundle size
- Add service worker for caching

## 📈 Monitoring & Logging

### Application Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs
tail -f /var/log/supervisor/frontend.*.log

# MongoDB logs
tail -f /var/log/mongodb/mongod.log
```

### Metrics & Monitoring
- Tool execution times
- Scan success rates
- Database performance
- API response times

## 🔒 Security Considerations

### Current Security Features
- Input validation and sanitization
- SQL injection prevention
- CORS protection
- Rate limiting (planned)

### Recommended Security Measures
- Implement authentication & authorization
- Use HTTPS in production
- Regular security audits
- Tool sandboxing
- Network segmentation

## 🚀 Deployment

### Production Deployment

#### Using Docker (Recommended)
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

#### Manual Deployment
1. Setup production MongoDB
2. Configure environment variables
3. Build frontend: `yarn build`
4. Deploy with nginx/apache
5. Use systemd for service management

### Environment Variables

#### Backend
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=reconflow_prod
DEBUG=false
LOG_LEVEL=INFO
```

#### Frontend
```env
REACT_APP_BACKEND_URL=https://api.reconflow.com
REACT_APP_ENV=production
```

## 📚 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit pull request
5. Follow code style guidelines

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- All the amazing security tool developers
- The open-source community
- Security researchers and bug bounty hunters

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the wiki
- **Community**: Join our Discord/Slack

---

**ReconFlow** - Automate your reconnaissance, focus on what matters. 🚀