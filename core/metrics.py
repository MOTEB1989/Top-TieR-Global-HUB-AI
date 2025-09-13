"""
Metrics and Observability for Top-TieR Global HUB AI
Provides request logging, performance tracking, and monitoring endpoints
"""
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import redis

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Centralized metrics collection and reporting"""
    
    def __init__(self):
        """Initialize metrics collector with Redis backend"""
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.metrics_ttl = int(os.getenv("METRICS_TTL", "86400"))  # 24 hours
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            logger.info(f"Metrics collector connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.warning(f"Redis connection failed for metrics: {e}. Metrics will be logged only.")
            self.redis_client = None
    
    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())[:8]
    
    def log_request(
        self,
        req_id: str,
        user: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: str = "/",
        method: str = "GET",
        model: Optional[str] = None,
        tokens: Optional[int] = None,
        duration: Optional[float] = None,
        cache_hit: bool = False,
        status_code: int = 200,
        error: Optional[str] = None,
        cost: Optional[float] = None,
        scope: Optional[str] = None
    ) -> bool:
        """Log request details for monitoring and analytics"""
        
        timestamp = datetime.utcnow().isoformat()
        
        # Create comprehensive log entry
        log_entry = {
            "req_id": req_id,
            "timestamp": timestamp,
            "user": user or "anonymous",
            "ip_address": ip_address or "unknown",
            "endpoint": endpoint,
            "method": method,
            "model": model,
            "tokens": tokens,
            "duration": duration,
            "cache_hit": cache_hit,
            "status_code": status_code,
            "error": error,
            "cost": cost,
            "scope": scope
        }
        
        # Log to standard logger
        log_level = logging.ERROR if error else logging.INFO
        logger.log(
            log_level,
            f"Request {req_id}: {method} {endpoint} -> {status_code} "
            f"(model={model}, tokens={tokens}, duration={duration:.3f}s, "
            f"cache_hit={cache_hit}, cost={cost})"
        )
        
        # Store in Redis for analytics
        if self.redis_client:
            try:
                # Store individual request
                request_key = f"metrics:request:{req_id}"
                self.redis_client.setex(
                    request_key,
                    self.metrics_ttl,
                    json.dumps(log_entry, default=str)
                )
                
                # Update daily aggregates
                date_key = datetime.utcnow().strftime("%Y-%m-%d")
                self._update_daily_metrics(date_key, log_entry)
                
                # Update counters
                self._update_counters(log_entry)
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to store metrics in Redis: {e}")
                return False
        
        return True
    
    def _update_daily_metrics(self, date_key: str, log_entry: Dict[str, Any]) -> None:
        """Update daily aggregate metrics"""
        daily_key = f"metrics:daily:{date_key}"
        
        try:
            # Get existing daily metrics
            existing_data = self.redis_client.get(daily_key)
            if existing_data:
                daily_metrics = json.loads(existing_data)
            else:
                daily_metrics = {
                    "date": date_key,
                    "total_requests": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "cache_hits": 0,
                    "errors": 0,
                    "models": {},
                    "endpoints": {},
                    "users": set(),
                    "avg_duration": 0.0,
                    "total_duration": 0.0
                }
            
            # Update metrics
            daily_metrics["total_requests"] += 1
            
            if log_entry.get("tokens"):
                daily_metrics["total_tokens"] += log_entry["tokens"]
            
            if log_entry.get("cost"):
                daily_metrics["total_cost"] += log_entry["cost"]
            
            if log_entry.get("cache_hit"):
                daily_metrics["cache_hits"] += 1
            
            if log_entry.get("error"):
                daily_metrics["errors"] += 1
            
            if log_entry.get("model"):
                model = log_entry["model"]
                daily_metrics["models"][model] = daily_metrics["models"].get(model, 0) + 1
            
            endpoint = log_entry.get("endpoint", "/")
            daily_metrics["endpoints"][endpoint] = daily_metrics["endpoints"].get(endpoint, 0) + 1
            
            if log_entry.get("user"):
                daily_metrics["users"].add(log_entry["user"])
            
            if log_entry.get("duration"):
                daily_metrics["total_duration"] += log_entry["duration"]
                daily_metrics["avg_duration"] = daily_metrics["total_duration"] / daily_metrics["total_requests"]
            
            # Convert set to list for JSON serialization
            daily_metrics["unique_users"] = len(daily_metrics["users"])
            daily_metrics["users"] = list(daily_metrics["users"])
            
            # Store updated metrics
            self.redis_client.setex(
                daily_key,
                self.metrics_ttl,
                json.dumps(daily_metrics, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to update daily metrics: {e}")
    
    def _update_counters(self, log_entry: Dict[str, Any]) -> None:
        """Update real-time counters"""
        try:
            # Increment request counter
            self.redis_client.incr("metrics:counters:total_requests")
            
            # Increment model-specific counter
            if log_entry.get("model"):
                model_key = f"metrics:counters:model:{log_entry['model']}"
                self.redis_client.incr(model_key)
            
            # Increment cache hit counter
            if log_entry.get("cache_hit"):
                self.redis_client.incr("metrics:counters:cache_hits")
            
            # Increment error counter
            if log_entry.get("error"):
                self.redis_client.incr("metrics:counters:errors")
                
        except Exception as e:
            logger.error(f"Failed to update counters: {e}")
    
    def get_daily_metrics(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get daily metrics for specified date (default: today)"""
        if not self.redis_client:
            return {"error": "Redis not available"}
        
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        try:
            daily_key = f"metrics:daily:{date}"
            data = self.redis_client.get(daily_key)
            
            if data:
                return json.loads(data)
            else:
                return {"date": date, "no_data": True}
                
        except Exception as e:
            logger.error(f"Failed to get daily metrics: {e}")
            return {"error": str(e)}
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics and counters"""
        if not self.redis_client:
            return {"error": "Redis not available"}
        
        try:
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_requests": int(self.redis_client.get("metrics:counters:total_requests") or 0),
                "cache_hits": int(self.redis_client.get("metrics:counters:cache_hits") or 0),
                "errors": int(self.redis_client.get("metrics:counters:errors") or 0),
                "models": {}
            }
            
            # Get model-specific counters
            model_keys = self.redis_client.keys("metrics:counters:model:*")
            for key in model_keys:
                model_name = key.split(":")[-1]
                metrics["models"][model_name] = int(self.redis_client.get(key) or 0)
            
            # Calculate cache hit rate
            total_requests = metrics["total_requests"]
            if total_requests > 0:
                metrics["cache_hit_rate"] = (metrics["cache_hits"] / total_requests) * 100
            else:
                metrics["cache_hit_rate"] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            return {"error": str(e)}
    
    def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        try:
            real_time = self.get_real_time_metrics()
            
            if "error" in real_time:
                return "# Error getting metrics\n"
            
            prometheus_output = []
            
            # Total requests
            prometheus_output.append("# HELP total_requests Total number of requests")
            prometheus_output.append("# TYPE total_requests counter")
            prometheus_output.append(f"total_requests {real_time['total_requests']}")
            
            # Cache hits
            prometheus_output.append("# HELP cache_hits Total number of cache hits")
            prometheus_output.append("# TYPE cache_hits counter")
            prometheus_output.append(f"cache_hits {real_time['cache_hits']}")
            
            # Errors
            prometheus_output.append("# HELP errors Total number of errors")
            prometheus_output.append("# TYPE errors counter")
            prometheus_output.append(f"errors {real_time['errors']}")
            
            # Cache hit rate
            prometheus_output.append("# HELP cache_hit_rate Cache hit rate percentage")
            prometheus_output.append("# TYPE cache_hit_rate gauge")
            prometheus_output.append(f"cache_hit_rate {real_time['cache_hit_rate']}")
            
            # Model usage
            for model, count in real_time["models"].items():
                prometheus_output.append(f"# HELP model_requests_{model} Requests for model {model}")
                prometheus_output.append(f"# TYPE model_requests_{model} counter")
                prometheus_output.append(f"model_requests_{{{model}}} {count}")
            
            return "\n".join(prometheus_output) + "\n"
            
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return f"# Error: {e}\n"
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display"""
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            today_metrics = self.get_daily_metrics(today)
            yesterday_metrics = self.get_daily_metrics(yesterday)
            real_time = self.get_real_time_metrics()
            
            return {
                "current_date": today,
                "real_time": real_time,
                "today": today_metrics,
                "yesterday": yesterday_metrics,
                "comparison": {
                    "requests_change": self._calculate_change(
                        today_metrics.get("total_requests", 0),
                        yesterday_metrics.get("total_requests", 0)
                    ),
                    "cost_change": self._calculate_change(
                        today_metrics.get("total_cost", 0),
                        yesterday_metrics.get("total_cost", 0)
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    def _calculate_change(self, current: float, previous: float) -> Dict[str, Any]:
        """Calculate percentage change between two values"""
        if previous == 0:
            return {"change": float('inf') if current > 0 else 0, "direction": "up" if current > 0 else "neutral"}
        
        change = ((current - previous) / previous) * 100
        direction = "up" if change > 0 else "down" if change < 0 else "neutral"
        
        return {"change": round(change, 2), "direction": direction}


# Global metrics instance
metrics = MetricsCollector()