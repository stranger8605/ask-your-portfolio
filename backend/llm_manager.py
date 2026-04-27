import httpx
import json
import os

class OllamaManager:
    def __init__(self, model="llama3", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/generate"
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

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

        # If Gemini API key is present, use Gemini for cloud deployment
        if self.gemini_api_key:
            return await self._generate_gemini(query, system_prompt)

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

    async def _generate_gemini(self, query, system_prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUser Query: {query}"}]
            }]
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    return f"Gemini API Error: {response.status_code}"
        except Exception as e:
            return f"Gemini Connection Error: {str(e)}"
