import json
import urllib.request
import time

lm_studio_key = "sk-lm-zNWbJXwG:QrJlaKoobkSLyhDe4lhe"
lms_url = "http://localhost:1234/v1/chat/completions"

# Fetch model
model_to_use = "meta/llama-3.3-70b"
try:
    models_req = urllib.request.Request(
        "http://localhost:1234/v1/models",
        headers={"Authorization": f"Bearer {lm_studio_key}"}
    )
    with urllib.request.urlopen(models_req, timeout=5) as m_res:
        m_data = json.loads(m_res.read().decode("utf-8"))
        if m_data.get("data") and len(m_data["data"]) > 0:
            model_to_use = m_data["data"][0]["id"]
            print(f"Auto-detected model: {model_to_use}")
except Exception as e:
    print(f"Model fetch error: {e}")

data = {
    "model": model_to_use,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in 5 words."}
    ],
    "temperature": 0.2
}

req = urllib.request.Request(
    lms_url,
    data=json.dumps(data).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {lm_studio_key}"
    }
)

print("Sending chat completions request...")
start_time = time.time()
try:
    with urllib.request.urlopen(req, timeout=60) as response:
        res_body = json.loads(response.read().decode("utf-8"))
        print(f"Success in {time.time() - start_time:.2f} seconds!")
        print("Response:", res_body["choices"][0]["message"]["content"])
except Exception as e:
    print(f"Error after {time.time() - start_time:.2f} seconds: {e}")
