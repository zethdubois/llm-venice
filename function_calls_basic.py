import os
import httpx
import json
from dotenv import load_dotenv

# load .env from the repo root / current working directory so
# VENICE_API_KEY in .env becomes available in os.environ
load_dotenv()

API_KEY = os.getenv("VENICE_API_KEY") or os.getenv("LLM_VENICE_KEY")
if not API_KEY:
    raise SystemExit("Set VENICE_API_KEY or LLM_VENICE_KEY")

BASE = "https://api.venice.ai/api/v1"
URL = f"{BASE}/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city and state"}
                },
                "required": ["location"],
            },
        },
    }
]

payload = {
    "model": "llama-3.3-70b",  # the Venice model id (sample uses model name without "venice/")
    "messages": [{"role": "user", "content": "What's the weather in San Francisco?"}],
    "tools": tools,  # include the function/tools spec
    # add any other Venice-specific fields here
}

r = httpx.post(URL, headers=headers, json=payload, timeout=60)
r.raise_for_status()
resp = r.json()
print("json dumps")
print(json.dumps(resp, indent=2))
# Example: look at the chosen message
try:
    print("chosen message:")
    print(resp["choices"][0]["message"])
except Exception:
    pass