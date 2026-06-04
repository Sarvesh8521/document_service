import streamlit as st
from frontend.components.header import render_header
from frontend.services.api_client import api_signup


def page_signup():
    """
    Signup page — collects name, email, password and creates an account.
    On success: sets session_state.user and redirects to dashboard.
    On failure: shows field-level errors from Django.
    """
    render_header(show_nav=False)

    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown("<div style='height:52px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="auth-card">'
            '<div class="auth-title">Create account</div>'
            '<div class="auth-sub">Join DocLens. Your documents stay private to you.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.session_state.auth_error:
            st.markdown(f'<div class="error-msg">&#x26A0; {st.session_state.auth_error}</div>', unsafe_allow_html=True)

        name     = st.text_input("Full Name",         placeholder="Dev Aggarwal",       key="signup_name")
        email    = st.text_input("Email",             placeholder="you@example.com",    key="signup_email")
        password = st.text_input("Password",          placeholder="Min. 6 characters",  key="signup_password", type="password")
        confirm  = st.text_input("Confirm Password",  placeholder="Repeat password",    key="signup_confirm",  type="password")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Create Account", type="primary", key="signup_btn", use_container_width=True):
            try:
                user = api_signup(name, email, password, confirm)
                st.session_state.user         = user
                st.session_state.auth_error   = ""
                st.session_state.auth_success = f"Account created! Welcome, {user['name']}."
                st.session_state.page         = "dashboard"
                st.rerun()
            except Exception as e:
                st.session_state.auth_error = str(e)
                st.rerun()

        st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)

        if st.button("Already have an account? Sign in", key="goto_login", use_container_width=True):
            st.session_state.auth_error = ""
            st.session_state.page       = "login"
            st.rerun()
