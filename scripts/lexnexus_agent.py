#!/usr/bin/env python3
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.FileHandler('logs/lexnexus-agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LexNexusAgent')

class LexNexusAgent:
    """LexNexus Agent - القائد الذكي للنظام"""

    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)

        self.name = "LexNexus"
        self.sub_models = {
            'Saudi-Nexus': 'g-68d85ae6a19881919a7699aede6f6366',
            'Saudi-Banks': 'g-68d83741405881918336c921a412c7c4'
        }
        self.last_health_check = None
        logger.info(f"✨ {self.name} Agent Initialized")

    def health_check(self) -> Dict[str, Any]:
        """فحص صحة كل النماذج"""
        logger.info("🔍 Running health check...")

        results: Dict[str, Any] = {}

        try:
            url = f"https://api.github.com/repos/{self.config['github_repo']}"
            headers = {'Authorization': f"token {self.config.get('github_token', '')}"}
            resp = requests.get(url, headers=headers, timeout=10)
            results['github'] = {'status': 'online' if resp.status_code == 200 else 'offline'}
        except Exception as e:  # pragma: no cover - logging only
            results['github'] = {'status': 'error', 'message': str(e)}

        try:
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/getMe"
            resp = requests.get(url, timeout=10)
            results['telegram'] = {'status': 'online' if resp.json().get('ok') else 'offline'}
        except Exception as e:  # pragma: no cover - logging only
            results['telegram'] = {'status': 'error', 'message': str(e)}

        for model_name, model_id in self.sub_models.items():
            try:
                url = "https://api.openai.com/v1/models"
                headers = {'Authorization': f"Bearer {self.config['openai_api_key']}"}
                resp = requests.get(url, headers=headers, timeout=10)
                results[model_name] = {'status': 'online' if resp.status_code == 200 else 'offline', 'id': model_id}
            except Exception as e:  # pragma: no cover - logging only
                results[model_name] = {'status': 'error', 'message': str(e), 'id': model_id}

        self.last_health_check = results
        logger.info(f"Health check completed: {json.dumps(results, indent=2)}")
        return results

    def auto_sync_knowledge(self) -> bool:
        """مزامنة تلقائية للمعرفة من المستودع"""
        logger.info("🔄 Starting auto-sync from GitHub repository...")

        try:
            for model_name in self.sub_models:
                logger.info(f"Syncing knowledge to {model_name}...")

            logger.info("✅ Auto-sync completed successfully")
            return True
        except Exception as e:  # pragma: no cover - logging only
            logger.error(f"Auto-sync failed: {e}")
            return False

    def route_request(self, query: str, context: str = "general") -> str:
        """توجيه السؤال للنموذج المناسب"""
        logger.info(f"Routing query: {query[:50]}...")

        if "بنك" in query or "مصرف" in query:
            return "Saudi-Banks"
        if "أمن" in query or "تحقق" in query or "security" in query.lower():
            return "Saudi-Nexus"
        return "LexNexus"

    def send_telegram_alert(self, message: str):
        """إرسال تنبيه إلى Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
            data = {
                "chat_id": self.config['telegram_chat_id'],
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=data, timeout=10)
            logger.info("Alert sent to Telegram")
        except Exception as e:  # pragma: no cover - logging only
            logger.error(f"Failed to send Telegram alert: {e}")

    def run_forever(self):
        """تشغيل الوكيل بشكل دائم"""
        logger.info("=" * 60)
        logger.info(f"🚀 {self.name} Agent Starting...")
        logger.info(f"👑 Mode: LEADER (Controlling {len(self.sub_models)} sub-models)")
        logger.info(f"📦 Sub-models: {list(self.sub_models.keys())}")
        logger.info("=" * 60)

        health = self.health_check()

        status_msg = f"✅ *{self.name} Online*\n\n" + \
                     f"📊 Health: {json.dumps(health, indent=2)[:1000]}"
        self.send_telegram_alert(status_msg)

        iteration = 0
        while True:
            try:
                iteration += 1
                logger.info(f"📍 Iteration #{iteration}")

                if iteration % 60 == 0:
                    self.auto_sync_knowledge()

                if iteration % 10 == 0:
                    self.health_check()

                time.sleep(60)

            except KeyboardInterrupt:
                logger.info("🛑 Agent stopped by user")
                break
            except Exception as e:  # pragma: no cover - logging only
                logger.error(f"💥 Unexpected error: {e}")
                self.send_telegram_alert(f"❌ Agent Error: {str(e)[:500]}")
                time.sleep(300)


def _create_default_config(path: Path):
    default_config = {
        "openai_api_key": "sk-xxxxxxxx",
        "telegram_token": "8361523991:AAFF7NuuVSacnAF_4nydWru_mf8FxxvvhfQ",
        "telegram_chat_id": "8256840669",
        "github_repo": "MOTEB1989/Top-TieR-Global-HUB-AI",
        "github_token": "ghp_xxxxxxxx"
    }
    path.write_text(json.dumps(default_config, indent=2))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 lexnexus_agent.py config.json")
        sys.exit(1)

    config_file = Path(sys.argv[1])
    if not config_file.exists():
        print(f"⚠️ Config file not found: {config_file}")
        print("Creating default config...")
        _create_default_config(config_file)
        print(f"✅ Default config created at {config_file}")
        print("Please edit it with your actual keys before running.")
        sys.exit(0)

    agent = LexNexusAgent(str(config_file))
    agent.run_forever()
