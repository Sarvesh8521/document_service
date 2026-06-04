import streamlit as st
from frontend.config import BASE_URL
from ai.groq_client import build_prompt, call_groq
import json


def api_login(email: str, password: str) -> dict:
    """
    Authenticates the user against Django's login endpoint.
    On success: returns user dict and loads document history.
    On failure: raises ValueError with a readable message.
    """
    if not email or not password:
        raise ValueError("Please fill in all fields.")

    r = st.session_state.http_session.post(
        f"{BASE_URL}/api/users/login/",
        json={"email": email, "password": password},
    )
    data = r.json()

    if r.status_code == 200:
        name = f"{data.get('first_name','')} {data.get('last_name','')}".strip() \
               or data.get('user_name', email.split('@')[0])
        user = {"name": name, "email": data.get("email_id", email)}

        # Fetch this user's document history right after login
        # so the dashboard shows their previous uploads immediately
        _load_history()

        return user

    raise ValueError(data.get("detail", "Login failed. Please check your credentials."))


def api_signup(name: str, email: str, password: str, confirm: str) -> dict:
    """
    Registers a new user with Django's register endpoint.
    Splits the full name into first + last for Django's model.
    Auto-generates a username from the email address.
    """
    if not name or not email or not password or not confirm:
        raise ValueError("Please fill in all fields.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")
    if password != confirm:
        raise ValueError("Passwords do not match.")

    parts      = name.strip().split(" ", 1)
    first_name = parts[0]
    last_name  = parts[1] if len(parts) > 1 else parts[0]
    user_name  = email.split("@")[0].replace(".", "_").lower()

    r = st.session_state.http_session.post(
        f"{BASE_URL}/api/users/register/",
        json={
            "first_name": first_name,
            "last_name":  last_name,
            "user_name":  user_name,
            "email_id":   email,
            "password":   password,
        },
    )
    data = r.json()

    if r.status_code == 201:
        return {"name": name, "email": email}

    # Flatten Django's field-level error dict into one readable string
    if isinstance(data, dict):
        messages = []
        for field, errors in data.items():
            messages.append(errors[0] if isinstance(errors, list) else str(errors))
        raise ValueError(" ".join(messages))

    raise ValueError("Registration failed. Please try again.")


def api_summarize(file_name: str, category: str, detail_level: str, uploaded_file) -> dict:
    """
    Full summarization pipeline:
    1. Upload file to Django → get parsed text back
    2. Send parsed text to Groq → get AI summary back
    3. Return structured result dict for the UI to display
    """
    # ── Step 1: Upload to Django ──
    csrf = st.session_state.http_session.cookies.get("csrftoken", "")
    uploaded_file.seek(0)  # Reset file pointer before sending

    resp = st.session_state.http_session.post(
        f"{BASE_URL}/api/documents/upload/",
        files={"file": (uploaded_file.name, uploaded_file, "application/octet-stream")},
        headers={"X-CSRFToken": csrf, "Referer": BASE_URL},
    )

    if resp.status_code == 403:
        raise ValueError("Session expired. Please sign out and sign back in.")
    if resp.status_code == 413:
        raise ValueError("File is too large. Please upload a file under 200MB.")
    if resp.status_code != 201:
        raise ValueError("File upload failed. Please check your connection and try again.")

    doc         = resp.json()
    parsed_text = doc.get("parsed_text", "")
    file_type   = doc.get("file_type", "unknown")
    file_size   = doc.get("file_size", 0)
    document_id = str(doc.get("document_id", ""))

    if doc.get("parse_status") == "failed":
        raise ValueError("Could not read this file. Make sure it is not password-protected or corrupted.")
    if not parsed_text.strip():
        raise ValueError("Document appears to be empty.")

    # ── Step 2: AI summarization via Groq ──
    prompt = build_prompt(parsed_text, category, detail_level, file_type)

    try:
        ai_result = call_groq(prompt)
    except json.JSONDecodeError:
        raise ValueError("The AI returned an unexpected response. Please try again.")
    except Exception as e:
        err = str(e).lower()
        if "rate limit" in err or "429" in err:
            raise ValueError("Too many requests. Please wait a moment and try again.")
        elif "api key" in err or "401" in err or "403" in err:
            raise ValueError("Invalid Groq API key. Please check your .env file.")
        elif "context" in err or "token" in err:
            raise ValueError("Document is too long. Try a shorter document.")
        else:
            raise ValueError("AI summarization is temporarily unavailable. Please try again.")

    # ── Step 3: Build result dict ──
    data_highlights = ai_result.get("data_highlights", [])
    data_highlights += [
        f"File type: {file_type.upper()}",
        f"File size: {round(file_size / 1024, 1)} KB",
        f"Doc ID: {document_id[:8]}...",
    ]

    return {
        "executive_summary": ai_result.get("executive_summary", "Summary not available."),
        "key_points":        ai_result.get("key_points", []),
        "action_items":      ai_result.get("action_items", []),
        "data_highlights":   data_highlights[:6],
        "category":          category,
        "detail_level":      detail_level,
        "file_name":         file_name,
    }


def _load_history():
    """
    Private helper — fetches the user's document history from Django
    right after login. Prefixed with _ to signal it's internal only.
    """
    try:
        csrf = st.session_state.http_session.cookies.get("csrftoken", "")
        history_resp = st.session_state.http_session.get(
            f"{BASE_URL}/api/documents/",
            headers={"X-CSRFToken": csrf, "Referer": BASE_URL},
        )
        if history_resp.status_code == 200:
            docs     = history_resp.json()
            doc_list = docs if isinstance(docs, list) else docs.get("results", [])
            st.session_state.history = [
                {
                    "file_name":    d.get("original_name") or d.get("file_name") or "Unknown",
                    "category":     "",
                    "detail_level": "",
                }
                for d in doc_list
                if d.get("original_name") or d.get("file_name")
            ]
    except Exception:
        st.session_state.history = []
