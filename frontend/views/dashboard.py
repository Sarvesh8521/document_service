import streamlit as st
from frontend.components.header import render_header
from frontend.themes import THEMES


def page_dashboard():
    """
    Dashboard page — shows stats, document history, and quick actions.
    All data comes from st.session_state which is populated at login
    and updated every time a document is analysed.
    """
    th = THEMES[st.session_state.theme]
    render_header(show_nav=True)

    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

    # ── Welcome section ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="padding:0 56px 40px;">
        <div style="font-size:11px;letter-spacing:2.5px;text-transform:uppercase;
            color:{th['eyebrow']};margin-bottom:12px;font-weight:600;">◈ Your Dashboard</div>
        <div style="font-weight:800;font-size:36px;letter-spacing:-1px;
            color:{th['text']};margin-bottom:8px;">
            Hello, {st.session_state.user['name'].split()[0]}
        </div>
        <div style="font-size:15px;color:{th['muted']};">
            Here is an overview of your document activity.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats cards ────────────────────────────────────────────────────────────
    history          = st.session_state.history
    cats_with_data   = list(set(h["category"] for h in history if h.get("category")))
    last_domain      = history[-1]["category"] if history and history[-1].get("category") else "—"
    last_file_raw    = history[-1]["file_name"] if history else "—"
    last_file        = last_file_raw[:14] + "…" if len(last_file_raw) > 14 else last_file_raw

    s1, s2, s3, s4 = st.columns(4)
    stats = [
        (str(len(history)),        "Documents Analysed"),
        (str(len(cats_with_data)), "Domains Used"),
        (last_domain,              "Last Domain"),
        (last_file,                "Last File"),
    ]
    for col, (num, label) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(
                f'<div class="stat-card" style="margin:0 8px;">'
                f'<div class="stat-number">{num}</div>'
                f'<div class="stat-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown(f'<div style="height:1px;background:{th["divider"]};margin:0 56px 40px;"></div>', unsafe_allow_html=True)

    # ── History + Quick Actions ────────────────────────────────────────────────
    h_col, a_col = st.columns([1.6, 1], gap="large")

    with h_col:
        st.markdown('<div style="padding-left:56px">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Recent Documents</div>', unsafe_allow_html=True)

        if not history:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">◈</div>
                <div class="empty-title">No documents yet</div>
                <div class="empty-sub">Head to the Analyser to process your first document</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for item in reversed(history[-8:]):
                badge = f'<div class="history-badge">{item["category"]}</div>' if item.get("category") else ""
                meta  = f'{item["detail_level"]} summary' if item.get("detail_level") else "Previously uploaded"
                st.markdown(
                    f'<div class="history-row">'
                    f'<div><div class="history-filename">{item["file_name"]}</div>'
                    f'<div class="history-meta">{meta}</div></div>'
                    f'{badge}</div>',
                    unsafe_allow_html=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)

    with a_col:
        st.markdown('<div style="padding-right:56px">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Quick Actions</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="background:{th["bg2"]};border:1.5px solid {th["border"]};'
            f'border-radius:12px;padding:24px 24px 20px;margin-bottom:14px;box-shadow:{th["shadow"]};">'
            f'<div style="font-weight:700;font-size:15px;color:{th["text"]};margin-bottom:6px;">Analyse a new document</div>'
            f'<div style="font-size:13px;color:{th["label"]};line-height:1.6;">Upload a file and get an AI summary instantly.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if st.button("◈  Go to Analyser", type="primary", key="dash_to_analyser", use_container_width=True):
            st.session_state.page = "analyser"
            st.rerun()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        st.markdown(
            f'<div style="background:{th["bg2"]};border:1.5px solid {th["border"]};'
            f'border-radius:12px;padding:20px 24px;box-shadow:{th["shadow"]};">'
            f'<div style="font-size:10px;letter-spacing:1.5px;text-transform:uppercase;'
            f'color:{th["label"]};margin-bottom:10px;font-weight:700;">Account</div>'
            f'<div style="font-size:14px;color:{th["text"]};margin-bottom:4px;font-weight:500;">'
            f'{st.session_state.user["name"]}</div>'
            f'<div style="font-size:12px;color:{th["label"]};">{st.session_state.user["email"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
