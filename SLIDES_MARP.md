---
marp: true
theme: uncover
class: invert
paginate: true
header: 'KubeCon Lightning Talk · The Golden Path for AI Agents on GKE'
footer: 'Sirisha · Cloud Architect, Google'
style: |
  section {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    text-align: left;
    padding: 40px 60px;
    font-size: 26px;
  }
  h1 {
    color: #38bdf8;
    font-size: 46px;
    margin-bottom: 12px;
  }
  h2 {
    color: #60a5fa;
    font-size: 36px;
    margin-bottom: 20px;
    border-bottom: 2px solid #1e293b;
    padding-bottom: 8px;
  }
  h3 {
    color: #93c5fd;
    font-size: 28px;
    margin-bottom: 10px;
  }
  code {
    background: #1e293b;
    color: #38bdf8;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 21px;
  }
  pre {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 16px;
    font-size: 19px;
    line-height: 1.35;
  }
  .highlight-yellow {
    background-color: #ca8a04;
    color: #fef08a;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 3px;
  }
  .blue-box {
    background: #1e3a8a;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 10px;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  .grid-4 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 14px 18px;
  }
  .badge {
    background: #0284c7;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: bold;
    display: inline-block;
  }
---

<!-- Slide 1 · Cover -->
# The Golden Path for AI Agents on GKE
### Isolating, Orchestrating & Governing Enterprise Agents at Scale

<br>

**Sirisha** · Cloud Architect, Google  
*KubeCon 10-Minute Lightning Talk*

<div class="blue-box" style="margin-top: 30px;">
  📢 <strong>CNCF Announcement:</strong> Google has officially contributed <strong>gVisor</strong> and <strong>Agent Substrate</strong> to the CNCF ecosystem.
</div>

---

<!-- Slide 2 · The Question -->
## The Two Questions

<div style="margin-top: 40px; font-size: 32px; line-height: 1.8;">

1. 🙋 **Show of hands:** Is an AI agent running in your Kubernetes cluster today?

<br>

2. 🔒 **Keep your hand up if...** You can tell me *exactly* what that agent is allowed to touch.

</div>

<br>

> **"That gap is this talk. And closing it is a platform engineering job."**

---

<!-- Slide 3 · SDLC vs Agentic Lifecycle -->
## From SDLC to the Agentic Lifecycle

| Dimension | Traditional Microservices | Autonomous AI Agents |
|---|---|---|
| **Logic** | Deterministic, sequential code | Looping, non-deterministic reasoning |
| **Compute** | Steady CPU/Memory profiles | Bursty execution + 90% waiting time |
| **Identity** | Single service identity | Acting on behalf of user + agent handover |
| **Health** | `200 OK` = Success | `200 OK` tells you nothing about accuracy |

<br>

*A platform built for microservices fails when hosting autonomous reasoning loops.*

---

<!-- Slide 4 · Failure Modes -->
## The 4 Agent Failure Modes on Kubernetes

<div class="grid-4" style="margin-top: 20px;">

<div class="card">
  <h3 style="color: #f87171;">1. Silent Loops</h3>
  Nothing crashes. The pod returns <code>200 OK</code> while runaway loops burn LLM tokens all night.
</div>

<div class="card">
  <h3 style="color: #fb923c;">2. Tool Sprawl</h3>
  Every team wires their agent directly to unvetted MCP servers and ad-hoc external APIs.
</div>

<div class="card">
  <h3 style="color: #facc15;">3. Idle Resources</h3>
  Agents hold memory, IPs, and expensive GPUs while waiting for model or human responses.
</div>

<div class="card">
  <h3 style="color: #c084fc;">4. Data Leaks</h3>
  PII and sensitive database records end up in raw prompts, debug logs, or model calls.
</div>

</div>

---

<!-- Slide 5 · Shift Down -->
## Shift-Left is Broken for AI. "Shift-Down"

Shift-left turned developers into security auditors and GPU schedulers.  
**Shift-down moves agent complexity into the GKE platform runtime.**

<div class="card" style="margin-top: 20px; border-left: 6px solid #38bdf8;">
  <strong>Top Layer: Developers Own Agent Uniqueness</strong><br>
  Prompts · Reasoning Graphs (LangGraph/ADK) · Business Tool Logic
</div>

<div class="card" style="margin-top: 10px; border-left: 6px solid #60a5fa;">
  <strong>Middle Layer: GKE Runtime Isolates & Schedules</strong><br>
  Agent Sandbox (gVisor) · Kueue & DWS Just-in-Time Compute · Agent Substrate
</div>

<div class="card" style="margin-top: 10px; border-left: 6px solid #818cf8;">
  <strong>Bottom Layer: Platform Services Govern & Observe</strong><br>
  Agent Gateway · Agent Registry (MCP) · Model Armor · OTel Tracing
</div>

---

<!-- Slide 6 · Isolate: Agent Sandbox & Substrate -->
## 1. Isolate: Agent Sandbox & Substrate

<div class="grid-2">

<div>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dynamic-code-interpreter
spec:
  # User-space kernel isolation
  runtimeClassName: gvisor  # 🟨 ZERO host kernel access
  
  # No cluster credentials
  automountServiceAccountToken: false
  
  containers:
  - name: python-runner
    image: python:3.11-slim
