import httpx
try:
    with httpx.Client() as client:
        response = client.post("http://localhost:8000/query", json={"query": "stock rate in last week"})
        print(response.json())
except Exception as e:
    print(f"Error: {e}")
