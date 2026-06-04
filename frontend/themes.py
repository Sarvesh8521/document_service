# ── Theme colour palettes ──────────────────────────────────────────────────────
# Each theme is a dictionary of named colour values.
# Every colour in the app reads from here — nothing is hardcoded elsewhere.
# To add a new theme, just add a new key to this dictionary.

THEMES = {
    "light": {
        "bg":           "#F7F8FC",
        "bg2":          "#FFFFFF",
        "bg3":          "#EEF0F6",
        "border":       "#E2E4EE",
        "border2":      "#CDD0E0",
        "text":         "#0D0D1A",
        "muted":        "#4A4A66",
        "label":        "#9090AA",
        "label2":       "#6B6B88",
        "accent":       "#1A1A2E",
        "accent_bg":    "rgba(26,26,46,0.06)",
        "accent_brd":   "rgba(26,26,46,0.15)",
        "accent_hov":   "#2A2A4E",
        "btn_text":     "#FFFFFF",
        "error_bg":     "#FFF0F0",
        "error_brd":    "#FFCCCC",
        "error_text":   "#CC2222",
        "card_text":    "#2A2A3E",
        "scrollbar":    "#CDD0E0",
        "hero_title":   "#0D0D1A",
        "hero_accent":  "#1A1A2E",
        "hero_sub":     "#6B6B88",
        "eyebrow":      "#6B6B88",
        "divider":      "#E2E4EE",
        "toggle_icon":  "🌙",
        "shadow":       "0 1px 3px rgba(0,0,0,0.08)",
    },
    "dark": {
        "bg":           "#0A0A0F",
        "bg2":          "#0E0E16",
        "bg3":          "#141420",
        "border":       "#1E1E28",
        "border2":      "#2A2A38",
        "text":         "#E8E6E0",
        "muted":        "#8888A0",
        "label":        "#444458",
        "label2":       "#666672",
        "accent":       "#C8F04B",
        "accent_bg":    "rgba(200,240,75,0.07)",
        "accent_brd":   "rgba(200,240,75,0.18)",
        "accent_hov":   "#D4F562",
        "btn_text":     "#0A0A0F",
        "error_bg":     "rgba(255,75,75,0.07)",
        "error_brd":    "rgba(255,75,75,0.18)",
        "error_text":   "#FF8888",
        "card_text":    "#AAAAB8",
        "scrollbar":    "#2A2A38",
        "hero_title":   "#E8E6E0",
        "hero_accent":  "#C8F04B",
        "hero_sub":     "#8888A0",
        "eyebrow":      "#C8F04B",
        "divider":      "#1E1E28",
        "toggle_icon":  "☀️",
        "shadow":       "none",
    },
}


