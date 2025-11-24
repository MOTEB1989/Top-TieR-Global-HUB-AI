"""
Alert Management Module
Provides alerting system with multiple channels (Slack, Email, etc.).
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertManager:
    """
    Manages alerts and notifications across multiple channels.
    
    Supports:
    - Multiple alert channels (Slack, Email, Webhook)
    - Alert levels (Info, Warning, Error, Critical)
    - Alert deduplication
    - Rate limiting
    """

    def __init__(self, service_name: str = "telegram-bot"):
        """
        Initialize alert manager.
        
        Args:
            service_name: Service identifier
        """
        self.service_name = service_name
        self.channels: Dict[str, Dict[str, Any]] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.dedup_window_seconds = 300  # 5 minutes

    def add_slack_channel(self, webhook_url: str, name: str = "slack"):
        """
        Add Slack webhook channel.
        
        Args:
            webhook_url: Slack webhook URL
            name: Channel identifier
        """
        self.channels[name] = {
            "type": "slack",
            "webhook_url": webhook_url,
        }

    def add_email_channel(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addrs: List[str],
        name: str = "email",
    ):
        """
        Add email channel.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            username: SMTP username
            password: SMTP password
            from_addr: Sender email address
            to_addrs: List of recipient email addresses
            name: Channel identifier
        """
        self.channels[name] = {
            "type": "email",
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "from_addr": from_addr,
            "to_addrs": to_addrs,
        }

    def add_webhook_channel(self, url: str, name: str = "webhook"):
        """
        Add generic webhook channel.
        
        Args:
            url: Webhook URL
            name: Channel identifier
        """
        self.channels[name] = {
            "type": "webhook",
            "url": url,
        }

    async def send_alert(
        self,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        metadata: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None,
    ) -> bool:
        """
        Send alert to configured channels.
        
        Args:
            message: Alert message
            level: Alert severity level
            metadata: Optional additional data
            channels: List of channel names (all if None)
            
        Returns:
            True if alert sent successfully
        """
        # Check deduplication
        if self._is_duplicate(message, level):
            return False
        
        alert_data = {
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.value,
            "message": message,
            "metadata": metadata or {},
        }
        
        # Record in history
        self.alert_history.append(alert_data)
        
        # Send to channels
        target_channels = channels if channels else list(self.channels.keys())
        results = []
        
        for channel_name in target_channels:
            if channel_name in self.channels:
                channel = self.channels[channel_name]
                
                if channel["type"] == "slack":
                    result = await self._send_slack(alert_data, channel)
                    results.append(result)
                elif channel["type"] == "email":
                    result = await self._send_email(alert_data, channel)
                    results.append(result)
                elif channel["type"] == "webhook":
                    result = await self._send_webhook(alert_data, channel)
                    results.append(result)
        
        return any(results)

    def _is_duplicate(self, message: str, level: AlertLevel) -> bool:
        """
        Check if alert is a duplicate within dedup window.
        
        Args:
            message: Alert message
            level: Alert level
            
        Returns:
            True if duplicate, False otherwise
        """
        now = datetime.utcnow()
        
        for alert in reversed(self.alert_history[-10:]):  # Check last 10 alerts
            alert_time = datetime.fromisoformat(alert["timestamp"].replace("Z", ""))
            time_diff = (now - alert_time).total_seconds()
            
            if time_diff <= self.dedup_window_seconds:
                if alert["message"] == message and alert["level"] == level.value:
                    return True
        
        return False

    async def _send_slack(self, alert: Dict[str, Any], channel: Dict[str, Any]) -> bool:
        """
        Send alert to Slack.
        
        Args:
            alert: Alert data
            channel: Channel configuration
            
        Returns:
            True if sent successfully
        """
        try:
            # Map alert level to Slack color
            color_map = {
                "info": "#36a64f",  # green
                "warning": "#ff9800",  # orange
                "error": "#f44336",  # red
                "critical": "#9c27b0",  # purple
            }
            
            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert["level"], "#808080"),
                        "title": f"{alert['level'].upper()}: {alert['service']}",
                        "text": alert["message"],
                        "fields": [
                            {
                                "title": "Timestamp",
                                "value": alert["timestamp"],
                                "short": True,
                            },
                            {
                                "title": "Level",
                                "value": alert["level"],
                                "short": True,
                            },
                        ],
                        "footer": alert["service"],
                        "ts": int(datetime.utcnow().timestamp()),
                    }
                ]
            }
            
            # Add metadata fields
            if alert.get("metadata"):
                for key, value in alert["metadata"].items():
                    payload["attachments"][0]["fields"].append(
                        {"title": key, "value": str(value), "short": True}
                    )
            
            async with aiohttp.ClientSession() as session:
                async with session.post(channel["webhook_url"], json=payload) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
            return False

    async def _send_email(self, alert: Dict[str, Any], channel: Dict[str, Any]) -> bool:
        """
        Send alert via email.
        
        Args:
            alert: Alert data
            channel: Channel configuration
            
        Returns:
            True if sent successfully
        """
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert['level'].upper()}] {alert['service']}"
            msg["From"] = channel["from_addr"]
            msg["To"] = ", ".join(channel["to_addrs"])
            
            # Email body
            text = f"""
