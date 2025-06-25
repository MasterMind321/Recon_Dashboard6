import requests
import sys
import json
import uuid
from datetime import datetime, timedelta
import random

class HierarchicalAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.target_id = None  # Will store a target ID for tests

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
                    
                    # Verify target has required fields for hierarchical display
                    required_fields = ['id', 'domain', 'status', 'type', 'created_at', 'updated_at', 'last_scan']
                    missing_fields = [field for field in required_fields if field not in data[0]]
                    
                    if missing_fields:
                        print(f"⚠️ Target missing required fields: {', '.join(missing_fields)}")
                    else:
                        print("✅ Target has all required fields for hierarchical display")
            else:
                print(f"⚠️ Expected a list of targets, got: {type(data)}")
                
        return success, data
    
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
            
            # Verify the target has all required fields for hierarchical display
            required_fields = ['id', 'domain', 'type', 'status', 'created_at', 'updated_at', 
                              'subdomains', 'vulnerabilities', 'severity', 'workflow']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️ Target missing required fields: {', '.join(missing_fields)}")
            else:
                print("✅ Target has all required fields for hierarchical display")
                
        return success, data
    
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
                    
            # Verify default fields
            if data.get('status') != 'pending':
                print(f"⚠️ Created target has incorrect status: {data.get('status')} (expected 'pending')")
                
            if data.get('subdomains') != 0:
                print(f"⚠️ Created target has incorrect subdomains count: {data.get('subdomains')} (expected 0)")
                
            if data.get('vulnerabilities') != 0:
                print(f"⚠️ Created target has incorrect vulnerabilities count: {data.get('vulnerabilities')} (expected 0)")
                
            if data.get('severity') != 'none':
                print(f"⚠️ Created target has incorrect severity: {data.get('severity')} (expected 'none')")
                
        return success, data
    
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
                    required_fields = ['subdomain', 'discovered_by', 'first_seen', 'last_seen', 'ip_addresses']
                    missing_fields = [field for field in required_fields if field not in first_subdomain]
                    
                    if missing_fields:
                        print(f"⚠️ Subdomain result missing required fields: {', '.join(missing_fields)}")
                    else:
                        print("✅ Subdomain result has all required fields for hierarchical display")
                        
                    # Print some subdomain examples
                    for i, subdomain in enumerate(data[:5]):
                        print(f"  Subdomain {i+1}: {subdomain.get('subdomain')}")
                        print(f"    Discovered by: {', '.join(subdomain.get('discovered_by', []))}")
                        print(f"    IP Addresses: {', '.join(subdomain.get('ip_addresses', []))}")
            else:
                print(f"⚠️ Expected a list of subdomains, got: {type(data)}")
                
        return success, data
    
    def test_get_target_liveness_results(self, target_id=None, alive_only=True, with_screenshots=False):
        """Test getting liveness results for a target"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for liveness results test")
                return False, {}
            target_id = self.target_id
            
        params = {
            "alive_only": str(alive_only).lower(),
            "with_screenshots": str(with_screenshots).lower()
        }
            
        success, data = self.run_test(
            f"Get Liveness Results for Target: {target_id}" + 
            (" (alive only)" if alive_only else "") +
            (" (with screenshots)" if with_screenshots else ""),
            "GET",
            f"api/targets/{target_id}/liveness-results",
            200,
            params=params
        )
        
        if success and data:
            if isinstance(data, list):
                print(f"Found {len(data)} liveness results for target")
                
                # Verify structure of liveness results
                if len(data) > 0:
                    first_result = data[0]
                    required_fields = ['subdomain', 'is_alive', 'status_code', 'response_time', 
                                      'technologies', 'ip_addresses', 'title', 'server']
                    missing_fields = [field for field in required_fields if field not in first_result]
                    
                    if missing_fields:
                        print(f"⚠️ Liveness result missing required fields: {', '.join(missing_fields)}")
                    else:
                        print("✅ Liveness result has all required fields for hierarchical display")
                        
                    # Print some subdomain examples
                    for i, result in enumerate(data[:3]):
                        print(f"  Subdomain {i+1}: {result.get('subdomain')}")
                        print(f"    Alive: {result.get('is_alive')}")
                        print(f"    Status code: {result.get('status_code', 'N/A')}")
                        print(f"    Title: {result.get('title', 'N/A')}")
                        print(f"    Server: {result.get('server', 'N/A')}")
                        print(f"    Technologies: {', '.join(result.get('technologies', []))}")
            else:
                print(f"⚠️ Expected a list of liveness results, got: {type(data)}")
                
        return success, data
    
    def test_get_target_javascript_results(self, target_id=None):
        """Test getting JavaScript results for a target"""
        if target_id is None:
            if self.target_id is None:
                print("⚠️ No target ID available for JavaScript results test")
                return False, {}
            target_id = self.target_id
            
        success, data = self.run_test(
            f"Get JavaScript Results for Target: {target_id}",
            "GET",
            f"api/targets/{target_id}/javascript-results",
            200
        )
        
        if success and data:
            if isinstance(data, list):
                print(f"Found {len(data)} JavaScript results for target")
                
                # Verify structure of JavaScript results
                if len(data) > 0:
                    first_result = data[0]
                    required_fields = ['subdomain', 'js_files', 'endpoints', 'keywords', 
                                      'total_js_files', 'total_endpoints', 'total_keywords']
                    missing_fields = [field for field in required_fields if field not in first_result]
                    
                    if missing_fields:
                        print(f"⚠️ JavaScript result missing required fields: {', '.join(missing_fields)}")
                    else:
                        print("✅ JavaScript result has all required fields for hierarchical display")
                        
                    # Print some subdomain examples
                    print(f"  Subdomain: {first_result.get('subdomain')}")
                    print(f"  Total JS files: {first_result.get('total_js_files')}")
                    print(f"  Total endpoints: {first_result.get('total_endpoints')}")
                    print(f"  Total keywords: {first_result.get('total_keywords')}")
                    
                    # Check JS files structure
                    if first_result.get('js_files') and len(first_result.get('js_files')) > 0:
                        js_file = first_result.get('js_files')[0]
                        js_required_fields = ['url', 'filename', 'size_bytes', 'is_external']
                        js_missing_fields = [field for field in js_required_fields if field not in js_file]
                        
                        if js_missing_fields:
                            print(f"⚠️ JS file missing required fields: {', '.join(js_missing_fields)}")
                        else:
                            print("✅ JS file has all required fields")
                    
                    # Check endpoints structure
                    if first_result.get('endpoints') and len(first_result.get('endpoints')) > 0:
                        endpoint = first_result.get('endpoints')[0]
                        endpoint_required_fields = ['url', 'method', 'endpoint_type', 'source_js_file']
                        endpoint_missing_fields = [field for field in endpoint_required_fields if field not in endpoint]
                        
                        if endpoint_missing_fields:
                            print(f"⚠️ Endpoint missing required fields: {', '.join(endpoint_missing_fields)}")
                        else:
                            print("✅ Endpoint has all required fields")
                    
                    # Check keywords structure
                    if first_result.get('keywords') and len(first_result.get('keywords')) > 0:
                        keyword = first_result.get('keywords')[0]
                        keyword_required_fields = ['value', 'keyword_type', 'source_js_file']
                        keyword_missing_fields = [field for field in keyword_required_fields if field not in keyword]
                        
                        if keyword_missing_fields:
                            print(f"⚠️ Keyword missing required fields: {', '.join(keyword_missing_fields)}")
                        else:
                            print("✅ Keyword has all required fields")
            else:
                print(f"⚠️ Expected a list of JavaScript results, got: {type(data)}")
                
        return success, data

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://f1fea40a-624c-44a3-a4aa-3eb86fa11569.preview.emergentagent.com"
    
    print(f"Testing Hierarchical Domain Results APIs at: {backend_url}")
    
    # Setup
    tester = HierarchicalAPITester(backend_url)

    # 1. Test Target Management APIs
    print("\n==== Target Management APIs ====")
    
    # Test getting all targets
    tester.test_get_targets()
    
    # If we don't have a target, create one
    if tester.target_id is None:
        print("\n--- Creating Test Target ---")
        tester.test_create_target("hierarchical-test.example.com", "domain")
    
    # Test getting target by ID
    if tester.target_id:
        tester.test_get_target_by_id(tester.target_id)
    
    # Test getting target statistics
    tester.test_get_target_stats()
    
    # 2. Test Subdomain APIs
    print("\n==== Subdomain APIs ====")
    
    # Test getting subdomains for a target
    if tester.target_id:
        tester.test_get_target_subdomains(tester.target_id)
    
    # 3. Test Liveness Results APIs
    print("\n==== Liveness Results APIs ====")
    
    # Test getting liveness results for a target
    if tester.target_id:
        tester.test_get_target_liveness_results(tester.target_id)
    
    # 4. Test JavaScript Analysis APIs
    print("\n==== JavaScript Analysis APIs ====")
    
    # Test getting JavaScript results for a target
    if tester.target_id:
        tester.test_get_target_javascript_results(tester.target_id)
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.2f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())