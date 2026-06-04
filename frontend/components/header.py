import streamlit as st
from frontend.themes import THEMES


def render_header(show_nav: bool = True):
    """
    Renders the top navigation bar.

    show_nav=True  → full nav with Dashboard, Analyser, theme toggle, Sign Out
    show_nav=False → logo only (used on login and signup pages)

    Why a shared component?
    Every page needs a header. Without this, we'd copy-paste the same
    header code into every page file. If we wanted to add a new nav item
    we'd have to update every page. With this, we update one function.
    """
    th = THEMES[st.session_state.theme]

    if show_nav and st.session_state.user:
        # ── Logged-in header: logo left, username right ──
        h1, h2 = st.columns([1, 1])
        with h1:
            st.markdown(
                f'<div style="padding:22px 0 18px 56px;border-bottom:1px solid {th["divider"]};">'
                f'<span class="doclens-logo">Doc<span>Lens</span></span></div>',
                unsafe_allow_html=True,
            )
        with h2:
            st.markdown(
                f'<div style="padding:22px 56px 18px 0;border-bottom:1px solid {th["divider"]};"'
                f'style="display:flex;align-items:center;justify-content:flex-end;">'
                f'<span style="font-size:13px;color:{th["label2"]};">{st.session_state.user["name"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Navigation buttons ──
        n1, n2, n3, n4, n5 = st.columns([2.5, 1, 1, 0.5, 1])
        with n2:
            if st.button("Dashboard", key="nav_dash", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
        with n3:
            if st.button("Analyser", key="nav_analyser", use_container_width=True):
                st.session_state.page = "analyser"
                st.rerun()
        with n4:
            # Theme toggle — just an emoji button
            if st.button(th["toggle_icon"], key="theme_toggle", use_container_width=True):
                st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
                st.rerun()
        with n5:
            if st.button("Sign Out", key="nav_signout", use_container_width=True):
                # Clear all session state — effectively logs the user out
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

    else:
        # ── Auth header: logo + badge + theme toggle ──
        h1, h2, h3 = st.columns([3, 2, 0.4])
        with h1:
            st.markdown(
                f'<div style="padding:22px 0 18px 56px;border-bottom:1px solid {th["divider"]};">'
                f'<span class="doclens-logo">Doc<span>Lens</span></span></div>',
                unsafe_allow_html=True,
            )
        with h2:
            st.markdown(
                f'<div style="padding:22px 0 18px;border-bottom:1px solid {th["divider"]};"'
                f'display:flex;align-items:center;justify-content:flex-end;">'
                f'<span style="font-size:11px;font-weight:500;letter-spacing:1.5px;'
                f'text-transform:uppercase;color:{th["label"]};border:1px solid {th["border"]};"'
                f'padding:5px 12px;border-radius:20px;">AI Document Intelligence</span></div>',
                unsafe_allow_html=True,
            )
        with h3:
            st.markdown(
                f'<div style="padding:16px 0 12px;border-bottom:1px solid {th["divider"]};"></div>',
                unsafe_allow_html=True,
            )
            if st.button(th["toggle_icon"], key="theme_toggle_auth", use_container_width=True):
                st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
                st.rerun()
