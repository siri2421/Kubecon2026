# The Golden Path for AI Agents on GKE
## 10-Minute KubeCon Lightning Talk / Booth Script
**Speaker:** Sirisha, Cloud Architect at Google  
**Format:** 11 Slides (~10 Minutes at a relaxed booth/stage pace)  
**Tone:** Conversational, authoritative, platform-engineering-focused

---

### Slide 1 · Cover (0:00–0:25)
> "Hi everyone, I'm Sirisha, a Cloud Architect at Google.
> 
> Most of us here have built golden paths for microservices: one template, and security, networking, and observability come for free.
> 
> And this week, Google donated gVisor and Agent Substrate to the CNCF, so the runtime layer for agents is becoming open, community infrastructure.
> 
> In the next ten minutes, I'll show you what the golden path looks like for AI agents on GKE."

---

### Slide 2 · The Question (0:25–0:55)
> "Quick show of hands. Is an AI agent running in your cluster today?
> 
> *[Pause.]*
> 
> Keep your hand up if you can tell me exactly what that agent is allowed to touch.
> 
> *[Pause, and let the hands drop.]*
> 
> That gap is this talk. And closing it is a platform engineering job."

---

### Slide 3 · From SDLC to the Agentic Lifecycle (0:55–1:45)
> "Our platforms were designed for microservices: deterministic code, steady CPU node pools, one service with one role, and tests that pass or fail.
> 
> Agents differ on every row. They reason in loops, so the same input can take a different path. Their compute is bursty. They act on behalf of a user and hand work to other agents. And a 200 OK tells you nothing about whether the answer was right.
> 
> Put agents on a platform built for microservices, and here's what happens."

---

### Slide 4 · Failure Modes (1:45–2:40)
> "Four failure modes keep showing up.
> 
> **Silent loops.** Nothing crashes. You just get 200s while tokens burn all night.
> 
> **Tool sprawl.** Every team wires its agent straight to whatever MCP server it likes.
> 
> **Idle resources.** Agents hold compute and accelerators while they sit waiting.
> 
> **Data leaks.** PII ends up in a prompt, a log or a model call.
> 
> If every app team has to solve these alone, you get ten different half-solutions. So we move the problem."

---

### Slide 5 · Shift Down (2:40–3:25)
> "Shift-left asked developers to own security and operations earlier. For agents, that would turn every developer into a GPU scheduler and a security analyst.
> 
> Shift-*down* does the opposite. We move those concerns into the platform.
> 
> *[Walk the layers top to bottom.]*
> - Developers own what's unique to their agent: prompts, the reasoning graph and tool logic.
> - The GKE runtime isolates and schedules.
> - Platform services govern identity, guardrails, tools and observability.
> 
> Let's take those one at a time, with real config."

---

### Slide 6 · Isolate (3:25–4:50)
> "First, isolation. Agents write and run code from prompts you didn't author, and a normal container shares the node's kernel.
> 
> **Agent Sandbox**, generally available on GKE, fixes that. *[Point at the yellow lines.]* `runtimeClassName: gvisor` puts a user-space kernel between the generated code and the node. And `automountServiceAccountToken: false` means the sandbox holds no Kubernetes credentials at all.
> 
> The warm pool hands out a ready sandbox almost instantly, and a default-deny network policy keeps it away from the metadata server.
> 
> GPU and TPU work goes through Kueue and Dynamic Workload Scheduler, so capacity is acquired when a job runs, instead of being reserved and left idle.
> 
> *[Point at the blue box.]* And at scale: agents spend most of their time *waiting*, on a model, a tool or a human. **Agent Substrate**, which reached 1.0 and GA on GKE last week, snapshots an idle agent, frees the pod, and resumes it on any warm worker in under half a second. You pay for active agents, not waiting ones. And it's now a CNCF Sandbox project, alongside gVisor."

---

### Slide 7 · Identify + Guard (4:50–5:55)
> "Second: who acted, and what was it told?
> 
> Three identities matter:
> - **The user:** their signed-in session, passed through the agent's context and logged with every action.
> - **The agent:** its own Kubernetes service account. With Workload Identity Federation for GKE, you grant IAM directly to that account, with no keys. *[Point at the code.]* This agent can read BigQuery, and nothing else.
> - **Access:** short-lived tokens, issued per call.
> 
> So your audit log reads: 'invoice-agent, acting for Alice, read this table.' Google's **Agent Identity** takes this further, with a SPIFFE-based identity for every agent.
> 
> Then two guards. **Model Armor** screens prompts and responses for injection, jailbreaks and sensitive data. And an **admission policy** *[point at the bottom code]* rejects any agent-code pod that isn't running in gVisor, before it ever schedules."

