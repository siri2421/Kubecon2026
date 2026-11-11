#!/usr/bin/env python3
"""
Applies exact typography rules across all slides in KubeCon decks:
  - Font family: Google Sans for all slide text (code blocks preserve code font)
  - Headings: Google Sans, 18 pt (Bold)
  - Subheadings: Google Sans, 12 pt (Bold)
  - All other text / body: Google Sans, 12 pt
"""

from pptx import Presentation
from pptx.util import Pt

TARGET_DECKS = [
    "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_KubeCon_12Slides.pptx",
    "/usr/local/google/home/ksiri/Documents/kubecon/Golden_Path_for_AI_Agents_Full_Polished.pptx"
]

FONT_NAME = "Google Sans"

# Headings across all 12 slides (exact matches)
HEADINGS = {
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

# Subheadings across all 12 slides
SUBHEADINGS = {
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

def is_code_shape(slide_idx, shape_idx, shape):
    """Accurately identifies code shapes on each slide."""
    if not shape.has_text_frame:
        return False
    text = shape.text_frame.text.strip()
    if not text:
        return False
    
    # Specific shape indices on code slides
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

def apply_typography_to_deck(prs_path):
    print(f"\nProcessing presentation: {prs_path}")
    prs = Presentation(prs_path)
    
    # Process the 12 main talk slides
    num_slides = min(12, len(prs.slides))
    for slide_idx in range(num_slides):
        slide = prs.slides[slide_idx]
        
        for shape_idx, shape in enumerate(slide.shapes):
            if not shape.has_text_frame:
                continue
                
            tf = shape.text_frame
            full_txt = tf.text.strip()
            
            # Skip page numbers
            if full_txt == "‹#›" or not full_txt:
                continue
                
            # If shape contains code, ensure JetBrains Mono and do not modify to Google Sans
            if is_code_shape(slide_idx, shape_idx, shape):
                for p in tf.paragraphs:
                    if p.font.name is None:
                        p.font.name = "JetBrains Mono"
                    for r in p.runs:
                        if r.font.name is None:
                            r.font.name = "JetBrains Mono"
                        if r.font.size is None:
                            r.font.size = Pt(9)
                continue
                
            for p_idx, p in enumerate(tf.paragraphs):
                p_txt = p.text.strip()
                if not p_txt:
                    continue
                
                # Determine hierarchy: Heading vs Subheading vs Body
                is_heading = (p_txt in HEADINGS or shape == slide.shapes.title)
                is_subheading = (
                    p_txt in SUBHEADINGS or
                    any(p_txt.startswith(x) for x in [
                        "01 ·", "02 ·", "03 ·", "04 ·",
                        "⚡ Agent Substrate", "⚡ Scaffolded", "🛡️ Built with",
                        "Asking every team"
                    ])
                )
                
                # Target styling
                target_font = FONT_NAME
                if is_heading:
                    target_size = Pt(18)
                    target_bold = True
                elif is_subheading:
                    target_size = Pt(12)
                    target_bold = True
                else:
                    # All body/general text
                    target_size = Pt(12)
                    target_bold = False
                
                # Apply at paragraph level
                p.font.name = target_font
                p.font.size = target_size
                if is_heading or is_subheading:
                    p.font.bold = True
                
                # Apply at run level (PowerPoint OpenXML requires run-level attributes)
                for r in p.runs:
                    r.font.name = target_font
                    r.font.size = target_size
                    if is_heading or is_subheading:
                        r.font.bold = True
                    else:
                        # For body text, preserve bold if specific labels like "User:", "Agent:", "•"
                        # were selectively bolded, otherwise set to False
                        if r.font.bold is not None and r.font.bold and any(p_txt.startswith(lbl) for lbl in ["User:", "Agent:", "Access:", "•"]):
                            r.font.bold = True
                        else:
                            r.font.bold = False

    prs.save(prs_path)
    print(f"Successfully applied Google Sans typography to {prs_path}")

def main():
    for deck in TARGET_DECKS:
        apply_typography_to_deck(deck)

if __name__ == "__main__":
    main()