```

</div>

<div>

### Zero-Trust Code Execution
* **Agent Sandbox:** `runtimeClassName: gvisor` intercepts syscalls in user space.
* **Metadata protection:** Default-deny egress blocks node metadata access.
* **Just-in-Time Accelerators:** Kueue & DWS acquire GPUs when jobs run, not while idling.

<div class="blue-box">
  <strong>Agent Substrate 1.0 (CNCF Sandbox):</strong><br>
  Snapshots idle agents waiting on models or humans. Frees the pod. Resumes in <strong>&lt; 0.5s</strong> on any warm worker!
</div>

</div>

</div>

---

<!-- Slide 7 · Identify + Guard -->
## 2. Identify + Guard: Least Privilege

<div class="grid-2">

<div>

### Three Distinct Identities
1. **The User:** Authenticated session context propagated with every tool action.
2. **The Agent:** Kubernetes Service Account mapped via **Workload Identity Federation** (e.g. read BigQuery only).
3. **Access Tokens:** Short-lived tokens issued per call. Zero static API keys.

</div>

<div>

### Two Platform Guardrails
* **Model Armor:** Screens prompts & responses for injection, jailbreaks, and PII leaks.
* **ValidatingAdmissionPolicy:** Enforces that any pod tagged for agent code execution *must* specify `runtimeClassName: gvisor` before scheduling.

```yaml
# Enforce gVisor at admission
spec:
  validations:
  - expression: "object.spec.runtimeClassName == 'gvisor'"
    message: "Agent code pods must run in gVisor!"
```

</div>

</div>

---

<!-- Slide 8 · Govern Tools: Agent Gateway & MCP -->
## 3. Govern Tools: The Agent Gateway

*Agents never call external tools directly. All MCP & A2A calls go through the Gateway.*

<div class="grid-4" style="margin-bottom: 16px;">
  <div class="card"><strong>1. Approved Catalog</strong><br>Agent Registry manages trusted MCP tools</div>
  <div class="card"><strong>2. RBAC Permissions</strong><br>Per-agent tool execution allowlists</div>
  <div class="card"><strong>3. Loop Breakers</strong><br>Rate limiting stops runaway token burn</div>
  <div class="card"><strong>4. Credential Injection</strong><br>API keys injected at call time; none in images</div>
</div>

```yaml
# NetworkPolicy: The Gateway is NOT optional
kind: NetworkPolicy
spec:
  podSelector: { matchLabels: { app.kubernetes.io/part-of: agent-workload } }
  egress:
  - to: [{ podSelector: { matchLabels: { app: agent-gateway } } }] # Egress locked to gateway
```

---

<!-- Slide 9 · Observe + Evaluate -->
## 4. Observe + Evaluate: The GenAI Flywheel

<div class="grid-2">

<div>

```yaml
# OpenTelemetry GenAI Semantic Conventions
attributes:
  gen_ai.system: "gemini"
  gen_ai.request.model: "gemini-1.5-pro"
  gen_ai.agent.name: "invoice-reconciler"
  gen_ai.usage.input_tokens: 1420
  gen_ai.usage.output_tokens: 310
  gen_ai.tool.name: "bigquery_query"
```

* **Loop Detection:** Automatic circuit breakers trigger on repeated token burn.
* **Gemini Cloud Assist:** Diagnoses blocked egress & quota alerts in plain English.

</div>

<div>

### The Quality Flywheel
```
 ┌───────────────────────────┐
 │   Trace Every Step (OTel) │
 └─────────────┬─────────────┘
               ▼
 ┌───────────────────────────┐
 │  Score Live Agent Answers │
 └─────────────┬─────────────┘
               ▼
 ┌───────────────────────────┐
 │ Failures ➔ New Test Cases │
 └─────────────┬─────────────┘
               ▼
 ┌───────────────────────────┐
 │ Gate Next Release on Eval │
 └───────────────────────────┘
```

</div>

</div>

---

<!-- Slide 10 · The Golden Path -->
## The Payoff: The `AgentApp` Abstraction

<div class="grid-2">

<div class="card" style="border: 2px solid #38bdf8;">

### What the Developer Writes (~10 lines)
```yaml
apiVersion: platform.k8s.io/v1alpha1
kind: AgentApp
metadata:
  name: invoice-agent
spec:
  framework: adk
  model: gemini-1.5-flash
  tools:
  - catalog/bigquery-readonly
  codeExecution: sandboxed
  budget:
    dailyTokens: 500000
```
*(Scaffolded instantly via **Gemini Code Assist**)*

</div>

<div class="card" style="border: 2px solid #10b981;">

### What GKE Deploys Automatically
* ✅ **gVisor Sandbox** with warm pool provisioning
* ✅ **Workload Identity** (least-privilege IAM)
* ✅ **Model Armor** prompt & response inspection
* ✅ **Agent Gateway** routes & egress lockdown
* ✅ **Agent Substrate** 0.5s snapshot/resume
* ✅ **OTel Tracing & Budget Alerts**

*Built with Helm, kro, or Crossplane + Backstage.*

</div>

</div>

---

<!-- Slide 11 · Codelab & Resources -->
## Start Building Your AI Agent Golden Path

<div class="grid-2" style="margin-top: 30px; align-items: center;">

<div>

### Hands-On KubeCon Codelab:
* 🛠️ Build an **ADK Agent** on GKE
* 🛡️ Isolate untrusted code with **Agent Sandbox (gVisor)**
* 🔑 Wire zero-key **Workload Identity**
* 🌐 Lock down egress with **Agent Gateway & NetworkPolicy**

<br>

**Find me at the Google Cloud booth all week!**

</div>

<div style="text-align: center;">

<div style="background: white; color: black; padding: 20px; border-radius: 12px; display: inline-block;">
  <div style="font-size: 70px;">📱</div>
  <div style="font-weight: bold; font-size: 20px; margin-top: 10px;">SCAN FOR CODELAB</div>
  <div style="font-size: 14px; color: #475569;">g.co/cloud/gke-agent-sandbox</div>
</div>

<br><br>

### **Thank You!**
*Questions? Let's connect.*

</div>

</div>
