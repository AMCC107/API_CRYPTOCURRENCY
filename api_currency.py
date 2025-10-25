from dotenv import load_dotenv
load_dotenv()
import os
import json
import requests

# ---- Environment ----
LLM_API_ENDPOINT = os.getenv("LLM_API_ENDPOINT", "https://api.asi1.ai/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "your-api-key")
LLM_MODEL = "asi1-extended"

headers = {
    "Authorization": f"Bearer {LLM_API_KEY}",
    "Content-Type": "application/json",
}

# ---- Target JSON schema ----
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "crypto_conversion",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": {
                "type": "string"
            }
        }
    }
}

# ---- Prompt input from user ----
user_input = input(
    "Enter your crypto query (e.g., 'value of ETH today' or 'convert 1 BTC to USD'): "
)

# ---- Prompt for the LLM ----
prompt = (
    "You can speak English and Spanish. "
    "Return ONLY valid JSON where each key is the source currency and the value is "
    "a string with the amount and the target currency, e.g., {\"PYUSD\": \"55.5 MXN\"}. "
    "No text, no markdown, no explanations. "
    f"User request: {user_input}. "
    "Only return the currency mentioned by the user. "
    "Available currencies: Bitcoin (BTC), Ethereum (ETH), USDT, PYUSD, USD, MXN."
)

# ---- Chat Completions payload ----
payload = {
    "model": LLM_MODEL,
    "messages": [
        {"role": "system", "content": "Consult with Chat-Assistand-101. Return ONLY valid JSON in the specified format."},
        {"role": "user", "content": prompt},
    ],
    "response_format": response_format,
}

# ---- Send request ----
resp = requests.post(
    f"{LLM_API_ENDPOINT}/chat/completions",
    headers=headers,
    json=payload,
    timeout=60,
)

if not resp.ok:
    print(resp.status_code, resp.text)
    resp.raise_for_status()

data = resp.json()

# ---- Parse JSON content ----
try:
    content = (
        (data.get("choices") or [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    parsed = json.loads(content) if content else None
except Exception:
    parsed = None

# ---- Output ----
print(json.dumps(parsed, indent=2) if parsed is not None else "None")
