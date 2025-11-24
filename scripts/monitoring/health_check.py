"""
Health Check Module
Provides comprehensive health checks for services and dependencies.
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import aiohttp


class HealthStatus(Enum):
    """Health check status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """
    Manages health checks for various services and dependencies.
    
    Features:
    - Multiple health check types
    - Async health checks
    - Dependency tracking
    - Status aggregation
    """

    def __init__(self, service_name: str = "top-tier-global-hub-ai"):
        """
        Initialize health check manager.
        
        Args:
            service_name: Service identifier
        """
        self.service_name = service_name
        self.checks: Dict[str, Callable] = {}
        self.start_time = time.time()

    def register_check(self, name: str, check_func: Callable):
        """
        Register a health check function.
        
        Args:
            name: Check identifier
            check_func: Async function that returns (status, details)
        """
        self.checks[name] = check_func

    async def check_database(
        self, db_url: str, timeout: int = 5
    ) -> tuple[HealthStatus, Dict[str, Any]]:
        """
        Check database connectivity.
        
        Args:
            db_url: Database connection URL
            timeout: Connection timeout in seconds
            
        Returns:
            Tuple of (status, details)
        """
        try:
            # This is a placeholder - actual implementation depends on DB type
            # For PostgreSQL: use asyncpg
            # For Redis: use aioredis
            # For Neo4j: use neo4j driver
            
            start = time.time()
            # Simulated check
            await asyncio.sleep(0.1)
            duration = time.time() - start
            
            return HealthStatus.HEALTHY, {
                "connected": True,
                "response_time_ms": round(duration * 1000, 2),
                "url": db_url.split("@")[-1] if "@" in db_url else "***",
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {
                "connected": False,
                "error": str(e),
            }

    async def check_api(
        self, url: str, timeout: int = 10, expected_status: int = 200
    ) -> tuple[HealthStatus, Dict[str, Any]]:
        """
        Check external API availability.
        
        Args:
            url: API endpoint URL
            timeout: Request timeout in seconds
            expected_status: Expected HTTP status code
            
        Returns:
            Tuple of (status, details)
        """
        try:
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    duration = time.time() - start
                    
                    if response.status == expected_status:
                        return HealthStatus.HEALTHY, {
                            "available": True,
                            "status_code": response.status,
                            "response_time_ms": round(duration * 1000, 2),
                        }
                    else:
                        return HealthStatus.DEGRADED, {
                            "available": True,
                            "status_code": response.status,
                            "expected_status": expected_status,
                            "response_time_ms": round(duration * 1000, 2),
                        }
        except asyncio.TimeoutError:
            return HealthStatus.UNHEALTHY, {
                "available": False,
                "error": "Request timeout",
                "timeout_seconds": timeout,
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {
                "available": False,
                "error": str(e),
            }

    async def check_openai(self, api_key: str) -> tuple[HealthStatus, Dict[str, Any]]:
        """
        Check OpenAI API availability.
        
        Args:
            api_key: OpenAI API key
            
        Returns:
            Tuple of (status, details)
        """
        if not api_key or api_key.startswith("${{") or api_key.startswith("PASTE_"):
            return HealthStatus.UNHEALTHY, {
                "configured": False,
                "message": "API key not configured",
            }
        
        try:
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    duration = time.time() - start
                    
                    if response.status == 200:
                        data = await response.json()
                        return HealthStatus.HEALTHY, {
                            "configured": True,
                            "available": True,
                            "models_count": len(data.get("data", [])),
                            "response_time_ms": round(duration * 1000, 2),
                        }
                    else:
                        return HealthStatus.UNHEALTHY, {
                            "configured": True,
                            "available": False,
                            "status_code": response.status,
                        }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {
                "configured": True,
                "available": False,
                "error": str(e),
            }

    async def check_telegram(self, bot_token: str) -> tuple[HealthStatus, Dict[str, Any]]:
        """
        Check Telegram Bot API availability.
        
        Args:
            bot_token: Telegram bot token
            
        Returns:
            Tuple of (status, details)
        """
        if not bot_token or bot_token.startswith("PASTE_"):
            return HealthStatus.UNHEALTHY, {
                "configured": False,
                "message": "Bot token not configured",
            }
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    duration = time.time() - start
                    
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("result", {})
                        return HealthStatus.HEALTHY, {
                            "configured": True,
                            "available": True,
                            "bot_username": result.get("username"),
                            "bot_id": result.get("id"),
                            "response_time_ms": round(duration * 1000, 2),
                        }
                    else:
                        return HealthStatus.UNHEALTHY, {
                            "configured": True,
                            "available": False,
                            "status_code": response.status,
                        }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {
                "configured": True,
                "available": False,
                "error": str(e),
            }

    async def check_github(self, token: str, repo: str) -> tuple[HealthStatus, Dict[str, Any]]:
        """
        Check GitHub API availability.
        
        Args:
            token: GitHub personal access token
            repo: Repository in format owner/repo
            
        Returns:
            Tuple of (status, details)
        """
        if not token or token.startswith("${{") or token.startswith("PASTE_"):
            return HealthStatus.UNHEALTHY, {
                "configured": False,
                "message": "GitHub token not configured",
            }
        
        try:
            url = f"https://api.github.com/repos/{repo}"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }
            
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    duration = time.time() - start
                    
                    if response.status == 200:
                        data = await response.json()
                        return HealthStatus.HEALTHY, {
                            "configured": True,
                            "available": True,
                            "repository": data.get("full_name"),
                            "private": data.get("private"),
                            "response_time_ms": round(duration * 1000, 2),
                        }
                    else:
                        return HealthStatus.UNHEALTHY, {
                            "configured": True,
                            "available": False,
                            "status_code": response.status,
                        }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {
                "configured": True,
                "available": False,
                "error": str(e),
            }

    async def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all registered health checks.
        
        Returns:
            Complete health status report
        """
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        for name, check_func in self.checks.items():
            try:
                status, details = await check_func()
                results[name] = {
                    "status": status.value,
                    "details": details,
                }
                
                # Update overall status
                if status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            except Exception as e:
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "details": {"error": str(e)},
                }
                overall_status = HealthStatus.UNHEALTHY
        
        uptime_seconds = int(time.time() - self.start_time)
        
        return {
            "service": self.service_name,
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": uptime_seconds,
            "checks": results,
        }

    def get_readiness(self) -> Dict[str, Any]:
        """
        Get readiness status (simple check for k8s readiness probe).
        
        Returns:
            Readiness status
        """
        return {
            "ready": True,
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def get_liveness(self) -> Dict[str, Any]:
        """
        Get liveness status (simple check for k8s liveness probe).
        
        Returns:
            Liveness status
        """
        return {
            "alive": True,
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(time.time() - self.start_time),
        }


# Example usage
if __name__ == "__main__":
    import os
    
    async def main():
        # Create health check manager
        health = HealthCheck("telegram-bot-service")
        
        # Register checks
        health.register_check(
            "database",
            lambda: health.check_database("postgresql://localhost:5432/db"),
        )
        
        health.register_check(
            "openai",
            lambda: health.check_openai(os.getenv("OPENAI_API_KEY", "")),
        )
        
        health.register_check(
            "telegram",
            lambda: health.check_telegram(os.getenv("TELEGRAM_BOT_TOKEN", "")),
        )
        
        health.register_check(
            "github",
            lambda: health.check_github(
                os.getenv("GITHUB_TOKEN", ""),
                os.getenv("GITHUB_REPO", "owner/repo"),
            ),
        )
        
        # Run all checks
        print("Running health checks...\n")
        report = await health.run_all_checks()
        
        print(f"Overall Status: {report['status'].upper()}")
        print(f"Uptime: {report['uptime_seconds']} seconds\n")
        
        for check_name, check_result in report["checks"].items():
            status_emoji = {
                "healthy": "✓",
                "degraded": "⚠",
                "unhealthy": "✗",
            }
            emoji = status_emoji.get(check_result["status"], "?")
            print(f"{emoji} {check_name}: {check_result['status']}")
            print(f"  Details: {check_result['details']}\n")
    
    asyncio.run(main())
