import streamlit as st
from frontend.components.header import render_header
from frontend.services.api_client import api_login
from frontend.themes import THEMES


def page_login():
    """
    Login page — hero section on the left, login form on the right.
    On successful login: sets session_state.user and redirects to dashboard.
    On failure: shows the error message from the API.
    """
    render_header(show_nav=False)
    th = THEMES[st.session_state.theme]

    hero_col, _, form_col = st.columns([1.2, 0.2, 1])

    with hero_col:
        st.markdown(f"""
        <div style="padding:80px 0 0 56px;">
            <div style="font-size:11px;letter-spacing:2.5px;text-transform:uppercase;
                color:{th['eyebrow']};margin-bottom:20px;font-weight:600;">
                ◈ AI Document Intelligence
            </div>
            <div style="font-weight:800;font-size:48px;line-height:1.05;
                letter-spacing:-2px;color:{th['hero_title']};margin-bottom:20px;">
                Turn documents<br>into <span style="color:{th['hero_accent']}">insight</span>
            </div>
            <div style="font-size:15px;line-height:1.7;color:{th['hero_sub']};
                max-width:400px;margin-bottom:40px;">
                Upload any PDF, Word doc, CSV, or text file and get a structured
                AI-generated summary tailored to your domain — in seconds.
            </div>
            <div style="display:flex;flex-direction:column;gap:12px;max-width:320px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="width:32px;height:32px;border-radius:8px;
                        background:{th['accent_bg']};border:1px solid {th['accent_brd']};
                        display:flex;align-items:center;justify-content:center;font-size:14px;">◈</div>
                    <span style="font-size:14px;color:{th['muted']};">Domain-aware AI summarization</span>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="width:32px;height:32px;border-radius:8px;
                        background:{th['accent_bg']};border:1px solid {th['accent_brd']};
                        display:flex;align-items:center;justify-content:center;font-size:14px;">◈</div>
                    <span style="font-size:14px;color:{th['muted']};">PDF, DOCX, CSV and TXT support</span>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="width:32px;height:32px;border-radius:8px;
                        background:{th['accent_bg']};border:1px solid {th['accent_brd']};
                        display:flex;align-items:center;justify-content:center;font-size:14px;">◈</div>
                    <span style="font-size:14px;color:{th['muted']};">Downloadable PDF report</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with form_col:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-card"><div class="auth-title">Welcome back</div>'
            '<div class="auth-sub">Sign in to access your documents and summaries.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.session_state.auth_error:
            st.markdown(f'<div class="error-msg">&#x26A0; {st.session_state.auth_error}</div>', unsafe_allow_html=True)
        if st.session_state.auth_success:
            st.markdown(f'<div class="success-msg">&#x2713; {st.session_state.auth_success}</div>', unsafe_allow_html=True)

        email    = st.text_input("Email",    placeholder="you@example.com",      key="login_email")
        password = st.text_input("Password", placeholder="Enter your password",  key="login_password", type="password")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Sign In", type="primary", key="login_btn", use_container_width=True):
            try:
                user = api_login(email, password)
                st.session_state.user         = user
                st.session_state.auth_error   = ""
                st.session_state.auth_success = ""
                st.session_state.page         = "dashboard"
                st.rerun()
            except Exception as e:
                st.session_state.auth_error = str(e)
                st.rerun()

        st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)

        if st.button("Create an account", key="goto_signup", use_container_width=True):
            st.session_state.auth_error = ""
            st.session_state.page       = "signup"
            st.rerun()
