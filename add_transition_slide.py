#!/usr/bin/env python3
"""
Adds a dedicated transition slide between Slide 5 ("Shift down") and Slide 6 ("01 · ISOLATE")
explaining how the platform transitions untrusted agent code into a governed production runtime
via the 4 Platform Boundaries.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Google Theme Colors matching Golden Path for AI Agents.pptx
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
COLOR_ARROW = RGBColor(128, 134, 139)       # #80868B

TRANSITION_NOTES = """TRANSITION (3:30–3:50, 20 sec). Bridge from thesis to technical implementation.

"So how does a platform team actually make 'shift-down' happen in reality?

When an autonomous agent runs on GKE, it doesn't get unrestricted access to the cluster. The platform places four continuous runtime boundaries around it:

First, we ISOLATE execution in gVisor sandboxes so dynamic code never touches the node.
Second, we IDENTIFY the agent with keyless Workload Identity and screen its prompts with Model Armor.
Third, we GOVERN every external tool call through a single gateway with circuit breakers.
And fourth, we OBSERVE every token and step with OpenTelemetry to close the quality flywheel.

Let's see how each boundary is implemented with real Kubernetes config—starting with isolation." """

CARDS_DATA = [
    {
        "num": "01",
        "title": "ISOLATE",
        "phase": "Runtime Sandbox",
        "bg_col": COLOR_BLUE_BG,
        "border_col": COLOR_BLUE_BORDER,
        "bullets": [
            "gVisor user-space kernel (runsc)",
            "Zero KSA token mounted",
            "Near-instant warm pool",
            "Kueue + DWS dynamic GPUs"
        ],
        "blocks": "Prevents node kernel escapes & idle silicon waste"
    },
    {
        "num": "02",
        "title": "IDENTIFY + GUARD",
        "phase": "Access & Safety",
        "bg_col": COLOR_GREEN_BG,
        "border_col": COLOR_GREEN_BORDER,
        "bullets": [
            "User session propagated",
            "Dedicated KSA per agent",
            "Keyless Workload Identity",
            "Model Armor & CEL admission"
        ],
        "blocks": "Prevents prompt injection & credential theft"
    },
    {
        "num": "03",
        "title": "GOVERN TOOLS",
        "phase": "Tool Gateway",
        "bg_col": COLOR_YELLOW_BG,
        "border_col": COLOR_YELLOW_BORDER,
        "bullets": [
            "Egress locked to Gateway",
            "Approved MCP & API catalog",
            "Rate limits & loop breakers",
            "Call-time credential injection"
        ],
        "blocks": "Prevents tool sprawl & runaway token burn"
    },
    {
        "num": "04",
        "title": "OBSERVE + EVAL",
        "phase": "Quality Flywheel",
        "bg_col": COLOR_RED_BG,
        "border_col": COLOR_RED_BORDER,
        "bullets": [
            "OTel GenAI span telemetry",
            "Token & latency attribution",
            "Real-time loop detection",
            "Eval test gating in CI/CD"
        ],
        "blocks": "Catches silent failures & regression loops"
    }
]

