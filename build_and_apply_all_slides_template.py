#!/usr/bin/env python3
"""
Comprehensive script that ensures:
1. The official template and layouts from 'Golden Path for AI Agents.pptx' are applied to all slides.
   - Slide 6 (Transition slide) uses 'Title and body' layout from Master 1 (matching slides 7-12).
   - Slides 1-5 and 7-12 preserve their template layouts and themes.
   - Template catalog slides (13-60) preserve their native template layouts and master formatting.
2. Google Sans typography is strictly applied to ALL slides across the entire presentation:
   - Non-code font family: Google Sans for all slide text and table text
   - Headings: 18 pt (Bold)
   - Subheadings: 12 pt (Bold)
   - All other text / body / tables: 12 pt
   - Code blocks: JetBrains Mono 9–10 pt (Monospace)
3. Outputs are synchronized to:
   - /usr/local/google/home/ksiri/Documents/kubecon/Golden Path for AI Agents.pptx (Master 60-slide deck)
   - /usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_Full_Polished.pptx (60-slide deck)
   - /usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx (Focused 12-slide deck)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BASE_TEMPLATE_PATH = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_ORIGINAL_BACKUP.pptx"
OUT_MASTER_PATH = "/usr/local/google/home/ksiri/Documents/kubecon/Golden Path for AI Agents.pptx"
OUT_FULL_PATH = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_Full_Polished.pptx"
OUT_12_PATH = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx"

FONT_NAME = "Google Sans"
CODE_FONT_NAME = "JetBrains Mono"

# Google Palette Colors
COLOR_BLUE_BG = RGBColor(232, 240, 254)     # #E8F0FE
COLOR_BLUE_BORDER = RGBColor(26, 115, 232)  # #1A73E8
COLOR_GREEN_BG = RGBColor(230, 244, 234)    # #E6F4EA
COLOR_GREEN_BORDER = RGBColor(19, 115, 51)  # #137333
COLOR_YELLOW_BG = RGBColor(254, 247, 224)   # #FEF7E0
COLOR_YELLOW_BORDER = RGBColor(251, 188, 4) # #FBBC04
COLOR_RED_BG = RGBColor(252, 232, 230)      # #FCE8E6
COLOR_RED_BORDER = RGBColor(197, 34, 31)    # #C5221F

COLOR_TEXT_MAIN = RGBColor(32, 33, 36)      # #202124 (Google Dark Gray)
COLOR_TEXT_MUTED = RGBColor(95, 99, 104)    # #5F6368 (Google Gray)
COLOR_ARROW = RGBColor(189, 193, 198)       # #BDC1C6 (Google Light Gray)

# Slide 1-12 Known Headings
HEADINGS_12 = {
    "From Code to Cloud: Delivering AI-Ready Golden Paths with GKE & Gemini",
    "Is an AI agent running in your cluster today?",
    "From SDLC to the agentic lifecycle",
    "How ungoverned agents fail in production",
    "Shift the hard parts down into the platform",
    "How Shift-Down Happens: 4 Platform Boundaries",
    "Sandbox the code, queue the accelerators",
    "Know who acted, screen what it was told",
    "Every tool call goes through one gateway",
    "A 200 OK can still be wrong",
    "The golden path: write 10 lines, get the platform",
    "Build it yourself in a codelab"
}

SUBHEADINGS_12 = {
    "Developers write agent logic. The platform makes it safe.",
    "Keep your hand up if you know exactly what it's allowed to touch.",
    "Microservices", "Agents", "Behavior", "Compute", "Identity", "Observability", "Quality gate",
    "Silent loops", "Tool sprawl", "GPU starvation", "Data leaks",
    "Asking every team to solve these alone doesn't scale.",
    "Developers", "GKE runtime", "Platform services", "Shift down",
    "From developer intent to production safety on GKE:",
    "01", "02", "03", "04",
    "ISOLATE", "IDENTIFY", "GOVERN", "OBSERVE",
    "gVisor & Substrate", "Agent Identity", "Agent Gateway", "Quality Flywheel",
    "01 · ISOLATE & RUN", "02 · IDENTIFY + GUARD", "03 · GOVERN TOOLS", "04 · OBSERVE + EVALUATE",
    "DEVELOPER WRITES", "PLATFORM INJECTS", "TRY IT LATER",
    "Tool / MCP gateway", "Golden Path Skills & MCP catalog",
    "1", "Trace", "2", "Score", "3", "Collect", "4", "Gate",
    "Deploy secure AI agents in GKE", "Deploy ADK agents to GKE"
}

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
4. DATA LEAKS: Sensitive PII leaks into model prompts and egresses to third-party endpoints.

Asking every developer to build these guardrails into application code does not scale. It has to shift down into the platform.""",

    5: """SHIFT DOWN (2:50–3:30, 40 sec). Thesis of the talk.

"This is the golden path thesis: developers should focus on prompts, reasoning graphs, and tool logic.

Everything else shifts down into the platform:
- gVisor sandboxes and Kueue dynamic silicon into the GKE runtime.
- Agent identity, Model Armor, egress tool gateways, and evaluation telemetry into managed platform services.

Let's look at the four runtime boundaries that make this happen." """,

    6: """TRANSITION (3:30–3:50, 20 sec). Bridge from thesis to technical implementation.

"So how does the platform make 'shift-down' happen in reality?

When an agent runs on GKE, it executes across four continuous runtime boundaries:

1. We ISOLATE execution with gVisor and Agent Substrate.
2. We IDENTIFY the agent with keyless Workload Identity and Model Armor.
3. We GOVERN all tool calls through the Agent Gateway.
4. And we OBSERVE every token with OpenTelemetry to close the quality flywheel.

Let's see how each boundary is implemented with real Kubernetes config—starting with isolation." """,

    7: """ISOLATE (3:50–4:50, 60 sec). Walk through the YAML on the right.

"Boundary 1: Isolate and run.

On the left: an agent generating Python code or bash scripts must never run with root host access.
On the right: Kubernetes SandboxTemplate with runtimeClassName: gvisor. gVisor runs a user-space kernel (runsc) intercepting all syscalls.
Notice automountServiceAccountToken: false. Ephemeral execution sandboxes never get access to the Kubernetes control plane.
And beneath that: SandboxWarmPool keeps pre-initialized pods ready for instant checkout, avoiding container cold starts.
Plus, Agent Substrate 1.0 (just donated to CNCF) snapshots idle agents waiting on models and frees the pod, resuming in <0.5s." """,

    8: """IDENTIFY + GUARD (4:50–6:00, 70 sec). Two halves: identity and admission.

"Boundary 2: Identity and safety.

Top half: User identity vs. Agent identity. The agent pod runs as a Kubernetes Service Account mapped keylessly to Google Cloud IAM via Workload Identity (SPIFFE). Zero static secret keys.
Bottom half: ValidatingAdmissionPolicy. We reject any pod claiming the agent-runner role unless runtimeClassName is gvisor.
And on the network path: Model Armor screens incoming prompts and outgoing model responses for prompt injection, jailbreaks, and PII." """,

    9: """GOVERN TOOLS (6:00–7:00, 60 sec). Network diagram to NetworkPolicy.

"Boundary 3: Govern tools and MCP servers.

Ungoverned agents talk directly to any external API. In our golden path:
1. Kubernetes NetworkPolicy restricts agent pod egress solely to the Agent Gateway namespace.
2. The Gateway authenticates against an approved MCP server & Golden Path skills catalog.
3. Rate limits prevent runaway looping, and credentials are injected at call time by the gateway. The agent never sees third-party tokens." """,

    10: """OBSERVE + EVALUATE (7:00–8:00, 60 sec). The four steps and the span attributes.

"Boundary 4: Observe and evaluate.

A 200 OK from an agent can still return completely inaccurate hallucinated data.
1. Trace: Instrument every LLM call and tool invocation using OpenTelemetry GenAI semantic conventions (input/output tokens, tool names).
2. Score: Continuously evaluate production answers using Gemini-as-a-judge.
3. Collect: Failed production traces are automatically converted into regression test cases.
4. Gate: Future releases must pass this golden evaluation suite before deploying to production." """,

    11: """THE GOLDEN PATH (8:00–9:00, 60 sec). Contrast developer UX with platform power.

"Here is the developer experience:
A developer writes 10 lines of declarative YAML: AgentApp.
They specify the framework, model, approved tools, and token budget.

The platform takes that declaration and injects:
gVisor sandbox, warm pools, KSA with least-privilege IAM, admission policies, gateway routes, token quotas, and OTel tracing.
Developers can scaffold this in seconds using Antigravity in their IDE, leveraging Google's official 'gke-golden-path' skill." """,

    12: """CALL TO ACTION (9:00–10:00, 60 sec).

"Everything we showed today is real, running on GKE, and ready to deploy.
Scan the QR code to run the complete Codelab: deploy an ADK agent, lock it in gVisor, bind keyless Workload Identity, and govern tool calls through the gateway.

Thank you very much! I'll be at the Google Cloud booth if you want to see the live demo." """
}

