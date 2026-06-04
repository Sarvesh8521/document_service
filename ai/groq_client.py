import json
from groq import Groq
from frontend.config import GROQ_API_KEY, GROQ_MODEL
from ai.prompts import PROMPTS, DETAIL_INSTRUCTIONS


def build_prompt(parsed_text: str, category: str, detail_level: str, file_type: str) -> str:
    """
    Assembles the final prompt to send to Groq by combining:
    - The domain-specific instructions (from PROMPTS)
    - The detail level instructions (from DETAIL_INSTRUCTIONS)
    - The actual document text

    The 12,000 character limit prevents exceeding Groq's token limit.
    Most documents are well under this — it only kicks in for very long files.
    """
    base_prompt        = PROMPTS.get(category, PROMPTS["Research"])
    detail_instruction = DETAIL_INSTRUCTIONS.get(detail_level, "")

    # Truncate very long documents to avoid token limit errors
    max_chars = 12000
    if len(parsed_text) > max_chars:
        parsed_text = parsed_text[:max_chars] + "\n\n[Document truncated for length...]"

    return f"""{base_prompt}

Detail level instruction: {detail_instruction}
File type: {file_type.upper()}

Document content:
{parsed_text}"""


def call_groq(prompt: str) -> dict:
    """
    Sends the prompt to Groq and returns a parsed dictionary.

    Why the JSON extraction logic?
    Sometimes LLMs wrap their JSON in markdown code blocks like:
    ```json
    { "executive_summary": "..." }
    ```
    We strip those out before parsing.

    The fallback handles cases where the AI returns malformed JSON —
    instead of crashing the whole app, we ask Groq again with a
    simpler, stricter prompt.
    """
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a document analysis assistant. Always respond with valid JSON only. No markdown, no explanation, just the JSON object."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,  # Low temperature = consistent, reliable output
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code blocks if present
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break

    # Extract just the JSON object — find first { and last }
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback — ask Groq again with a simpler, stricter prompt
        fallback = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Respond with valid JSON only. No extra text whatsoever."
                },
                {
                    "role": "user",
                    "content": (
                        "Generate a document summary JSON with these exact keys: "
                        "executive_summary (string), key_points (array of 5 strings), "
                        "action_items (array of 3 strings), data_highlights (array of 3 strings). "
                        f"Base it on this text: {prompt[:3000]}"
                    )
                }
            ],
            temperature=0.1,
            max_tokens=800,
        )
        fb    = fallback.choices[0].message.content.strip()
        start = fb.find("{")
        end   = fb.rfind("}") + 1
        return json.loads(fb[start:end])
