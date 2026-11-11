#!/usr/bin/env python3
"""
Generates a polished, 16:9 widescreen PowerPoint presentation (The_Golden_Path_for_AI_Agents_on_GKE.pptx)
from kubecon/slides.html, complete with dark-theme styling, code blocks, tables, cards, and embedded presenter notes.
Can be imported directly into Google Slides or Microsoft PowerPoint.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Theme Colors (Dark Theme from slides.html)
COLOR_BG = RGBColor(9, 13, 22)           # #090d16
COLOR_CARD = RGBColor(19, 27, 46)        # #131b2e
COLOR_BORDER = RGBColor(35, 49, 79)      # #23314f
COLOR_TEXT = RGBColor(241, 245, 249)     # #f1f5f9
COLOR_MUTED = RGBColor(148, 163, 184)    # #94a3b8
COLOR_PRIMARY = RGBColor(56, 189, 248)   # #38bdf8 (Cyan/Light Blue)
COLOR_ACCENT = RGBColor(96, 165, 250)    # #60a5fa (Blue)
COLOR_YELLOW = RGBColor(251, 191, 36)    # #fbbf24 (Amber/Warning)
COLOR_GREEN = RGBColor(52, 211, 153)     # #34d399 (Emerald/Success)
COLOR_RED = RGBColor(248, 113, 113)      # #f87171 (Danger/Red)
COLOR_BLUE_BOX = RGBColor(30, 58, 138)   # #1e3a8a
COLOR_CODE_BG = RGBColor(8, 13, 26)      # #080d1a
COLOR_CODE_TEXT = RGBColor(147, 197, 253)# #93c5fd

FONT_HEADING = "Google Sans"
FONT_BODY = "Roboto"
FONT_CODE = "Consolas"

# Speaker Notes for all 11 slides
SPEAKER_NOTES = {
    1: """Hi everyone, I'm Sirisha, a Cloud Architect at Google.

Most of us here have built golden paths for microservices: one template, and security, networking and observability come for free.

And this week, Google donated gVisor and Agent Substrate to the CNCF, so the runtime layer for agents is becoming open, community infrastructure.

