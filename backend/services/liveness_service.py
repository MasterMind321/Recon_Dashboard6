import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
import base64
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple
import aiohttp
import re
from pathlib import Path

from ..models.liveness_models import (
    LivenessTool, LivenessStatus, LivenessResult, 
    LivenessToolResult, LivenessJob, TLSInfo, TechStackInfo, CDNWAFInfo
)
from .database import get_database

logger = logging.getLogger(__name__)

class LivenessService:
    def __init__(self):
        self.tools_installed = {}
        self.tool_paths = {}
        self.screenshots_dir = "/app/backend/data/screenshots"
        # Ensure screenshots directory exists
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    async def check_tool_installation(self, tool: LivenessTool) -> bool:
        """Check if a tool is installed and accessible"""
        try:
            if tool == LivenessTool.HTTPX:
                result = await self._run_command(["httpx", "-version"], timeout=10)
                return result.returncode == 0
            elif tool == LivenessTool.TLSX:
                result = await self._run_command(["tlsx", "-version"], timeout=10)
                return result.returncode == 0
            elif tool == LivenessTool.GOWITNESS:
                result = await self._run_command(["gowitness", "version"], timeout=10)
                return result.returncode == 0
            elif tool == LivenessTool.WAFW00F:
                result = await self._run_command(["wafw00f", "--help"], timeout=10)
                return result.returncode == 0
            elif tool == LivenessTool.WHATWEB:
                result = await self._run_command(["whatweb", "--version"], timeout=10)
                return result.returncode == 0
            elif tool == LivenessTool.WAPPALYZER:
                # Check if Node.js and wappalyzer-cli are installed
                result = await self._run_command(["node", "--version"], timeout=10)
                if result.returncode != 0:
                    return False
                result = await self._run_command(["npx", "wappalyzer", "--help"], timeout=10)
                return result.returncode == 0
            elif tool == LivenessTool.CMSEEK:
                # Check if CMSeeK exists in expected location
                cmseek_path = "/opt/CMSeeK/cmseek.py"
                return os.path.exists(cmseek_path)
            else:
                # For tools we implement ourselves (like cdncheck which is built into httpx)
                return True
        except Exception as e:
            logger.error(f"Error checking {tool} installation: {e}")
            return False

    async def install_tool(self, tool: LivenessTool) -> bool:
        """Install a specific tool"""
        try:
            logger.info(f"Installing tool: {tool}")
            
            if tool == LivenessTool.HTTPX:
                result = await self._run_command([
                    "go", "install", "-v", "github.com/projectdiscovery/httpx/cmd/httpx@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == LivenessTool.TLSX:
                result = await self._run_command([
                    "go", "install", "github.com/projectdiscovery/tlsx/cmd/tlsx@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == LivenessTool.GOWITNESS:
                result = await self._run_command([
                    "go", "install", "github.com/sensepost/gowitness@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == LivenessTool.WAFW00F:
                result = await self._run_command([
                    "pip", "install", "wafw00f"
                ], timeout=180)
                return result.returncode == 0
                
            elif tool == LivenessTool.WHATWEB:
                result = await self._run_command([
                    "apt", "update"
                ], timeout=60)
                if result.returncode == 0:
                    result = await self._run_command([
                        "apt", "install", "-y", "whatweb"
                    ], timeout=300)
                return result.returncode == 0
                
            elif tool == LivenessTool.WAPPALYZER:
                # Install Node.js if not present
                node_check = await self._run_command(["node", "--version"], timeout=10)
                if node_check.returncode != 0:
                    # Install Node.js
                    result = await self._run_command([
                        "curl", "-fsSL", "https://deb.nodesource.com/setup_18.x", "|", "bash", "-"
                    ], timeout=120)
                    if result.returncode == 0:
                        result = await self._run_command([
                            "apt", "install", "-y", "nodejs"
                        ], timeout=300)
                        if result.returncode != 0:
                            return False
                
                # Install wappalyzer globally
                result = await self._run_command([
                    "npm", "install", "-g", "wappalyzer"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == LivenessTool.CMSEEK:
                # Clone CMSeeK repository
                result = await self._run_command([
                    "git", "clone", "https://github.com/Tuhinshubhra/CMSeeK.git", "/opt/CMSeeK"
                ], timeout=180)
                if result.returncode == 0:
                    # Install Python dependencies
                    result = await self._run_command([
                        "pip", "install", "-r", "/opt/CMSeeK/requirements.txt"
                    ], timeout=180)
                return result.returncode == 0
                
            return True
                
        except Exception as e:
            logger.error(f"Error installing {tool}: {e}")
            return False

    async def install_all_tools(self) -> Dict[LivenessTool, bool]:
        """Install all liveness/fingerprinting tools"""
        results = {}
        
        for tool in LivenessTool:
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

    async def run_httpx(self, hosts: List[str]) -> Tuple[Dict[str, LivenessResult], LivenessToolResult]:
        """Run httpx tool for liveness check and basic info"""
        start_time = time.time()
        results = {}
        
        try:
            # Create input file with hosts
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                for host in hosts:
                    # Add both http and https variants
                    f.write(f"http://{host}\n")
                    f.write(f"https://{host}\n")
                temp_file = f.name
            
            try:
                # Run httpx with comprehensive options
                result = await self._run_command([
                    "httpx", "-l", temp_file, "-sc", "-cl", "-server", "-title", 
                    "-location", "-ct", "-rt", "-cdn", "-waf", "-json", "-silent"
                ], timeout=300)
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    # Parse JSON output
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            try:
                                data = json.loads(line)
                                host = data.get('host', '').replace('http://', '').replace('https://', '')
                                
                                # Create CDN/WAF info
                                cdn_waf_info = CDNWAFInfo(
                                    cdn_provider=data.get('cdn'),
                                    waf_provider=data.get('waf'),
                                    is_behind_cdn=bool(data.get('cdn')),
                                    is_behind_waf=bool(data.get('waf'))
                                )
                                
                                # Create liveness result
                                results[host] = LivenessResult(
                                    subdomain=host,
                                    is_alive=True,
                                    status_code=data.get('status_code'),
                                    response_time=data.get('response_time', 0) / 1000,  # Convert to seconds
                                    content_length=data.get('content_length'),
                                    title=data.get('title'),
                                    server=data.get('webserver'),
                                    location=data.get('location'),
                                    cdn_waf_info=cdn_waf_info,
                                    checked_by=[LivenessTool.HTTPX],
                                    response_headers={}  # Could be extended to capture headers
                                )
                            except json.JSONDecodeError:
                                continue
                                
                    return results, LivenessToolResult(
                        tool=LivenessTool.HTTPX,
                        status="success",
                        execution_time=execution_time,
                        hosts_checked=len(hosts),
                        alive_hosts=len(results)
                    )
                else:
                    return results, LivenessToolResult(
                        tool=LivenessTool.HTTPX,
                        status="failed",
                        execution_time=execution_time,
                        hosts_checked=len(hosts),
                        alive_hosts=0,
                        error_message=result.stderr
                    )
                    
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            return results, LivenessToolResult(
                tool=LivenessTool.HTTPX,
                status="failed",
                execution_time=time.time() - start_time,
                hosts_checked=len(hosts),
                alive_hosts=0,
                error_message=str(e)
            )

    async def run_tlsx(self, hosts: List[str]) -> Tuple[Dict[str, TLSInfo], LivenessToolResult]:
        """Run tlsx tool for TLS certificate information"""
        start_time = time.time()
        results = {}
        
        try:
            # Create input file with hosts
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                for host in hosts:
                    f.write(f"{host}\n")
                temp_file = f.name
            
            try:
                result = await self._run_command([
                    "tlsx", "-l", temp_file, "-json", "-silent"
                ], timeout=300)
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    # Parse JSON output
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            try:
                                data = json.loads(line)
                                host = data.get('host', '')
                                
                                # Parse certificate info
                                cert_info = data.get('certificate', {})
                                results[host] = TLSInfo(
                                    issuer=cert_info.get('issuer'),
                                    subject=cert_info.get('subject'),
                                    san=cert_info.get('san', []),
                                    signature_algorithm=cert_info.get('signature_algorithm'),
                                    version=data.get('version')
                                )
                            except json.JSONDecodeError:
                                continue
                                
                    return results, LivenessToolResult(
                        tool=LivenessTool.TLSX,
                        status="success",
                        execution_time=execution_time,
                        hosts_checked=len(hosts),
                        alive_hosts=len(results)
                    )
                else:
                    return results, LivenessToolResult(
                        tool=LivenessTool.TLSX,
                        status="failed",
                        execution_time=execution_time,
                        hosts_checked=len(hosts),
                        alive_hosts=0,
                        error_message=result.stderr
                    )
                    
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            return results, LivenessToolResult(
                tool=LivenessTool.TLSX,
                status="failed",
                execution_time=time.time() - start_time,
                hosts_checked=len(hosts),
                alive_hosts=0,
                error_message=str(e)
            )

    async def run_gowitness(self, hosts: List[str]) -> Tuple[Dict[str, str], LivenessToolResult]:
        """Run gowitness for web screenshots"""
        start_time = time.time()
        results = {}
        
        try:
            # Create input file with hosts
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                for host in hosts:
                    f.write(f"https://{host}\n")
                    f.write(f"http://{host}\n")
                temp_file = f.name
            
            # Create temporary output directory
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    result = await self._run_command([
                        "gowitness", "file", "-f", temp_file, "-P", temp_dir, "--disable-logging"
                    ], timeout=600)  # Longer timeout for screenshots
                    
                    execution_time = time.time() - start_time
                    
                    if result.returncode == 0:
                        # Process screenshot files
                        for screenshot_file in Path(temp_dir).glob("*.png"):
                            try:
                                # Read screenshot and convert to base64
                                with open(screenshot_file, "rb") as img_file:
                                    img_data = img_file.read()
                                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                                    
                                # Extract host from filename
                                filename = screenshot_file.stem
                                # gowitness typically creates files like https-example.com.png
                                host = filename.replace('https-', '').replace('http-', '').replace('-', '.')
                                results[host] = img_base64
                            except Exception as e:
                                logger.error(f"Error processing screenshot {screenshot_file}: {e}")
                                
                        return results, LivenessToolResult(
                            tool=LivenessTool.GOWITNESS,
                            status="success",
                            execution_time=execution_time,
                            hosts_checked=len(hosts),
                            alive_hosts=len(results)
                        )
                    else:
                        return results, LivenessToolResult(
                            tool=LivenessTool.GOWITNESS,
                            status="failed",
                            execution_time=execution_time,
                            hosts_checked=len(hosts),
                            alive_hosts=0,
                            error_message=result.stderr
                        )
                        
                finally:
                    os.unlink(temp_file)
                    
        except Exception as e:
            return results, LivenessToolResult(
                tool=LivenessTool.GOWITNESS,
                status="failed",
                execution_time=time.time() - start_time,
                hosts_checked=len(hosts),
                alive_hosts=0,
                error_message=str(e)
            )

    async def run_wafw00f(self, hosts: List[str]) -> Tuple[Dict[str, CDNWAFInfo], LivenessToolResult]:
        """Run wafw00f for WAF detection"""
        start_time = time.time()
        results = {}
        
        try:
            for host in hosts:
                try:
                    result = await self._run_command([
                        "wafw00f", f"https://{host}", "-o", "/dev/stdout", "-f", "json"
                    ], timeout=60)
                    
                    if result.returncode == 0 and result.stdout:
                        try:
                            data = json.loads(result.stdout)
                            waf_info = CDNWAFInfo(
                                waf_provider=data.get('firewall'),
                                is_behind_waf=bool(data.get('detected')),
                                waf_type=data.get('firewall')
                            )
                            results[host] = waf_info
                        except json.JSONDecodeError:
                            # Try to parse text output
                            if "is behind" in result.stdout:
                                waf_match = re.search(r'is behind (.+?) \(', result.stdout)
                                if waf_match:
                                    results[host] = CDNWAFInfo(
                                        waf_provider=waf_match.group(1),
                                        is_behind_waf=True,
                                        waf_type=waf_match.group(1)
                                    )
                except Exception as e:
                    logger.error(f"Error checking WAF for {host}: {e}")
                    continue
                    
            execution_time = time.time() - start_time
            
            return results, LivenessToolResult(
                tool=LivenessTool.WAFW00F,
                status="success",
                execution_time=execution_time,
                hosts_checked=len(hosts),
                alive_hosts=len(results)
            )
                
        except Exception as e:
            return results, LivenessToolResult(
                tool=LivenessTool.WAFW00F,
                status="failed",
                execution_time=time.time() - start_time,
                hosts_checked=len(hosts),
                alive_hosts=0,
                error_message=str(e)
            )

    async def run_whatweb(self, hosts: List[str]) -> Tuple[Dict[str, TechStackInfo], LivenessToolResult]:
        """Run whatweb for technology stack detection"""
        start_time = time.time()
        results = {}
        
        try:
            for host in hosts:
                try:
                    result = await self._run_command([
                        "whatweb", f"https://{host}", "--log-json=/dev/stdout"
                    ], timeout=60)
                    
                    if result.returncode == 0 and result.stdout:
                        try:
                            data = json.loads(result.stdout)
                            plugins = data.get('plugins', {})
                            
                            tech_info = TechStackInfo()
                            
                            # Extract technology information
                            for plugin_name, plugin_data in plugins.items():
                                plugin_name_lower = plugin_name.lower()
                                
                                if 'server' in plugin_name_lower or plugin_name in ['Apache', 'Nginx', 'IIS']:
                                    tech_info.server = plugin_name
                                elif any(cms in plugin_name_lower for cms in ['wordpress', 'drupal', 'joomla']):
                                    tech_info.cms = plugin_name
                                elif any(js in plugin_name_lower for js in ['jquery', 'angular', 'react', 'vue']):
                                    tech_info.javascript_libraries.append(plugin_name)
                                elif any(fw in plugin_name_lower for fw in ['bootstrap', 'foundation']):
                                    tech_info.frameworks.append(plugin_name)
                                else:
                                    tech_info.technologies.append(plugin_name)
                            
                            results[host] = tech_info
                            
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse whatweb JSON output for {host}")
                except Exception as e:
                    logger.error(f"Error running whatweb for {host}: {e}")
                    continue
                    
            execution_time = time.time() - start_time
            
            return results, LivenessToolResult(
                tool=LivenessTool.WHATWEB,
                status="success",
                execution_time=execution_time,
                hosts_checked=len(hosts),
                alive_hosts=len(results)
            )
                
        except Exception as e:
            return results, LivenessToolResult(
                tool=LivenessTool.WHATWEB,
                status="failed",
                execution_time=time.time() - start_time,
                hosts_checked=len(hosts),
                alive_hosts=0,
                error_message=str(e)
            )

    async def check_liveness_and_fingerprint(
        self, 
        hosts: List[str], 
        target_id: str, 
        domain: str,
        tools: List[LivenessTool] = None,
        include_screenshots: bool = True,
        include_tech_stack: bool = True,
        include_tls_info: bool = True
    ) -> LivenessJob:
        """Main function to check liveness and fingerprint hosts"""
        if tools is None:
            tools = list(LivenessTool)
        
        # Create liveness job
        job = LivenessJob(
            target_id=target_id,
            domain=domain,
            subdomains=hosts,
            status=LivenessStatus.RUNNING,
            started_at=datetime.utcnow(),
            total_hosts=len(hosts)
        )
        
        # Store job in database
        db = get_database()
        await db.liveness_jobs.insert_one(job.dict())
        
        all_results = {}  # host -> LivenessResult
        tool_results = []
        
        try:
            # Run each tool
            for tool in tools:
                logger.info(f"Running {tool} for {len(hosts)} hosts")
                
                try:
                    if tool == LivenessTool.HTTPX:
                        host_results, result = await self.run_httpx(hosts)
                        # Merge results
                        for host, liveness_result in host_results.items():
                            if host not in all_results:
                                all_results[host] = liveness_result
                            else:
                                # Update existing result
                                all_results[host].checked_by.append(LivenessTool.HTTPX)
                                if liveness_result.is_alive:
                                    all_results[host].is_alive = True
                                if liveness_result.status_code:
                                    all_results[host].status_code = liveness_result.status_code
                                if liveness_result.response_time:
                                    all_results[host].response_time = liveness_result.response_time
                                if liveness_result.cdn_waf_info:
                                    all_results[host].cdn_waf_info = liveness_result.cdn_waf_info
                                    
                    elif tool == LivenessTool.TLSX and include_tls_info:
                        tls_results, result = await self.run_tlsx(hosts)
                        # Merge TLS info into existing results
                        for host, tls_info in tls_results.items():
                            if host not in all_results:
                                all_results[host] = LivenessResult(
                                    subdomain=host,
                                    is_alive=True,
                                    tls_info=tls_info,
                                    checked_by=[LivenessTool.TLSX]
                                )
                            else:
                                all_results[host].tls_info = tls_info
                                all_results[host].checked_by.append(LivenessTool.TLSX)
                                
                    elif tool == LivenessTool.GOWITNESS and include_screenshots:
                        screenshot_results, result = await self.run_gowitness(hosts)
                        # Merge screenshots into existing results
                        for host, screenshot_b64 in screenshot_results.items():
                            if host not in all_results:
                                all_results[host] = LivenessResult(
                                    subdomain=host,
                                    is_alive=True,
                                    screenshot_base64=screenshot_b64,
                                    checked_by=[LivenessTool.GOWITNESS]
                                )
                            else:
                                all_results[host].screenshot_base64 = screenshot_b64
                                all_results[host].checked_by.append(LivenessTool.GOWITNESS)
                                
                    elif tool == LivenessTool.WAFW00F:
                        waf_results, result = await self.run_wafw00f(hosts)
                        # Merge WAF info
                        for host, waf_info in waf_results.items():
                            if host not in all_results:
                                all_results[host] = LivenessResult(
                                    subdomain=host,
                                    is_alive=True,
                                    cdn_waf_info=waf_info,
                                    checked_by=[LivenessTool.WAFW00F]
                                )
                            else:
                                if all_results[host].cdn_waf_info:
                                    # Merge WAF info with existing CDN info
                                    existing = all_results[host].cdn_waf_info
                                    existing.waf_provider = waf_info.waf_provider or existing.waf_provider
                                    existing.is_behind_waf = waf_info.is_behind_waf or existing.is_behind_waf
                                    existing.waf_type = waf_info.waf_type or existing.waf_type
                                else:
                                    all_results[host].cdn_waf_info = waf_info
                                all_results[host].checked_by.append(LivenessTool.WAFW00F)
                                
                    elif tool == LivenessTool.WHATWEB and include_tech_stack:
                        tech_results, result = await self.run_whatweb(hosts)
                        # Merge tech stack info
                        for host, tech_info in tech_results.items():
                            if host not in all_results:
                                all_results[host] = LivenessResult(
                                    subdomain=host,
                                    is_alive=True,
                                    tech_stack=tech_info,
                                    checked_by=[LivenessTool.WHATWEB]
                                )
                            else:
                                all_results[host].tech_stack = tech_info
                                all_results[host].checked_by.append(LivenessTool.WHATWEB)
                                
                    else:
                        # For tools not yet implemented, create a placeholder result
                        result = LivenessToolResult(
                            tool=tool,
                            status="not_implemented",
                            execution_time=0,
                            hosts_checked=len(hosts),
                            alive_hosts=0,
                            error_message="Tool not yet implemented"
                        )
                    
                    tool_results.append(result)
                    logger.info(f"{tool} completed - found {result.alive_hosts} alive hosts")
                    
                except Exception as e:
                    logger.error(f"Error running {tool}: {e}")
                    tool_results.append(LivenessToolResult(
                        tool=tool,
                        status="failed",
                        execution_time=0,
                        hosts_checked=len(hosts),
                        alive_hosts=0,
                        error_message=str(e)
                    ))
            
            # Convert results to list
            liveness_results = list(all_results.values())
            
            # Update job status
            job.status = LivenessStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.alive_hosts = len([r for r in liveness_results if r.is_alive])
            job.tools_executed = tool_results
            job.results = liveness_results
            
            # Check if any tools failed
            failed_tools = [r for r in tool_results if r.status in ["failed", "timeout"]]
            if failed_tools and len(failed_tools) < len(tools):
                job.status = LivenessStatus.PARTIAL
            elif len(failed_tools) == len(tools):
                job.status = LivenessStatus.FAILED
            
        except Exception as e:
            logger.error(f"Error in liveness checking: {e}")
            job.status = LivenessStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.notes = f"Liveness check failed: {str(e)}"
        
        # Update job in database
        await db.liveness_jobs.update_one(
            {"id": job.id},
            {"$set": job.dict()}
        )
        
        return job

# Global service instance
liveness_service = LivenessService()