import streamlit as st
from frontend.components.header import render_header
from frontend.components.pdf_report import generate_pdf_report
from frontend.services.api_client import api_summarize, api_summarize_multiple, api_upload_files, _summarize_text
from frontend.themes import THEMES


def page_analyser():
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
            Upload one or more files, pick a domain, and get a structured AI summary in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1.15], gap="large")

    with left_col:
        st.markdown('<div style="padding-left:56px">', unsafe_allow_html=True)

        # ── Step 1: Upload multiple files ──
        st.markdown('<div class="panel-label">01 — Upload Documents</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload",
            type=["pdf", "docx", "csv", "txt"],
            label_visibility="collapsed",
            accept_multiple_files=True,
        )

        if uploaded_files and len(uploaded_files) > 1:
            st.markdown(
                f'<div style="font-size:12.5px;color:{th["accent"]};margin-top:6px;font-weight:500;">'
                f'✓ {len(uploaded_files)} files selected</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Step 2: Domain ──
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

        # ── Step 3: Summary style ──
        st.markdown('<div class="panel-label">03 — Summary Style</div>', unsafe_allow_html=True)
        opts = ["Brief", "Detailed", "Bullet-only"]
        sel  = st.radio(
            "Style", options=opts,
            index=opts.index(st.session_state.selected_detail),
            horizontal=True, label_visibility="collapsed",
        )
        st.session_state.selected_detail = sel

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Step 4: Summary mode (only when multiple files) ──
        multiple = uploaded_files and len(uploaded_files) > 1
        if multiple:
            st.markdown('<div class="panel-label">04 — Summary Mode</div>', unsafe_allow_html=True)
            st.markdown(
                f'<p style="font-size:13px;color:{th["muted"]};margin-bottom:12px;">'
                f'{len(uploaded_files)} files selected — how do you want the summary?</p>',
                unsafe_allow_html=True,
            )

            m1, m2 = st.columns(2)
            with m1:
                ind_type = "primary" if st.session_state.get("summary_mode") == "individual" else "secondary"
                if st.button("📄  Individual summaries", key="mode_individual",
                             use_container_width=True, type=ind_type):
                    st.session_state.summary_mode = "individual"
                    st.rerun()
            with m2:
                com_type = "primary" if st.session_state.get("summary_mode") == "combined" else "secondary"
                if st.button("📋  Combined summary", key="mode_combined",
                             use_container_width=True, type=com_type):
                    st.session_state.summary_mode = "combined"
                    st.rerun()

            if st.session_state.get("summary_mode"):
                mode_label = "One summary per document" if st.session_state.summary_mode == "individual" else "All documents merged into one summary"
                st.markdown(
                    f'<div style="font-size:12px;color:{th["accent"]};margin-top:8px;">✓ {mode_label}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Validation ──
        has_files    = bool(uploaded_files)
        has_category = bool(st.session_state.selected_category)
        has_mode     = not multiple or bool(st.session_state.get("summary_mode"))
        can_submit   = has_files and has_category and has_mode

        if not can_submit:
            missing = []
            if not has_files:    missing.append("a file")
            if not has_category: missing.append("a domain")
            if not has_mode:     missing.append("a summary mode")
            st.markdown(
                f'<p style="font-size:12px;color:{th["label"]};margin-bottom:10px;">'
                f'Still need: {", ".join(missing)}</p>',
                unsafe_allow_html=True,
            )

        btn_label = "◈  Analyse Documents" if multiple else "◈  Analyse Document"
        if st.button(btn_label, disabled=not can_submit, use_container_width=True,
                     type="primary", key="analyse_btn"):

            mode = st.session_state.get("summary_mode", "individual")

            if not multiple or mode == "individual":
                # ── Individual: upload all at once, summarise each separately ──
                with st.spinner(f"Uploading {len(uploaded_files)} file(s) and analysing…"):
                    try:
                        results = api_summarize_multiple(
                            uploaded_files=uploaded_files,
                            category=st.session_state.selected_category,
                            detail_level=st.session_state.selected_detail,
                        )
                        for r in results:
                            st.session_state.history.append({
                                "file_name":    r["file_name"],
                                "category":     st.session_state.selected_category,
                                "detail_level": st.session_state.selected_detail,
                            })
                        st.session_state.results     = results
                        st.session_state.result      = results[0] if results else None
                        st.session_state.result_mode = "individual"
                    except Exception as e:
                        st.error(str(e))

            else:
                # ── Combined: upload all at once, merge parsed text, one AI call ──
                with st.spinner(f"Uploading and combining {len(uploaded_files)} documents…"):
                    try:
                        # Upload all files in one request using new bulk endpoint
                        docs = api_upload_files(uploaded_files)

                        if not docs:
                            st.error("Could not parse any of the uploaded files.")
                        else:
                            # Merge all parsed text together
                            all_texts  = []
                            file_names = []
                            for doc in docs:
                                text = doc.get("parsed_text", "")
                                name = doc.get("original_name", "Unknown")
                                if text.strip():
                                    all_texts.append(f"--- {name} ---\n{text}")
                                    file_names.append(name)
                                    st.session_state.history.append({
                                        "file_name":    name,
                                        "category":     st.session_state.selected_category,
                                        "detail_level": st.session_state.selected_detail,
                                    })

                            combined_text = "\n\n".join(all_texts)
                            combined_name = f"{len(file_names)} documents combined"
                            result = _summarize_text(
                                parsed_text=combined_text,
                                file_type="mixed",
                                file_size=0,
                                document_id="combined",
                                file_name=combined_name,
                                category=st.session_state.selected_category,
                                detail_level=st.session_state.selected_detail,
                            )
                            st.session_state.results     = [result]
                            st.session_state.result      = result
                            st.session_state.result_mode = "combined"

                    except Exception as e:
                        st.error(str(e))

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Right: Output panel ────────────────────────────────────────────────────
    with right_col:
        st.markdown('<div style="padding-right:56px">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Output</div>', unsafe_allow_html=True)

        results     = st.session_state.get("results", [])
        result_mode = st.session_state.get("result_mode", "individual")

        if not results:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">◈</div>
                <div class="empty-title">No document analysed yet</div>
                <div class="empty-sub">Upload a file, select a domain, and hit Analyse</div>
            </div>
            """, unsafe_allow_html=True)

        elif len(results) > 1 and result_mode == "individual":
            # Multiple individual results — use tabs
            tab_labels = [
                r["file_name"][:18] + "…" if len(r["file_name"]) > 18 else r["file_name"]
                for r in results
            ]
            tabs = st.tabs(tab_labels)
            for tab, r in zip(tabs, results):
                with tab:
                    _render_result(r)

        else:
            # Single result or combined
            if result_mode == "combined":
                n = len(uploaded_files) if uploaded_files else "multiple"
                st.markdown(
                    f'<div style="font-size:12px;color:#C8F04B;margin-bottom:12px;font-weight:500;">'
                    f'◈ Combined summary of {n} documents</div>',
                    unsafe_allow_html=True,
                )
            _render_result(results[0])

        st.markdown('</div>', unsafe_allow_html=True)


def _render_result(r: dict):
    """Renders a single result — meta pills, 4 cards, download button."""

    st.markdown(
        f'<div class="meta-row">'
        f'<div class="meta-pill accent">◈ {r["category"]}</div>'
        f'<div class="meta-pill">{r["file_name"]}</div>'
        f'<div class="meta-pill">{r["detail_level"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="output-card">'
        f'<div class="output-card-label">Executive Summary</div>'
        f'<div class="output-body">{r["executive_summary"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    bullets = "".join([
        f'<div class="bullet-item"><div class="bullet-dot"></div>'
        f'<div class="bullet-text">{p}</div></div>'
        for p in r["key_points"]
    ])
    st.markdown(
        f'<div class="output-card"><div class="output-card-label">Key Points</div>{bullets}</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        ah = "".join([
            f'<div class="bullet-item"><div class="bullet-dot" style="background:#7B8CFF"></div>'
            f'<div class="bullet-text">{a}</div></div>'
            for a in r["action_items"]
        ])
        st.markdown(
            f'<div class="output-card"><div class="output-card-label" style="color:#7B8CFF">Action Items</div>{ah}</div>',
            unsafe_allow_html=True,
        )
    with c2:
        dh = "".join([
            f'<div class="bullet-item"><div class="bullet-dot" style="background:#F0A04B"></div>'
            f'<div class="bullet-text">{d}</div></div>'
            for d in r["data_highlights"]
        ])
        st.markdown(
            f'<div class="output-card"><div class="output-card-label" style="color:#F0A04B">Data Highlights</div>{dh}</div>',
            unsafe_allow_html=True,
        )

    pdf = generate_pdf_report(r)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="↓  Download Report (.pdf)",
        data=pdf,
        file_name=f"doclens_{r['file_name'].split('.')[0]}_summary.pdf",
        mime="application/pdf",
        use_container_width=True,
        key=f"dl_{r['file_name']}_{r['category']}",
    )
