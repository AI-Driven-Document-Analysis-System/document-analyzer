import os
import uuid
import json
import time
from typing import Optional, Dict, Any

import requests

# Test user ID from database
TEST_USER_ID = "79d0bed5-c1c1-4faf-82d4-fed1a28472d5"


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_ROOT = f"{BASE_URL}/api/chat"

# Optional LLM override via env (otherwise the API will use its defaults and require env in the server)
PROVIDER = os.getenv("PROVIDER")  # e.g., "gemini", "groq", "openai"
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")  # optional


def post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
	url = f"{API_ROOT}{path}"
	resp = requests.post(url, json=payload, timeout=60)
	resp.raise_for_status()
	return resp.json()


def get(path: str) -> Dict[str, Any]:
	url = f"{API_ROOT}{path}"
	resp = requests.get(url, timeout=60)
	resp.raise_for_status()
	return resp.json()


def patch(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
	url = f"{API_ROOT}{path}"
	resp = requests.patch(url, json=payload, timeout=60)
	resp.raise_for_status()
	return resp.json()


def delete(path: str) -> Dict[str, Any]:
	url = f"{API_ROOT}{path}"
	resp = requests.delete(url, timeout=60)
	resp.raise_for_status()
	try:
		return resp.json()
	except Exception:
		return {"status": resp.status_code}


def maybe_llm_config() -> Optional[Dict[str, Any]]:
	if PROVIDER and API_KEY:
		cfg: Dict[str, Any] = {
			"provider": PROVIDER,
			"api_key": API_KEY,
			"temperature": 0.7,
			"streaming": False,
		}
		if MODEL:
			cfg["model"] = MODEL
		return cfg
	return None


def main() -> None:
	print(f"Using API root: {API_ROOT}")
	conv_title = f"Flow test {int(time.time())}"
	user_id = TEST_USER_ID  # Using test user ID from database
	
	# 1) Create a conversation
	payload_create = {"title": conv_title}
	if user_id:
		payload_create["user_id"] = user_id
	print("Creating conversation...")
	conv = post("/conversations", payload_create)
	conversation_id = conv["id"]
	print("Conversation:", json.dumps(conv, default=str, indent=2))

	# 2) Send first message
	msg1 = {
		"message": "How far in advance do I need to request leave again?",
		"conversation_id": conversation_id,
	}
	cfg = maybe_llm_config()
	if cfg:
		msg1["llm_config"] = cfg
	print("Sending first message...")
	r1 = post("/message", msg1)
	print("First response:", json.dumps(r1, default=str, indent=2))

	# 3) Send second message in same conversation
	msg2 = {
		"message": "So that means I can work different hours if my manager approves, right?",
		"conversation_id": conversation_id,
	}
	if cfg:
		msg2["llm_config"] = cfg
	print("Sending second message...")
	r2 = post("/message", msg2)
	print("Second response:", json.dumps(r2, default=str, indent=2))

	# 4) Fetch conversation history
	print("Fetching conversation history...")
	hist = get(f"/conversations/{conversation_id}/history")
	print("History:", json.dumps(hist, default=str, indent=2))
	print(f"Message count reported: {hist.get('message_count')}")

	# 5) Optional: rename conversation
	print("Renaming conversation...")
	renamed = patch(f"/conversations/{conversation_id}", {"title": f"{conv_title} (renamed)"})
	print("Renamed:", json.dumps(renamed, default=str, indent=2))

	# 6) Optional: delete conversation (uncomment to enable)
	# print("Deleting conversation...")
	# deleted = delete(f"/conversations/{conversation_id}")
	# print("Deleted:", json.dumps(deleted, default=str, indent=2))

	print("Done.")


if __name__ == "__main__":
	try:
		main()
	except requests.HTTPError as http_err:
		print("HTTP error:", http_err)
		if http_err.response is not None:
			try:
				print("Response:", http_err.response.json())
			except Exception:
				print("Response text:", http_err.response.text)
	except Exception as e:
		print("Error:", e)