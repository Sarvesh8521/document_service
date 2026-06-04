import streamlit as st
from frontend.components.header import render_header
from frontend.components.pdf_report import generate_pdf_report
from frontend.services.api_client import api_summarize
from frontend.themes import THEMES


def page_analyser():
    """
    Analyser page — the core feature of DocLens.
    Three-step flow: upload file → select domain → choose style → analyse.
    Output panel renders when st.session_state.result is populated.
    """
    th = THEMES[st.session_state.theme]
    render_header(show_nav=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="padding:56px 56px 40px;max-width:860px;">
        <div style="font-size:11px;letter-spacing:2.5px;text-transform:uppercase;
            color:{th['eyebrow']};margin-bottom:16px;font-weight:600;">◈ Smart Summarization</div>
        <h1 style="font-weight:800;font-size:52px;line-height:1.05;letter-spacing:-2px;
            color:{th['hero_title']};margin-bottom:18px;">
            Turn any document<br>into <span style="color:{th['hero_accent']}">clear insight</span>
        </h1>
        <p style="font-size:16px;line-height:1.65;color:{th['hero_sub']};max-width:520px;">
            Upload a file, pick a domain, and get a structured AI summary in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.15], gap="large")

    # ── Left: Input controls ───────────────────────────────────────────────────
    with left_col:
        st.markdown('<div style="padding-left:56px">', unsafe_allow_html=True)

        # Step 1 — Upload
        st.markdown('<div class="panel-label">01 — Upload Document</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload",
            type=["pdf", "docx", "csv", "txt"],
            label_visibility="collapsed",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Step 2 — Domain
        st.markdown('<div class="panel-label">02 — Select Domain</div>', unsafe_allow_html=True)
        if st.session_state.selected_category:
            st.markdown(
                f'<div class="selected-cat-label">✓ Selected: {st.session_state.selected_category}</div>',
                unsafe_allow_html=True,
            )

        categories = [
            ("💼", "Sales"),      ("📚", "Education"),  ("⚙️", "Technology"),
            ("⚕️", "Healthcare"), ("⚖️", "Legal"),       ("📊", "Finance"),
            ("🏗️", "Operations"), ("🎯", "Marketing"),   ("🔬", "Research"),
        ]
        for i in range(0, len(categories), 3):
            row  = categories[i:i+3]
            cols = st.columns(3)
            for col, (icon, label) in zip(cols, row):
                with col:
                    if st.button(f"{icon}  {label}", key=f"cat_{label}", use_container_width=True):
                        st.session_state.selected_category = label
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Step 3 — Summary style
        st.markdown('<div class="panel-label">03 — Summary Style</div>', unsafe_allow_html=True)
        opts = ["Brief", "Detailed", "Bullet-only"]
        sel  = st.radio(
            "Style",
            options=opts,
            index=opts.index(st.session_state.selected_detail),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.selected_detail = sel

        st.markdown("<br>", unsafe_allow_html=True)

        # Validation hint
        can_submit = uploaded_file is not None and st.session_state.selected_category is not None
        if not can_submit:
            missing = (["a file"] if not uploaded_file else []) + \
                      (["a domain"] if not st.session_state.selected_category else [])
            st.markdown(
                f'<p style="font-size:12px;color:{th["label"]};margin-bottom:10px;">'
                f'Still need: {", ".join(missing)}</p>',
                unsafe_allow_html=True,
            )

        # Analyse button
        if st.button(
            "◈  Analyse Document",
            disabled=not can_submit,
            use_container_width=True,
            type="primary",
            key="analyse_btn",
        ):
            with st.spinner("Uploading and analysing your document…"):
                try:
                    result = api_summarize(
                        file_name=uploaded_file.name,
                        category=st.session_state.selected_category,
                        detail_level=st.session_state.selected_detail,
                        uploaded_file=uploaded_file,
                    )
                    st.session_state.result = result
                    st.session_state.history.append({
                        "file_name":    uploaded_file.name,
                        "category":     st.session_state.selected_category,
                        "detail_level": st.session_state.selected_detail,
                    })
                except Exception as e:
                    st.error(str(e))

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Right: Output panel ────────────────────────────────────────────────────
    with right_col:
        st.markdown('<div style="padding-right:56px">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Output</div>', unsafe_allow_html=True)

        if st.session_state.result is None:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">◈</div>
                <div class="empty-title">No document analysed yet</div>
                <div class="empty-sub">Upload a file, select a domain, and hit Analyse</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            r = st.session_state.result

            # Meta pills
            st.markdown(
                f'<div class="meta-row">'
                f'<div class="meta-pill accent">◈ {r["category"]}</div>'
                f'<div class="meta-pill">{r["file_name"]}</div>'
                f'<div class="meta-pill">{r["detail_level"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Executive Summary
            st.markdown(
                f'<div class="output-card">'
                f'<div class="output-card-label">Executive Summary</div>'
                f'<div class="output-body">{r["executive_summary"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Key Points
            bullets = "".join([
                f'<div class="bullet-item"><div class="bullet-dot"></div>'
                f'<div class="bullet-text">{p}</div></div>'
                for p in r["key_points"]
            ])
            st.markdown(
                f'<div class="output-card">'
                f'<div class="output-card-label">Key Points</div>{bullets}</div>',
                unsafe_allow_html=True,
            )

            # Action Items + Data Highlights
            c1, c2 = st.columns(2)
            with c1:
                ah = "".join([
                    f'<div class="bullet-item">'
                    f'<div class="bullet-dot" style="background:#7B8CFF"></div>'
                    f'<div class="bullet-text">{a}</div></div>'
                    for a in r["action_items"]
                ])
                st.markdown(
                    f'<div class="output-card">'
                    f'<div class="output-card-label" style="color:#7B8CFF">Action Items</div>{ah}</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                dh = "".join([
                    f'<div class="bullet-item">'
                    f'<div class="bullet-dot" style="background:#F0A04B"></div>'
                    f'<div class="bullet-text">{d}</div></div>'
                    for d in r["data_highlights"]
                ])
                st.markdown(
                    f'<div class="output-card">'
                    f'<div class="output-card-label" style="color:#F0A04B">Data Highlights</div>{dh}</div>',
                    unsafe_allow_html=True,
                )

            # Download button
            pdf = generate_pdf_report(r)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="↓  Download Report (.pdf)",
                data=pdf,
                file_name=f"doclens_{r['file_name'].split('.')[0]}_summary.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)
