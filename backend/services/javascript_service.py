import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
import re
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple
import aiohttp
from urllib.parse import urljoin, urlparse
from pathlib import Path

from ..models.javascript_models import (
    JavaScriptTool, JavaScriptDiscoveryStatus, JavaScriptDiscoveryResult, 
    JavaScriptToolResult, JavaScriptDiscoveryJob, JSFileInfo, EndpointInfo, 
    KeywordInfo, EndpointType, HTTPMethod
)
from .database import get_database

logger = logging.getLogger(__name__)

class JavaScriptDiscoveryService:
    def __init__(self):
        self.tools_installed = {}
        self.tool_paths = {}
        
    async def check_tool_installation(self, tool: JavaScriptTool) -> bool:
        """Check if a tool is installed and accessible"""
        try:
            if tool == JavaScriptTool.SUBJS:
                result = await self._run_command(["subjs", "-h"], timeout=10)
                return result.returncode == 0
            elif tool == JavaScriptTool.XNLINKFINDER:
                result = await self._run_command(["python3", "-c", "import xnLinkFinder"], timeout=10)
                return result.returncode == 0
            elif tool == JavaScriptTool.LINKFINDER:
                result = await self._run_command(["python3", "-c", "import linkfinder"], timeout=10)
                return result.returncode == 0
            elif tool == JavaScriptTool.GETJSWORDS:
                getjswords_path = "/opt/getjswords/getjswords.py"
                return os.path.exists(getjswords_path)
            elif tool == JavaScriptTool.JSPARSER:
                result = await self._run_command(["python3", "-c", "import jsparser"], timeout=10)
                return result.returncode == 0
            elif tool == JavaScriptTool.JSBEAUTIFIER:
                result = await self._run_command(["python3", "-c", "import jsbeautifier"], timeout=10)
                return result.returncode == 0
            else:
                return True
        except Exception as e:
            logger.error(f"Error checking {tool} installation: {e}")
            return False

    async def install_tool(self, tool: JavaScriptTool) -> bool:
        """Install a specific tool"""
        try:
            logger.info(f"Installing tool: {tool}")
            
            if tool == JavaScriptTool.SUBJS:
                result = await self._run_command([
                    "go", "install", "github.com/lc/subjs@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == JavaScriptTool.XNLINKFINDER:
                result = await self._run_command([
                    "pip", "install", "xnLinkFinder"
                ], timeout=180)
                return result.returncode == 0
                
            elif tool == JavaScriptTool.LINKFINDER:
                result = await self._run_command([
                    "pip", "install", "linkfinder"
                ], timeout=180)
                return result.returncode == 0
                
            elif tool == JavaScriptTool.GETJSWORDS:
                # Clone getjswords repository
                result = await self._run_command([
                    "git", "clone", "https://github.com/m4ll0k/getjswords.git", "/opt/getjswords"
                ], timeout=180)
                if result.returncode == 0:
                    # Install any dependencies if requirements.txt exists
                    requirements_path = "/opt/getjswords/requirements.txt"
                    if os.path.exists(requirements_path):
                        result = await self._run_command([
                            "pip", "install", "-r", requirements_path
                        ], timeout=180)
                return result.returncode == 0
                
            elif tool == JavaScriptTool.JSPARSER:
                result = await self._run_command([
                    "pip", "install", "jsparser"
                ], timeout=180)
                return result.returncode == 0
                
            elif tool == JavaScriptTool.JSBEAUTIFIER:
                result = await self._run_command([
                    "pip", "install", "jsbeautifier"
                ], timeout=180)
                return result.returncode == 0
                
            return True
                
        except Exception as e:
            logger.error(f"Error installing {tool}: {e}")
            return False

    async def install_all_tools(self) -> Dict[JavaScriptTool, bool]:
        """Install all JavaScript discovery tools"""
        results = {}
        
        for tool in JavaScriptTool:
            try:
                # Check if already installed
                if await self.check_tool_installation(tool):
                    logger.info(f"{tool} already installed")
                    results[tool] = True
                    continue
                    
                # Try to install
                success = await self.install_tool(tool)
                results[tool] = success
                
                if success:
                    logger.info(f"Successfully installed {tool}")
                else:
                    logger.error(f"Failed to install {tool}")
                    
            except Exception as e:
                logger.error(f"Exception installing {tool}: {e}")
                results[tool] = False
                
        return results

    async def _run_command(self, command: List[str], timeout: int = 60, input_data: str = None) -> subprocess.CompletedProcess:
        """Run a command asynchronously with timeout"""
        try:
            # Handle piped commands
            if "|" in command:
                # For complex shell commands, run through bash
                command_str = " ".join(command)
                process = await asyncio.create_subprocess_shell(
                    command_str,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    stdin=asyncio.subprocess.PIPE if input_data else None
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    stdin=asyncio.subprocess.PIPE if input_data else None
                )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=input_data.encode() if input_data else None),
                timeout=timeout
            )
            
            return subprocess.CompletedProcess(
                args=command,
                returncode=process.returncode,
                stdout=stdout.decode(errors='ignore') if stdout else '',
                stderr=stderr.decode(errors='ignore') if stderr else ''
            )
            
        except asyncio.TimeoutError:
            logger.error(f"Command timed out: {' '.join(command)}")
            return subprocess.CompletedProcess(
                args=command,
                returncode=-1,
                stdout='',
                stderr='Command timed out'
            )
        except Exception as e:
            logger.error(f"Error running command {' '.join(command)}: {e}")
            return subprocess.CompletedProcess(
                args=command,
                returncode=-1,
                stdout='',
                stderr=str(e)
            )

    async def run_subjs(self, hosts: List[str]) -> Tuple[Dict[str, List[JSFileInfo]], JavaScriptToolResult]:
        """Run subjs tool to extract JS URLs from HTML"""
        start_time = time.time()
        results = {}
        
        try:
            # Create input file with hosts
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                for host in hosts:
                    f.write(f"https://{host}\n")
                    f.write(f"http://{host}\n")
                temp_file = f.name
            
            try:
                result = await self._run_command([
                    "subjs", "-i", temp_file
                ], timeout=300)
                
                execution_time = time.time() - start_time
                total_js_files = 0
                
                if result.returncode == 0:
                    # Parse output - subjs returns one JS URL per line
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if line and line.startswith('http'):
                            try:
                                parsed_url = urlparse(line)
                                domain = parsed_url.netloc
                                
                                # Determine which host this JS file belongs to
                                source_host = None
                                for host in hosts:
                                    if host in domain:
                                        source_host = host
                                        break
                                
                                if not source_host:
                                    source_host = hosts[0]  # Default to first host
                                
                                js_info = JSFileInfo(
                                    url=line,
                                    source_page=f"https://{source_host}",
                                    is_external=not any(host in domain for host in hosts),
                                    discovered_by=[JavaScriptTool.SUBJS]
                                )
                                
                                if source_host not in results:
                                    results[source_host] = []
                                results[source_host].append(js_info)
                                total_js_files += 1
                                
                            except Exception as e:
                                logger.error(f"Error parsing JS URL {line}: {e}")
                                continue
                                
                    return results, JavaScriptToolResult(
                        tool=JavaScriptTool.SUBJS,
                        status="success",
                        execution_time=execution_time,
                        hosts_checked=len(hosts),
                        js_files_found=total_js_files,
                        endpoints_found=0,
                        keywords_found=0
                    )
                else:
                    return results, JavaScriptToolResult(
                        tool=JavaScriptTool.SUBJS,
                        status="failed",
                        execution_time=execution_time,
                        hosts_checked=len(hosts),
                        js_files_found=0,
                        endpoints_found=0,
                        keywords_found=0,
                        error_message=result.stderr
                    )
                    
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            return results, JavaScriptToolResult(
                tool=JavaScriptTool.SUBJS,
                status="failed",
                execution_time=time.time() - start_time,
                hosts_checked=len(hosts),
                js_files_found=0,
                endpoints_found=0,
                keywords_found=0,
                error_message=str(e)
            )

    async def run_linkfinder(self, js_urls: List[str]) -> Tuple[List[EndpointInfo], JavaScriptToolResult]:
        """Run linkfinder tool to extract endpoints from JS files"""
        start_time = time.time()
        endpoints = []
        
        try:
            for js_url in js_urls[:10]:  # Limit to first 10 JS files to avoid timeout
                try:
                    result = await self._run_command([
                        "python3", "-c", 
                        f"""
import sys
sys.path.append('/usr/local/lib/python3.11/site-packages')
import linkfinder
import requests
import re

try:
    response = requests.get('{js_url}', timeout=30, verify=False)
    if response.status_code == 200:
        links = linkfinder.find_links(response.text)
        for link in links:
            print(link)
except Exception as e:
    print(f"Error: {{e}}", file=sys.stderr)
"""
                    ], timeout=60)
                    
                    if result.returncode == 0 and result.stdout:
                        for line in result.stdout.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('Error'):
                                endpoint = EndpointInfo(
                                    url=line,
                                    source_js_file=js_url,
                                    confidence_score=0.7,
                                    discovered_by=[JavaScriptTool.LINKFINDER]
                                )
                                endpoints.append(endpoint)
                                
                except Exception as e:
                    logger.error(f"Error processing {js_url} with linkfinder: {e}")
                    continue
                    
            execution_time = time.time() - start_time
            
            return endpoints, JavaScriptToolResult(
                tool=JavaScriptTool.LINKFINDER,
                status="success",
                execution_time=execution_time,
                hosts_checked=len(js_urls),
                js_files_found=0,
                endpoints_found=len(endpoints),
                keywords_found=0
            )
                
        except Exception as e:
            return endpoints, JavaScriptToolResult(
                tool=JavaScriptTool.LINKFINDER,
                status="failed",
                execution_time=time.time() - start_time,
                hosts_checked=len(js_urls),
                js_files_found=0,
                endpoints_found=0,
                keywords_found=0,
                error_message=str(e)
            )

    async def run_jsbeautifier(self, js_content: str) -> Tuple[str, bool]:
        """Run jsbeautifier to beautify minified JS"""
        try:
            # Simple check if JS is minified (long lines, no proper formatting)
            lines = js_content.split('\n')
            avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
            is_minified = avg_line_length > 200 or len(lines) < 10
            
            if is_minified:
                result = await self._run_command([
                    "python3", "-c", 
                    f"""
import jsbeautifier
content = '''{js_content}'''
options = jsbeautifier.default_options()
options.indent_size = 2
print(jsbeautifier.beautify(content, options))
"""
                ], timeout=30)
                
                if result.returncode == 0:
                    return result.stdout, True
                    
            return js_content, is_minified
            
        except Exception as e:
            logger.error(f"Error beautifying JS: {e}")
            return js_content, False

    async def extract_endpoints_with_regex(self, js_content: str, js_url: str) -> List[EndpointInfo]:
        """Extract endpoints using regex patterns"""
        endpoints = []
        
        # Common endpoint patterns
        patterns = [
            r'["\']([/][^"\']*)["\']',  # Paths starting with /
            r'["\']([a-zA-Z0-9]+://[^"\']*)["\']',  # Full URLs
            r'["\']([^"\']*\.(?:json|xml|txt|csv)[^"\']*)["\']',  # File extensions
            r'(?:fetch|ajax|get|post)\s*\(\s*["\']([^"\']+)["\']',  # API calls
            r'["\']([^"\']*(?:api|endpoint|service)[^"\']*)["\']',  # API-related paths
        ]
        
        for pattern in patterns:
            try:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    if len(match) > 3 and not match.startswith('data:'):
                        # Determine endpoint type and method
                        endpoint_type = EndpointType.UNKNOWN
                        method = HTTPMethod.UNKNOWN
                        confidence = 0.5
                        
                        if 'api' in match.lower():
                            endpoint_type = EndpointType.API
                            confidence = 0.8
                        elif 'ajax' in js_content.lower():
                            endpoint_type = EndpointType.AJAX
                            confidence = 0.7
                        elif match.endswith('.json'):
                            endpoint_type = EndpointType.REST
                            confidence = 0.9
                        
                        endpoint = EndpointInfo(
                            url=match,
                            method=method,
                            endpoint_type=endpoint_type,
                            source_js_file=js_url,
                            confidence_score=confidence,
                            discovered_by=[JavaScriptTool.JSPARSER]
                        )
                        endpoints.append(endpoint)
                        
            except Exception as e:
                logger.error(f"Error with regex pattern {pattern}: {e}")
                continue
                
        return endpoints

    async def extract_keywords(self, js_content: str, js_url: str) -> List[KeywordInfo]:
        """Extract sensitive keywords from JS content"""
        keywords = []
        
        # Sensitive keyword patterns
        patterns = {
            'api_key': [r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', r'apikey["\']?\s*[:=]\s*["\']([^"\']+)["\']'],
            'token': [r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']', r'auth[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']'],
            'secret': [r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']', r'client[_-]?secret["\']?\s*[:=]\s*["\']([^"\']+)["\']'],
            'password': [r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']', r'passwd["\']?\s*[:=]\s*["\']([^"\']+)["\']'],
            'config': [r'config["\']?\s*[:=]\s*\{([^}]+)\}', r'settings["\']?\s*[:=]\s*\{([^}]+)\}'],
            'database': [r'db[_-]?(?:host|user|pass|name)["\']?\s*[:=]\s*["\']([^"\']+)["\']'],
            'aws': [r'aws[_-]?(?:access|secret)[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']'],
        }
        
        for keyword_type, regex_patterns in patterns.items():
            for pattern in regex_patterns:
                try:
                    matches = re.finditer(pattern, js_content, re.IGNORECASE)
                    for match in matches:
                        keyword_value = match.group(1) if match.groups() else match.group(0)
                        
                        # Get context around the match
                        start = max(0, match.start() - 50)
                        end = min(len(js_content), match.end() + 50)
                        context = js_content[start:end].replace('\n', ' ').strip()
                        
                        # Filter out obvious false positives
                        if len(keyword_value) > 3 and not any(exclude in keyword_value.lower() 
                                                             for exclude in ['example', 'placeholder', 'test', 'demo']):
                            
                            confidence = 0.6
                            if keyword_type in ['api_key', 'token', 'secret'] and len(keyword_value) > 10:
                                confidence = 0.9
                            elif keyword_type == 'password' and len(keyword_value) > 6:
                                confidence = 0.8
                            
                            keyword_info = KeywordInfo(
                                keyword=keyword_value,
                                context=context,
                                keyword_type=keyword_type,
                                source_js_file=js_url,
                                confidence_score=confidence,
                                discovered_by=[JavaScriptTool.GETJSWORDS]
                            )
                            keywords.append(keyword_info)
                            
                except Exception as e:
                    logger.error(f"Error extracting keywords with pattern {pattern}: {e}")
                    continue
                    
        return keywords

    async def analyze_javascript_files(
        self, 
        hosts: List[str], 
        target_id: str, 
        domain: str,
        tools: List[JavaScriptTool] = None,
        include_external_js: bool = False,
        deep_analysis: bool = True,
        keyword_extraction: bool = True
    ) -> JavaScriptDiscoveryJob:
        """Main function to discover and analyze JavaScript files"""
        if tools is None:
            tools = list(JavaScriptTool)
        
        # Create JavaScript discovery job
        job = JavaScriptDiscoveryJob(
            target_id=target_id,
            domain=domain,
            subdomains=hosts,
            status=JavaScriptDiscoveryStatus.RUNNING,
            started_at=datetime.utcnow(),
            total_hosts=len(hosts)
        )
        
        # Store job in database
        db = get_database()
        await db.javascript_jobs.insert_one(job.dict())
        
        all_results = {}  # host -> JavaScriptDiscoveryResult
        tool_results = []
        
        try:
            # Step 1: Extract JS URLs using subjs
            if JavaScriptTool.SUBJS in tools:
                logger.info(f"Running subjs to find JS files for {len(hosts)} hosts")
                js_results, result = await self.run_subjs(hosts)
                tool_results.append(result)
                
                # Initialize results for each host
                for host in hosts:
                    all_results[host] = JavaScriptDiscoveryResult(
                        subdomain=host,
                        js_files=js_results.get(host, []),
                        checked_by=[JavaScriptTool.SUBJS]
                    )
            
            # Step 2: Analyze JS files for endpoints and keywords
            all_js_urls = []
            for host_results in all_results.values():
                all_js_urls.extend([js.url for js in host_results.js_files])
            
            if deep_analysis and all_js_urls:
                logger.info(f"Performing deep analysis on {len(all_js_urls)} JS files")
                
                # Download and analyze each JS file
                async with aiohttp.ClientSession() as session:
                    for js_url in all_js_urls[:20]:  # Limit to prevent timeout
                        try:
                            async with session.get(js_url, timeout=30) as response:
                                if response.status == 200:
                                    js_content = await response.text()
                                    
                                    # Beautify if needed
                                    if JavaScriptTool.JSBEAUTIFIER in tools:
                                        js_content, was_minified = await self.run_jsbeautifier(js_content)
                                        # Update JS file info
                                        for host_result in all_results.values():
                                            for js_file in host_result.js_files:
                                                if js_file.url == js_url:
                                                    js_file.is_minified = was_minified
                                                    js_file.size = len(js_content)
                                    
                                    # Extract endpoints
                                    endpoints = await self.extract_endpoints_with_regex(js_content, js_url)
                                    
                                    # Extract keywords if enabled
                                    keywords = []
                                    if keyword_extraction:
                                        keywords = await self.extract_keywords(js_content, js_url)
                                    
                                    # Add results to appropriate host
                                    for host, host_result in all_results.items():
                                        if any(js.url == js_url for js in host_result.js_files):
                                            host_result.endpoints.extend(endpoints)
                                            host_result.keywords.extend(keywords)
                                            break
                                            
                        except Exception as e:
                            logger.error(f"Error analyzing JS file {js_url}: {e}")
                            continue
            
            # Update job statistics
            total_js_files = sum(len(result.js_files) for result in all_results.values())
            total_endpoints = sum(len(result.endpoints) for result in all_results.values())
            total_keywords = sum(len(result.keywords) for result in all_results.values())
            
            # Update each result's totals
            for result in all_results.values():
                result.total_js_files = len(result.js_files)
                result.total_endpoints = len(result.endpoints)
                result.total_keywords = len(result.keywords)
            
            # Update job status
            job.status = JavaScriptDiscoveryStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.total_js_files = total_js_files
            job.total_endpoints = total_endpoints
            job.total_keywords = total_keywords
            job.tools_executed = tool_results
            job.results = list(all_results.values())
            
            # Check if any tools failed
            failed_tools = [r for r in tool_results if r.status in ["failed", "timeout"]]
            if failed_tools and len(failed_tools) < len(tools):
                job.status = JavaScriptDiscoveryStatus.PARTIAL
            elif len(failed_tools) == len(tools):
                job.status = JavaScriptDiscoveryStatus.FAILED
            
        except Exception as e:
            logger.error(f"Error in JavaScript discovery: {e}")
            job.status = JavaScriptDiscoveryStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.notes = f"JavaScript discovery failed: {str(e)}"
        
        # Update job in database
        await db.javascript_jobs.update_one(
            {"id": job.id},
            {"$set": job.dict()}
        )
        
        return job

# Global service instance
javascript_service = JavaScriptDiscoveryService()