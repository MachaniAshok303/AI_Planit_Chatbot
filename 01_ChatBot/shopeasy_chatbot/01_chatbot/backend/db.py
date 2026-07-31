"""Supabase Database Client integration for PlanitShop Chatbot."""
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("planit_db")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_ANON_KEY", "") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_client = None


def get_supabase_client():
    global _client
    if _client is not None:
        return _client
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        from supabase import create_client
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _client
    except Exception as e:
        logger.warning(f"Failed to initialize Supabase client: {e}")
        return None


def is_supabase_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


def save_chat_message(session_id: str, role: str, content: str, model: Optional[str] = None) -> bool:
    client = get_supabase_client()
    if not client:
        return False
    try:
        data = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "model": model or "llama-3.3-70b-versatile",
        }
        client.table("chat_messages").insert(data).execute()
        return True
    except Exception as e:
        logger.error(f"Error saving message to Supabase: {e}")
        return False


def get_session_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    client = get_supabase_client()
    if not client:
        return []
    try:
        res = (
            client.table("chat_messages")
            .select("role, content, model, created_at")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching session history from Supabase: {e}")
        return []