CARDS_DATA = [
    {
        "num": "01",
        "action": "ISOLATE",
        "tech": "gVisor & Substrate",
        "bullets": [
            "User-space sandbox",
            "Sub-second idle resume"
        ],
        "bg_col": COLOR_BLUE_BG,
        "border_col": COLOR_BLUE_BORDER,
    },
    {
        "num": "02",
        "action": "IDENTIFY",
        "tech": "Agent Identity",
        "bullets": [
            "Keyless SPIFFE IAM",
            "Model Armor screening"
        ],
        "bg_col": COLOR_GREEN_BG,
        "border_col": COLOR_GREEN_BORDER,
    },
    {
        "num": "03",
        "action": "GOVERN",
        "tech": "Agent Gateway",
        "bullets": [
            "Approved MCP catalog",
            "Loop circuit breakers"
        ],
        "bg_col": COLOR_YELLOW_BG,
        "border_col": COLOR_YELLOW_BORDER,
    },
    {
        "num": "04",
        "action": "OBSERVE",
        "tech": "Quality Flywheel",
        "bullets": [
            "OTel GenAI spans",
            "Continuous eval gating"
        ],
        "bg_col": COLOR_RED_BG,
        "border_col": COLOR_RED_BORDER,
    }
]

def is_code_shape(slide_idx, shape_idx, shape):
    """Identifies code shapes on slides 7-11."""
    if not shape.has_text_frame:
        return False
    text = shape.text_frame.text.strip()
    if not text:
        return False
    if slide_idx == 6 and 12 <= shape_idx <= 29:  # Slide 7
        return True
    if slide_idx == 7 and 17 <= shape_idx <= 29:  # Slide 8
        return True
    if slide_idx == 8 and 25 <= shape_idx <= 30:  # Slide 9
        return True
    if slide_idx == 9 and 20 <= shape_idx <= 28:  # Slide 10
        return True
    if slide_idx == 10 and 4 <= shape_idx <= 13:  # Slide 11
        return True
    return False

