# Codelab 2: Deploy ADK Agents to GKE
### *Package, Containerize, and Run an Autonomous Agent on Kubernetes*

**Duration:** ~25 minutes  
**Level:** Intermediate  
**Focus:** Developer Inner-Loop, Google GenAI SDK / ADK, Containerization, Golden Path Deployment

---

## 🎯 What You Will Build

In this codelab, you will write, containerize, and deploy a production-grade **Autonomous Invoice Audit Agent** using Google's **Agent Development Kit (ADK)** and the Gemini model:

1. **Agent Logic:** Implement a Python reasoning loop with tools that queries BigQuery read-only views and reconciles invoices against company purchase order rules.
2. **Observability Spans:** Export OpenTelemetry GenAI semantic spans (`gen_ai.operation.name`, `gen_ai.usage.input_tokens`) to Cloud Trace.
3. **Secure Containerization:** Build a hardened, non-root, multi-stage Docker container.
4. **Golden Path Declaration:** Write the 10-line `AgentApp` manifest and deploy it to GKE.

---

## 📋 Prerequisites

* Python 3.11+ installed locally.
* Google Cloud CLI (`gcloud`) authenticated.
* A GKE cluster with Artifact Registry and Gemini API access:
  ```bash
  export PROJECT_ID="<your-project-id>"
  export REGION="us-central1"
  export ARTIFACT_REPO="agent-runtimes"

  gcloud auth login
  gcloud config set project $PROJECT_ID
  gcloud services enable container.googleapis.com \
                         artifactregistry.googleapis.com \
                         aiplatform.googleapis.com
  ```

---

## 🐍 Step 1: Write the ADK Agent Logic (`agent.py`)

Inspect [`agent.py`](./agent.py). This script initializes the Gemini 1.5 Flash model, binds an approved enterprise tool (`query_invoices_table`), instruments OpenTelemetry tracing, and serves a FastAPI HTTP endpoint for agent invocations:

```python
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Invoice Audit ADK Agent", version="1.0.0")

# Initialize Gemini Client (uses Workload Identity keyless authentication)
client = genai.Client()

# Tool Declaration
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
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## 📦 Step 2: Containerize with a Hardened Multi-Stage Dockerfile

Inspect [`Dockerfile`](./Dockerfile). Notice that we run as an unprivileged non-root user (`uid 10001`) and pass `--no-cache-dir` at the command line:

```dockerfile
# Stage 1: Build & Dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Hardened Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY agent.py .

ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080
USER 10001
CMD ["python", "agent.py"]
```

Build and push the image to Google Artifact Registry:

```bash
# Create repository if not already created
gcloud artifacts repositories create $ARTIFACT_REPO \
    --repository-format=docker \
    --location=$REGION \
    --description="AI Agent Runtimes"

# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build & Push
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/invoice-agent:v1.0"
docker build -t $IMAGE_URI .
docker push $IMAGE_URI
```

---

## 📜 Step 3: Write the Golden Path `AgentApp` Manifest

Now, as an application developer, you do not write complex Kubernetes networking, quotas, or admission YAML. You declare your intent in [`agentapp.yaml`](./agentapp.yaml):

```yaml
apiVersion: platform.k8s.io/v1alpha1
kind: AgentApp
metadata:
  name: invoice-agent
  namespace: finance-workloads
  labels:
    team: finance
spec:
  framework: adk
  model: gemini-1.5-flash
  image: us-central1-docker.pkg.dev/your-project-id/agent-runtimes/invoice-agent:v1.0
  tools:
    - catalog/bigquery-readonly
    - catalog/jira-mcp
  runsGeneratedCode: true
  tokenBudgetPerDay: 2M
```

---

## 🚀 Step 4: Deploy & Verify on GKE

Apply the manifest:

```bash
kubectl apply -f agentapp.yaml
```

Check the status of the agent deployment:

```bash
kubectl get agentapp invoice-agent -n finance-workloads
kubectl get pods -n finance-workloads -l app.kubernetes.io/name=invoice-agent
```

### Test Invocation:
Port-forward to the running agent pod and send an audit prompt:

```bash
kubectl port-forward svc/invoice-agent 8080:8080 -n finance-workloads &

curl -s -X POST http://localhost:8080/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Audit pending invoices for vendor VEND-992 and verify approval status."}' | jq .
```

**Expected JSON Response:**
```json
{
  "status": "SUCCESS",
  "output": "I audited vendor VEND-992. Found 2 pending invoices totaling $6,050.50. Both match PO records and are APPROVED.",
  "usage": {
    "prompt_tokens": 142,
    "candidates_tokens": 58
  }
}
```

---

## 📊 Step 5: Observe GenAI Telemetry in Cloud Trace

Because the GKE Golden Path injected OpenTelemetry collectors:
1. Open the **Google Cloud Console** → **Trace** → **Trace Explorer**.
2. Filter by span attribute: `gen_ai.system = "gemini"`.
3. You can inspect exact token consumption per invocation, tool execution latency, and step count.

---

## 🎓 Next Steps
Now that you have deployed the ADK agent, complete [**Codelab 1**](../01-deploy-secure-ai-agents-in-gke/README.md) to wrap this agent in gVisor sandboxing and lock down egress with NetworkPolicies!
