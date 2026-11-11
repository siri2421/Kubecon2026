#!/usr/bin/env python3
"""
Synchronizes the official Google template presentation (Golden Path for AI Agents.pptx)
with the refined talk track, updated speaker notes, and enhanced Slide 2 hook.
Produces:
  1. Golden_Path_for_AI_Agents_KubeCon_11Slides.pptx (Focused 11-slide deck for presenting)
  2. Golden_Path_for_AI_Agents_Full_Polished.pptx (Full 59-slide deck with appendix)
"""

import os
from pptx import Presentation

INPUT_PATH = "/usr/local/google/home/ksiri/Documents/kubecon/Golden Path for AI Agents.pptx"
OUT_11_PATH = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_KubeCon_11Slides.pptx"
OUT_FULL_PATH = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_Full_Polished.pptx"

# Synchronized speaker notes combining the detailed technical talk notes with timing and stage cues
POLISHED_NOTES = {
    1: """RUN OF SHOW (10 min): Cover 0:00 · Question 0:20 · SDLC to ADLC 0:50 · Failure modes 1:50 · Shift down 2:50 · Isolate 3:40 · Identify + Guard 4:50 · Govern Tools 6:00 · Observe + Evaluate 7:00 · The Golden Path 8:00 · Codelab 9:00

Hi everyone, I'm Sirisha, a Cloud Architect at Google.

Most of us here have spent years building golden paths for microservices: one template, and security, networking, and observability come for free.

And this week, Google donated gVisor and Agent Substrate to the CNCF, so the runtime layer for agents is becoming open, community infrastructure.

In the next ten minutes, I'll show you what the golden path looks like for AI agents on GKE.""",

    2: """QUESTION (0:20–0:50, 30 sec). Ask both questions out loud and wait for hands.

"Quick show of hands: Is an AI agent—or an LLM service calling tools—running in your cluster today?

[Pause and look around the room.]

(If hands are few): 'And for those who didn't raise your hand—are you sure? Or did a developer just deploy a container with an MCP client and an API key?'

Now, keep your hand up if you can tell me exactly what APIs, databases, or MCP tools that agent is allowed to touch, or what stops it if it enters a loop.

[Pause, and watch the hands drop.]

That gap is this talk. And closing it is a platform engineering job.""",

    3: """SDLC TO ADLC (0:50–1:50, 60 sec). Read across one or two rows, not all five.

"Our platforms were built for microservices: deterministic code, static CPU node pools, one service with one identity, and tests that pass or fail.

Agents differ on every row:
- Behavior: non-deterministic reasoning loops.
- Compute: bursty accelerators with 90% waiting time on I/O.
- Identity: acts for a user and delegates across agents.
- Observability: 200 OK tells you nothing about accuracy.
- Quality: continuous evaluation rather than binary pass/fail.

Put agents on a platform built for microservices, and failure modes appear immediately." """,

    4: """FAILURE MODES (1:50–2:50, 60 sec). One sentence each.

1. SILENT LOOPS: Agents don't crash. Pods return 200 OK while infinite loops burn LLM tokens all night long.
2. TOOL SPRAWL: Every team wires their agent directly to unvetted MCP servers and ad-hoc third-party APIs.
3. GPU STARVATION: Agents hold expensive GPU/TPU reservations while sitting idle waiting on network I/O.
4. DATA LEAKS: Sensitive internal data and PII leak into uninspected prompts, debug logs, or unauthorized model calls.

If every application team has to solve these alone, you get ten different half-solutions. So we move the problem.""",

    5: """SHIFT DOWN (2:50–3:40, 50 sec). The thesis of the talk.

"Shift-left asked developers to own security and operations earlier. For agents, that would turn every developer into a GPU scheduler and a security analyst.

Shift-down does the opposite: we move those concerns down into the platform.

[Walk the layers top to bottom]:
- Developers own what is unique to their agent: prompts, reasoning graphs, and tool logic.
- GKE runtime isolates and schedules: gVisor sandboxes, Kueue + DWS for accelerators, and Agent Substrate.
- Platform services govern: agent identity, Model Armor, tool gateways, and tracing with evals.

Let's look at each layer, with real config." """,

    6: """ISOLATE (3:40–4:50, 70 sec). Answers unsafe generated code and GPU starvation.

"First, isolation. Agents write and run code from prompts you didn't author, and a normal container shares the host Linux kernel.

Agent Sandbox fixes that: 'runtimeClassName: gvisor' puts a user-space kernel between the generated code and the node. And 'automountServiceAccountToken: false' means the sandbox holds zero Kubernetes credentials.

Warm pools hand out a ready sandbox in milliseconds, and a default-deny egress policy keeps the sandbox away from the metadata server.

GPU and TPU work goes through Kueue and Dynamic Workload Scheduler (DWS), so accelerators are acquired just-in-time and released immediately.

And at scale: Agent Substrate snapshots idle agents waiting on models or humans, frees the pod, and resumes in under 0.5s." """,

    7: """IDENTIFY + GUARD (4:50–6:00, 70 sec). Answers the data-leak failure mode and 'who did this?'.

Three identities matter:
1. USER: the signed-in session, passed in context and logged with every action.
2. AGENT: dedicated Kubernetes service account with Workload Identity Federation (least privilege: read BigQuery only, zero static keys).
3. ACCESS: short-lived tokens issued per call.

Two guards:
- Model Armor screens prompts and responses for injection, jailbreaks, and sensitive data.
- Admission policy (ValidatingAdmissionPolicy) rejects any agent-code pod that isn't running in gVisor before it ever schedules.""" ,

    8: """GOVERN TOOLS (6:00–7:00, 60 sec). Answers tool-sprawl and silent loops.

"Agents never call tools directly. Every MCP server, REST API, and agent-to-agent call goes through one gateway.

The Gateway:
1. Approved Catalog: Agent Registry acts as the enterprise source of truth.
2. Per-Agent Permissions: strict tool allowlists per workload.
3. Rate Limits & Loop Breakers: stops runaway token burn.
4. Credential Injection: injected at call time; no API keys in images.

Enforced by NetworkPolicy: agent namespaces can only reach the gateway. Without that, the gateway is just a suggestion." """,

    9: """OBSERVE + EVALUATE (7:00–8:00, 60 sec). Answers the silent loop failure mode and closes the lifecycle.

"An agent can return 200 OK and still be wrong, or be stuck in a loop. So every agent gets:

1. TRACING: OpenTelemetry GenAI semantic conventions record the agent, model, tools, and input/output tokens. Per-agent cost attribution and automated loop detection come straight out of these lines.
2. THE QUALITY FLYWHEEL: Trace every step, score live answers continuously, collect failures into evaluation test cases, and gate the next release on passing them. Every production failure hardens the test suite." """,

    10: """THE GOLDEN PATH (8:00–9:00, 60 sec). The payoff: everything packaged.

"Here's what a developer on the golden path actually writes: about ten lines. Framework, model, tools from the approved catalog, whether it runs generated code, and a daily token budget.

And here's what the platform turns that into, automatically: gVisor sandbox with warm pool, Workload Identity, Model Armor, gateway routes with egress lockdown, quotas and budget alerts, and tracing with evaluation.

'AgentApp' is the interface your platform team defines. You can build it today with Helm, kro or Crossplane, and put Backstage on top.

Developers ship agents fast. The platform team owns the boundary they run in." """,

    11: """CODELAB (9:00–10:00). Leave this slide up through Q&A; people photograph QR codes.

"Everything shown today is in a codelab you can do on your own time. It walks you through building an ADK agent, isolating code in Agent Sandbox with gVisor, wiring Workload Identity, and locking down egress.

Scan the QR code, and come find me at the Google Cloud booth all week. I'd love to hear how you're running AI agents on your clusters.

Thank you!" """
}