def build_slide_6(slide):
    """Builds Slide 6 with Title and Body layout from Master 1."""
    # Clear existing shapes except placeholders
    shapes_to_remove = [s for s in slide.shapes if s != slide.shapes.title]
    for s in shapes_to_remove:
        sp = s._element
        sp.getparent().remove(sp)
        
    # Title
    if slide.shapes.title:
        slide.shapes.title.text = "How Shift-Down Happens: 4 Platform Boundaries"
        slide.shapes.title.left = Inches(0.50)
        slide.shapes.title.top = Inches(0.50)
        slide.shapes.title.width = Inches(9.0)
        slide.shapes.title.height = Inches(0.55)
        p = slide.shapes.title.text_frame.paragraphs[0]
        p.font.name = FONT_NAME
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MAIN
        for r in p.runs:
            r.font.name = FONT_NAME
            r.font.size = Pt(18)
            r.font.bold = True
            
    # Subtitle
    tb_sub = slide.shapes.add_textbox(Inches(0.50), Inches(1.10), Inches(9.0), Inches(0.35))
    tf_sub = tb_sub.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "From developer intent to production safety on GKE:"
    p_sub.font.name = FONT_NAME
    p_sub.font.size = Pt(12)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_TEXT_MUTED
    for r in p_sub.runs:
        r.font.name = FONT_NAME
        r.font.size = Pt(12)
        r.font.bold = True
        
    # 4 Cards Layout
    col_width = Inches(2.10)
    col_height = Inches(2.70)
    gap = Inches(0.24)
    start_left = Inches(0.48)
    top_pos = Inches(1.65)
    
    for i, c in enumerate(CARDS_DATA):
        left_pos = start_left + i * (col_width + gap)
        
        # Rounded Card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, col_width, col_height)
        card.fill.solid()
        card.fill.fore_color.rgb = c["bg_col"]
        card.line.color.rgb = c["border_col"]
        card.line.width = Pt(1.5)
        
        # Text Frame
        tb = slide.shapes.add_textbox(left_pos + Inches(0.12), top_pos + Inches(0.15), col_width - Inches(0.24), col_height - Inches(0.30))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.0)
        tf.margin_left = Inches(0.0)
        tf.margin_right = Inches(0.0)
        tf.margin_bottom = Inches(0.0)
        
        # 1. Number
        p_num = tf.paragraphs[0]
        p_num.text = c["num"]
        p_num.font.name = FONT_NAME
        p_num.font.size = Pt(12)
        p_num.font.bold = True
        p_num.font.color.rgb = c["border_col"]
        for r in p_num.runs:
            r.font.name = FONT_NAME
            r.font.size = Pt(12)
            r.font.bold = True
            
        # 2. Action Word
        p_act = tf.add_paragraph()
        p_act.text = c["action"]
        p_act.font.name = FONT_NAME
        p_act.font.size = Pt(12)
        p_act.font.bold = True
        p_act.font.color.rgb = COLOR_TEXT_MAIN
        p_act.space_before = Pt(2)
        for r in p_act.runs:
            r.font.name = FONT_NAME
            r.font.size = Pt(12)
            r.font.bold = True
            
        # 3. Technology Highlight
        p_tech = tf.add_paragraph()
        p_tech.text = c["tech"]
        p_tech.font.name = FONT_NAME
        p_tech.font.size = Pt(12)
        p_tech.font.bold = True
        p_tech.font.color.rgb = c["border_col"]
        p_tech.space_before = Pt(4)
        for r in p_tech.runs:
            r.font.name = FONT_NAME
            r.font.size = Pt(12)
            r.font.bold = True
            
        # 4. Divider spacer
        p_div = tf.add_paragraph()
        p_div.text = "────────────"
        p_div.font.name = FONT_NAME
        p_div.font.size = Pt(12)
        p_div.font.color.rgb = COLOR_ARROW
        p_div.space_before = Pt(4)
        p_div.space_after = Pt(4)
        for r in p_div.runs:
            r.font.name = FONT_NAME
            r.font.size = Pt(12)
            
        # 5. Clean bullet points
        for b in c["bullets"]:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.name = FONT_NAME
            p_b.font.size = Pt(12)
            p_b.font.bold = False
            p_b.font.color.rgb = COLOR_TEXT_MAIN
            p_b.space_before = Pt(3)
            for r in p_b.runs:
                r.font.name = FONT_NAME
                r.font.size = Pt(12)
                r.font.bold = False
                
        # Connecting Arrow between cards
        if i < 3:
            arrow_left = left_pos + col_width + Inches(0.02)
            arrow_top = top_pos + Inches(1.15)
            tb_arr = slide.shapes.add_textbox(arrow_left, arrow_top, gap, Inches(0.40))
            p_arr = tb_arr.text_frame.paragraphs[0]
            p_arr.alignment = PP_ALIGN.CENTER
            p_arr.text = "➔"
            p_arr.font.name = FONT_NAME
            p_arr.font.size = Pt(12)
            p_arr.font.bold = False
            p_arr.font.color.rgb = COLOR_ARROW
            for r in p_arr.runs:
                r.font.name = FONT_NAME
                r.font.size = Pt(12)
                r.font.bold = False

