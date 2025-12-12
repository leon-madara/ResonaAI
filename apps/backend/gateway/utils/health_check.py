"""
Health check utilities for API Gateway
"""

import httpx
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class HealthChecker:
    """Health checker for microservices"""
    
    def __init__(self, service_urls: Dict[str, str], timeout: int = 5):
        self.service_urls = service_urls
        self.timeout = timeout
        self.http_client = httpx.AsyncClient(timeout=timeout)
    
    async def check_service(self, service_name: str, service_url: str) -> Dict[str, Any]:
        """Check health of a single service"""
        try:
            response = await self.http_client.get(f"{service_url}/health")
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "details": response.json()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response.elapsed.total_seconds()
                }
                
        except httpx.TimeoutException:
            return {
                "status": "unhealthy",
                "error": "timeout",
                "response_time": self.timeout
            }
        except httpx.ConnectError:
            return {
                "status": "unhealthy",
                "error": "connection_failed",
                "response_time": 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": 0
            }
    
    async def check_all_services(self) -> Dict[str, Any]:
        """Check health of all services"""
        tasks = []
        for service_name, service_url in self.service_urls.items():
            task = self.check_service(service_name, service_url)
            tasks.append((service_name, task))
        
        results = {}
        for service_name, task in tasks:
            try:
                result = await task
                results[service_name] = result
            except Exception as e:
                results[service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "response_time": 0
                }
        
        return results
    
    async def check_service_health(self, service_name: str) -> bool:
        """Check if a specific service is healthy"""
        if service_name not in self.service_urls:
            return False
        
        service_url = self.service_urls[service_name]
        result = await self.check_service(service_name, service_url)
        return result["status"] == "healthy"
    
    async def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status of a specific service"""
        if service_name not in self.service_urls:
            return {
                "status": "unknown",
                "error": "Service not found"
            }
        
        service_url = self.service_urls[service_name]
        return await self.check_service(service_name, service_url)
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