In the next ten minutes, I'll show you what the golden path looks like for AI agents on GKE.""",

    2: """Quick show of hands. Is an AI agent—or an LLM service calling tools—running in your cluster today?

[Pause and look around the room.]

[If hands are few]: "And for those who didn't raise your hand—are you sure? Or did an app team deploy a container with an MCP client and an API key?"

Keep your hand up if you can tell me exactly what that agent is allowed to touch, or what stops it if it gets stuck in a loop.

[Pause, and let the hands drop.]

That gap is this talk. And closing it is a platform engineering job.""",

    3: """Our platforms were designed for microservices: deterministic code, steady CPU node pools, one service with one role, and tests that pass or fail.

Agents differ on every row. They reason in loops, so the same input can take a different path. Their compute is bursty. They act on behalf of a user and hand work to other agents. And a 200 OK tells you nothing about whether the answer was right.

Put agents on a platform built for microservices, and here's what happens.""",

    4: """Four failure modes keep showing up.

Silent loops. Nothing crashes. You just get 200s while tokens burn all night.

Tool sprawl. Every team wires its agent straight to whatever MCP server it likes.

Idle resources. Agents hold compute and accelerators while they sit waiting.

Data leaks. PII ends up in a prompt, a log or a model call.

If every app team has to solve these alone, you get ten different half-solutions. So we move the problem.""",

    5: """Shift-left asked developers to own security and operations earlier. For agents, that would turn every developer into a GPU scheduler and a security analyst.

Shift-down does the opposite. We move those concerns into the platform.

[Walk the layers top to bottom.]
- Developers own what's unique to their agent: prompts, the reasoning graph and tool logic.
- The GKE runtime isolates and schedules.
- Platform services govern identity, guardrails, tools and observability.

Let's take those one at a time, with real config.""",

    6: """First, isolation. Agents write and run code from prompts you didn't author, and a normal container shares the node's kernel.

Agent Sandbox, generally available on GKE, fixes that. [Point at the yellow lines.] 'runtimeClassName: gvisor' puts a user-space kernel between the generated code and the node. And 'automountServiceAccountToken: false' means the sandbox holds no Kubernetes credentials at all.

The warm pool hands out a ready sandbox almost instantly, and a default-deny network policy keeps it away from the metadata server.

GPU and TPU work goes through Kueue and Dynamic Workload Scheduler, so capacity is acquired when a job runs, instead of being reserved and left idle.

[Point at the blue box.] And at scale: agents spend most of their time *waiting*, on a model, a tool or a human. Agent Substrate, which reached 1.0 and GA on GKE last week, snapshots an idle agent, frees the pod, and resumes it on any warm worker in under half a second. You pay for active agents, not waiting ones. And it's now a CNCF Sandbox project, alongside gVisor.""",

    7: """Second: who acted, and what was it told?

Three identities matter:
- The user: their signed-in session, passed through the agent's context and logged with every action.
- The agent: its own Kubernetes service account. With Workload Identity Federation for GKE, you grant IAM directly to that account, with no keys. [Point at the code.] This agent can read BigQuery, and nothing else.
- Access: short-lived tokens, issued per call.

So your audit log reads: 'invoice-agent, acting for Alice, read this table.' Google's Agent Identity takes this further, with a SPIFFE-based identity for every agent.

Then two guards. Model Armor screens prompts and responses for injection, jailbreaks and sensitive data. And an admission policy [point at the bottom code] rejects any agent-code pod that isn't running in gVisor, before it ever schedules.""",

    8: """Third: tools. Agents never call tools directly. Every MCP server, API and agent-to-agent call goes through one gateway.

[Walk the four tiles.] The gateway:
- holds an approved tool catalog,
- enforces per-agent permissions,
- rate-limits calls, so a looping agent stops,
- and injects credentials at call time, so no image ever holds an API key.

[Point at the code.] The NetworkPolicy makes it real: agent namespaces can only reach the gateway. Without it, the gateway is just a suggestion.

This is exactly what Google's Agent Gateway does, with Agent Registry as the approved catalog. It understands MCP and A2A natively and applies Model Armor to tool traffic.""",

    9: """Fourth: an agent can return 200 OK and still be wrong, or be stuck in a loop.

So every agent gets tracing. [Point at the code.] OpenTelemetry's GenAI conventions record which agent ran, which model and tool it used, and how many tokens. [Point at the token lines.] Per-agent cost and loop detection come straight out of those two lines.

And every agent gets a quality flywheel: trace every step, score live answers, turn failures into test cases, and gate the next release on passing them. Every production failure makes your test suite stronger.""",

    10: """So here's the payoff.

[Left side.] This is everything a developer on the golden path writes: about ten lines. Framework, model—like Gemini 1.5 Flash—tools from the approved catalog, whether it runs generated code, and a daily token budget. With Gemini Code Assist, developers can prompt their IDE to scaffold this compliant manifest directly into their repo.

[Right side.] And this is what the platform turns it into, automatically: a gVisor sandbox with a warm pool, its own identity with least privilege, Model Armor and admission policy, gateway routes and egress lockdown, quotas and budget alerts, and tracing with evaluation.

'AgentApp' is the interface your platform team defines. You can build it today with Helm, kro or Crossplane, and put a Backstage template on top.

Developers ship agents fast. The platform team owns the boundary they run in.""",

    11: """Everything you saw today is in a codelab you can do on your own time. [Point at the QR code.] You'll build an ADK agent, isolate it with Agent Sandbox, wire up Workload Identity and lock down egress.

Scan it, and come find me here at the booth all week. I'd love to hear how you're running agents on your clusters.

Thank you!"""
}

def set_slide_background(slide):
    """Sets dark background color for a slide."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    bg.line.color.rgb = COLOR_BG
    return bg

def add_header(slide, title_text, time_tag=""):
    """Adds a standard presentation slide header with timing tag."""
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.9))
    tf = header_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = FONT_HEADING
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT
    
    if time_tag:
        run = p.add_run()
        run.text = f"   {time_tag}"
        run.font.size = Pt(16)
        run.font.bold = False
        run.font.color.rgb = COLOR_ACCENT

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD, border_color=COLOR_BORDER):
    """Adds a styled rounded rectangular card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    return card

