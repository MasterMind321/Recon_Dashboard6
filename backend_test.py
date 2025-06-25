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

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://a18fa612-ecf9-4f60-a088-f097f6006d1b.preview.emergentagent.com"
    
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