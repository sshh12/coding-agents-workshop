#!/usr/bin/env python3
"""Compose the race side-by-side video with timestamped narrator callouts.

Usage:
    # 1. Record screen recordings of each agent session as A.mov and B.mov
    # 2. Extract frames (1 per second):
    mkdir -p /tmp/race-frames/A /tmp/race-frames/B
    ffmpeg -i A.mov -vf "fps=1" /tmp/race-frames/A/frame_%03d.png
    ffmpeg -i B.mov -vf "fps=1" /tmp/race-frames/B/frame_%03d.png

    # 3. Generate annotated frames:
    python3 race-video-edit.py

    # 4. Assemble into video (0.7x speed):
    ffmpeg -y -framerate 1 -i /tmp/race-frames/out/frame_%03d.png \
        -c:v libx264 -crf 23 -pix_fmt yuv420p -r 30 -an /tmp/race-normal.mp4
    ffmpeg -y -i /tmp/race-normal.mp4 -vf "setpts=1.43*PTS" \
        -c:v libx264 -crf 23 -an race-side-by-side.mp4

Requirements: pip install Pillow
"""

import os
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths
A_DIR = "/tmp/race-frames/A"
B_DIR = "/tmp/race-frames/B"
OUT_DIR = "/tmp/race-frames/out"
os.makedirs(OUT_DIR, exist_ok=True)

# Frame counts
A_COUNT = len([f for f in os.listdir(A_DIR) if f.endswith(".png")])
B_COUNT = len([f for f in os.listdir(B_DIR) if f.endswith(".png")])
TOTAL = max(A_COUNT, B_COUNT)

# Dimensions
VW, VH = 1224, 1372  # each video panel
HEADER_H = 90
CALLOUT_H = 76
CANVAS_W = VW * 2
CANVAS_H = HEADER_H + CALLOUT_H + VH  # 1538 (even, required by libx264)


# ── Colors ──────────────────────────────────────────────────────────────────

BG = (17, 17, 17)
HEADER_BG = (17, 17, 17)
CALLOUT_BG = (30, 30, 30)
WHITE = (250, 250, 250)
ACCENT = (100, 200, 255)


# ── Fonts ───────────────────────────────────────────────────────────────────

