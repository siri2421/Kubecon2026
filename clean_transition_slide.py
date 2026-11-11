#!/usr/bin/env python3
"""
Redesigns Slide 6 (The Transition Slide) to a clean, minimalist, high-impact format:
- Replaces dense text blocks with generous whitespace and clear visual hierarchy.
- Focuses on the 4 core actions (ISOLATE, IDENTIFY, GOVERN, OBSERVE) and their flagship technologies.
- Aligns perfectly with Google presentation design guidelines ('less is more').
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Google Theme Colors
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

TRANSITION_NOTES = """TRANSITION (3:30–3:50, 20 sec). Bridge from thesis to technical implementation.

"So how does the platform make 'shift-down' happen in reality?

When an agent runs on GKE, it executes across four continuous runtime boundaries:

1. We ISOLATE execution with gVisor and Agent Substrate.
2. We IDENTIFY the agent with keyless Workload Identity and Model Armor.
3. We GOVERN all tool calls through the Agent Gateway.
4. And we OBSERVE every token with OpenTelemetry to close the quality flywheel.

Let's see how each boundary is implemented with real Kubernetes config—starting with isolation." """

def rebuild_slide_6(slide):
    # Remove existing shapes except title/subtitle if clean, or recreate all shapes
    # First, let's remove existing card shapes (keep slide background and header)
    shapes_to_remove = []
    for s in slide.shapes:
        if s != slide.shapes.title:
            shapes_to_remove.append(s)
            
    for s in shapes_to_remove:
        sp = s._element
        sp.getparent().remove(sp)
        
    # Set Title
    if slide.shapes.title:
        slide.shapes.title.text = "How Shift-Down Happens: 4 Platform Boundaries"
        slide.shapes.title.left = Inches(0.50)
        slide.shapes.title.top = Inches(0.50)
        slide.shapes.title.width = Inches(9.0)
        slide.shapes.title.height = Inches(0.55)
        tf = slide.shapes.title.text_frame
        p = tf.paragraphs[0]
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MAIN
        
    # Subhead (clean single line)
    tb_sub = slide.shapes.add_textbox(Inches(0.50), Inches(1.10), Inches(9.0), Inches(0.35))
    tf_sub = tb_sub.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "From developer intent to production safety on GKE:"
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = COLOR_TEXT_MUTED
    
    # 4 Cards Layout (spacious, balanced)
    col_width = Inches(2.10)
    col_height = Inches(2.70)
    gap = Inches(0.24)
    start_left = Inches(0.48)
    top_pos = Inches(1.75)
    
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
        
        # 1. Number (Large & Bold, e.g. 01)
        p_num = tf.paragraphs[0]
        p_num.text = c["num"]
        p_num.font.size = Pt(28)
        p_num.font.bold = True
        p_num.font.color.rgb = c["border_col"]
        
        # 2. Action Word (e.g. ISOLATE)
        p_act = tf.add_paragraph()
        p_act.text = c["action"]
        p_act.font.size = Pt(15)
        p_act.font.bold = True
        p_act.font.color.rgb = COLOR_TEXT_MAIN
        p_act.space_before = Pt(2)
        
        # 3. Technology Highlight
        p_tech = tf.add_paragraph()
        p_tech.text = c["tech"]
        p_tech.font.size = Pt(11)
        p_tech.font.bold = True
        p_tech.font.color.rgb = c["border_col"]
        p_tech.space_before = Pt(4)
        
        # 4. Divider spacer
        p_div = tf.add_paragraph()
        p_div.text = "────────────"
        p_div.font.size = Pt(8)
        p_div.font.color.rgb = COLOR_ARROW
        p_div.space_before = Pt(4)
        p_div.space_after = Pt(4)
        
        # 5. Clean, punchy bullet points (only 2 lines!)
        for b in c["bullets"]:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.size = Pt(10)
            p_b.font.color.rgb = COLOR_TEXT_MAIN
            p_b.space_before = Pt(3)
            
        # Connecting Arrow between cards
        if i < 3:
            arrow_left = left_pos + col_width + Inches(0.02)
            arrow_top = top_pos + Inches(1.15)
            tb_arr = slide.shapes.add_textbox(arrow_left, arrow_top, gap, Inches(0.40))
            p_arr = tb_arr.text_frame.paragraphs[0]
            p_arr.alignment = PP_ALIGN.CENTER
            p_arr.text = "➔"
            p_arr.font.size = Pt(14)
            p_arr.font.bold = True
            p_arr.font.color.rgb = COLOR_ARROW
            
    # Clean speaker note
    slide.notes_slide.notes_text_frame.text = TRANSITION_NOTES

def main():
    target_12 = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx"
    target_full = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_Full_Polished.pptx"
    
    for path in [target_12, target_full]:
        prs = Presentation(path)
        slide6 = prs.slides[5] # index 5 is Slide 6
        rebuild_slide_6(slide6)
        prs.save(path)
        print(f"Successfully redesigned Slide 6 in: {path}")

if __name__ == "__main__":
    main()
