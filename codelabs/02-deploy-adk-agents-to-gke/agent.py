"""
Autonomous Invoice Audit Agent built with Google GenAI / ADK
Runs as a governed Kubernetes workload on GKE.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from google import genai
from google.genai import types

app = FastAPI(title="Invoice Audit ADK Agent", version="1.0.0")

# Initialize Gemini Client (uses Workload Identity Federation automatically)
client = genai.Client()

def query_invoices_table(vendor_id: str, max_amount: float = 10000.0) -> dict:
    """Mock query to BigQuery invoices read-only dataset via Agent Gateway."""
    return {
        "vendor_id": vendor_id,
        "status": "APPROVED",
        "pending_invoices": [
            {"invoice_id": "INV-2026-001", "amount": 4200.50, "match_po": True},
            {"invoice_id": "INV-2026-002", "amount": 1850.00, "match_po": True}
        ]
    }

class AgentRequest(BaseModel):
    prompt: str

@app.post("/v1/invoke")
def invoke_agent(req: AgentRequest):
    try:
        response = client.models.generate_content(
            model=os.getenv("MODEL_NAME", "gemini-1.5-flash"),
            contents=req.prompt,
            config=types.GenerateContentConfig(
                tools=[query_invoices_table],
                temperature=0.2,
                system_instruction="You are an enterprise finance auditor. Reconcile invoices accurately."
            )
        )
        return {
            "status": "SUCCESS",
            "output": response.text,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthz")
def health():
    return {"status": "HEALTHY"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
