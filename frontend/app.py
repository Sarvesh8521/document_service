"""
DocLens — Smart Document Summarizer
Entry point for the Streamlit frontend.

This file does three things only:
1. Page config
2. Session state initialisation
3. Route to the right page based on session state

All logic lives in the imported modules.
Run with: streamlit run frontend/app.py
"""
import streamlit as st
import requests

# ── Page imports ───────────────────────────────────────────────────────────────
from frontend.views.login     import page_login
from frontend.views.signup    import page_signup
from frontend.views.dashboard import page_dashboard
from frontend.views.analyser  import page_analyser
from frontend.themes          import THEMES, get_css

# ── Page config ────────────────────────────────────────────────────────────────
# Must be the very first Streamlit call in the script
st.set_page_config(
    page_title="DocLens",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ─────────────────────────────────────────────────────
# These only get set if the key doesn't already exist.
# That's the critical check — without it every rerun would reset everything.
defaults = {
    "page":               "login",
    "user":               None,
    "selected_category":  None,
    "selected_detail":    "Detailed",
    "result":             None,
    "history":            [],
    "auth_error":         "",
    "auth_success":       "",
    "theme":              "light",
    "results":            [],
    "result_mode":        "individual",
    "summary_mode":       None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HTTP session ───────────────────────────────────────────────────────────────
# Stored in session_state so the login cookie persists across reruns.
# A plain requests.post() would forget the cookie immediately.
if "http_session" not in st.session_state:
    st.session_state.http_session = requests.Session()

# ── Inject theme CSS ───────────────────────────────────────────────────────────
t = THEMES[st.session_state.theme]
st.markdown(get_css(t), unsafe_allow_html=True)

# ── Router ─────────────────────────────────────────────────────────────────────
# This runs on every rerun. Checks two things:
# 1. Is anyone logged in? (user is None or not)
# 2. Which page do they want?
# No logged-in user can never reach dashboard or analyser.
if st.session_state.user is None:
    if st.session_state.page == "signup":
        page_signup()
    else:
        page_login()
else:
    if st.session_state.page == "analyser":
        page_analyser()
    else:
        page_dashboard()
