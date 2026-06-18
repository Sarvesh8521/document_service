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
        f"{BASE_URL}/users/login/",
        json={"email": email, "password": password},
    )

    try:
        data = r.json()
    except Exception:
        raise ValueError(f"Server returned an unexpected response (status {r.status_code}). Make sure the backend is running.")

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
        f"{BASE_URL}/users/register/",
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


def api_upload_files(uploaded_files: list) -> list:
    """
    Uploads one or more files to Sarvesh's new bulk upload endpoint.
    Sends all files in a single POST request using the 'files' field (array).
    Returns a list of parsed document dicts — one per successfully uploaded file.

    New API response format (array):
    [
        {
            "filename": "report.pdf",
            "success": true,
            "error": null,
            "document": {
                "document_id": 1,
                "id": "uuid...",
                "original_name": "report.pdf",
                "parsed_text": "...",
                "file_type": "pdf",
                "file_size": 12345,
                ...
            }
        },
        ...
    ]
    """
    csrf = st.session_state.http_session.cookies.get("csrftoken", "")

    # Build multipart files list — same field name "files" for each file
    # requests allows multiple values for the same field name this way
    files_payload = []
    for f in uploaded_files:
        f.seek(0)
        files_payload.append(("files", (f.name, f, "application/octet-stream")))

    resp = st.session_state.http_session.post(
        f"{BASE_URL}/documents/upload/",
        files=files_payload,
        headers={"X-CSRFToken": csrf, "Referer": BASE_URL},
    )

    if resp.status_code == 403:
        raise ValueError("Session expired. Please sign out and sign back in.")
    if resp.status_code == 413:
        raise ValueError("Files are too large. Please upload files under 200MB each.")
    if resp.status_code != 201:
        raise ValueError("File upload failed. Please check your connection and try again.")

    results = resp.json()  # list of {filename, success, error, document}

    # Filter to only successful uploads and return their document dicts
    parsed_docs = []
    for item in results:
        if item.get("success") and item.get("document"):
            parsed_docs.append(item["document"])
        elif not item.get("success"):
            # Log the failure but don't crash — other files may have succeeded
            st.warning(f"{item.get('filename', 'Unknown file')}: {item.get('error', 'Upload failed')}")

    return parsed_docs


def api_summarize(file_name: str, category: str, detail_level: str, uploaded_file) -> dict:
    """
    Summarizes a single file.
    Uploads it via the new bulk endpoint (passing one file),
    then runs Groq AI on the parsed text.
    """
    docs = api_upload_files([uploaded_file])

    if not docs:
        raise ValueError("File upload failed or file could not be parsed.")

    doc = docs[0]
    return _summarize_doc(doc, file_name, category, detail_level)


def api_summarize_multiple(uploaded_files: list, category: str, detail_level: str) -> list:
    """
    Uploads all files at once using the new bulk endpoint,
    then runs Groq AI on each parsed document individually.
    Returns a list of result dicts — one per file.
    """
    docs = api_upload_files(uploaded_files)

    results = []
    for doc in docs:
        file_name = doc.get("original_name", "Unknown")
        try:
            result = _summarize_doc(doc, file_name, category, detail_level)
            results.append(result)
        except Exception as e:
            st.error(f"{file_name}: {str(e)}")

    return results


def _summarize_doc(doc: dict, file_name: str, category: str, detail_level: str) -> dict:
    """
    Runs Groq AI summarization on a parsed document dict from Django.
    Shared by both single and multiple file flows.
    """
    parsed_text = doc.get("parsed_text", "")
    file_type   = doc.get("file_type", "unknown")
    file_size   = doc.get("file_size", 0)
    document_id = str(doc.get("id") or doc.get("document_id", ""))

    if doc.get("parse_status") == "failed":
        raise ValueError("Could not read this file. Make sure it is not password-protected or corrupted.")
    if not parsed_text.strip():
        raise ValueError("Document appears to be empty.")

    return _summarize_text(
        parsed_text=parsed_text,
        file_type=file_type,
        file_size=file_size,
        document_id=document_id,
        file_name=file_name,
        category=category,
        detail_level=detail_level,
    )


def _summarize_text(parsed_text: str, file_type: str, file_size: int,
                    document_id: str, file_name: str, category: str, detail_level: str) -> dict:
    """
    Runs AI summarization on already-parsed text.
    Used by combined mode — text from multiple files is merged before calling this.
    """
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
            raise ValueError("Combined document is too long. Try fewer or shorter files.")
        else:
            raise ValueError("AI summarization is temporarily unavailable. Please try again.")

    data_highlights = ai_result.get("data_highlights", [])
    data_highlights += [
        f"File type: {file_type.upper()}",
        f"Combined size: {round(file_size / 1024, 1)} KB" if file_size else "Multiple files combined",
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
            f"{BASE_URL}/documents/",
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