Alert from {alert['service']}

Level: {alert['level']}
Time: {alert['timestamp']}
Message: {alert['message']}

Metadata:
{json.dumps(alert.get('metadata', {}), indent=2)}
            """
            
            msg.attach(MIMEText(text, "plain"))
            
            # Send email
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._send_smtp(
                    channel["smtp_server"],
                    channel["smtp_port"],
                    channel["username"],
                    channel["password"],
                    channel["from_addr"],
                    channel["to_addrs"],
                    msg,
                ),
            )
            return True
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False

    def _send_smtp(self, server, port, username, password, from_addr, to_addrs, msg):
        """Send email via SMTP (blocking operation)."""
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)

    async def _send_webhook(self, alert: Dict[str, Any], channel: Dict[str, Any]) -> bool:
        """
        Send alert to generic webhook.
        
        Args:
            alert: Alert data
            channel: Channel configuration
            
        Returns:
            True if sent successfully
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(channel["url"], json=alert) as response:
                    return response.status in [200, 201, 202]
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")
            return False

    def get_alert_stats(self) -> Dict[str, Any]:
        """
        Get alert statistics.
        
        Returns:
            Alert statistics
        """
        level_counts = {}
        for alert in self.alert_history:
            level = alert["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            "total_alerts": len(self.alert_history),
            "by_level": level_counts,
            "channels_configured": len(self.channels),
            "recent_alerts": self.alert_history[-5:] if self.alert_history else [],
        }

    def clear_history(self):
        """Clear alert history."""
        self.alert_history.clear()


# Global alert manager instance
_alert_manager_instance: Optional[AlertManager] = None


def get_alert_manager(service_name: str = "telegram-bot") -> AlertManager:
    """
    Get or create global alert manager.
    
    Args:
        service_name: Service identifier
        
    Returns:
        AlertManager instance
    """
    global _alert_manager_instance
    if _alert_manager_instance is None:
        _alert_manager_instance = AlertManager(service_name)
    return _alert_manager_instance


# Example usage
if __name__ == "__main__":

    async def main():
        # Create alert manager
        alerts = get_alert_manager("example-service")
        
        # Configure Slack channel (example - would need real webhook)
        # alerts.add_slack_channel("https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
        
        # Configure webhook channel
        alerts.add_webhook_channel("https://example.com/webhook", "custom")
        
        # Send alerts
        print("Sending test alerts...\n")
        
        await alerts.send_alert(
            "Service started successfully",
            level=AlertLevel.INFO,
            metadata={"version": "1.0.0", "environment": "production"},
        )
        
        await alerts.send_alert(
            "High memory usage detected",
            level=AlertLevel.WARNING,
            metadata={"memory_usage": "85%", "threshold": "80%"},
        )
        
        await alerts.send_alert(
            "Database connection failed",
            level=AlertLevel.ERROR,
            metadata={"database": "postgresql", "attempts": 3},
        )
        
        await alerts.send_alert(
            "Critical system failure",
            level=AlertLevel.CRITICAL,
            metadata={"component": "core", "error": "OutOfMemory"},
        )
        
        # Get statistics
        print("=== Alert Statistics ===\n")
        stats = alerts.get_alert_stats()
        print(f"Total Alerts: {stats['total_alerts']}")
        print(f"By Level: {stats['by_level']}")
        print(f"Channels: {stats['channels_configured']}")
        
        print("\n✓ Alert examples completed")
    
    asyncio.run(main())