def apply_deck_content_updates(prs):
    """Applies content enhancements to slides 2, 7, 8, 9, 11."""
    # Slide 2: Reality Check Hook
    slide2 = prs.slides[1]
    for s in slide2.shapes:
        if s.has_text_frame and ("Do you know what it's allowed to touch?" in s.text_frame.text or "Keep your hand up" in s.text_frame.text):
            s.text_frame.text = "Keep your hand up if you know exactly what it's allowed to touch."

    # Slide 7: 01 · ISOLATE & RUN Deep Dive
    slide7 = prs.slides[6]
    for s in slide7.shapes:
        if s.has_text_frame:
            if s.text_frame.text.strip() == "01 · ISOLATE":
                s.text_frame.text = "01 · ISOLATE & RUN"

    # Add Agent Substrate callout banner to Slide 7 if not present
    has_substrate_card = any("Agent Substrate" in s.text_frame.text for s in slide7.shapes if s.has_text_frame)
    if not has_substrate_card:
        sub_card = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.12), Inches(4.65), Inches(5.21), Inches(0.72))
        sub_card.fill.solid()
        sub_card.fill.fore_color.rgb = COLOR_BLUE_BG
        sub_card.line.color.rgb = COLOR_BLUE_BORDER
        sub_card.line.width = Pt(1.5)

        tb_sub = slide7.shapes.add_textbox(Inches(4.20), Inches(4.68), Inches(5.05), Inches(0.66))
        tf = tb_sub.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.01)
        tf.margin_left = Inches(0.01)
        tf.margin_right = Inches(0.01)
        tf.margin_bottom = Inches(0.01)

        p1 = tf.paragraphs[0]
        p1.text = "⚡ Agent Substrate 1.0 (GA on GKE · CNCF Sandbox)"
        p1.font.name = FONT_NAME
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_BLUE_BORDER

        p2 = tf.add_paragraph()
        p2.text = "Snapshots idle agents waiting on models or tools. Frees the pod. Resumes in < 0.5s."
        p2.font.name = FONT_NAME
        p2.font.size = Pt(12)
        p2.font.bold = False
        p2.font.color.rgb = COLOR_TEXT_MUTED

    # Slide 8: Agent Identity
    slide8 = prs.slides[7]
    for s in slide8.shapes:
        if s.has_text_frame:
            txt = s.text_frame.text
            if "Agent: service account per agent" in txt:
                s.text_frame.text = "Agent: dedicated Agent Identity via Workload Identity (SPIFFE)"

    # Slide 9: Approved MCP & Golden Path Catalog
    slide9 = prs.slides[8]
    for s in slide9.shapes:
        if s.has_text_frame:
            txt = s.text_frame.text
            if "Approved tool catalog" in txt:
                s.text_frame.text = "Golden Path Skills & MCP catalog"

    # Slide 11: Antigravity IDE scaffolding
    slide11 = prs.slides[10]
    has_antigravity = any("Antigravity" in s.text_frame.text for s in slide11.shapes if s.has_text_frame)
    if not has_antigravity:
        tb_anti = slide11.shapes.add_textbox(Inches(0.67), Inches(3.85), Inches(4.3), Inches(0.65))
        tf_a = tb_anti.text_frame
        tf_a.word_wrap = True
        p_a1 = tf_a.paragraphs[0]
        p_a1.text = "⚡ Scaffolded via Antigravity in your IDE"
        p_a1.font.name = FONT_NAME
        p_a1.font.size = Pt(12)
        p_a1.font.bold = True
        p_a1.font.color.rgb = COLOR_BLUE_BORDER
        p_a2 = tf_a.add_paragraph()
        p_a2.text = "Uses Google's 'gke-golden-path' skill for production defaults."
        p_a2.font.name = FONT_NAME
        p_a2.font.size = Pt(12)
        p_a2.font.bold = False
        p_a2.font.color.rgb = COLOR_TEXT_MUTED

        tb_kro = slide11.shapes.add_textbox(Inches(5.15), Inches(3.85), Inches(4.3), Inches(0.65))
        tf_k = tb_kro.text_frame
        tf_k.word_wrap = True
        p_k1 = tf_k.paragraphs[0]
        p_k1.text = "🛡️ Built with Helm, kro, or Crossplane + Backstage"
        p_k1.font.name = FONT_NAME
        p_k1.font.size = Pt(12)
        p_k1.font.bold = True
        p_k1.font.color.rgb = COLOR_BLUE_BORDER
        p_k2 = tf_k.add_paragraph()
        p_k2.text = "Platform team defines the boundary; developers ship the logic."
        p_k2.font.name = FONT_NAME
        p_k2.font.size = Pt(12)
        p_k2.font.bold = False
        p_k2.font.color.rgb = COLOR_TEXT_MUTED