def build_transition_slide(prs, insert_index=5):
    """Creates the transition slide and inserts it at insert_index."""
    layout = prs.slide_layouts[1] # TITLE layout
    slide = prs.slides.add_slide(layout)
    
    # 1. Slide Title
    if slide.shapes.title:
        slide.shapes.title.text = "How Shift-Down Happens: 4 Platform Boundaries"
        slide.shapes.title.left = Inches(0.50)
        slide.shapes.title.top = Inches(0.45)
        slide.shapes.title.width = Inches(9.0)
        slide.shapes.title.height = Inches(0.55)
        tf = slide.shapes.title.text_frame
        p = tf.paragraphs[0]
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MAIN
        
    # 2. Subtitle / Thesis statement
    tb_sub = slide.shapes.add_textbox(Inches(0.50), Inches(1.05), Inches(9.0), Inches(0.40))
    tf_sub = tb_sub.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "As an agent executes, GKE enforces four continuous lifecycle boundaries:"
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = COLOR_TEXT_MUTED
    
    # 3. 4 Columns
    col_width = Inches(2.10)
    col_height = Inches(3.40)
    gap = Inches(0.22)
    start_left = Inches(0.45)
    top_pos = Inches(1.50)
    
    for i, c in enumerate(CARDS_DATA):
        left_pos = start_left + i * (col_width + gap)
        
        # Rounded Card
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, col_width, col_height)
        card.fill.solid()
        card.fill.fore_color.rgb = c["bg_col"]
        card.line.color.rgb = c["border_col"]
        card.line.width = Pt(1.5)
        
        # Text Frame
        tb = slide.shapes.add_textbox(left_pos + Inches(0.08), top_pos + Inches(0.08), col_width - Inches(0.16), col_height - Inches(0.16))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.02)
        tf.margin_left = Inches(0.02)
        tf.margin_right = Inches(0.02)
        tf.margin_bottom = Inches(0.02)
        
        # Number Badge (e.g. 01)
        p_num = tf.paragraphs[0]
        p_num.text = c["num"]
        p_num.font.size = Pt(18)
        p_num.font.bold = True
        p_num.font.color.rgb = c["border_col"]
        
        # Pillar Title (e.g. ISOLATE)
        p_title = tf.add_paragraph()
        p_title.text = c["title"]
        p_title.font.size = Pt(13)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_TEXT_MAIN
        p_title.space_before = Pt(2)
        
        # Phase Tag
        p_phase = tf.add_paragraph()
        p_phase.text = f"• {c['phase']}"
        p_phase.font.size = Pt(10)
        p_phase.font.bold = True
        p_phase.font.color.rgb = c["border_col"]
        p_phase.space_before = Pt(2)
        
        # Key Mechanisms (bullet points)
        for bullet in c["bullets"]:
            p_b = tf.add_paragraph()
            p_b.text = f"› {bullet}"
            p_b.font.size = Pt(9.5)
            p_b.font.color.rgb = COLOR_TEXT_MAIN
            p_b.space_before = Pt(3)
            
        # Protection Summary
        p_blk = tf.add_paragraph()
        p_blk.text = f"🛡️ {c['blocks']}"
        p_blk.font.size = Pt(9)
        p_blk.font.italic = True
        p_blk.font.color.rgb = COLOR_TEXT_MUTED
        p_blk.space_before = Pt(6)
        
        # Connecting Arrow between cards
        if i < 3:
            arrow_left = left_pos + col_width + Inches(0.02)
            arrow_top = top_pos + Inches(1.50)
            tb_arr = slide.shapes.add_textbox(arrow_left, arrow_top, gap, Inches(0.35))
            p_arr = tb_arr.text_frame.paragraphs[0]
            p_arr.alignment = PP_ALIGN.CENTER
            p_arr.text = "➔"
            p_arr.font.size = Pt(14)
            p_arr.font.bold = True
            p_arr.font.color.rgb = COLOR_ARROW
            
    # Speaker Notes
    slide.notes_slide.notes_text_frame.text = TRANSITION_NOTES
    
    # Move slide from end to insert_index
    sldIdLst = prs.slides._sldIdLst
    slide_elem = sldIdLst[-1]
    sldIdLst.insert(insert_index, slide_elem)
    
    return slide

def main():
    base_11_path = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_KubeCon_11Slides.pptx"
    out_12_path = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx"
    
    prs = Presentation(base_11_path)
    build_transition_slide(prs, insert_index=5)
    prs.save(out_12_path)
    print(f"Successfully generated 12-slide deck with transition slide: {out_12_path}")
    
    # Also update full polished deck
    full_path = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_Full_Polished.pptx"
    prs_full = Presentation(full_path)
    build_transition_slide(prs_full, insert_index=5)
    prs_full.save(full_path)
    print(f"Successfully updated full 60-slide deck with transition slide: {full_path}")

if __name__ == "__main__":
    main()