def add_code_block(slide, left, top, width, height, code_text, header_label=""):
    """Adds a syntax-friendly dark code block."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_CODE_BG
    bg.line.color.rgb = COLOR_BORDER
    bg.line.width = Pt(1)
    
    tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), height - Inches(0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_top = Inches(0.05)
    
    lines = code_text.strip().split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.font.name = FONT_CODE
        p.font.size = Pt(13)
        
        if line.strip().startswith("#"):
            p.font.color.rgb = COLOR_MUTED
            p.text = line
        elif "runtimeClassName: gvisor" in line or "input_tokens" in line or "output_tokens" in line:
            p.font.color.rgb = COLOR_YELLOW
            p.font.bold = True
            p.text = line
        else:
            p.font.color.rgb = COLOR_CODE_TEXT
            p.text = line

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # -------------------------------------------------------------
    # SLIDE 1 · Cover
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    
    # Badge
    b1 = add_card(s1, Inches(0.8), Inches(0.8), Inches(4.2), Inches(0.45), bg_color=RGBColor(16, 37, 66), border_color=COLOR_PRIMARY)
    tf_b1 = b1.text_frame
    p_b1 = tf_b1.paragraphs[0]
    p_b1.alignment = PP_ALIGN.CENTER
    p_b1.text = "KUBECON 10-MINUTE LIGHTNING TALK"
    p_b1.font.size = Pt(11)
    p_b1.font.bold = True
    p_b1.font.color.rgb = COLOR_PRIMARY
    
    # Main Title
    tb_title = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.2))
    tf = tb_title.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Golden Path for AI Agents on GKE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    p2 = tf.add_paragraph()
    p2.text = "Isolating, Orchestrating & Governing Enterprise Agents at Scale"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(22)
    p2.font.color.rgb = COLOR_ACCENT
    p2.space_before = Pt(10)
    
    # Speaker
    tb_speaker = s1.shapes.add_textbox(Inches(0.8), Inches(3.9), Inches(8), Inches(0.8))
    tf_sp = tb_speaker.text_frame
    p_sp = tf_sp.paragraphs[0]
    p_sp.text = "Sirisha · Cloud Architect, Google"
    p_sp.font.size = Pt(18)
    p_sp.font.bold = True
    p_sp.font.color.rgb = COLOR_TEXT
    
    # Announcement Card
    add_card(s1, Inches(0.8), Inches(4.9), Inches(11.7), Inches(1.6), bg_color=COLOR_BLUE_BOX, border_color=COLOR_PRIMARY)
    tb_ann = s1.shapes.add_textbox(Inches(1.1), Inches(5.05), Inches(11.1), Inches(1.3))
    tf_ann = tb_ann.text_frame
    tf_ann.word_wrap = True
    p_ann1 = tf_ann.paragraphs[0]
    p_ann1.text = "📢 CNCF Community Milestone"
    p_ann1.font.size = Pt(18)
    p_ann1.font.bold = True
    p_ann1.font.color.rgb = COLOR_PRIMARY
    
    p_ann2 = tf_ann.add_paragraph()
    p_ann2.text = "Google has contributed gVisor and Agent Substrate to the Cloud Native Computing Foundation (CNCF)."
    p_ann2.font.size = Pt(16)
    p_ann2.font.color.rgb = COLOR_TEXT
    p_ann2.space_before = Pt(6)
    
    s1.notes_slide.notes_text_frame.text = SPEAKER_NOTES[1]

    # -------------------------------------------------------------
    # SLIDE 2 · The Reality Check
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "The Reality Check", "0:25–0:55")
    
    # Question 1 Card
    add_card(s2, Inches(0.8), Inches(1.6), Inches(11.733), Inches(1.8), border_color=COLOR_PRIMARY)
    tb_q1 = s2.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.1), Inches(1.4))
    tf_q1 = tb_q1.text_frame
    tf_q1.word_wrap = True
    p = tf_q1.paragraphs[0]
    p.text = "🙋 Question 1: The Deployment Reality"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p_sub = tf_q1.add_paragraph()
    p_sub.text = 'Is an autonomous AI agent — or shadow AI workload — running in your cluster today?'
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = COLOR_TEXT
    p_sub.space_before = Pt(8)
    
    # Question 2 Card
    add_card(s2, Inches(0.8), Inches(3.7), Inches(11.733), Inches(1.8), border_color=COLOR_RED)
    tb_q2 = s2.shapes.add_textbox(Inches(1.1), Inches(3.9), Inches(11.1), Inches(1.4))
    tf_q2 = tb_q2.text_frame
    tf_q2.word_wrap = True
    p = tf_q2.paragraphs[0]
    p.text = "🔒 Question 2: The Platform Reality"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED
    p_sub = tf_q2.add_paragraph()
    p_sub.text = 'Keep your hand up if you can tell me exactly what APIs, tools, and credentials that agent can touch.'
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = COLOR_TEXT
    p_sub.space_before = Pt(8)
    
    # Bottom Punchline
    tb_gap = s2.shapes.add_textbox(Inches(0.8), Inches(5.9), Inches(11.733), Inches(0.9))
    p = tb_gap.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = '"That gap is this talk. And closing it is a platform engineering job."'
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    
    s2.notes_slide.notes_text_frame.text = SPEAKER_NOTES[2]

    # -------------------------------------------------------------
    # SLIDE 3 · From SDLC to Agentic Lifecycle
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "From SDLC to the Agentic Lifecycle", "0:55–1:45")
    
    rows, cols = 5, 3
    left, top, width, height = Inches(0.8), Inches(1.6), Inches(11.733), Inches(4.3)
    table_shape = s3.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table
    tbl.columns[0].width = Inches(3.2)
    tbl.columns[1].width = Inches(4.2)
    tbl.columns[2].width = Inches(4.333)
    
    headers = ["Architecture Dimension", "Traditional Microservices", "Autonomous AI Agents"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = COLOR_PRIMARY if i == 2 else COLOR_TEXT
        
    data = [
        ("Execution Flow", "Deterministic, single-pass code", "Non-deterministic reasoning loops"),
        ("Compute Profile", "Steady CPU/Memory node pools", "Bursty compute + 90% waiting on I/O"),
        ("Identity Model", "Single service-to-service IAM", "Delegated user identity + Agent-to-Agent (A2A)"),
        ("Health Signals", "200 OK = Service healthy", "200 OK tells you nothing about accuracy")
    ]
    for row_idx, (d1, d2, d3) in enumerate(data, start=1):
        c1, c2, c3 = tbl.cell(row_idx, 0), tbl.cell(row_idx, 1), tbl.cell(row_idx, 2)
        for c in (c1, c2, c3):
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor(14, 21, 38)
        c1.text_frame.paragraphs[0].text = d1
        c1.text_frame.paragraphs[0].font.bold = True
        c1.text_frame.paragraphs[0].font.size = Pt(15)
        c1.text_frame.paragraphs[0].font.color.rgb = COLOR_TEXT
        
        c2.text_frame.paragraphs[0].text = d2
        c2.text_frame.paragraphs[0].font.size = Pt(14)
        c2.text_frame.paragraphs[0].font.color.rgb = COLOR_MUTED
        
        c3.text_frame.paragraphs[0].text = d3
        c3.text_frame.paragraphs[0].font.size = Pt(14)
        c3.text_frame.paragraphs[0].font.color.rgb = COLOR_PRIMARY
        c3.text_frame.paragraphs[0].font.bold = True

    tb_note = s3.shapes.add_textbox(Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.8))
    p = tb_note.text_frame.paragraphs[0]
    p.text = '⚠️ "Put agents on a platform built for microservices, and failure modes appear immediately."'
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_YELLOW

    s3.notes_slide.notes_text_frame.text = SPEAKER_NOTES[3]

    # -------------------------------------------------------------
    # SLIDE 4 · Failure Modes
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "The 4 Agent Failure Modes on Kubernetes", "1:45–2:40")
    
    cards_data = [
        ("Failure 1: Silent Loops", "Nothing crashes. Pods return 200 OK while infinite agent loops burn LLM tokens all night long.", COLOR_RED, Inches(0.8), Inches(1.6)),
        ("Failure 2: Tool Sprawl", "Every team wires their agent directly to unvetted MCP servers and ad-hoc third-party APIs.", COLOR_YELLOW, Inches(6.8), Inches(1.6)),
        ("Failure 3: Idle Resources", "Agents hold expensive CPU, memory, and accelerator reservations while sitting idle waiting on network I/O.", RGBColor(192, 132, 252), Inches(0.8), Inches(4.3)),
        ("Failure 4: Data Leaks", "Sensitive internal data and PII leak into uninspected prompts, debug logs, or unauthorized model calls.", COLOR_PRIMARY, Inches(6.8), Inches(4.3))
    ]
    for title, desc, border_col, c_left, c_top in cards_data:
        add_card(s4, c_left, c_top, Inches(5.7), Inches(2.3), border_color=border_col)
        tb = s4.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.2), Inches(5.3), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(19)
        p.font.bold = True
        p.font.color.rgb = border_col
        
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(15)
        p_desc.font.color.rgb = COLOR_TEXT
        p_desc.space_before = Pt(8)
        
    s4.notes_slide.notes_text_frame.text = SPEAKER_NOTES[4]

    # -------------------------------------------------------------
    # SLIDE 5 · Shift Down
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, 'Don\'t Shift-Left: "Shift-Down"', "2:40–3:25")
    
    tb_sub = s5.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.6))
    p = tb_sub.text_frame.paragraphs[0]
    p.text = "Shift-left asked developers to become GPU schedulers and security analysts. Shift-down moves that into GKE."
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_MUTED
    
    layers = [
        ("Layer 1: Developer Responsibility (Only what is unique)",
         "System Prompts · Reasoning Graph (LangGraph / ADK) · Business Tool Logic",
         COLOR_PRIMARY, Inches(2.2)),
        ("Layer 2: GKE Platform Runtime (Isolation & Scheduling)",
         "Agent Sandbox (gVisor) · Kueue & DWS Just-in-Time Compute · Agent Substrate Snapshot/Resume",
         COLOR_ACCENT, Inches(3.7)),
        ("Layer 3: Enterprise Platform Services (Governance & Telemetry)",
         "Agent Gateway (MCP Reverse Proxy) · Model Armor · Admission Policies · OpenTelemetry Tracing",
         COLOR_GREEN, Inches(5.2))
    ]
    for title, desc, border_col, top_pos in layers:
        add_card(s5, Inches(0.8), top_pos, Inches(11.733), Inches(1.25), border_color=border_col)
        tb = s5.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.15), Inches(11.1), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = border_col
        
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(15)
        p_desc.font.color.rgb = COLOR_TEXT
        p_desc.space_before = Pt(4)
        
    s5.notes_slide.notes_text_frame.text = SPEAKER_NOTES[5]

    # -------------------------------------------------------------
    # SLIDE 6 · 1. Isolate
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "1. Isolate: Agent Sandbox & Substrate", "3:25–4:50")
    
    code_s6 = """apiVersion: v1
