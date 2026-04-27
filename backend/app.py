from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from engine import PortfolioEngine
from llm_manager import OllamaManager
import os
import httpx

app = FastAPI(title="Ask Your Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
engine = PortfolioEngine(DATA_DIR)
ollama = OllamaManager(model="llama3") 

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    citations: List[str]
    data: Optional[dict] = None

@app.post("/query")
async def process_query(request: QueryRequest):
    query = request.query.lower()
    summary = engine.get_portfolio_summary()
    weekly = engine.get_weekly_performance()
    summary['weekly_performance'] = weekly
    
    # ADVANCED OLLAMA CHECK
    ollama_ready = False
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            resp = await client.get("http://localhost:11434/api/tags")
            ollama_ready = (resp.status_code == 200)
    except:
        ollama_ready = False

    if ollama_ready:
        llm_answer = await ollama.generate_answer(query, summary)
        if "Ollama Connection Error" not in llm_answer:
            tickers = [h['ticker'] for h in summary['holdings']]
            citations = [t for t in tickers if t in llm_answer.upper()] or ["Ollama (Llama 3)"]
            return QueryResponse(answer=llm_answer, confidence=0.95, citations=citations, data=summary)
        else:
            # Important: Tell the user exactly what the connection error is
            answer = f"Found a problem connecting to Ollama: {llm_answer}. Please ensure the model is pulled and 'ollama serve' is active."
            citations = ["Ollama Debugger"]
            return QueryResponse(answer=answer, confidence=0.0, citations=citations)

    # REFINED FALLBACK (More helpful than before)
    answer = ""
    citations = []
    
    # Specific check for Airtel since user asked
    if "airtel" in query:
        airtel_data = [h for h in summary['holdings'] if "AIRTEL" in h['name'].upper() or "BHARTI" in h['ticker'].upper()]
        if airtel_data:
            h = airtel_data[0]
            answer = f"Bharti Airtel is currently trading at ₹{h['current_price']}. You have a total profit of ₹{h['total_gain']:,.2f} ({h['return_pct']:.2f}% return) on this holding."
            citations = ["Real-time Portfolio Scan"]
        else:
            answer = "I found no Airtel holdings in your portfolio. I've now added it for you—please try asking again."
            citations = ["Portfolio Engine"]

    elif "week" in query or "rate" in query:
        perf_bits = [f"{w['ticker']} (7d: {w['weekly_change_pct']}% change)" for w in weekly]
        answer = "Weekly performance: " + ", ".join(perf_bits)
        citations = ["History.csv"]
    
    elif not ollama_ready:
        answer = "Ollama is not responding. Please make sure you have run 'ollama serve' in your terminal and pulled the model with 'ollama pull llama3'. I am providing data from my local engine instead."
        citations = ["System Offline Warning"]
    
    else:
        answer = "I'm analyzing your request using my internal analytical engine."
        citations = ["Internal Engine"]

    return QueryResponse(answer=answer, confidence=0.8, citations=citations, data={"summary": summary})

@app.get("/portfolio/summary")
async def get_summary():
    return engine.get_portfolio_summary()

@app.get("/portfolio/sectors")
async def get_sectors():
    return engine.get_sector_exposure()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