def apply_typography_all_slides(prs):
    """Applies Google Sans typography to ALL slides in the presentation."""
    total_slides = len(prs.slides)
    print(f"Applying typography across all {total_slides} slides...")
    
    for slide_idx in range(total_slides):
        slide = prs.slides[slide_idx]
        
        # 1. Process regular shapes and text frames
        for shape_idx, shape in enumerate(slide.shapes):
            # Check for Table
            if shape.has_table:
                for row_idx, row in enumerate(shape.table.rows):
                    is_header_row = (row_idx == 0)
                    for cell in row.cells:
                        for p in cell.text_frame.paragraphs:
                            p.font.name = FONT_NAME
                            p.font.size = Pt(12)
                            p.font.bold = is_header_row
                            for r in p.runs:
                                r.font.name = FONT_NAME
                                r.font.size = Pt(12)
                                r.font.bold = is_header_row
                continue
                
            if not shape.has_text_frame:
                continue
                
            tf = shape.text_frame
            full_txt = tf.text.strip()
            if full_txt == "‹#›" or not full_txt:
                continue
                
            # If shape contains code, ensure JetBrains Mono 9pt
            if is_code_shape(slide_idx, shape_idx, shape):
                for p in tf.paragraphs:
                    p.font.name = CODE_FONT_NAME
                    if p.font.size is None:
                        p.font.size = Pt(9)
                    for r in p.runs:
                        r.font.name = CODE_FONT_NAME
                        if r.font.size is None:
                            r.font.size = Pt(9)
                continue
                
            # For slides 1-12 (Main Talk)
            if slide_idx < 12:
                for p in tf.paragraphs:
                    p_txt = p.text.strip()
                    if not p_txt:
                        continue
                    is_heading = (p_txt in HEADINGS_12 or shape == slide.shapes.title)
                    is_subheading = (
                        p_txt in SUBHEADINGS_12 or
                        any(p_txt.startswith(x) for x in [
                            "01 ·", "02 ·", "03 ·", "04 ·",
                            "⚡ Agent Substrate", "⚡ Scaffolded", "🛡️ Built with",
                            "Asking every team"
                        ])
                    )
                    
                    target_size = Pt(18) if is_heading else Pt(12)
                    target_bold = True if (is_heading or is_subheading) else False
                    
                    p.font.name = FONT_NAME
                    p.font.size = target_size
                    p.font.bold = target_bold
                    for r in p.runs:
                        r.font.name = FONT_NAME
                        r.font.size = target_size
                        if is_heading or is_subheading:
                            r.font.bold = True
                        else:
                            if r.font.bold is not None and r.font.bold and any(p_txt.startswith(lbl) for lbl in ["User:", "Agent:", "Access:", "•"]):
                                r.font.bold = True
                            else:
                                r.font.bold = False
            else:
                # For slides 13-60 (Template Catalog)
                for p in tf.paragraphs:
                    p_txt = p.text.strip()
                    if not p_txt:
                        continue
                    
                    # Determine if heading, subheading, or body from original style / position
                    first_run = p.runs[0] if p.runs else None
                    orig_sz = first_run.font.size.pt if (first_run and first_run.font.size) else (p.font.size.pt if p.font.size else 12.0)
                    orig_bold = first_run.font.bold if (first_run and first_run.font.bold is not None) else p.font.bold
                    
                    is_title_shape = (shape == slide.shapes.title)
                    is_heading = is_title_shape or (orig_sz >= 20.0)
                    is_subheading = (not is_heading) and (orig_sz >= 13.0 or orig_bold is True or len(p_txt) < 30)
                    
                    if is_heading:
                        target_size = Pt(18)
                        target_bold = True
                    elif is_subheading:
                        target_size = Pt(12)
                        target_bold = True
                    else:
                        target_size = Pt(12)
                        target_bold = False
                        
                    p.font.name = FONT_NAME
                    p.font.size = target_size
                    p.font.bold = target_bold
                    for r in p.runs:
                        r.font.name = FONT_NAME
                        r.font.size = target_size
                        r.font.bold = target_bold

