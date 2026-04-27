import httpx
import json

def check_ollama():
    try:
        response = httpx.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            print(f"SUCCESS: Found Ollama models: {models}")
        else:
            print(f"FAILED: Ollama returned status {response.status_code}")
    except Exception as e:
        print(f"FAILED: Could not connect to Ollama. Is 'ollama serve' running? Error: {e}")

if __name__ == "__main__":
    check_ollama()