def get_css(t: dict) -> str:
    """
    Takes a theme dictionary and returns a complete CSS string.
    Called once per rerun — Streamlit injects it into the page.
    The f-string substitutes every {t["key"]} with the actual colour value.
    """
    return f"""<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background-color: {t["bg"]} !important;
    color: {t["text"]} !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
.doclens-logo {{ font-weight: 800; font-size: 22px; color: {t["text"]}; }}
.doclens-logo span {{ color: {t["accent"]}; }}

[data-testid="stTextInput"] input {{
    background: {t["bg2"]} !important;
    border: 1.5px solid {t["border"]} !important;
    border-radius: 8px !important;
    color: {t["text"]} !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    box-shadow: {t["shadow"]} !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: {t["accent"]} !important;
    box-shadow: 0 0 0 3px {t["accent_bg"]} !important;
}}
[data-testid="stTextInput"] input::placeholder {{ color: {t["label"]} !important; }}
[data-testid="stTextInput"] label {{
    color: {t["label2"]} !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}}

[data-testid="stButton"] button[kind="primary"] {{
    background: {t["accent"]} !important;
    color: {t["btn_text"]} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 13px 28px !important;
    width: 100% !important;
    transition: background 0.15s !important;
}}
[data-testid="stButton"] button[kind="primary"]:hover {{
    background: {t["accent_hov"]} !important;
}}
[data-testid="stButton"] button[kind="secondary"] {{
    background: {t["bg2"]} !important;
    color: {t["muted"]} !important;
    border: 1.5px solid {t["border"]} !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    padding: 10px 16px !important;
    width: 100% !important;
    box-shadow: {t["shadow"]} !important;
}}
[data-testid="stButton"] button[kind="secondary"]:hover {{
    border-color: {t["accent"]} !important;
    color: {t["text"]} !important;
}}

[data-testid="stFileUploaderDropzone"] {{
    background: {t["bg2"]} !important;
    border: 2px dashed {t["border2"]} !important;
    border-radius: 12px !important;
    padding: 32px 24px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 12px !important;
    box-shadow: {t["shadow"]} !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{ border-color: {t["accent"]} !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] {{
    color: {t["muted"]} !important;
    font-size: 13.5px !important;
    text-align: center !important;
    pointer-events: none !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] span {{ color: {t["muted"]} !important; }}
[data-testid="stFileUploaderDropzone"] button {{
    background: {t["accent"]} !important;
    color: {t["btn_text"]} !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 8px 20px !important;
    position: static !important;
    display: block !important;
    width: auto !important;
}}

[data-testid="stRadio"] > div {{ gap: 8px !important; }}
[data-testid="stRadio"] label {{
    background: {t["bg2"]} !important;
    border: 1.5px solid {t["border"]} !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    color: {t["text"]} !important;
    font-size: 13px !important;
    cursor: pointer !important;
    box-shadow: {t["shadow"]} !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    border-color: {t["accent"]} !important;
    background: {t["accent_bg"]} !important;
    color: {t["accent"]} !important;
}}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {{
    color: {t["text"]} !important;
    font-size: 13px !important;
}}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] {{
    color: {t["text"]} !important;
}}
[data-testid="stRadio"] span {{ color: {t["text"]} !important; }}
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {{ display: none !important; }}

[data-testid="stDownloadButton"] button {{
    background: {t["bg2"]} !important;
    color: {t["accent"]} !important;
    border: 1.5px solid {t["accent_brd"]} !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    width: 100% !important;
    box-shadow: {t["shadow"]} !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    background: {t["accent_bg"]} !important;
    border-color: {t["accent"]} !important;
}}

.output-card {{
    background: {t["bg2"]}; border: 1.5px solid {t["border"]};
    border-radius: 12px; padding: 24px 28px; margin-bottom: 14px;
    box-shadow: {t["shadow"]};
}}
.output-card-label {{
    font-size: 10px; font-weight: 700; letter-spacing: 2.5px;
    text-transform: uppercase; color: {t["accent"]}; margin-bottom: 12px;
}}
.output-body {{ font-size: 15px; line-height: 1.7; color: {t["card_text"]}; }}
.bullet-item {{
    display: flex; gap: 12px; padding: 9px 0;
    border-bottom: 1px solid {t["border"]}; align-items: flex-start;
}}
.bullet-item:last-child {{ border-bottom: none; }}
.bullet-dot {{ width: 6px; height: 6px; border-radius: 50%; background: {t["accent"]}; flex-shrink: 0; margin-top: 8px; }}
.bullet-text {{ font-size: 14px; line-height: 1.6; color: {t["card_text"]}; }}
.meta-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 24px; }}
.meta-pill {{ font-size: 12px; color: {t["label2"]}; background: {t["bg3"]}; border: 1px solid {t["border"]}; border-radius: 20px; padding: 4px 13px; }}
.meta-pill.accent {{ color: {t["accent"]}; background: {t["accent_bg"]}; border-color: {t["accent_brd"]}; }}
.empty-state {{ background: {t["bg2"]}; border: 1.5px dashed {t["border2"]}; border-radius: 12px; padding: 60px 32px; text-align: center; }}
.empty-icon {{ font-size: 36px; margin-bottom: 16px; opacity: 0.25; }}
.empty-title {{ font-weight: 700; font-size: 16px; color: {t["label2"]}; margin-bottom: 8px; }}
.empty-sub {{ font-size: 13px; color: {t["label"]}; }}
.panel-label {{ font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: {t["label"]}; margin-bottom: 16px; }}
.selected-cat-label {{ font-size: 12.5px; color: {t["accent"]}; margin-bottom: 6px; font-weight: 500; }}
.section-divider {{ height: 1px; background: {t["divider"]}; margin: 0 56px 48px; }}
.stat-card {{ background: {t["bg2"]}; border: 1.5px solid {t["border"]}; border-radius: 12px; padding: 20px 24px; box-shadow: {t["shadow"]}; }}
.stat-number {{ font-weight: 800; font-size: 36px; color: {t["accent"]}; line-height: 1; }}
.stat-label {{ font-size: 11px; color: {t["label"]}; margin-top: 6px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }}
.history-row {{ display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; background: {t["bg2"]}; border: 1px solid {t["border"]}; border-radius: 10px; margin-bottom: 8px; box-shadow: {t["shadow"]}; }}
.history-filename {{ font-size: 14px; color: {t["text"]}; font-weight: 500; }}
.history-meta {{ font-size: 12px; color: {t["label"]}; margin-top: 3px; }}
.history-badge {{ font-size: 11px; color: {t["accent"]}; background: {t["accent_bg"]}; border: 1px solid {t["accent_brd"]}; border-radius: 20px; padding: 3px 10px; font-weight: 600; }}
.auth-card {{ background: {t["bg2"]}; border: 1.5px solid {t["border"]}; border-radius: 16px; padding: 40px 40px 36px; box-shadow: {t["shadow"]}; }}
.auth-title {{ font-weight: 800; font-size: 26px; letter-spacing: -0.5px; color: {t["text"]}; margin-bottom: 6px; }}
.auth-sub {{ font-size: 14px; color: {t["label2"]}; margin-bottom: 28px; line-height: 1.5; }}
.auth-divider {{ display: flex; align-items: center; gap: 12px; margin: 20px 0; color: {t["label"]}; font-size: 12px; }}
.auth-divider::before, .auth-divider::after {{ content: ''; flex: 1; height: 1px; background: {t["border"]}; }}
.error-msg {{ background: {t["error_bg"]}; border: 1px solid {t["error_brd"]}; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: {t["error_text"]}; margin-bottom: 12px; }}
.success-msg {{ background: {t["accent_bg"]}; border: 1px solid {t["accent_brd"]}; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: {t["accent"]}; margin-bottom: 12px; }}

::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: {t["bg"]}; }}
::-webkit-scrollbar-thumb {{ background: {t["scrollbar"]}; border-radius: 4px; }}
</style>"""
