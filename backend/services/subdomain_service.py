import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple
import aiohttp
import re

from ..models.subdomain_models import (
    SubdomainTool, EnumerationStatus, SubdomainResult, 
    ToolResult, EnumerationJob
)
from .database import get_database

logger = logging.getLogger(__name__)

class SubdomainEnumerationService:
    def __init__(self):
        self.tools_installed = {}
        self.tool_paths = {}
        
    async def check_tool_installation(self, tool: SubdomainTool) -> bool:
        """Check if a tool is installed and accessible"""
        try:
            if tool == SubdomainTool.SUBFINDER:
                result = await self._run_command(["subfinder", "-version"], timeout=10)
                return result.returncode == 0
            elif tool == SubdomainTool.AMASS:
                result = await self._run_command(["amass", "-version"], timeout=10)
                return result.returncode == 0
            elif tool == SubdomainTool.PUREDNS:
                result = await self._run_command(["puredns", "--help"], timeout=10)
                return result.returncode == 0
            elif tool == SubdomainTool.DNSX:
                result = await self._run_command(["dnsx", "-version"], timeout=10)
                return result.returncode == 0
            elif tool == SubdomainTool.GOTATOR:
                result = await self._run_command(["gotator", "--help"], timeout=10)
                return result.returncode == 0
            elif tool == SubdomainTool.GITHUB_SUBDOMAINS:
                result = await self._run_command(["github-subdomains", "--help"], timeout=10)
                return result.returncode == 0
            elif tool == SubdomainTool.MAPCIDR:
                result = await self._run_command(["mapcidr", "--help"], timeout=10)
                return result.returncode == 0
            elif tool == SubdomainTool.DNSGEN:
                result = await self._run_command(["dnsgen", "--help"], timeout=10)
                return result.returncode == 0
            else:
                # For tools we implement ourselves (crtsh, asnlookup)
                return True
        except Exception as e:
            logger.error(f"Error checking {tool} installation: {e}")
            return False

    async def install_tool(self, tool: SubdomainTool) -> bool:
        """Install a specific tool"""
        try:
            logger.info(f"Installing tool: {tool}")
            
            if tool == SubdomainTool.SUBFINDER:
                result = await self._run_command([
                    "go", "install", "-v", "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == SubdomainTool.AMASS:
                # Install amass via apt for easier installation
                result = await self._run_command([
                    "apt", "update"
                ], timeout=60)
                if result.returncode == 0:
                    result = await self._run_command([
                        "apt", "install", "-y", "amass"
                    ], timeout=300)
                return result.returncode == 0
                
            elif tool == SubdomainTool.PUREDNS:
                result = await self._run_command([
                    "go", "install", "github.com/d3mondev/puredns/v2@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == SubdomainTool.DNSX:
                result = await self._run_command([
                    "go", "install", "-v", "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == SubdomainTool.GOTATOR:
                result = await self._run_command([
                    "go", "install", "github.com/Josue87/gotator@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == SubdomainTool.GITHUB_SUBDOMAINS:
                result = await self._run_command([
                    "go", "install", "github.com/gwen001/github-subdomains@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == SubdomainTool.MAPCIDR:
                result = await self._run_command([
                    "go", "install", "-v", "github.com/projectdiscovery/mapcidr/cmd/mapcidr@latest"
                ], timeout=300)
                return result.returncode == 0
                
            elif tool == SubdomainTool.DNSGEN:
                result = await self._run_command([
                    "pip", "install", "dnsgen"
                ], timeout=180)
                return result.returncode == 0
                
            return True
                
        except Exception as e:
            logger.error(f"Error installing {tool}: {e}")
            return False

    async def install_all_tools(self) -> Dict[SubdomainTool, bool]:
        """Install all subdomain enumeration tools"""
        results = {}
        
        for tool in SubdomainTool:
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

    async def run_subfinder(self, domain: str) -> Tuple[Set[str], ToolResult]:
        """Run subfinder tool"""
        start_time = time.time()
        subdomains = set()
        
        try:
            result = await self._run_command([
                "subfinder", "-d", domain, "-silent", "-o", "/dev/stdout"
            ], timeout=120)
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and '.' in line:
                        subdomains.add(line.lower())
                        
                return subdomains, ToolResult(
                    tool=SubdomainTool.SUBFINDER,
                    status="success",
                    execution_time=execution_time,
                    subdomains_found=len(subdomains)
                )
            else:
                return subdomains, ToolResult(
                    tool=SubdomainTool.SUBFINDER,
                    status="failed",
                    execution_time=execution_time,
                    subdomains_found=0,
                    error_message=result.stderr
                )
                
        except Exception as e:
            return subdomains, ToolResult(
                tool=SubdomainTool.SUBFINDER,
                status="failed",
                execution_time=time.time() - start_time,
                subdomains_found=0,
                error_message=str(e)
            )

    async def run_amass(self, domain: str) -> Tuple[Set[str], ToolResult]:
        """Run amass tool"""
        start_time = time.time()
        subdomains = set()
        
        try:
            result = await self._run_command([
                "amass", "enum", "-passive", "-d", domain, "-o", "/dev/stdout"
            ], timeout=300)
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and '.' in line:
                        subdomains.add(line.lower())
                        
                return subdomains, ToolResult(
                    tool=SubdomainTool.AMASS,
                    status="success",
                    execution_time=execution_time,
                    subdomains_found=len(subdomains)
                )
            else:
                return subdomains, ToolResult(
                    tool=SubdomainTool.AMASS,
                    status="failed",
                    execution_time=execution_time,
                    subdomains_found=0,
                    error_message=result.stderr
                )
                
        except Exception as e:
            return subdomains, ToolResult(
                tool=SubdomainTool.AMASS,
                status="failed",
                execution_time=time.time() - start_time,
                subdomains_found=0,
                error_message=str(e)
            )

    async def run_crtsh(self, domain: str) -> Tuple[Set[str], ToolResult]:
        """Run crt.sh certificate transparency search"""
        start_time = time.time()
        subdomains = set()
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://crt.sh/?q=%.{domain}&output=json"
                async with session.get(url, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        for cert in data:
                            if 'name_value' in cert:
                                # Parse certificate names
                                names = cert['name_value'].split('\n')
                                for name in names:
                                    name = name.strip().lower()
                                    if name.endswith(f'.{domain}') or name == domain:
                                        # Remove wildcards
                                        if name.startswith('*.'):
                                            name = name[2:]
                                        if name and '.' in name:
                                            subdomains.add(name)
                                            
            execution_time = time.time() - start_time
            return subdomains, ToolResult(
                tool=SubdomainTool.CRTSH,
                status="success",
                execution_time=execution_time,
                subdomains_found=len(subdomains)
            )
            
        except Exception as e:
            return subdomains, ToolResult(
                tool=SubdomainTool.CRTSH,
                status="failed",
                execution_time=time.time() - start_time,
                subdomains_found=0,
                error_message=str(e)
            )

    async def run_dnsgen(self, domain: str, known_subdomains: Set[str] = None) -> Tuple[Set[str], ToolResult]:
        """Run dnsgen for subdomain permutation"""
        start_time = time.time()
        subdomains = set()
        
        try:
            # Create input file with known subdomains
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                if known_subdomains:
                    for sub in known_subdomains:
                        f.write(f"{sub}\n")
                else:
                    f.write(f"{domain}\n")
                temp_file = f.name
            
            try:
                result = await self._run_command([
                    "dnsgen", temp_file
                ], timeout=120)
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        line = line.strip().lower()
                        if line and '.' in line and (line.endswith(f'.{domain}') or line == domain):
                            subdomains.add(line)
                            
                    return subdomains, ToolResult(
                        tool=SubdomainTool.DNSGEN,
                        status="success",
                        execution_time=execution_time,
                        subdomains_found=len(subdomains)
                    )
                else:
                    return subdomains, ToolResult(
                        tool=SubdomainTool.DNSGEN,
                        status="failed",
                        execution_time=execution_time,
                        subdomains_found=0,
                        error_message=result.stderr
                    )
                    
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            return subdomains, ToolResult(
                tool=SubdomainTool.DNSGEN,
                status="failed",
                execution_time=time.time() - start_time,
                subdomains_found=0,
                error_message=str(e)
            )

    async def enumerate_subdomains(self, domain: str, target_id: str, tools: List[SubdomainTool] = None) -> EnumerationJob:
        """Main function to enumerate subdomains using all available tools"""
        if tools is None:
            tools = list(SubdomainTool)
        
        # Create enumeration job
        job = EnumerationJob(
            target_id=target_id,
            domain=domain,
            status=EnumerationStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        # Store job in database
        db = get_database()
        await db.enumeration_jobs.insert_one(job.dict())
        
        all_subdomains = {}  # subdomain -> list of tools that found it
        tool_results = []
        
        try:
            # Run each tool
            for tool in tools:
                logger.info(f"Running {tool} for domain: {domain}")
                
                try:
                    if tool == SubdomainTool.SUBFINDER:
                        subs, result = await self.run_subfinder(domain)
                    elif tool == SubdomainTool.AMASS:
                        subs, result = await self.run_amass(domain)
                    elif tool == SubdomainTool.CRTSH:
                        subs, result = await self.run_crtsh(domain)
                    elif tool == SubdomainTool.DNSGEN:
                        known_subs = set(all_subdomains.keys()) if all_subdomains else None
                        subs, result = await self.run_dnsgen(domain, known_subs)
                    else:
                        # For tools not yet implemented, create a placeholder result
                        subs = set()
                        result = ToolResult(
                            tool=tool,
                            status="not_implemented",
                            execution_time=0,
                            subdomains_found=0,
                            error_message="Tool not yet implemented"
                        )
                    
                    tool_results.append(result)
                    
                    # Merge results
                    for subdomain in subs:
                        if subdomain not in all_subdomains:
                            all_subdomains[subdomain] = []
                        all_subdomains[subdomain].append(tool)
                        
                    logger.info(f"{tool} found {len(subs)} subdomains")
                    
                except Exception as e:
                    logger.error(f"Error running {tool}: {e}")
                    tool_results.append(ToolResult(
                        tool=tool,
                        status="failed",
                        execution_time=0,
                        subdomains_found=0,
                        error_message=str(e)
                    ))
            
            # Create subdomain results
            subdomain_results = []
            for subdomain, discovered_by in all_subdomains.items():
                subdomain_results.append(SubdomainResult(
                    subdomain=subdomain,
                    discovered_by=discovered_by
                ))
            
            # Update job status
            job.status = EnumerationStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.total_subdomains = sum(len(subs) for subs, _ in [])  # Total from all tools
            job.unique_subdomains = len(all_subdomains)
            job.tools_executed = tool_results
            job.subdomains = subdomain_results
            
            # Check if any tools failed
            failed_tools = [r for r in tool_results if r.status in ["failed", "timeout"]]
            if failed_tools and len(failed_tools) < len(tools):
                job.status = EnumerationStatus.PARTIAL
            elif len(failed_tools) == len(tools):
                job.status = EnumerationStatus.FAILED
            
        except Exception as e:
            logger.error(f"Error in subdomain enumeration: {e}")
            job.status = EnumerationStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.notes = f"Enumeration failed: {str(e)}"
        
        # Update job in database
        await db.enumeration_jobs.update_one(
            {"id": job.id},
            {"$set": job.dict()}
        )
        
        # Update target with subdomain count
        await db.targets.update_one(
            {"id": target_id},
            {"$set": {
                "subdomains": job.unique_subdomains,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return job

# Global service instance
subdomain_service = SubdomainEnumerationService()