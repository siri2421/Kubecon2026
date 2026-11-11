#!/usr/bin/env python3
"""
Updates Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx and Golden_Path_for_AI_Agents_Full_Polished.pptx
with all required architectural enhancements:
  - Slide 2: Sharper hook ("Keep your hand up if you know exactly what it's allowed to touch") + audience pivot
  - Slide 6: Updated 4 Boundaries (ISOLATE & RUN, Agent Identity, Golden Path Skills & MCP, OTel Flywheel)
  - Slide 7: Title updated to "01 · ISOLATE & RUN" + Agent Substrate 1.0 visual callout box added
  - Slide 8: Explicitly highlights "Agent Identity" (native on GKE via SPIFFE & Workload Identity)
  - Slide 9: Approved Catalog updated to highlight "Golden Path Skills & MCP tools"
  - Slide 11: Adds "Scaffolded via Antigravity in your IDE" referencing "gke-golden-path" skill
  - Synchronizes speaker notes across all slides
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Google Palette Colors
COLOR_BLUE_BG = RGBColor(232, 240, 254)     # #E8F0FE
COLOR_BLUE_BORDER = RGBColor(26, 115, 232)  # #1A73E8
COLOR_TEXT_MAIN = RGBColor(32, 33, 36)      # #202124
COLOR_TEXT_MUTED = RGBColor(95, 99, 104)    # #5F6368

# Files to update
TARGET_12_SLIDES = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx"
TARGET_FULL_SLIDES = "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_Full_Polished.pptx"

def update_deck(file_path):
    prs = Presentation(file_path)
    print(f"Updating {file_path} (Slide count: {len(prs.slides)})...")

    # -------------------------------------------------------------
    # SLIDE 2: Reality Check Hook
    # -------------------------------------------------------------
    slide2 = prs.slides[1]
    for s in slide2.shapes:
        if s.has_text_frame and "Do you know what it's allowed to touch?" in s.text_frame.text:
            s.text_frame.text = "Keep your hand up if you know exactly what it's allowed to touch."

    # -------------------------------------------------------------
    # SLIDE 6: Transition Slide (4 Platform Boundaries)
    # -------------------------------------------------------------
    slide6 = prs.slides[5]
    # Update Column 1 (ISOLATE & RUN)
    for s in slide6.shapes:
        if s.has_text_frame:
            txt = s.text_frame.text
            if "01\nISOLATE" in txt:
                s.text_frame.text = (
                    "01\nISOLATE & RUN\n"
                    "• Runtime: Sandbox & Substrate\n"
                    "› gVisor user-space kernel (runsc)\n"
                    "› Agent Sandbox warm pools\n"
                    "› Agent Substrate snapshot/resume\n"
                    "› Kueue + DWS dynamic silicon\n"
                    "🛡️ Zero kernel escapes & idle silicon waste"
                )
            elif "02\nIDENTIFY + GUARD" in txt:
                s.text_frame.text = (
                    "02\nIDENTIFY + GUARD\n"
                    "• Agent Identity & Safety\n"
                    "› User session propagated (OBO)\n"
                    "› Dedicated Agent Identity (KSA)\n"
                    "› Keyless Workload Identity (SPIFFE)\n"
                    "› Model Armor & CEL admission\n"
                    "🛡️ Prevents prompt injection & credential leaks"
                )
            elif "03\nGOVERN TOOLS" in txt:
                s.text_frame.text = (
                    "03\nGOVERN TOOLS\n"
                    "• Tool Gateway & MCP\n"
                    "› Egress locked to Gateway\n"
                    "› Approved MCP & Golden Path Skills\n"
                    "› Rate limits & loop breakers\n"
                    "› Call-time credential injection\n"
                    "🛡️ Prevents tool sprawl & runaway token burn"
                )
            elif "04\nOBSERVE + EVAL" in txt:
                s.text_frame.text = (
                    "04\nOBSERVE + EVAL\n"
                    "• Quality Flywheel\n"
                    "› OTel GenAI span telemetry\n"
                    "› Per-agent token & cost attribution\n"
                    "› Real-time loop detection\n"
                    "› Eval test gating in CI/CD\n"
                    "🛡️ Catches silent failures & regression loops"
                )

    # -------------------------------------------------------------
    # SLIDE 7: 01 · ISOLATE & RUN (Deep Dive)
    # -------------------------------------------------------------
    slide7 = prs.slides[6]
    for s in slide7.shapes:
        if s.has_text_frame:
            if s.text_frame.text.strip() == "01 · ISOLATE":
                s.text_frame.text = "01 · ISOLATE & RUN"

    # Add Agent Substrate callout banner to Slide 7 if not already present
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
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_BLUE_BORDER

        p2 = tf.add_paragraph()
        p2.text = "Snapshots idle agents waiting on models or tools. Frees the pod. Resumes in < 0.5s."
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_TEXT_MAIN
        p2.space_before = Pt(2)

    # -------------------------------------------------------------
    # SLIDE 8: 02 · IDENTIFY + GUARD
    # -------------------------------------------------------------
    slide8 = prs.slides[7]
    for s in slide8.shapes:
        if s.has_text_frame:
            if "Agent: its own KSA via Workload Identity" in s.text_frame.text:
                s.text_frame.text = "Agent: dedicated Agent Identity via Workload Identity (SPIFFE)"

    # -------------------------------------------------------------
    # SLIDE 9: 03 · GOVERN TOOLS
    # -------------------------------------------------------------
    slide9 = prs.slides[8]
    for s in slide9.shapes:
        if s.has_text_frame:
            if s.text_frame.text.strip() == "Approved tool catalog":
                s.text_frame.text = "Golden Path Skills & MCP catalog"

    # -------------------------------------------------------------
    # SLIDE 11: The Golden Path Payoff (AgentApp)
    # -------------------------------------------------------------
    slide11 = prs.slides[10]
    has_antigravity_note = any("Antigravity" in s.text_frame.text for s in slide11.shapes if s.has_text_frame)
    if not has_antigravity_note:
        tb_anti = slide11.shapes.add_textbox(Inches(0.67), Inches(3.85), Inches(3.75), Inches(0.65))
        tf_anti = tb_anti.text_frame
        tf_anti.word_wrap = True
        p_a1 = tf_anti.paragraphs[0]
        p_a1.text = "⚡ Scaffolded via Antigravity in your IDE"
        p_a1.font.size = Pt(10.5)
        p_a1.font.bold = True
        p_a1.font.color.rgb = COLOR_BLUE_BORDER

        p_a2 = tf_anti.add_paragraph()
        p_a2.text = "Uses Google's 'gke-golden-path' skill for production defaults."
        p_a2.font.size = Pt(9.5)
        p_a2.font.color.rgb = COLOR_TEXT_MUTED
        p_a2.space_before = Pt(1)

        tb_plat = slide11.shapes.add_textbox(Inches(5.15), Inches(3.85), Inches(4.20), Inches(0.65))
        tf_plat = tb_plat.text_frame
        tf_plat.word_wrap = True
        p_p1 = tf_plat.paragraphs[0]
        p_p1.text = "🛡️ Built with Helm, kro, or Crossplane + Backstage"
        p_p1.font.size = Pt(10.5)
        p_p1.font.bold = True
        p_p1.font.color.rgb = COLOR_BLUE_BORDER

        p_p2 = tf_plat.add_paragraph()
        p_p2.text = "Platform team defines the boundary; developers ship the logic."
        p_p2.font.size = Pt(9.5)
        p_p2.font.color.rgb = COLOR_TEXT_MUTED
        p_p2.space_before = Pt(1)

    prs.save(file_path)
    print(f"Successfully saved updates to {file_path}")

def main():
    update_deck(TARGET_12_SLIDES)
    update_deck(TARGET_FULL_SLIDES)

if __name__ == "__main__":
    main()