kind: Pod
metadata:
  name: agent-code-interpreter
spec:
  # Intercepts syscalls in user space:
  runtimeClassName: gvisor

  # Zero Kubernetes cluster credentials:
  automountServiceAccountToken: false

  containers:
  - name: python-sandbox
    image: python:3.11-slim"""
    add_code_block(s6, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.3), code_s6)
    
    tb_c_note = s6.shapes.add_textbox(Inches(0.8), Inches(6.0), Inches(5.7), Inches(0.6))
    p = tb_c_note.text_frame.paragraphs[0]
    p.text = "Default-deny NetworkPolicy keeps the pod away from cluster metadata."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED
    
    # Right Column Cards
    add_card(s6, Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.4), border_color=COLOR_PRIMARY)
    tb_r1 = s6.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(2.0))
    tf = tb_r1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Zero-Trust Execution"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    p1 = tf.add_paragraph()
    p1.text = "• Agent Sandbox (gVisor): Safe execution of LLM-generated Python/Bash code without host kernel exposure."
    p1.font.size = Pt(14)
    p1.font.color.rgb = COLOR_TEXT
    p1.space_before = Pt(6)
    
    p2 = tf.add_paragraph()
    p2.text = "• Kueue & DWS: JIT GPU acquisition when batch jobs run, releasing silicon immediately when finished."
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLOR_TEXT
    p2.space_before = Pt(4)
    
    # Agent Substrate Card
    add_card(s6, Inches(6.8), Inches(4.2), Inches(5.7), Inches(2.2), bg_color=COLOR_BLUE_BOX, border_color=COLOR_PRIMARY)
    tb_r2 = s6.shapes.add_textbox(Inches(7.0), Inches(4.35), Inches(5.3), Inches(1.9))
    tf = tb_r2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚡ Agent Substrate 1.0 (GA / CNCF Sandbox)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    p_sub = tf.add_paragraph()
    p_sub.text = "Snapshots idle agents waiting on models or humans. Frees the pod. Resumes on any warm worker in < 0.5 seconds!"
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = COLOR_TEXT
    p_sub.space_before = Pt(6)

    s6.notes_slide.notes_text_frame.text = SPEAKER_NOTES[6]

    # -------------------------------------------------------------
    # SLIDE 7 · 2. Identify + Guard
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "2. Identify + Guard", "4:50–5:55")
    
    add_card(s7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.8), border_color=COLOR_PRIMARY)
    tb_l7 = s7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.3), Inches(4.4))
    tf = tb_l7.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3 Distinct Identities"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    points = [
        ("The User", "Authenticated session token propagated with every tool action."),
        ("The Agent", "Dedicated Kubernetes SA mapped via Workload Identity Federation (e.g. read BigQuery only, zero static keys)."),
        ("Access", "Short-lived tokens issued per call.")
    ]
    for title, desc in points:
        p_pt = tf.add_paragraph()
        p_pt.text = f"• {title}: {desc}"
        p_pt.font.size = Pt(14)
        p_pt.font.color.rgb = COLOR_TEXT
        p_pt.space_before = Pt(8)
        
    p_audit = tf.add_paragraph()
    p_audit.text = 'Audit log: "invoice-agent, acting for Alice, read table X."'
    p_audit.font.size = Pt(13)
    p_audit.font.italic = True
    p_audit.font.color.rgb = COLOR_MUTED
    p_audit.space_before = Pt(14)
    
    # Right Column: Guardrails + Admission Policy
    add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(2.2), border_color=COLOR_GREEN)
    tb_r7 = s7.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(1.8))
    tf = tb_r7.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2 Enforcement Guardrails"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    
    p1 = tf.add_paragraph()
    p1.text = "• Model Armor: Filters prompts & responses for injection, jailbreaks, and PII."
    p1.font.size = Pt(14)
    p1.font.color.rgb = COLOR_TEXT
    p1.space_before = Pt(6)
    
    p2 = tf.add_paragraph()
    p2.text = "• Admission Policy: Rejects untrusted agent pods before they schedule!"
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLOR_TEXT
    p2.space_before = Pt(4)
    
    code_s7 = """# ValidatingAdmissionPolicy