def load_font(size):
    for path in [
        "/System/Library/Fonts/SFCompact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

font_header = load_font(48)
font_callout = load_font(34)


# ── Callouts ────────────────────────────────────────────────────────────────
# (start_sec, end_sec, text)
# Single narrative stream describing the key thing happening across both panels.
# Edit these to match your specific race recording.

CALLOUTS = [
    (1,  2,  "Both agents receive the same prompt: add experiment tagging"),
    (3,  4,  "A reads config.py + tests (1+1=2)  \u2022  B auto-loads 50-line CLAUDE.md with repo map"),
    (5,  6,  "A reads requirements.txt \u2014 Pydantic installed, zero schemas  \u2022  B spawns exploration sub-agent"),
    (7,  8,  "A: \"I have a clear picture\" \u2014 never searched for 'tags', never read h.py"),
    (9,  11, "A dumps ExperimentTag model into the 600-line god file (app.py)"),
    (12, 13, "B finds tags/ directory \u2014 CLAUDE.md told it exactly where to look"),
    (14, 16, "A writes tag endpoints \u2014 never calls sanitize()  \u2022  B reads pre-built tag model + schema"),
    (17, 20, "A wires up template in stuff/ with inline CSS  \u2022  B reads experiment detail template"),
    (21, 25, "A finishes template \u2014 pill badges, more inline CSS added to the god file"),
    (26, 27, "A rewrites entire test file \u2014 3 placeholders replaced with 11 self-written tests"),
    (28, 29, "A: test attempt #1 fails (python not found), #2 fails (pytest not installed)"),
    (30, 35, "A: pip install pytest httpx \u2014 installing its own test deps  \u2022  B still exploring (33 parallel reads)"),
    (36, 37, "A tests finally running on third attempt"),
    (38, 42, "A done in 38s \u2014 11 self-graded tests pass, 3 files changed, sanitize() copied into new code"),
    (43, 46, "A is frozen on last frame \u2014 it's done. B is still reading the codebase thoroughly"),
    (47, 50, "B exploration complete: 33 tool calls, 45k tokens. Full codebase context acquired"),
    (51, 57, "B synthesizing what it learned \u2014 re-reading key files for implementation"),
    (58, 60, "B: \"The TODO comment spells out exactly what's needed\" \u2014 the money quote"),
    (61, 63, "B implements create_tag \u2014 one file, Pydantic schemas, proper 404/409/201 status codes"),
    (64, 64, "B removes #noqa lint comment \u2014 TagCreate is now used, suppression unnecessary"),
    (65, 66, "B: python not found (same hiccup as A), retries with python3"),
    (67, 68, "B: 6 tag tests pass \u2014 including 4 pre-written tests that were failing before"),
    (69, 72, "All 28 tests pass. Ruff clean. One file changed. Done."),
    (73, 76, "Same model. Same prompt. A: 3 files, self-graded. B: 1 file, 28 verified tests."),
]


# ── Helpers ─────────────────────────────────────────────────────────────────

def get_callout(sec):
    for start, end, text in CALLOUTS:
        if start <= sec <= end:
            return text
    return ""


def center_text(draw, text, font, y, width, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, fill=fill, font=font)


# ── Build frames ────────────────────────────────────────────────────────────

for sec in range(1, TOTAL + 1):
    # Load video frames (clamp A to last frame if past its duration)
    a_idx = min(sec, A_COUNT)
    b_idx = min(sec, B_COUNT)

    a_path = os.path.join(A_DIR, f"frame_{a_idx:03d}.png")
    b_path = os.path.join(B_DIR, f"frame_{b_idx:03d}.png")

    a_frame = Image.open(a_path).resize((VW, VH))
    b_frame = Image.open(b_path).resize((VW, VH))

    # Create canvas
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(canvas)

    # Header bar
    draw.rectangle([(0, 0), (CANVAS_W, HEADER_H)], fill=HEADER_BG)

    # "A — The Mess" on left half
    a_label = "A \u2014 The Mess"
    a_bbox = draw.textbbox((0, 0), a_label, font=font_header)
    a_tw = a_bbox[2] - a_bbox[0]
    draw.text(((VW - a_tw) // 2, 18), a_label, fill=WHITE, font=font_header)

    # "B — Optimized" on right half
    b_label = "B \u2014 Optimized"
    b_bbox = draw.textbbox((0, 0), b_label, font=font_header)
    b_tw = b_bbox[2] - b_bbox[0]
    draw.text((VW + (VW - b_tw) // 2, 18), b_label, fill=WHITE, font=font_header)

    # Divider line under header
    draw.line([(0, HEADER_H - 1), (CANVAS_W, HEADER_H - 1)], fill=(50, 50, 50))

    # Callout bar
    draw.rectangle([(0, HEADER_H), (CANVAS_W, HEADER_H + CALLOUT_H)], fill=CALLOUT_BG)
    callout = get_callout(sec)
    if callout:
        center_text(draw, callout, font_callout, HEADER_H + 18, CANVAS_W, ACCENT)

    # Paste video frames
    canvas.paste(a_frame, (0, HEADER_H + CALLOUT_H))
    canvas.paste(b_frame, (VW, HEADER_H + CALLOUT_H))

    # Vertical divider between panels
    draw.line([(VW, HEADER_H + CALLOUT_H), (VW, CANVAS_H)], fill=(50, 50, 50), width=2)

    canvas.save(os.path.join(OUT_DIR, f"frame_{sec:03d}.png"))
    print(f"  frame {sec}/{TOTAL}", end="\r")

print(f"\nDone. {TOTAL} frames written to {OUT_DIR}")
print("Next: assemble with ffmpeg (see docstring for commands)")
