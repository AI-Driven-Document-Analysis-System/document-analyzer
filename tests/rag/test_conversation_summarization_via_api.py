#!/usr/bin/env python3
"""
End-to-end test to verify conversation summarization and pruning via API endpoints.

This script:
- Creates a conversation via /api/chat/conversations
- Sends 20 messages (your provided list) via /api/chat/message
- Verifies summarization was triggered (metadata.needs_summarization becomes True)
- Verifies a system summary message exists in conversation history
- Verifies older messages were pruned (<= 24 user/assistant messages total after 20 sends)

Run:
  python tests/rag/test_conversation_summarization_via_api.py

Requirement:
- Server running at BASE_URL (default http://localhost:8000)
- GROQ_API_KEY present in the server environment (or .env loaded by server)
"""

import os
import time
import json
from typing import Dict, Any, List

import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_ROOT = f"{BASE_URL}/api/chat"


MESSAGES: List[str] = [
    "What are the key financial metrics in the Q4 2024 report?",
    "How does Q4 2024 compare to Q3 2024?",
    "What are the main risks identified in the quarterly report?",
    "Can you analyze the cash flow from the Q4 report?",
    "What are the growth projections for Q1 2025?",
    "How much was the total revenue in Q4 2024?",
    "What are the key operational challenges mentioned in the report?",
    "Can you summarize the executive summary from Q4 2024?",
    "What are the main competitive advantages discussed?",
    "How does the company plan to address market challenges?",
    "What was the revenue growth percentage in Q4?",
    "Can you analyze the profit margins from the quarterly report?",
    "What are the key performance indicators mentioned?",
    "How far in advance do I need to request leave?",
    "What are the standard work hours according to company policy?",
    "Can you explain the dress code policy?",
    "What are the internet usage guidelines?",
    "How many days of paid leave are employees entitled to?",
    "What should I do if I have safety concerns?",
    "Can you explain the confidentiality requirements?",
]


def post(path: str, payload: Dict[str, Any], timeout_s: int = 120) -> Dict[str, Any]:
    url = f"{API_ROOT}{path}"
    resp = requests.post(url, json=payload, timeout=timeout_s)
    resp.raise_for_status()
    return resp.json()


def get(path: str, timeout_s: int = 60) -> Dict[str, Any]:
    url = f"{API_ROOT}{path}"
    resp = requests.get(url, timeout=timeout_s)
    resp.raise_for_status()
    return resp.json()


def check_server_health() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def main() -> None:
    print("🚀 Starting conversation summarization test via API")
    print(f"API root: {API_ROOT}")

    if not check_server_health():
        print("❌ Server is not healthy or not running. Start it first: python run.py")
        return

    # 1) Create conversation (gets a UUID we can use with history/stats endpoints)
    print("🧪 Creating conversation...")
    conv = post("/conversations", {"title": f"Summarization Test {int(time.time())}"})
    conversation_id = conv["id"]
    print("✅ Conversation created:", conversation_id)

    # 2) Send 20 messages
    print("💬 Sending 20 messages to trigger summarization...")
    needs_summarization_triggered = False
    first_questions_snapshot = set(MESSAGES[:4])  # messages that should be pruned later

    for idx, msg in enumerate(MESSAGES, start=1):
        payload: Dict[str, Any] = {
            "message": msg,
            "conversation_id": conversation_id,
            "user_id": "user-1",
            "memory_type": "summary",
            # Allow server to load GROQ_API_KEY from its env automatically
            "llm_config": {
                "provider": "groq",
                "model": "llama-3.1-8b-instant",
                "temperature": 0.3,
                "streaming": False,
            },
        }

        try:
            start = time.time()
            res = post("/message", payload, timeout_s=180)
            elapsed = time.time() - start
        except requests.HTTPError as http_err:
            print(f"❌ HTTP error on message {idx}: {http_err}")
            if http_err.response is not None:
                print("Response:", http_err.response.text)
            return
        except Exception as e:
            print(f"❌ Error on message {idx}: {e}")
            return

        meta = res.get("metadata", {})
        ns = bool(meta.get("needs_summarization", False))
        if ns:
            needs_summarization_triggered = True

        # Prepare one-line truncated answer snippet
        answer = res.get("response", "")
        snippet = " ".join(answer.replace("\n", " ").replace("\r", " ").split())
        if len(snippet) > 160:
            snippet = snippet[:160] + "..."

        # Print question and one-line answer snippet
        print(f"  ✅ Q{idx} ({elapsed:.2f}s, ns={ns}) | {msg} | A: {snippet}")

        # Gentle pacing to avoid rate limits
        time.sleep(1)

    # 3) Fetch history and stats
    print("📜 Fetching conversation history and stats...")
    history = get(f"/conversations/{conversation_id}/history")
    stats = get(f"/conversations/{conversation_id}/stats")

    messages: List[Dict[str, Any]] = history.get("messages", [])

    # Presence of system summary
    summary_msgs = [m for m in messages if m.get("role") == "system" and (m.get("metadata") or {}).get("type") == "conversation_summary"]
    has_summary = len(summary_msgs) > 0

    # Count only user+assistant messages
    ua_messages = [m for m in messages if m.get("role") in ("user", "assistant")]

    # Verify older specific user messages are pruned (not present as raw user/assistant entries)
    present_older = [m for m in ua_messages if m.get("content") in first_questions_snapshot]

    # Print quick summary
    print("\n—— Results ——")
    print("Summarization triggered flag:", needs_summarization_triggered)
    print("System summary present:", has_summary)
    print("Total messages in history:", len(messages))
    print("User+Assistant messages after run:", len(ua_messages))
    print("Older first 4 messages still present as raw entries:", len(present_older))
    print("Stats:", json.dumps(stats, default=str, indent=2))

    # 4) Assertions (raise AssertionError on failure)
    # a) Summarization should have triggered at least once (around 17th send)
    assert needs_summarization_triggered, "Summarization was never triggered (metadata.needs_summarization stayed False)."

    # b) A system summary message must exist
    assert has_summary, "No system conversation summary message found in history."

    # c) After pruning, user+assistant messages should be much fewer than 40.
    #    Expectation: keep last 8 pairs (16 messages) + up to 4 new pairs afterward (8 messages) = <= 24.
    assert len(ua_messages) <= 24, f"Expected <= 24 user/assistant messages after pruning, found {len(ua_messages)}."

    # d) The earliest user messages should no longer appear as raw user/assistant entries
    assert len(present_older) == 0, "Older user messages were not pruned from raw history."

    print("\n🎉 Test passed: summarization and pruning via API are working as expected.")


if __name__ == "__main__":
    main()


