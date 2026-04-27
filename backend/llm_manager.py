import httpx
import json

class OllamaManager:
    def __init__(self, model="llama3", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/generate"

    async def generate_answer(self, query: str, context: dict):
        # Format the portfolio context into a readable string for the LLM
        holdings_str = "\n".join([
            f"- {h['ticker']} ({h['name']}): Price: {h['current_price']}, Day Change: {h['day_return_pct']:.2f}%, Total Return: {h['return_pct']:.2f}%"
            for h in context.get('holdings', [])
        ])

        system_prompt = f"""
        You are a Disciplined Financial Assistant for an HNI Portfolio.
        Use ONLY the following context to answer the user query.
        If the data is missing, say you don't know the specific detail.

        ### Portfolio Context
        Total Value: {context.get('total_current')}
        Total Return: {context.get('total_return_pct')}%
        Day Performance: {context.get('day_return_pct')}%
        
        Weekly Trends (7-day change):
        {context.get('weekly_performance')}
        
        Holdings:
        {holdings_str}

        ### Instructions
        1. Be professional and concise.
        2. Always cite specific tickers when discussing performance.
        3. If asked about risk, look at sector concentration or high beta stocks.
        4. Focus on accuracy over speculation.
        """

        payload = {
            "model": self.model,
            "prompt": f"User Query: {query}\n\nContext-Based Answer:",
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', "I couldn't generate an answer.")
                else:
                    return f"Error: Ollama server returned code {response.status_code}."
        except Exception as e:
            error_msg = f"Ollama Connection Error: {str(e)}"
            print(f"DEBUG: {error_msg}")
            return error_msg