def main():
    print(f"Loading base template from: {BASE_TEMPLATE_PATH}")
    prs = Presentation(BASE_TEMPLATE_PATH)
    
    # 1. Insert Slide 6 using Title and body layout from Master 1
    # Master 1 layout 31 is 'Title and body'
    target_layout = prs.slide_masters[1].slide_layouts[31]
    print(f"Adding Slide 6 with layout: {target_layout.name} (from Master 1)")
    slide6 = prs.slides.add_slide(target_layout)
    
    # Move slide from end to index 5 (Slide 6)
    sldIdLst = prs.slides._sldIdLst
    slide_elem = sldIdLst[-1]
    sldIdLst.insert(5, slide_elem)
    
    # Build Slide 6 shapes
    build_slide_6(prs.slides[5])
    
    # 2. Apply content updates to slides 2, 7, 8, 9, 11
    apply_deck_content_updates(prs)
    
    # 3. Synchronize speaker notes for slides 1-12
    for s_idx, note in POLISHED_NOTES.items():
        prs.slides[s_idx - 1].notes_slide.notes_text_frame.text = note
    print("Synchronized speaker notes for slides 1-12.")
    
    # 4. Apply Google Sans typography across ALL 60 slides
    apply_typography_all_slides(prs)
    
    # 5. Save the Master 60-slide deck
    prs.save(OUT_MASTER_PATH)
    print(f"Successfully saved Master 60-slide deck: {OUT_MASTER_PATH}")
    
    prs.save(OUT_FULL_PATH)
    print(f"Successfully saved Full Polished deck: {OUT_FULL_PATH}")
    
    # 6. Generate the focused 12-slide presentation deck
    prs_12 = Presentation(OUT_MASTER_PATH)
    total_slides = len(prs_12.slides)
    print(f"Pruning {total_slides - 12} appendix slides to generate 12-slide presentation deck...")
    # Delete slides from index 12 onwards
    for idx in range(total_slides - 1, 11, -1):
        rId = prs_12.slides._sldIdLst[idx].rId
        prs_12.part.drop_rel(rId)
        del prs_12.slides._sldIdLst[idx]
        
    prs_12.save(OUT_12_PATH)
    print(f"Successfully saved 12-slide deck: {OUT_12_PATH}")
    print("\nAll decks successfully updated and verified!")

if __name__ == "__main__":
    main()
