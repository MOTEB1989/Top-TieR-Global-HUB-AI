#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
session_store.py

Session CRUD & persistence for multi-session support.
إدارة الجلسات مع الحفظ الدائم (file-based).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionStore:
    """Manages user sessions with file-based persistence."""
    
    def __init__(self, base_path: str = "analysis/sessions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.max_messages = 50  # Default, can be overridden
        
    def _get_user_dir(self, user_id: int) -> Path:
        """Get or create user-specific directory."""
        user_dir = self.base_path / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def _get_session_path(self, user_id: int, session_name: str) -> Path:
        """Get path to session file."""
        return self._get_user_dir(user_id) / f"{session_name}.json"
    
    def create_session(self, user_id: int, session_name: str) -> bool:
        """Create a new session."""
        session_path = self._get_session_path(user_id, session_name)
        if session_path.exists():
            return False
        
        session_data = {
            "name": session_name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "messages": [],
            "metadata": {
                "model": "gpt-4o-mini",
                "provider": "openai",
                "persona": "default"
            }
        }
        
        try:
            with session_path.open("w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            logger.info(f"[session_store] Created session '{session_name}' for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"[session_store] Failed to create session: {e}")
            return False
    
    def get_session(self, user_id: int, session_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session."""
        session_path = self._get_session_path(user_id, session_name)
        if not session_path.exists():
            # Auto-create default session
            if session_name == "default":
                self.create_session(user_id, session_name)
            else:
                return None
        
        try:
            with session_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[session_store] Failed to read session: {e}")
            return None
    
    def save_session(self, user_id: int, session_name: str, session_data: Dict[str, Any]) -> bool:
        """Save session data."""
        session_path = self._get_session_path(user_id, session_name)
        session_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Trim messages if exceeding max
        if len(session_data.get("messages", [])) > self.max_messages:
            session_data["messages"] = session_data["messages"][-self.max_messages:]
        
        try:
            with session_path.open("w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"[session_store] Failed to save session: {e}")
            return False
    
    def list_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """List all sessions for a user."""
        user_dir = self._get_user_dir(user_id)
        sessions = []
        
        for session_file in user_dir.glob("*.json"):
            try:
                with session_file.open("r", encoding="utf-8") as f:
                    session_data = json.load(f)
                    sessions.append({
                        "name": session_data.get("name", session_file.stem),
                        "created_at": session_data.get("created_at", "N/A"),
                        "updated_at": session_data.get("updated_at", "N/A"),
                        "message_count": len(session_data.get("messages", [])),
                        "model": session_data.get("metadata", {}).get("model", "N/A"),
                        "provider": session_data.get("metadata", {}).get("provider", "N/A")
                    })
            except Exception as e:
                logger.warning(f"[session_store] Failed to read session {session_file}: {e}")
        
        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    def delete_session(self, user_id: int, session_name: str) -> bool:
        """Delete a session."""
        if session_name == "default":
            logger.warning("[session_store] Cannot delete default session, clearing instead")
            return self.clear_session(user_id, session_name)
        
        session_path = self._get_session_path(user_id, session_name)
        if not session_path.exists():
            return False
        
        try:
            session_path.unlink()
            logger.info(f"[session_store] Deleted session '{session_name}' for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"[session_store] Failed to delete session: {e}")
            return False
    
    def clear_session(self, user_id: int, session_name: str) -> bool:
        """Clear messages in a session."""
        session_data = self.get_session(user_id, session_name)
        if not session_data:
            return False
        
        session_data["messages"] = []
        return self.save_session(user_id, session_name, session_data)
    
    def append_message(self, user_id: int, session_name: str, role: str, content: str) -> bool:
        """Append a message to session."""
        session_data = self.get_session(user_id, session_name)
        if not session_data:
            return False
        
        session_data["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return self.save_session(user_id, session_name, session_data)
    
    def get_messages(self, user_id: int, session_name: str) -> List[Dict[str, str]]:
        """Get messages from session (without timestamps for API calls)."""
        session_data = self.get_session(user_id, session_name)
        if not session_data:
            return []
        
        # Return messages in API format (role, content only)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in session_data.get("messages", [])
        ]
    
    def update_metadata(self, user_id: int, session_name: str, key: str, value: Any) -> bool:
        """Update session metadata."""
        session_data = self.get_session(user_id, session_name)
        if not session_data:
            return False
        
        if "metadata" not in session_data:
            session_data["metadata"] = {}
        
        session_data["metadata"][key] = value
        return self.save_session(user_id, session_name, session_data)
    
    def get_metadata(self, user_id: int, session_name: str, key: str, default: Any = None) -> Any:
        """Get session metadata value."""
        session_data = self.get_session(user_id, session_name)
        if not session_data:
            return default
        
        return session_data.get("metadata", {}).get(key, default)
    
    def export_session(self, user_id: int, session_name: str, format: str = "json") -> Optional[str]:
        """Export session in specified format."""
        session_data = self.get_session(user_id, session_name)
        if not session_data:
            return None
        
        if format == "json":
            return json.dumps(session_data, ensure_ascii=False, indent=2)
        elif format == "md":
            lines = [
                f"# جلسة: {session_name}",
                f"\n**تاريخ الإنشاء:** {session_data.get('created_at', 'N/A')}",
                f"**آخر تحديث:** {session_data.get('updated_at', 'N/A')}",
                f"**النموذج:** {session_data.get('metadata', {}).get('model', 'N/A')}",
                f"**المزود:** {session_data.get('metadata', {}).get('provider', 'N/A')}",
                "\n---\n",
            ]
            
            for msg in session_data.get("messages", []):
                role_label = "👤 المستخدم" if msg["role"] == "user" else "🤖 المساعد"
                lines.append(f"\n## {role_label}\n")
                lines.append(msg["content"])
                lines.append("\n")
            
            return "\n".join(lines)
        
        return None
