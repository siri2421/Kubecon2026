# Hands-on Codelabs: AI Agents on GKE
### *From Secure Platform Infrastructure to Application Packaging*

Welcome to the companion codelabs for the KubeCon 2026 talk:  
**"From Code to Cloud: Delivering AI-Ready Golden Paths with GKE & Gemini"**

---

## 🛠️ The 2 Codelabs

| Codelab | Audience | Focus Area | What You Will Build |
| :--- | :--- | :--- | :--- |
| [**Codelab 1: Deploy Secure AI Agents on GKE**](./01-deploy-secure-ai-agents-in-gke/README.md) | Platform Engineers & SREs | **Security & Sandboxing** | Configure **gVisor (`runsc`)** user-space sandbox isolation, deploy `SandboxWarmPool` for instant cold-start elimination, bind keyless **Workload Identity**, apply egress `NetworkPolicy`, and enforce `ValidatingAdmissionPolicy`. |
| [**Codelab 2: Deploy ADK Agents to GKE**](./02-deploy-adk-agents-to-gke/README.md) | Application Developers & AI Engineers | **Agent Development & Packaging** | Write an enterprise **ADK Python agent** with Gemini 1.5 Flash and BigQuery tools, package into a non-root multi-stage container, and deploy via the 10-line `AgentApp` Golden Path manifest. |

---

## 🧭 Suggested Path

1. **Start with Codelab 1** if you are responsible for cluster security, zero-trust sandboxing, and platform guardrails.
2. **Start with Codelab 2** if you are writing agent code and want to package an autonomous reasoning loop for Kubernetes.
3. Combine both to see the complete end-to-end "Shift-Down" experience!
