"""Supabase Database Client & PostgREST API integration for PlanitShop Chatbot."""
import os
import json
import logging
import urllib.request
from typing import List, Dict, Any, Optional

logger = logging.getLogger("planit_db")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xxgonoixtpzkfpbcnpuy.supabase.co").rstrip("/")
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
        logger.warning(f"Supabase SDK client unavailable, using PostgREST HTTP fallback: {e}")
        return None


def is_supabase_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


def save_chat_message(session_id: str, role: str, content: str, model: Optional[str] = None) -> bool:
    payload = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "model": model or "llama-3.3-70b-versatile",
    }
    
    # 1. Try Supabase SDK client first
    client = get_supabase_client()
    if client:
        try:
            client.table("chat_messages").insert(payload).execute()
            return True
        except Exception as e:
            logger.warning(f"SDK insert failed, trying HTTP REST: {e}")

    # 2. PostgREST HTTP API fallback
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
        
    try:
        url = f"{SUPABASE_URL}/rest/v1/chat_messages"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status in (200, 201)
    except Exception as e:
        logger.error(f"PostgREST HTTP insert error: {e}")
        return False


def get_session_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    # 1. Try Supabase SDK client first
    client = get_supabase_client()
    if client:
        try:
            res = (
                client.table("chat_messages")
                .select("role, content, model, created_at")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            if res.data:
                return res.data
        except Exception as e:
            logger.warning(f"SDK fetch failed, trying HTTP REST: {e}")

    # 2. PostgREST HTTP API fallback
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []

    try:
        url = f"{SUPABASE_URL}/rest/v1/chat_messages?session_id=eq.{session_id}&order=created_at.asc&limit={limit}&select=role,content,model,created_at"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"PostgREST HTTP select error: {e}")
    return []