def update_presentation():
    # 1. Update Full Presentation
    prs = Presentation(INPUT_PATH)
    
    # Update Slide 2 Text for sharper hook
    slide2 = prs.slides[1]
    for shape in slide2.shapes:
        if shape.has_text_frame:
            txt = shape.text_frame.text.strip()
            if "Do you know what it's allowed to touch?" in txt:
                shape.text_frame.text = "Keep your hand up if you know exactly what it's allowed to touch."
    
    # Update speaker notes on all 11 slides
    for idx in range(11):
        slide = prs.slides[idx]
        if idx + 1 in POLISHED_NOTES:
            slide.notes_slide.notes_text_frame.text = POLISHED_NOTES[idx + 1]
            
    # Save the polished full deck
    prs.save(OUT_FULL_PATH)
    print(f"Saved full polished deck (59 slides): {OUT_FULL_PATH}")
    
    # 2. Create the focused 11-Slide Deck
    prs_11 = Presentation(OUT_FULL_PATH)
    total_slides = len(prs_11.slides)
    for i in range(total_slides - 1, 10, -1):
        rId = prs_11.slides._sldIdLst[i].rId
        prs_11.part.drop_rel(rId)
        del prs_11.slides._sldIdLst[i]
        
    prs_11.save(OUT_11_PATH)
    print(f"Saved clean presentation (11 slides): {OUT_11_PATH}")

if __name__ == "__main__":
    update_presentation()