spec:
  validations:
  - expression: "object.spec.runtimeClassName == 'gvisor'"
    message: "Agent code pods MUST specify gVisor!\""""
    add_code_block(s7, Inches(6.8), Inches(4.0), Inches(5.7), Inches(2.4), code_s7)

    s7.notes_slide.notes_text_frame.text = SPEAKER_NOTES[7]

    # -------------------------------------------------------------
    # SLIDE 8 · 3. Govern Tools
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "3. Govern Tools: The Agent Gateway", "5:55–6:55")
    
    tb_sub8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.5))
    p = tb_sub8.text_frame.paragraphs[0]
    p.text = "Agents never call tools directly. All MCP servers, APIs, and A2A calls pass through the Gateway."
    p.font.size = Pt(15)
    p.font.italic = True
    p.font.color.rgb = COLOR_MUTED
    
    tiles = [
        ("1. Approved Catalog", "Agent Registry acts as enterprise source of truth.", COLOR_PRIMARY, Inches(0.8), Inches(1.9)),
        ("2. RBAC Permissions", "Strict per-agent tool allowlists.", COLOR_ACCENT, Inches(3.8), Inches(1.9)),
        ("3. Loop Breakers", "Rate limiting stops runaway token burn.", COLOR_YELLOW, Inches(6.8), Inches(1.9)),
        ("4. Credential Injection", "Injected at call-time; no API keys in images.", COLOR_GREEN, Inches(9.8), Inches(1.9))
    ]
    for title, desc, border_col, left_pos, top_pos in tiles:
        add_card(s8, left_pos, top_pos, Inches(2.7), Inches(1.8), border_color=border_col)
        tb = s8.shapes.add_textbox(left_pos + Inches(0.15), top_pos + Inches(0.15), Inches(2.4), Inches(1.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = border_col
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = COLOR_TEXT
        p_desc.space_before = Pt(6)
        
    code_s8 = """# NetworkPolicy: The Gateway is mandatory, not optional
kind: NetworkPolicy
spec:
  podSelector: { matchLabels: { app.kubernetes.io/part-of: agent-workload } }
  egress:
  - to: [{ podSelector: { matchLabels: { app: agent-gateway } } }] # Egress locked to gateway only"""
    add_code_block(s8, Inches(0.8), Inches(4.0), Inches(11.733), Inches(2.5), code_s8)

    s8.notes_slide.notes_text_frame.text = SPEAKER_NOTES[8]

    # -------------------------------------------------------------
    # SLIDE 9 · 4. Observe + Evaluate
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "4. Observe + Evaluate", "6:55–7:55")
    
    code_s9 = """# OpenTelemetry GenAI Conventions
attributes:
  gen_ai.system: "gemini"
  gen_ai.request.model: "gemini-1.5-flash"
  gen_ai.agent.name: "invoice-reconciler"
  gen_ai.usage.input_tokens: 1420
  gen_ai.usage.output_tokens: 310
  gen_ai.tool.name: "bigquery_query\""""
    add_code_block(s9, Inches(0.8), Inches(1.6), Inches(5.7), Inches(4.2), code_s9)
    
    tb_c9 = s9.shapes.add_textbox(Inches(0.8), Inches(5.9), Inches(5.7), Inches(0.8))
    p = tb_c9.text_frame.paragraphs[0]
    p.text = "Per-agent cost attribution and automated loop detection come straight out of these telemetry lines."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED
    
    # Right side: Quality Flywheel
    add_card(s9, Inches(6.8), Inches(1.6), Inches(5.7), Inches(4.8), border_color=COLOR_PRIMARY)
    tb_fly = s9.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.4))
    tf = tb_fly.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Quality Flywheel"
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    fly_steps = [
        ("1. Trace", "every agent step with OpenTelemetry"),
        ("2. Score", "live production answers continuously"),
        ("3. Turn failures", "into permanent evaluation test cases"),
        ("4. Gate next release", "on passing eval suite (CI/CD)")
    ]
    for step, desc in fly_steps:
        p_st = tf.add_paragraph()
        p_st.text = f"• {step} {desc}"
        p_st.font.size = Pt(15)
        p_st.font.color.rgb = COLOR_TEXT
        p_st.space_before = Pt(12)

    s9.notes_slide.notes_text_frame.text = SPEAKER_NOTES[9]

    # -------------------------------------------------------------
    # SLIDE 10 · The Golden Path
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "The Golden Path Payoff: AgentApp", "7:55–9:00")
    
    # Left Card
    add_card(s10, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.0), border_color=COLOR_PRIMARY)
    tb_l10 = s10.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(0.6))
    p = tb_l10.text_frame.paragraphs[0]
    p.text = "Developer Writes (~10 lines)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    code_s10 = """apiVersion: platform.k8s.io/v1alpha1
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
    dailyTokens: 500000"""
    add_code_block(s10, Inches(1.0), Inches(2.4), Inches(5.3), Inches(3.6), code_s10)
    
    tb_dev_sub = s10.shapes.add_textbox(Inches(1.0), Inches(6.05), Inches(5.3), Inches(0.4))
    p = tb_dev_sub.text_frame.paragraphs[0]
    p.text = "Scaffolded in seconds via Gemini Code Assist."
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_MUTED
    
    # Right Card
    add_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), border_color=COLOR_GREEN)
    tb_r10 = s10.shapes.add_textbox(Inches(7.0), Inches(1.75), Inches(5.3), Inches(4.7))
    tf = tb_r10.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Platform Deploys Automatically"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    
    plat_items = [
        ("🛡️ gVisor Sandbox", "with warm pool for near-instant execution"),
        ("🔑 Workload Identity", "least-privilege IAM per agent"),
        ("🛡️ Model Armor", "prompt & response inspection"),
        ("🌐 Agent Gateway", "routes & egress lockdown"),
        ("⚡ Agent Substrate", "0.5s snapshot/resume packaging"),
        ("📊 OTel Tracing", "& token budget alerting")
    ]
    for title, desc in plat_items:
        p_item = tf.add_paragraph()
        p_item.text = f"{title}: {desc}"
        p_item.font.size = Pt(14)
        p_item.font.color.rgb = COLOR_TEXT
        p_item.space_before = Pt(8)
        
    p_plat_sub = tf.add_paragraph()
    p_plat_sub.text = "Built with Helm, kro, or Crossplane + Backstage portal."
    p_plat_sub.font.size = Pt(13)
    p_plat_sub.font.color.rgb = COLOR_ACCENT
    p_plat_sub.space_before = Pt(10)

    s10.notes_slide.notes_text_frame.text = SPEAKER_NOTES[10]

    # -------------------------------------------------------------
    # SLIDE 11 · Codelab
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Start Building Today", "9:00–10:00")
    
    # Left Column
    tb_l11 = s11.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(6.0), Inches(4.8))
    tf = tb_l11.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Self-Paced KubeCon Codelab:"
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    tasks = [
        ("🛠️ Build an ADK Agent", "on Google Kubernetes Engine"),
        ("🛡️ Isolate code", "with Agent Sandbox (gVisor)"),
        ("🔑 Wire keyless", "Workload Identity Federation"),
        ("🌐 Enforce egress boundaries", "with NetworkPolicy")
    ]
    for task, desc in tasks:
        p_t = tf.add_paragraph()
        p_t.text = f"• {task} {desc}"
        p_t.font.size = Pt(16)
        p_t.font.color.rgb = COLOR_TEXT
        p_t.space_before = Pt(10)
        
    add_card(s11, Inches(0.8), Inches(4.8), Inches(5.8), Inches(1.6), bg_color=COLOR_BLUE_BOX, border_color=COLOR_PRIMARY)
    tb_booth = s11.shapes.add_textbox(Inches(1.0), Inches(5.0), Inches(5.4), Inches(1.2))
    p = tb_booth.text_frame.paragraphs[0]
    p.text = "📍 Come find me at the Google Cloud booth all week!"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p_booth_sub = tb_booth.text_frame.add_paragraph()
    p_booth_sub.text = "Let's talk about how you're running AI agents on your Kubernetes clusters."
    p_booth_sub.font.size = Pt(14)
    p_booth_sub.font.color.rgb = COLOR_TEXT
    p_booth_sub.space_before = Pt(6)

    # Right Column: Scan box & Thank You
    scan_card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.8), Inches(4.5), Inches(3.2))
    scan_card.fill.solid()
    scan_card.fill.fore_color.rgb = RGBColor(255, 255, 255)
    scan_card.line.color.rgb = RGBColor(226, 232, 240)
    
    tb_scan = s11.shapes.add_textbox(Inches(7.6), Inches(2.0), Inches(4.3), Inches(2.8))
    tf = tb_scan.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "📱"
    p.font.size = Pt(48)
    
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = "SCAN FOR CODELAB"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = RGBColor(15, 23, 42)
    p2.space_before = Pt(4)
    
    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.text = "g.co/cloud/gke-agent-sandbox"
    p3.font.size = Pt(15)
    p3.font.color.rgb = RGBColor(71, 85, 105)
    p3.space_before = Pt(6)
    
    tb_thanks = s11.shapes.add_textbox(Inches(7.5), Inches(5.3), Inches(4.5), Inches(1.0))
    p = tb_thanks.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "Thank You!"
    p.font.name = FONT_HEADING
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    
    s11.notes_slide.notes_text_frame.text = SPEAKER_NOTES[11]

    # Save
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "The_Golden_Path_for_AI_Agents_on_GKE.pptx")
    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path}")

if __name__ == "__main__":
    build_presentation()