---

### Slide 8 · Govern Tools (5:55–6:55)
> "Third: tools. Agents never call tools directly. Every MCP server, API and agent-to-agent call goes through one gateway.
> 
> *[Walk the four tiles.]* The gateway:
> - holds an approved tool catalog,
> - enforces per-agent permissions,
> - rate-limits calls, so a looping agent stops,
> - and injects credentials at call time, so no image ever holds an API key.
> 
> *[Point at the code.]* The NetworkPolicy makes it real: agent namespaces can only reach the gateway. Without it, the gateway is just a suggestion.
> 
> This is exactly what Google's **Agent Gateway** does, with **Agent Registry** as the approved catalog. It understands MCP and A2A natively and applies Model Armor to tool traffic."

---

### Slide 9 · Observe + Evaluate (6:55–7:55)
> "Fourth: an agent can return 200 OK and still be wrong, or be stuck in a loop.
> 
> So every agent gets **tracing**. *[Point at the code.]* OpenTelemetry's GenAI conventions record which agent ran, which model and tool it used, and how many tokens. *[Point at the token lines.]* Per-agent cost and loop detection come straight out of those two lines.
> 
> And every agent gets a **quality flywheel**: trace every step, score live answers, turn failures into test cases, and gate the next release on passing them. Every production failure makes your test suite stronger."

---

### Slide 10 · The Golden Path (7:55–9:00)
> "So here's the payoff.
> 
> *[Left side.]* This is everything a developer on the golden path writes: about ten lines. Framework, model, tools from the approved catalog, whether it runs generated code, and a daily token budget.
> 
> *[Right side.]* And this is what the platform turns it into, automatically: a gVisor sandbox with a warm pool, its own identity with least privilege, Model Armor and admission policy, gateway routes and egress lockdown, quotas and budget alerts, and tracing with evaluation.
> 
> `AgentApp` is the interface *your* platform team defines. You can build it today with Helm, kro or Crossplane, and put a Backstage template on top.
> 
> Developers ship agents fast. The platform team owns the boundary they run in."

---

### Slide 11 · Codelab & Wrap-up (9:00–10:00)
> "Everything you saw today is in a codelab you can do on your own time. *[Point at the QR code.]* You'll build an ADK agent, isolate it with Agent Sandbox, wire up Workload Identity and lock down egress.
> 
> Scan it, and come find me here at the booth all week. I'd love to hear how you're running agents on your clusters.
> 
> Thank you!"

---

### Q&A Crib Sheet

| Question | Recommended Answer |
|---|---|
| **"Agent Sandbox vs. Agent Substrate?"** | **Agent Sandbox** gives you an isolated, hardened pod per agent workload (preventing kernel exploits). **Substrate** sits on top and packs thousands of mostly idle/waiting agents onto a small pool of pods via sub-second snapshot/resume. |
| **"Can I use Substrate today?"** | It's GA on GKE Standard clusters 1.37+ (not Autopilot yet). Note: no direct GPU passthrough into agents, and database/MCP connections reconnect after resume. |
| **"Is Agent Gateway available on GKE?"** | GKE is on its list of governed runtimes. Until native GKE support is fully turned on, the NetworkPolicy-plus-gateway pattern shown on Slide 8 is the direct reference implementation. |
| **"Is there a managed option?"** | **Agent Compute Engine**, offering hardware-isolated microVMs per agent, is coming in preview. **Substrate** is the open, Kubernetes-native path. |
| **"Does this work outside GKE?"** | Yes! Agent Sandbox, Substrate, and gVisor are open source. ValidatingAdmissionPolicy, NetworkPolicy, and ResourceQuota are all standard upstream Kubernetes. |
| **"Which agent frameworks?"** | Any framework: Google GenAI ADK, LangGraph, CrewAI, AutoGen, or raw custom code. The platform governance controls sit underneath the application code. |

---
**Pre-stage Checklist:**
- [ ] Ensure QR code on Slide 11 is high contrast and links to the codelab.
- [ ] Confirm code highlighting colors match the slide cues (*"yellow lines"*, *"blue box"*, *"bottom code"*).
