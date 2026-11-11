# Delivering AI-Ready Golden Paths with GKE & Gemini
### *KubeCon 2026 Presentation Companion Repository*

**Speaker:** Sirisha Karra · Cloud Engineer, Google  
**Talk:** *From Code to Cloud: Delivering AI-Ready Golden Paths with GKE & Gemini*  
**Repository:** [https://github.com/siri2421/Kubecon2026](https://github.com/siri2421/Kubecon2026)

---

## 🎯 Executive Overview & Architecture Philosophy: "Shift-Down"

Traditional platform engineering "Shift-Left" burdened developers with Kubernetes networking, GPU scheduling, admission policies, and security sandboxing.

For AI agents, modern platform engineering implements **"Shift-Down"**:
1. **The Developer Contract:** The developer writes ~10 lines of declarative intent specifying the model, tools, and budget (`AgentApp`).
2. **The Platform Engine:** GKE and platform controllers automatically expand that spec into zero-trust production infrastructure (gVisor isolation, Workload Identity, Model Armor, Agent Gateway, and OpenTelemetry tracing).

```
   ┌─────────────────────────────────────────────────────────────┐
   │             DEVELOPER WRITES (~10 Lines YAML)               │
   │  kind: AgentApp (model, framework, tools, token budget)     │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ (Scaffolded via Antigravity / gke-golden-path)
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                 THE 4 PLATFORM BOUNDARIES                   │
   ├──────────────────────────────┬──────────────────────────────┤
   │ 01 · ISOLATE & RUN           │ 02 · IDENTIFY + GUARD        │
   │ • gVisor sandbox (runsc)     │ • Keyless Workload Identity  │
   │ • Agent Sandbox warm pools   │ • Per-Agent SPIFFE identity  │
   │ • Agent Substrate snapshot   │ • Model Armor prompt defense │
   │ • Kueue JIT accelerator queue│ • ValidatingAdmissionPolicy  │
   ├──────────────────────────────┼──────────────────────────────┤
   │ 03 · GOVERN TOOLS            │ 04 · OBSERVE + EVALUATE      │
   │ • Agent Gateway routing      │ • OpenTelemetry GenAI spans  │
   │ • Vetted MCP catalog         │ • Token & cost attribution   │
   │ • Egress NetworkPolicy       │ • Gemini-as-a-judge evals    │
   │ • Rate limits & loop breakers│ • Release gating in CI/CD    │
   └──────────────────────────────┴──────────────────────────────┘
```

---

## 📂 Repository Contents

* [**`codelabs/`**](./codelabs/): Hands-on, step-by-step tutorials featured in the talk:
  * [**Codelab 1: Deploy Secure AI Agents on GKE**](./codelabs/01-deploy-secure-ai-agents-in-gke/README.md) — gVisor sandbox, Workload Identity, warm pools, egress NetworkPolicy, admission controls.
  * [**Codelab 2: Deploy ADK Agents to GKE**](./codelabs/02-deploy-adk-agents-to-gke/README.md) — Python ADK agent with Gemini 1.5 Flash, container packaging, and `AgentApp` Golden Path deployment.
* [**`Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx`**](./Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx): Official 12-slide KubeCon presentation deck with synchronized speaker notes, Google Sans typography, and embedded QR code.
* [**`golden-template/`**](./golden-template/): Production Kubernetes manifests and developer spec templates:
  * [`agentapp-sample.yaml`](./golden-template/agentapp-sample.yaml): The 10-line developer interface.
  * [`platform-manifests.yaml`](./golden-template/platform-manifests.yaml): Complete expanded production infrastructure bundle.
* [**`KUBECON_FINAL_SCRIPT.md`**](./KUBECON_FINAL_SCRIPT.md): Complete verbatim talk track, minute-by-minute cues, and Q&A crib sheet.
* [**`TALK_TRACK_OUTLINE.md`**](./TALK_TRACK_OUTLINE.md): Narrative arc, failure modes breakdown, and technical deep dives.

---

## 💻 1. The Developer Spec: `AgentApp`

Developers focus purely on agent logic, prompt graphs, and enterprise tools:

```yaml
apiVersion: platform.k8s.io/v1alpha1
kind: AgentApp
metadata:
  name: invoice-agent
  team: finance
spec:
  framework: adk
  model: gemini
  tools: 
    - catalog/bigquery-readonly
    - catalog/jira-mcp
  runsGeneratedCode: true
  tokenBudgetPerDay: 2M
```

---

## 🛡️ 2. What GKE Injects Automatically

| Platform Layer | Rendered Kubernetes Resource | Production Security Guarantee |
| :--- | :--- | :--- |
| **01 · Runtime Sandbox** | `SandboxTemplate` + `SandboxWarmPool` | Intercepts syscalls via gVisor (`runsc`). Blocks node kernel escapes. `automountServiceAccountToken: false` prevents control plane tampering. |
| **01 · Silicon Scheduling** | `Kueue` ResourceFlavor + ClusterQueue | JIT accelerator queuing. Dynamic GPU/TPU checkout with zero idle reservations. |
| **02 · Identity** | `ServiceAccount` with Workload Identity | Dedicated keyless SPIFFE identity (`principal://iam.googleapis.com/.../sa/invoice-agent`). Zero static private keys. |
| **02 · Safety Guardrails** | `ValidatingAdmissionPolicy` + `Model Armor` | Rejects non-sandboxed agent runners. Model Armor screens prompts/responses for prompt injection, jailbreaks, and PII leaks. |
| **03 · Tool Governance** | `NetworkPolicy` + `Gateway API` | Egress locked strictly to the Agent Gateway namespace. Gateway handles auth, rate limiting, and loop breakers. |
| **04 · Observability** | OpenTelemetry Collector Spans | Captures `gen_ai.operation.name`, `gen_ai.usage.input_tokens`, and tool names for real-time cost attribution and continuous eval gating. |

---

## 🔗 Verified Reference Links & Upstream Projects

All references below are live and verified:

### 1. Scaffolding & Golden Paths
* **Google Cloud Architecture Framework (GKE Best Practices):** [cloud.google.com/architecture/framework](https://cloud.google.com/architecture/framework)
* **Google Cloud Foundation Toolkit (CFT Blueprints):** [github.com/GoogleCloudPlatform/cloud-foundation-toolkit](https://github.com/GoogleCloudPlatform/cloud-foundation-toolkit)
* **kro (Kubernetes Resource Orchestrator for `AgentApp` CRDs):** [kro.run](https://kro.run)

### 2. Runtime Isolation & Sandboxing
* **GKE Sandbox (Official Google Cloud Documentation):** [cloud.google.com/kubernetes-engine/docs/concepts/sandbox-pods](https://cloud.google.com/kubernetes-engine/docs/concepts/sandbox-pods)
* **gVisor Container Sandbox (`runsc` Kernel):** [gvisor.dev](https://gvisor.dev) · [github.com/google/gvisor](https://github.com/google/gvisor)
* **Kubernetes SIGs Agent Sandbox (CRD Project):** [github.com/kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox)
* **Kueue (CNCF Accelerator & GPU Queuing):** [kueue.sigs.k8s.io](https://kueue.sigs.k8s.io) · [github.com/kubernetes-sigs/kueue](https://github.com/kubernetes-sigs/kueue)

### 3. Agent Identity & Safety Guards
* **GKE Workload Identity Federation (Canonical GA Production Identity):** [cloud.google.com/kubernetes-engine/docs/how-to/workload-identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
* **GKE Security Hardening Guide (CIS Benchmarks):** [cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster](https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster)
* **Google Cloud Model Armor (Inline Prompt & PII Defense):** [cloud.google.com/security/products/model-armor](https://cloud.google.com/security/products/model-armor)

### 4. Tool Governance & Egress Routing
* **GKE Network Policies (Egress Lockdown Guide):** [cloud.google.com/kubernetes-engine/docs/how-to/network-policy](https://cloud.google.com/kubernetes-engine/docs/how-to/network-policy)
* **Kubernetes Gateway API (MCP & Tool Routing):** [gateway-api.sigs.k8s.io](https://gateway-api.sigs.k8s.io) · [github.com/kubernetes-sigs/gateway-api](https://github.com/kubernetes-sigs/gateway-api)

### 5. Observability & Tracing
* **OpenTelemetry GenAI Semantic Conventions (Standard Spans):** [opentelemetry.io/docs/specs/semconv/gen-ai/](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
* **Vertex AI Agent Engine Overview:** [cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)

---

## 🚀 Getting Started: Hands-on Deployment

To test the golden path deployment locally on your GKE cluster:

```bash
# 1. Apply the platform foundation (Namespace, ServiceAccount, NetworkPolicy)
kubectl apply -f golden-template/platform-manifests.yaml

# 2. Deploy your agent declaration
kubectl apply -f golden-template/agentapp-sample.yaml

# 3. Verify gVisor sandbox runtime
kubectl get pods -n finance-workloads -o jsonpath='{.items[*].spec.runtimeClassName}'
# Output: gvisor
```

---

## 👤 Speaker Contact

* **Sirisha Karra** — Cloud Engineer, Google
* **Session:** *From Code to Cloud: Delivering AI-Ready Golden Paths with GKE & Gemini*
* **Booth:** Meet me at the Google Cloud booth at KubeCon!
