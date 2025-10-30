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

def get_weather(location: str) -> dict:
    """Mock weather function - replace with real API call"""
    return {
        "location": location,
        "temperature": "15°C",
        "conditions": "Partly cloudy",
        "humidity": "65%"
    }

msg = resp["choices"][0]["message"]
if msg.get("tool_calls"):
    tool_call = msg["tool_calls"][0]
    
    # Parse the model's requested arguments
    args = json.loads(tool_call["function"]["arguments"])
    
    # Call YOUR local function
    weather_result = get_weather(**args)
    
    # Send the result back to the model
    follow_up = payload["messages"] + [
        {
            "role": "assistant",
            "content": None,
            "tool_calls": msg["tool_calls"]
        },
        {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(weather_result)
        }
    ]
    
    r2 = httpx.post(URL, headers=headers, json={
        "model": payload["model"],
        "messages": follow_up
    }, timeout=60)
    
    if r2.status_code >= 400:
        print(f"\nError {r2.status_code}:")
        print(r2.text)  # Will show Venice's error message
        
    r2.raise_for_status()
    
    # NOW the model will give you a natural language response
    final_resp = r2.json()
    print("json dumps")
    print(json.dumps(resp, indent=2))
    print("\nFinal answer:")
    print(final_resp["choices"][0]["message"]["content"])
else:
    # Direct text response (no tool call)
    print(msg.get("content"))