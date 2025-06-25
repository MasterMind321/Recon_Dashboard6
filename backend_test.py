import requests
import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import random

class ReconAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.tool_id = None  # Will store a tool ID for update/install tests
        self.scan_result_id = None  # Will store a scan result ID for tests
        self.target_id = None  # Will store a target ID for target management tests
        self.enumeration_job_id = None  # Will store an enumeration job ID for tests

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "api",
            200
        )

    def test_create_status_check(self, client_name):
        """Test creating a status check"""
        return self.run_test(
            "Create Status Check",
            "POST",
            "api/status",
            200,
            data={"client_name": client_name}
        )

    def test_get_status_checks(self):
        """Test getting all status checks"""
        return self.run_test(
            "Get Status Checks",
            "GET",
            "api/status",
            200
        )
        
    def test_get_all_tools(self):
        """Test getting all reconnaissance tools"""
        success, data = self.run_test(
            "Get All Tools",
            "GET",
            "api/tools",
            200
        )
        
        if success and data:
            # Store a tool ID for later tests
            if isinstance(data, list) and len(data) > 0:
                self.tool_id = data[0].get('id')
                print(f"Found {len(data)} tools")
                
                # Verify specific tools are present
                tool_names = [tool.get('name') for tool in data]
                required_tools = ['subfinder', 'amass', 'nuclei', 'httpx', 'dalfox', 'sqlmap', 'gau', 'waybackurls', 'ffuf', 'feroxbuster']
                
                missing_tools = [tool for tool in required_tools if tool not in tool_names]
                if missing_tools:
                    print(f"⚠️ Missing required tools: {', '.join(missing_tools)}")
                else:
                    print(f"✅ All required tools are present")
                
                # Verify categories are properly assigned
                categories = set(tool.get('category') for tool in data)
                print(f"Found categories: {', '.join(categories)}")
                
                # Verify all 10 categories are present
                expected_categories = {
                    "subdomain_enumeration", 
                    "liveness_fingerprinting", 
                    "javascript_endpoint",
                    "vulnerability_scanning", 
                    "historical_data", 
                    "directory_fuzzing",
                    "port_scanning",
                    "cloud_recon",
                    "reporting_notification",
                    "utility_misc"
                }
                
                missing_categories = expected_categories - set(categories)
                if missing_categories:
                    print(f"⚠️ Missing categories: {', '.join(missing_categories)}")
                else:
                    print(f"✅ All 10 categories are present")
                
                # Check color coding
                for tool in data:
                    if not tool.get('icon_color') or not tool.get('category_color'):
                        print(f"⚠️ Tool {tool.get('name')} is missing color coding")
                        
                # Verify we have at least 58 tools
                if len(data) < 58:
                    print(f"⚠️ Expected at least 58 tools, but found {len(data)}")
                else:
                    print(f"✅ Found {len(data)} tools (expected at least 58)")
            else:
                print("⚠️ No tools returned from API")
                
        return success, data
    
    def test_get_tools_by_category(self, category):
        """Test getting tools by category"""
        success, data = self.run_test(
            f"Get Tools by Category: {category}",
            "GET",
            f"api/tools/category/{category}",
            200
        )
        
        if success and data:
            if isinstance(data, list):
                print(f"Found {len(data)} tools in category '{category}'")
                
                # Verify all tools in this response have the correct category
                for tool in data:
                    if tool.get('category') != category:
                        print(f"⚠️ Tool {tool.get('name')} has incorrect category: {tool.get('category')} (expected {category})")
                        success = False
            else:
                print(f"⚠️ Expected a list of tools, got: {type(data)}")
                success = False
                
        return success, data
    
    def test_get_tool_stats(self):
        """Test getting tool statistics"""
        success, data = self.run_test(
            "Get Tool Statistics",
            "GET",
            "api/tools/stats",
            200
        )
        
        if success and data:
            # Verify the structure of the stats response
            if 'installation' in data and 'status' in data and 'categories' in data:
                print("✅ Tool statistics structure is correct")
                
                # Print some stats for verification
                print(f"Installation stats: {json.dumps(data['installation'], indent=2)}")
                print(f"Status stats: {json.dumps(data['status'], indent=2)}")
                print(f"Category counts: {json.dumps(data['categories'], indent=2)}")
                
                # Verify all 10 categories are present in the stats
                expected_categories = {
                    "subdomain_enumeration", 
                    "liveness_fingerprinting", 
                    "javascript_endpoint",
                    "vulnerability_scanning", 
                    "historical_data", 
                    "directory_fuzzing",
                    "port_scanning",
                    "cloud_recon",
                    "reporting_notification",
                    "utility_misc"
                }
                
                missing_categories = expected_categories - set(data['categories'].keys())
                if missing_categories:
                    print(f"⚠️ Missing categories in stats: {', '.join(missing_categories)}")
                    success = False
                else:
                    print(f"✅ All 10 categories are present in stats")
                    
                # Verify total tool count matches expected
                total_tools = sum(data['categories'].values())
                if total_tools < 58:
                    print(f"⚠️ Total tools in stats ({total_tools}) is less than expected (58+)")
                    success = False
                else:
                    print(f"✅ Total tools in stats: {total_tools}")
            else:
                print("⚠️ Tool statistics structure is incorrect")
                success = False
                
        return success, data
    
    def test_update_tool(self, tool_id):
        """Test updating a tool"""
        if not tool_id:
            print("⚠️ No tool ID available for update test")
            return False, {}
            
        update_data = {
            "installation_status": "installed",
            "tool_status": "online",
            "version": "1.0.0",
            "cpu_usage": 5.0,
            "memory_usage": 10.0
        }
        
        return self.run_test(
            f"Update Tool: {tool_id}",
            "PUT",
            f"api/tools/{tool_id}",
            200,
            data=update_data
        )
    
    def test_install_tool(self, tool_id):
        """Test tool installation endpoint"""
        if not tool_id:
            print("⚠️ No tool ID available for install test")
            return False, {}
            
        return self.run_test(
            f"Install Tool: {tool_id}",
            "POST",
            f"api/tools/{tool_id}/install",
            200
        )
        
    def test_invalid_tool_id(self):
        """Test with an invalid tool ID"""
        invalid_id = "invalid-tool-id-12345"
        return self.run_test(
            "Invalid Tool ID",
            "PUT",
            f"api/tools/{invalid_id}",
            404,
            data={"installation_status": "installed"}
        )
        
    def test_invalid_category(self):
        """Test with an invalid category"""
        return self.run_test(
            "Invalid Category",
            "GET",
            "api/tools/category/invalid_category",
            422  # FastAPI validation error
        )
        
    def test_create_scan_result(self, tool_name, category):
        """Test creating a new scan result"""
        scan_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        scan_data = {
            "id": scan_id,
            "target": "example.com",
            "tool_name": tool_name,
            "category": category,
            "status": "completed",
            "results": {
                "findings": [
                    {"type": "subdomain", "value": "api.example.com"},
                    {"type": "subdomain", "value": "admin.example.com"}
                ],
                "summary": {
                    "total_findings": 2,
                    "severity": "medium"
                }
            },
            "start_time": (now - timedelta(minutes=5)).isoformat(),
            "end_time": now.isoformat(),
            "duration_seconds": 300,
            "output_file": "/tmp/scan_results.json"
        }
        
        success, data = self.run_test(
            "Create Scan Result",
            "POST",
            "api/scan-results",
            200,
            data=scan_data
        )
        
        if success and data:
            self.scan_result_id = data.get('id')
            print(f"Created scan result with ID: {self.scan_result_id}")
            
        return success, data
    
    def test_get_scan_results(self):
        """Test getting all scan results"""
        success, data = self.run_test(
            "Get Scan Results",
            "GET",
            "api/scan-results",
            200
        )
        
        if success and data:
            if isinstance(data, list):
                print(f"Found {len(data)} scan results")
                
                # Verify structure of scan results
                if len(data) > 0:
                    first_result = data[0]
                    required_fields = ['id', 'target', 'tool_name', 'category', 'status', 'results', 'start_time']
                    missing_fields = [field for field in required_fields if field not in first_result]
                    
                    if missing_fields:
                        print(f"⚠️ Scan result missing required fields: {', '.join(missing_fields)}")
                        success = False
                    else:
                        print("✅ Scan result has all required fields")
            else:
                print(f"⚠️ Expected a list of scan results, got: {type(data)}")
                success = False
                
        return success, data
    
    def test_get_scan_results_with_filter(self, target):
        """Test getting scan results with target filter"""
        return self.run_test(
            f"Get Scan Results for target: {target}",
            "GET",
            "api/scan-results",
            200,
            params={"target": target}
        )
        
    # Target Management API Tests
    def test_get_target_stats(self):
        """Test getting target statistics"""
        success, data = self.run_test(
            "Get Target Statistics",
            "GET",
            "api/targets/stats",
            200
        )
        
        if success and data:
            # Verify the structure of the stats response
            required_fields = ['total_targets', 'active_scans', 'total_subdomains', 
                              'total_vulnerabilities', 'by_status', 'by_type', 'by_severity']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️ Target stats missing required fields: {', '.join(missing_fields)}")
                success = False
            else:
                print("✅ Target stats has all required fields")
                print(f"Total targets: {data['total_targets']}")
                print(f"Active scans: {data['active_scans']}")
                print(f"Total subdomains: {data['total_subdomains']}")
                print(f"Total vulnerabilities: {data['total_vulnerabilities']}")
                print(f"By status: {json.dumps(data['by_status'], indent=2)}")
                print(f"By type: {json.dumps(data['by_type'], indent=2)}")
                print(f"By severity: {json.dumps(data['by_severity'], indent=2)}")
                
        return success, data
    
    def test_get_targets(self):
        """Test getting all targets"""
        success, data = self.run_test(
            "Get All Targets",
            "GET",
            "api/targets",
            200
        )
        
        if success and data:
            if isinstance(data, list):
                print(f"Found {len(data)} targets")
                
                # If we have targets, store one ID for later tests
                if len(data) > 0:
                    self.target_id = data[0].get('id')
                    print(f"Using target ID for tests: {self.target_id}")
            else:
                print(f"⚠️ Expected a list of targets, got: {type(data)}")
                success = False
                
        return success, data
    
    def test_get_targets_with_filters(self, status=None, target_type=None):
        """Test getting targets with filters"""
        params = {}
        if status:
            params['status'] = status
        if target_type:
            params['type'] = target_type
            
        filter_desc = []
        if status:
            filter_desc.append(f"status={status}")
        if target_type:
            filter_desc.append(f"type={target_type}")
            
        filter_str = " and ".join(filter_desc) if filter_desc else "no filters"
        
        success, data = self.run_test(
            f"Get Targets with filters: {filter_str}",
            "GET",
            "api/targets",
            200,
            params=params
        )
        
        if success and data:
            if isinstance(data, list):
                print(f"Found {len(data)} targets with {filter_str}")
                
                # Verify filters were applied correctly
                if status and len(data) > 0:
                    for target in data:
                        if target.get('status') != status:
                            print(f"⚠️ Target {target.get('id')} has incorrect status: {target.get('status')} (expected {status})")
                            success = False
                
                if target_type and len(data) > 0:
                    for target in data:
                        if target.get('type') != target_type:
                            print(f"⚠️ Target {target.get('id')} has incorrect type: {target.get('type')} (expected {target_type})")
                            success = False
            else:
                print(f"⚠️ Expected a list of targets, got: {type(data)}")
                success = False
                
        return success, data
    
    def test_create_target(self, domain=None, target_type=None):
        """Test creating a new target"""
        if domain is None:
            # Generate a random domain to avoid duplicates
            random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
            domain = f"test-{random_id}.example.com"
            
        if target_type is None:
            target_type = random.choice(["domain", "ip", "cidr"])
            
        target_data = {
            "domain": domain,
            "type": target_type,
            "workflow": "full-recon",
            "notes": f"Test target created at {datetime.utcnow().isoformat()}"
        }
        
        success, data = self.run_test(
            f"Create Target: {domain} ({target_type})",
            "POST",
            "api/targets",
            200,
            data=target_data
        )
        
        if success and data:
            self.target_id = data.get('id')
            print(f"Created target with ID: {self.target_id}")
            
            # Verify the created target has the correct data
            for key, value in target_data.items():
                if data.get(key) != value:
                    print(f"⚠️ Created target has incorrect {key}: {data.get(key)} (expected {value})")
                    success = False
                    
            # Verify default fields
            if data.get('status') != 'pending':
                print(f"⚠️ Created target has incorrect status: {data.get('status')} (expected 'pending')")
                success = False
                
            if data.get('subdomains') != 0:
                print(f"⚠️ Created target has incorrect subdomains count: {data.get('subdomains')} (expected 0)")
                success = False
                
            if data.get('vulnerabilities') != 0:
                print(f"⚠️ Created target has incorrect vulnerabilities count: {data.get('vulnerabilities')} (expected 0)")
                success = False
                
            if data.get('severity') != 'none':
                print(f"⚠️ Created target has incorrect severity: {data.get('severity')} (expected 'none')")
                success = False
                
        return success, data
    
    def test_create_duplicate_target(self, domain, target_type):
        """Test creating a duplicate target (should fail)"""
        target_data = {
            "domain": domain,
            "type": target_type,
            "workflow": "full-recon",
            "notes": "Duplicate target test"
        }
        
        return self.run_test(
            f"Create Duplicate Target: {domain}",
            "POST",
            "api/targets",
            400,  # Expect 400 Bad Request for duplicate
            data=target_data
        )
    
    def test_get_target_by_id(self, target_id=None):
        """Test getting a specific target by ID"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for get test")
                return False, {}
            target_id = self.target_id
            
        success, data = self.run_test(
            f"Get Target by ID: {target_id}",
            "GET",
            f"api/targets/{target_id}",
            200
        )
        
        if success and data:
            print(f"Retrieved target: {data.get('domain')} ({data.get('type')})")
            
            # Verify the target has all required fields
            required_fields = ['id', 'domain', 'type', 'status', 'created_at', 'updated_at', 
                              'subdomains', 'vulnerabilities', 'severity', 'workflow']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️ Target missing required fields: {', '.join(missing_fields)}")
                success = False
            else:
                print("✅ Target has all required fields")
                
        return success, data
    
    def test_get_target_invalid_id(self):
        """Test getting a target with an invalid ID"""
        invalid_id = str(uuid.uuid4())  # Generate a random UUID that shouldn't exist
        
        return self.run_test(
            f"Get Target with Invalid ID: {invalid_id}",
            "GET",
            f"api/targets/{invalid_id}",
            404  # Expect 404 Not Found
        )
    
    def test_update_target(self, target_id=None):
        """Test updating a target"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for update test")
                return False, {}
            target_id = self.target_id
            
        update_data = {
            "status": "active",
            "notes": f"Updated at {datetime.utcnow().isoformat()}"
        }
        
        success, data = self.run_test(
            f"Update Target: {target_id}",
            "PUT",
            f"api/targets/{target_id}",
            200,
            data=update_data
        )
        
        if success and data:
            print(f"Updated target: {data.get('domain')} (status: {data.get('status')})")
            
            # Verify the update was applied correctly
            for key, value in update_data.items():
                if data.get(key) != value:
                    print(f"⚠️ Updated target has incorrect {key}: {data.get(key)} (expected {value})")
                    success = False
                    
        return success, data
    
    def test_update_target_invalid_id(self):
        """Test updating a target with an invalid ID"""
        invalid_id = str(uuid.uuid4())  # Generate a random UUID that shouldn't exist
        
        update_data = {
            "status": "active",
            "notes": "This update should fail"
        }
        
        return self.run_test(
            f"Update Target with Invalid ID: {invalid_id}",
            "PUT",
            f"api/targets/{invalid_id}",
            404,  # Expect 404 Not Found
            data=update_data
        )
    
    def test_start_scan(self, target_id=None):
        """Test starting a scan for a target"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for scan test")
                return False, {}
            target_id = self.target_id
            
        success, data = self.run_test(
            f"Start Scan for Target: {target_id}",
            "POST",
            f"api/targets/{target_id}/scan",
            200
        )
        
        if success and data:
            print(f"Started scan for target: {data.get('domain')}")
            
            # Verify the scan was started correctly
            if data.get('status') != 'scanning':
                print(f"⚠️ Target has incorrect status after scan start: {data.get('status')} (expected 'scanning')")
                success = False
                
            if data.get('last_scan') is None:
                print("⚠️ Target missing last_scan timestamp after scan start")
                success = False
                
        return success, data
    
    def test_start_scan_invalid_id(self):
        """Test starting a scan for a target with an invalid ID"""
        invalid_id = str(uuid.uuid4())  # Generate a random UUID that shouldn't exist
        
        return self.run_test(
            f"Start Scan with Invalid Target ID: {invalid_id}",
            "POST",
            f"api/targets/{invalid_id}/scan",
            404  # Expect 404 Not Found
        )
    
    def test_delete_target(self, target_id=None):
        """Test deleting a target"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for delete test")
                return False, {}
            target_id = self.target_id
            
        success, data = self.run_test(
            f"Delete Target: {target_id}",
            "DELETE",
            f"api/targets/{target_id}",
            200
        )
        
        if success:
            print(f"Successfully deleted target: {target_id}")
            
            # Verify the target was actually deleted by trying to get it
            verify_success, _ = self.run_test(
                f"Verify Target Deletion: {target_id}",
                "GET",
                f"api/targets/{target_id}",
                404  # Expect 404 Not Found after deletion
            )
            
            if not verify_success:
                print(f"⚠️ Target {target_id} was not properly deleted")
                success = False
                
        return success, data
    
    def test_delete_target_invalid_id(self):
        """Test deleting a target with an invalid ID"""
        invalid_id = str(uuid.uuid4())  # Generate a random UUID that shouldn't exist
        
        return self.run_test(
            f"Delete Target with Invalid ID: {invalid_id}",
            "DELETE",
            f"api/targets/{invalid_id}",
            404  # Expect 404 Not Found
        )
        
    # Subdomain Enumeration API Tests
    def test_get_tools_status(self):
        """Test getting subdomain enumeration tools status"""
        success, data = self.run_test(
            "Get Subdomain Enumeration Tools Status",
            "GET",
            "api/tools/status",
            200
        )
        
        if success and data:
            # Verify the structure of the response
            if 'tools' in data and 'total_tools' in data and 'installed_tools' in data:
                print("✅ Tools status structure is correct")
                
                # Print tools status
                print(f"Total tools: {data['total_tools']}")
                print(f"Installed tools: {data['installed_tools']}")
                
                # Check specific tools
                tools = data['tools']
                for tool, installed in tools.items():
                    print(f"Tool {tool}: {'Installed' if installed else 'Not installed'}")
                    
                # Verify all 10 tools are present
                expected_tools = [
                    "subfinder", "amass", "crtsh", "puredns", "dnsx", 
                    "gotator", "dnsgen", "github-subdomains", "mapcidr", "asnlookup"
                ]
                
                missing_tools = [tool for tool in expected_tools if tool not in tools]
                if missing_tools:
                    print(f"⚠️ Missing tools in status: {', '.join(missing_tools)}")
                    success = False
                else:
                    print(f"✅ All 10 subdomain enumeration tools are present in status")
            else:
                print("⚠️ Tools status structure is incorrect")
                success = False
                
        return success, data
    
    def test_install_tools(self):
        """Test installing subdomain enumeration tools"""
        return self.run_test(
            "Install Subdomain Enumeration Tools",
            "POST",
            "api/tools/install",
            200
        )
    
    def test_start_subdomain_enumeration(self, target_id=None, tools=None):
        """Test starting subdomain enumeration for a target"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for subdomain enumeration test")
                return False, {}
            target_id = self.target_id
            
        data = {"notes": "Test subdomain enumeration"}
        if tools:
            data["tools"] = tools
            
        success, response = self.run_test(
            f"Start Subdomain Enumeration for Target: {target_id}",
            "POST",
            f"api/targets/{target_id}/enumerate-subdomains",
            200,
            data=data
        )
        
        if success and response:
            self.enumeration_job_id = response.get('id')
            print(f"Created enumeration job with ID: {self.enumeration_job_id}")
            
            # Verify the job has the correct data
            if response.get('target_id') != target_id:
                print(f"⚠️ Enumeration job has incorrect target_id: {response.get('target_id')} (expected {target_id})")
                success = False
                
            if response.get('status') != 'pending':
                print(f"⚠️ Enumeration job has incorrect status: {response.get('status')} (expected 'pending')")
                success = False
                
        return success, response
    
    def test_start_subdomain_enumeration_invalid_target(self):
        """Test starting subdomain enumeration for an invalid target"""
        invalid_id = str(uuid.uuid4())  # Generate a random UUID that shouldn't exist
        
        return self.run_test(
            f"Start Subdomain Enumeration with Invalid Target ID: {invalid_id}",
            "POST",
            f"api/targets/{invalid_id}/enumerate-subdomains",
            404,  # Expect 404 Not Found
            data={"notes": "This should fail"}
        )
    
    def test_get_enumeration_job(self, job_id=None):
        """Test getting a specific enumeration job"""
        if job_id is None:
            if self.enumeration_job_id is None:
                print("⚠️ No enumeration job ID available for get test")
                return False, {}
            job_id = self.enumeration_job_id
            
        success, data = self.run_test(
            f"Get Enumeration Job: {job_id}",
            "GET",
            f"api/enumeration-jobs/{job_id}",
            200
        )
        
        if success and data:
            print(f"Retrieved enumeration job for domain: {data.get('domain')} (status: {data.get('status')})")
            
            # Verify the job has all required fields
            required_fields = ['id', 'target_id', 'domain', 'status', 'created_at']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️ Enumeration job missing required fields: {', '.join(missing_fields)}")
                success = False
            else:
                print("✅ Enumeration job has all required fields")
                
        return success, data
    
    def test_get_enumeration_job_invalid_id(self):
        """Test getting an enumeration job with an invalid ID"""
        invalid_id = str(uuid.uuid4())  # Generate a random UUID that shouldn't exist
        
        return self.run_test(
            f"Get Enumeration Job with Invalid ID: {invalid_id}",
            "GET",
            f"api/enumeration-jobs/{invalid_id}",
            404  # Expect 404 Not Found
        )
    
    def test_get_target_enumeration_jobs(self, target_id=None):
        """Test getting enumeration jobs for a target"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for enumeration jobs test")
                return False, {}
            target_id = self.target_id
            
        success, data = self.run_test(
            f"Get Enumeration Jobs for Target: {target_id}",
            "GET",
            f"api/targets/{target_id}/enumeration-jobs",
            200
        )
        
        if success and data:
            if isinstance(data, list):
                print(f"Found {len(data)} enumeration jobs for target")
                
                # Verify structure of enumeration jobs
                if len(data) > 0:
                    first_job = data[0]
                    required_fields = ['id', 'target_id', 'domain', 'status', 'created_at']
                    missing_fields = [field for field in required_fields if field not in first_job]
                    
                    if missing_fields:
                        print(f"⚠️ Enumeration job missing required fields: {', '.join(missing_fields)}")
                        success = False
                    else:
                        print("✅ Enumeration job has all required fields")
            else:
                print(f"⚠️ Expected a list of enumeration jobs, got: {type(data)}")
                success = False
                
        return success, data
    
    def test_get_target_enumeration_jobs_invalid_target(self):
        """Test getting enumeration jobs for an invalid target"""
        invalid_id = str(uuid.uuid4())  # Generate a random UUID that shouldn't exist
        
        return self.run_test(
            f"Get Enumeration Jobs with Invalid Target ID: {invalid_id}",
            "GET",
            f"api/targets/{invalid_id}/enumeration-jobs",
            404  # Expect 404 Not Found
        )
    
    def test_get_target_subdomains(self, target_id=None, alive_only=False):
        """Test getting subdomains for a target"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for subdomains test")
                return False, {}
            target_id = self.target_id
            
        params = {}
        if alive_only:
            params["alive_only"] = "true"
            
        success, data = self.run_test(
            f"Get Subdomains for Target: {target_id}" + (" (alive only)" if alive_only else ""),
            "GET",
            f"api/targets/{target_id}/subdomains",
            200,
            params=params
        )
        
        if success and data:
            if isinstance(data, list):
                print(f"Found {len(data)} subdomains for target")
                
                # Verify structure of subdomains
                if len(data) > 0:
                    first_subdomain = data[0]
                    required_fields = ['subdomain', 'discovered_by', 'first_seen', 'last_seen']
                    missing_fields = [field for field in required_fields if field not in first_subdomain]
                    
                    if missing_fields:
                        print(f"⚠️ Subdomain result missing required fields: {', '.join(missing_fields)}")
                        success = False
                    else:
                        print("✅ Subdomain result has all required fields")
                        
                    # Print some subdomain examples
                    for i, subdomain in enumerate(data[:5]):
                        print(f"  Subdomain {i+1}: {subdomain.get('subdomain')}")
                        print(f"    Discovered by: {', '.join(subdomain.get('discovered_by', []))}")
            else:
                print(f"⚠️ Expected a list of subdomains, got: {type(data)}")
                success = False
                
        return success, data
    
    def test_get_target_subdomains_invalid_target(self):
        """Test getting subdomains for an invalid target"""
        invalid_id = str(uuid.uuid4())  # Generate a random UUID that shouldn't exist
        
        return self.run_test(
            f"Get Subdomains with Invalid Target ID: {invalid_id}",
            "GET",
            f"api/targets/{invalid_id}/subdomains",
            404  # Expect 404 Not Found
        )
    
    def test_get_enumeration_stats(self):
        """Test getting overall enumeration statistics"""
        success, data = self.run_test(
            "Get Enumeration Statistics",
            "GET",
            "api/subdomains/stats",
            200
        )
        
        if success and data:
            # Verify the structure of the stats response
            required_fields = ['total_jobs', 'active_jobs', 'completed_jobs', 
                              'failed_jobs', 'total_subdomains_discovered', 
                              'by_status', 'by_tool_success_rate', 'avg_execution_time']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️ Enumeration stats missing required fields: {', '.join(missing_fields)}")
                success = False
            else:
                print("✅ Enumeration stats has all required fields")
                print(f"Total jobs: {data['total_jobs']}")
                print(f"Active jobs: {data['active_jobs']}")
                print(f"Completed jobs: {data['completed_jobs']}")
                print(f"Failed jobs: {data['failed_jobs']}")
                print(f"Total subdomains discovered: {data['total_subdomains_discovered']}")
                print(f"By status: {json.dumps(data['by_status'], indent=2)}")
                print(f"Tool success rates: {json.dumps(data['by_tool_success_rate'], indent=2)}")
                print(f"Average execution time: {data['avg_execution_time']:.2f} seconds")
                if data.get('most_productive_tool'):
                    print(f"Most productive tool: {data['most_productive_tool']}")
                
        return success, data

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://8340ecb9-18ff-4ec4-8c2c-bd0260fbc6ea.preview.emergentagent.com"
    
    print(f"Testing API at: {backend_url}")
    
    # Setup
    tester = ReconAPITester(backend_url)
    test_client = f"test_client_{datetime.now().strftime('%H%M%S')}"

    # Run tests
    print("\n==== Basic API Health Check ====")
    root_success, _ = tester.test_root_endpoint()
    if not root_success:
        print("❌ Root endpoint test failed, stopping tests")
        return 1

    print("\n==== Status Check Endpoints ====")
    create_success, status_data = tester.test_create_status_check(test_client)
    get_success, statuses = tester.test_get_status_checks()

    print("\n==== Tool Management Endpoints ====")
    # Get all tools
    all_tools_success, tools_data = tester.test_get_all_tools()
    
    # Test category endpoints for each valid category
    categories = [
        "subdomain_enumeration", 
        "liveness_fingerprinting", 
        "javascript_endpoint",
        "vulnerability_scanning", 
        "historical_data", 
        "directory_fuzzing",
        "port_scanning",
        "cloud_recon",
        "reporting_notification",
        "utility_misc"
    ]
    
    for category in categories:
        tester.test_get_tools_by_category(category)
    
    # Test tool statistics
    tester.test_get_tool_stats()
    
    # Test tool update and installation if we have a tool ID
    if tester.tool_id:
        tester.test_update_tool(tester.tool_id)
        tester.test_install_tool(tester.tool_id)
    
    # Test scan results endpoints
    print("\n==== Scan Results Endpoints ====")
    if tester.tool_id and all_tools_success and tools_data:
        # Find a tool to use for scan result test
        tool_name = tools_data[0].get('name')
        category = tools_data[0].get('category')
        
        # Create a scan result
        tester.test_create_scan_result(tool_name, category)
        
        # Get all scan results
        tester.test_get_scan_results()
        
        # Get scan results with filter
        tester.test_get_scan_results_with_filter("example.com")
    else:
        print("⚠️ Skipping scan results tests due to missing tool data")
    
    # Test Target Management API
    print("\n==== Target Management Endpoints ====")
    
    # 1. First test target stats (should be empty initially)
    print("\n--- Initial Target Stats ---")
    tester.test_get_target_stats()
    
    # 2. Test getting all targets (should be empty initially)
    print("\n--- Initial Targets List ---")
    tester.test_get_targets()
    
    # 3. Create multiple targets with different types
    print("\n--- Creating Test Targets ---")
    domain_target_success, domain_data = tester.test_create_target("example.com", "domain")
    ip_target_success, ip_data = tester.test_create_target(f"10.0.0.{random.randint(1, 254)}", "ip")
    cidr_target_success, cidr_data = tester.test_create_target(f"192.168.{random.randint(1, 254)}.0/24", "cidr")
    
    # Store target IDs for later cleanup
    domain_target_id = domain_data.get('id') if domain_target_success and domain_data else None
    ip_target_id = ip_data.get('id') if ip_target_success and ip_data else None
    cidr_target_id = cidr_data.get('id') if cidr_target_success and cidr_data else None
    
    # 4. Test duplicate target creation (should fail)
    if domain_target_success and domain_data:
        tester.test_create_duplicate_target(domain_data.get('domain'), domain_data.get('type'))
    
    # 5. Test getting targets again (should have our new targets)
    print("\n--- Updated Targets List ---")
    tester.test_get_targets()
    
    # 6. Test filtering targets by type
    print("\n--- Filtering Targets ---")
    tester.test_get_targets_with_filters(target_type="domain")
    tester.test_get_targets_with_filters(target_type="ip")
    tester.test_get_targets_with_filters(target_type="cidr")
    
    # 7. Test getting target by ID
    print("\n--- Getting Target by ID ---")
    if domain_target_id:
        tester.test_get_target_by_id(domain_target_id)
    
    # 8. Test getting target with invalid ID
    tester.test_get_target_invalid_id()
    
    # 9. Test updating target
    print("\n--- Updating Target ---")
    if domain_target_id:
        tester.test_update_target(domain_target_id)
    
    # 10. Test updating target with invalid ID
    tester.test_update_target_invalid_id()
    
    # 11. Test starting scan
    print("\n--- Starting Scan ---")
    if domain_target_id:
        tester.test_start_scan(domain_target_id)
    
    # 12. Test starting scan with invalid ID
    tester.test_start_scan_invalid_id()
    
    # Test Subdomain Enumeration API
    print("\n==== Subdomain Enumeration Endpoints ====")
    
    # 1. Test getting tools status
    print("\n--- Subdomain Enumeration Tools Status ---")
    tester.test_get_tools_status()
    
    # 2. Test installing tools
    print("\n--- Installing Subdomain Enumeration Tools ---")
    tester.test_install_tools()
    
    # 3. Test getting tools status again (should show installation in progress)
    print("\n--- Updated Tools Status ---")
    tester.test_get_tools_status()
    
    # 4. Test starting subdomain enumeration
    print("\n--- Starting Subdomain Enumeration ---")
    if domain_target_id:
        # Test with specific tools (crt.sh and dnsgen should be working)
        tester.test_start_subdomain_enumeration(domain_target_id, ["crtsh", "dnsgen"])
    
    # 5. Test starting subdomain enumeration with invalid target
    tester.test_start_subdomain_enumeration_invalid_target()
    
    # 6. Test getting enumeration job
    print("\n--- Getting Enumeration Job ---")
    if tester.enumeration_job_id:
        tester.test_get_enumeration_job(tester.enumeration_job_id)
    
    # 7. Test getting enumeration job with invalid ID
    tester.test_get_enumeration_job_invalid_id()
    
    # 8. Test getting enumeration jobs for target
    print("\n--- Getting Enumeration Jobs for Target ---")
    if domain_target_id:
        tester.test_get_target_enumeration_jobs(domain_target_id)
    
    # 9. Test getting enumeration jobs for invalid target
    tester.test_get_target_enumeration_jobs_invalid_target()
    
    # 10. Test getting subdomains for target
    print("\n--- Getting Subdomains for Target ---")
    if domain_target_id:
        tester.test_get_target_subdomains(domain_target_id)
    
    # 11. Test getting subdomains for invalid target
    tester.test_get_target_subdomains_invalid_target()
    
    # 12. Test getting enumeration statistics
    print("\n--- Getting Enumeration Statistics ---")
    tester.test_get_enumeration_stats()
    
    # 13. Test target stats again (should show our targets with updated subdomain counts)
    print("\n--- Updated Target Stats ---")
    tester.test_get_target_stats()
    
    # 14. Test deleting targets
    print("\n--- Deleting Targets ---")
    if domain_target_id:
        tester.test_delete_target(domain_target_id)
    if ip_target_id:
        tester.test_delete_target(ip_target_id)
    if cidr_target_id:
        tester.test_delete_target(cidr_target_id)
    
    # 15. Test deleting target with invalid ID
    tester.test_delete_target_invalid_id()
    
    # 16. Test target stats one more time (should be back to empty)
    print("\n--- Final Target Stats ---")
    tester.test_get_target_stats()
    
    # Test error conditions
    print("\n==== Error Conditions ====")
    tester.test_invalid_tool_id()
    tester.test_invalid_category()

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.2f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())