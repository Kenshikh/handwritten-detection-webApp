"""
Handwritten Character Recognition - Streamlit App
Dashboard plus OCR workspace for college project presentation
"""

import base64
import html
import hashlib
import io
import json
import os
from datetime import datetime
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

import pandas as pd
import streamlit as st
from groq import Groq
from PIL import Image


st.set_page_config(
    page_title="Handwriting Recognition",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


DATA_FILE = Path("dashboard_data.json")
MEMORY_FILE = Path("transcription_memory.json")


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Source+Sans+3:wght@400;600;700&display=swap');

        :root {
            --bg: #f4f7fb;
            --surface: #ffffff;
            --surface-soft: #eef3f9;
            --surface-strong: #f8fbff;
            --text: #14213d;
            --muted: #5c6b82;
            --line: #d9e2ef;
            --primary: #3a34c8;
            --primary-strong: #2921a5;
            --accent: #eeedff;
            --success: #1f9a62;
            --warning: #d09b24;
            --danger: #d5585f;
            --shadow: 0 18px 48px rgba(15, 36, 66, 0.10);
            --radius: 22px;
        }

        html, body, [class*="css"] {
            font-family: 'Source Sans 3', sans-serif;
            color: var(--text);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(99, 102, 241, 0.12), transparent 26%),
                radial-gradient(circle at top right, rgba(15, 76, 129, 0.09), transparent 22%),
                linear-gradient(180deg, #fafbff 0%, var(--bg) 100%);
        }

        .block-container {
            max-width: 1220px;
            padding-top: 1.8rem;
            padding-bottom: 2.25rem;
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }

        .stDeployButton {
            display: none;
        }

        [data-testid="stSidebar"] {
            background: #f8fbff;
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] * {
            color: var(--text) !important;
        }

        [data-testid="stFileUploader"] {
            background: var(--surface-soft);
            border: 1.5px dashed #a9bdd7 !important;
            border-radius: 18px !important;
            padding: 1rem;
            margin-top: 1rem;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: var(--primary) !important;
            background: #f4f5ff;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 999px !important;
            border: none !important;
            font-weight: 700 !important;
            min-height: 3rem !important;
            padding: 0.75rem 1.5rem !important;
            transition: 0.2s ease;
            box-shadow: none !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--primary) 0%, #5d56ea 100%) !important;
            color: white !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            filter: brightness(0.98);
        }

        .stDownloadButton > button {
            background: white !important;
            color: var(--primary-strong) !important;
            border: 1px solid #d7d4ff !important;
        }

        .nav-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.4rem;
            background: linear-gradient(135deg, #2f2ac0 0%, #4b46e3 100%);
            border-radius: 28px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 16px 40px rgba(47, 42, 192, 0.20);
        }

        .brand {
            font-family: 'Manrope', sans-serif;
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #ffffff;
        }

        .brand-sub {
            font-size: 0.98rem;
            color: rgba(255, 255, 255, 0.84);
        }

        .side-brand {
            font-family: 'Manrope', sans-serif;
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--primary-strong);
            line-height: 1.35;
            margin-bottom: 0.35rem;
        }

        .side-brand-sub {
            font-size: 0.95rem;
            color: var(--muted);
            line-height: 1.7;
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(240,239,255,0.98));
            border: 1px solid #e1e4fb;
            border-radius: 30px;
            padding: 2.8rem 2.6rem;
            box-shadow: var(--shadow);
            overflow: hidden;
            position: relative;
            max-width: 860px;
            margin: 3.4rem auto 0;
            text-align: center;
        }

        .hero-card::after {
            content: "";
            position: absolute;
            inset: auto -60px -80px auto;
            width: 230px;
            height: 230px;
            background: radial-gradient(circle, rgba(58, 52, 200, 0.14), transparent 70%);
        }

        .eyebrow {
            display: inline-block;
            background: var(--accent);
            color: var(--primary-strong);
            font-size: 0.86rem;
            font-weight: 700;
            border-radius: 999px;
            padding: 0.45rem 0.85rem;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-family: 'Manrope', sans-serif;
            font-size: clamp(2.3rem, 4vw, 4.4rem);
            line-height: 1.08;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin: 0 auto;
            max-width: 720px;
        }

        .home-copy {
            max-width: 640px;
            color: var(--muted);
            line-height: 1.9;
            font-size: 1.05rem;
            margin: 1rem auto 0;
        }

        .home-actions {
            max-width: 220px;
            margin: 2rem auto 0;
        }

        .workspace-shell {
            margin-top: 0.35rem;
        }

        .side-panel {
            position: sticky;
            top: 1.15rem;
        }

        .side-panel-copy {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.55;
            margin-bottom: 1.15rem;
        }

        .side-nav-title {
            font-family: 'Manrope', sans-serif;
            font-size: 1rem;
            font-weight: 800;
            color: var(--primary-strong);
            margin-bottom: 0.25rem;
        }

        .side-nav-copy {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.5;
            margin-bottom: 1rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--line) !important;
            border-radius: 24px !important;
            padding: 1.15rem !important;
            box-shadow: 0 14px 36px rgba(15, 36, 66, 0.08);
        }

        .side-panel .stButton {
            margin-bottom: 0.7rem;
        }

        .side-panel .stButton:last-child {
            margin-bottom: 0;
        }

        .side-panel .stButton > button {
            background: #ffffff !important;
            border: 1px solid #d9e2ef !important;
            color: var(--text) !important;
            box-shadow: none !important;
        }

        .side-panel .stButton > button:hover {
            background: #f7f9fd !important;
            filter: none !important;
        }

        .side-panel .stButton > button {
            min-height: 3.1rem !important;
        }

        .page-shell {
            max-width: 100%;
            margin: 0;
        }

        .upload-card,
        .result-card,
        .dash-card,
        .toolbar-card,
        .activity-card {
            background: rgba(255, 255, 255, 0.97);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            box-shadow: 0 8px 24px rgba(16, 39, 71, 0.05);
        }

        .toolbar-card {
            padding: 1rem 1.1rem;
            margin-bottom: 1.15rem;
        }

        .upload-card {
            max-width: 980px;
            margin: 0 auto;
            padding: 1.85rem;
        }

        .upload-card-title,
        .section-title {
            font-family: 'Manrope', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.45rem;
        }

        .section-title {
            font-size: 1.15rem;
            margin-bottom: 0.8rem;
        }

        .upload-card-copy,
        .card-copy,
        .status-note,
        .dashboard-copy {
            color: var(--muted);
            line-height: 1.7;
        }

        .dashboard-head {
            margin-bottom: 1rem;
        }

        .dashboard-title {
            font-family: 'Manrope', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.25rem;
        }

        .upload-tips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 1rem;
            margin-bottom: 0.35rem;
        }

        .tip-pill {
            background: #f3f7fc;
            border: 1px solid #d9e2ef;
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            color: var(--muted);
            font-size: 0.92rem;
        }

        .preview-frame {
            background: var(--surface-strong);
            border: 1px solid #dbe5f0;
            border-radius: 18px;
            padding: 0.9rem;
            margin-top: 1rem;
        }

        .notice-card {
            background: #fff8e8;
            border: 1px solid #f0d9a7;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            margin: 1rem 0;
            color: #5f4b1a;
            line-height: 1.65;
            font-size: 0.96rem;
        }

        .notice-title {
            font-family: 'Manrope', sans-serif;
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
            color: #6b4f12;
        }

        .result-wrap {
            max-width: 980px;
            margin: 1.5rem auto 0;
        }

        .result-card,
        .dash-card,
        .activity-card {
            padding: 1.25rem;
        }

        .result-text {
            background: #f8fbff;
            border: 1px solid #dbe5f0;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            line-height: 1.7;
            white-space: pre-wrap;
            color: var(--text);
            min-height: 130px;
        }

        .metric-strip {
            margin-top: 1rem;
            margin-bottom: 0.6rem;
        }

        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.85rem 1rem;
            box-shadow: 0 8px 24px rgba(16, 39, 71, 0.04);
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
        }

        .result-actions {
            margin-top: 1rem;
        }

        .result-actions .stButton,
        .result-actions .stDownloadButton {
            width: 100%;
        }

        .result-actions .stButton > button,
        .result-actions .stDownloadButton > button {
            width: 100%;
        }

        .dash-stat {
            padding: 1.15rem 1.2rem;
            min-height: 128px;
        }

        .dash-stat-top {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            margin-bottom: 0.75rem;
        }

        .dash-dot {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            display: inline-block;
        }

        .dash-label {
            color: var(--muted);
            font-size: 0.94rem;
        }

        .dash-value {
            font-family: 'Manrope', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            line-height: 1;
        }

        .dash-change {
            margin-top: 0.55rem;
            font-size: 0.92rem;
            font-weight: 700;
        }

        .activity-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            padding: 0.85rem 0;
            border-bottom: 1px solid #edf1f7;
        }

        .activity-row:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .activity-time {
            color: var(--muted);
            white-space: nowrap;
        }

        @media (max-width: 900px) {
            .hero-card {
                padding: 2rem 1.2rem;
            }

            .upload-card,
            .result-wrap {
                max-width: 100%;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


class Config:
    GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    TEMPERATURE = 0.2
    MAX_TOKENS = 2048


PROVIDER_MODELS = {
    "Groq": [
        "meta-llama/llama-4-scout-17b-16e-instruct",
    ],
    "Gemini": [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
    ],
}


def default_dashboard_data():
    return {
        "stats": {
            "processed_docs": 0,
            "successful_ocr": 0,
            "errors": 0,
            "active_users": 0,
            "processed_change": "0%",
            "successful_change": "0%",
            "errors_change": "0%",
            "active_change": "0%",
        },
        "volume": [],
        "recent_documents": [],
        "recent_activity": [],
    }


def ensure_data_file():
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps(default_dashboard_data(), indent=2), encoding="utf-8")


def ensure_memory_file():
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(json.dumps({"entries": []}, indent=2), encoding="utf-8")


def load_dashboard_data():
    ensure_data_file()
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = default_dashboard_data()
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data


def load_memory_data():
    ensure_memory_file()
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = {"entries": []}
        MEMORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if "entries" not in data or not isinstance(data["entries"], list):
        data = {"entries": []}
    return data


def save_memory_data(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def image_signature(image_bytes: bytes) -> str:
    return hashlib.sha256(image_bytes).hexdigest()


def build_memory_context(current_signature: str, limit: int = 5) -> str:
    memory_data = load_memory_data()
    entries = memory_data.get("entries", [])
    same_image = [entry for entry in entries if entry.get("image_signature") == current_signature]
    other_recent = [entry for entry in entries if entry.get("image_signature") != current_signature]

    selected = same_image[-3:] + other_recent[-2:]
    selected = selected[-limit:]
    if not selected:
        return "No prior correction memory."

    lines = []
    for idx, entry in enumerate(selected, start=1):
        lines.append(
            "\n".join(
                [
                    f"Memory {idx}:",
                    f"- File: {entry.get('file_name', 'Unknown')}",
                    f"- User feedback: {entry.get('feedback', '')}",
                    f"- Corrected transcription: {entry.get('corrected_text', '')}",
                ]
            )
        )
    return "\n\n".join(lines)


def remember_correction(file_name, image_bytes, prior_text, feedback, corrected_text):
    memory_data = load_memory_data()
    memory_data["entries"].append(
        {
            "file_name": file_name,
            "image_signature": image_signature(image_bytes),
            "previous_text": prior_text,
            "feedback": feedback,
            "corrected_text": corrected_text,
            "saved_at": datetime.now().isoformat(),
        }
    )
    memory_data["entries"] = memory_data["entries"][-25:]
    save_memory_data(memory_data)


def update_dashboard_after_run(file_name, file_size_bytes, status):
    data = load_dashboard_data()
    processed_at = datetime.now()
    processed_time = datetime.now().strftime("%I:%M %p").lstrip("0")
    size_label = f"{file_size_bytes / (1024 * 1024):.1f} MB"

    data["recent_documents"].insert(
        0,
        {
            "document": file_name,
            "size": size_label,
            "status": status,
            "processed_time": processed_time,
            "processed_at": processed_at.isoformat(),
        },
    )
    data["recent_documents"] = data["recent_documents"][:6]

    activity_message = f"Processed {file_name}" if status == "Completed" else f"OCR failed on {file_name}"
    data["recent_activity"].insert(0, {"message": activity_message, "time": processed_time})
    data["recent_activity"] = data["recent_activity"][:6]

    data["stats"]["processed_docs"] += 1
    if status == "Completed":
        data["stats"]["successful_ocr"] += 1
    else:
        data["stats"]["errors"] += 1

    day_key = processed_at.strftime("%a")
    for point in data["volume"]:
        if point["day"] == day_key:
            point["documents"] += 1
            break
    else:
        data["volume"].append({"day": day_key, "documents": 1})

    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def encode_image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def build_recognition_prompt(image_bytes: bytes) -> str:
    memory_context = build_memory_context(image_signature(image_bytes))

    return f"""Please carefully read and transcribe ALL visible text from this image.

Instructions:
1. Extract every word, number, and character you can see
2. This includes handwritten text, printed text, labels, headings, symbols, and mixed-content text
3. Maintain the original line breaks and structure as closely as possible
4. If text is unclear, make your best guess and mark it with [unclear]
5. Only return the transcribed text, no additional commentary
6. Preserve capitalization as written

Past correction memory:
{memory_context}

Transcription:"""


def build_reevaluate_prompt(image_bytes: bytes, generated_text: str) -> str:
    memory_context = build_memory_context(image_signature(image_bytes))

    return f"""You are reviewing a text transcription generated by an AI system.

Compare the image with the current transcription.
The image may contain handwritten text, printed text, symbols, or a mix of all of them.
If the transcription contains an error, return only the corrected transcription.
If the transcription is already accurate, reply with exactly: The transcription is correct.
Do not include explanations, notes, or any extra commentary.

Current transcription:
{generated_text}

Past correction memory:
{memory_context}
"""


def build_feedback_prompt(image_bytes: bytes, generated_text: str, user_feedback: str, file_name: str) -> str:
    current_signature = image_signature(image_bytes)
    memory_context = build_memory_context(current_signature)

    return f"""You are reviewing a text transcription generated by an AI system.

The user has provided feedback. You must always use:
1. The image
2. The current transcription
3. The user's feedback
4. Past correction memory

Task:
- Re-read the image carefully
- The image may contain handwritten text, printed text, symbols, or mixed formatting
- Consider the user's feedback even if the current text looks mostly correct
- Use the correction memory to avoid repeating earlier mistakes
- Return only the best updated transcription
- Do not add explanations, labels, notes, or commentary

Current file:
{file_name}

Current transcription:
{generated_text}

User feedback:
{user_feedback}

Past correction memory:
{memory_context}
"""


def call_groq_model(api_key, model, prompt, image_bytes, mime_type="image/jpeg", streaming=False):
    client = Groq(api_key=api_key)
    base64_image = encode_image_to_base64(image_bytes)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                },
            ],
        }
    ]

    if streaming:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            top_p=1,
            stream=True,
        )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        max_tokens=Config.MAX_TOKENS,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content.strip()


def call_gemini_model(api_key, model, prompt, image_bytes, mime_type="image/jpeg"):
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": encode_image_to_base64(image_bytes),
                        }
                    },
                    {"text": prompt},
                ]
            }
        ]
    }
    request = urlrequest.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urlerror.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Gemini request failed: {error_body}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Gemini connection failed: {exc}") from exc

    candidates = body.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Gemini returned no candidates: {body}")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts if "text" in part).strip()
    if not text:
        raise RuntimeError(f"Gemini returned an empty response: {body}")
    return text


def run_multimodal_text(provider, api_key, model, prompt, image_bytes, mime_type="image/jpeg", streaming=False):
    if provider == "Gemini":
        return call_gemini_model(api_key, model, prompt, image_bytes, mime_type)
    return call_groq_model(api_key, model, prompt, image_bytes, mime_type, streaming=streaming)


def init_session_state():
    defaults = {
        "page": "home",
        "uploaded_image_bytes": None,
        "uploaded_mime_type": None,
        "last_result": "",
        "last_file": "",
        "last_timestamp": "",
        "reevaluate_mode": False,
        "reevaluate_feedback": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_navbar():
    st.markdown(
        """
        <div class="nav-bar">
            <div>
                <div class="brand">Handwriting Recognition System</div>
                <div class="brand-sub">AI-powered handwritten text transcription</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown("### Configuration")
        provider = "Gemini"
        model = st.selectbox(
            "Model",
            options=PROVIDER_MODELS[provider],
            index=0,
            help="Choose the model used for OCR and re-evaluation.",
        )
        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...",
            help="Get your key from Google AI Studio.",
        )
        use_streaming = False
        st.caption("Gemini runs in non-streaming mode in this app.")
        st.markdown("### Input Tips")
        st.markdown(
            """
            - Use a clear image with good lighting
            - Keep the handwritten text centered
            - Prefer dark ink on a plain background
            - JPG, PNG, BMP, and WEBP are supported
            """
        )
    return provider, model, api_key_input, use_streaming


def render_side_nav():
    with st.container(border=True):
        st.markdown('<div class="side-panel">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="side-brand">Handwriting Recognition System</div>
            <div class="side-brand-sub">AI-powered handwritten text transcription</div>
            <div style="height: 1rem;"></div>
            <div class="side-nav-title">Navigation</div>
            <div class="side-panel-copy">Switch between pages.</div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Dashboard", key="side_dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

        if st.button("OCR Workspace", key="side_ocr", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()

        if st.button("Home", key="side_home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_home_page():
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">AI Vision Demo</div>
            <h1 class="hero-title">Handwriting Recognition System</h1>
            <div class="home-copy">
                Advanced AI-powered handwriting recognition with real-time transcription, verification, and comprehensive analytics dashboard for your document processing workflow.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1.4, 1, 1.4])
    with center_col:
        st.markdown('<div class="home-actions">', unsafe_allow_html=True)
        if st.button("Start", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_stat_card(label, value, change, dot_color, change_color):
    st.markdown(
        f"""
        <div class="dash-card dash-stat">
            <div class="dash-stat-top">
                <span class="dash-dot" style="background:{dot_color};"></span>
                <span class="dash-label">{html.escape(label)}</span>
            </div>
            <div class="dash-value">{html.escape(value)}</div>
            <div class="dash-change" style="color:{change_color};">{html.escape(change)} from last week</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message):
    st.info(message)


def build_chart_data(data):
    if data["volume"]:
        return pd.DataFrame(data["volume"]).set_index("day")

    recent_documents = data.get("recent_documents", [])
    if not recent_documents:
        return pd.DataFrame()

    dated_records = []
    undated_count = 0
    for item in reversed(recent_documents):
        processed_at = item.get("processed_at")
        if processed_at:
            try:
                stamp = datetime.fromisoformat(processed_at)
                dated_records.append(stamp.strftime("%d %b"))
                continue
            except ValueError:
                pass
        undated_count += 1

    if dated_records:
        counts = {}
        for label in dated_records:
            counts[label] = counts.get(label, 0) + 1
        return pd.DataFrame(
            [{"day": key, "documents": value} for key, value in counts.items()]
        ).set_index("day")

    return pd.DataFrame(
        [
            {"day": f"Run {index + 1}", "documents": 1}
            for index in range(undated_count)
        ]
    ).set_index("day")


def render_dashboard_page():
    data = load_dashboard_data()
    stats = data["stats"]

    nav_col, content_col = st.columns([0.9, 3.4], gap="large")
    with nav_col:
        render_side_nav()

    with content_col:
        st.markdown('<div class="workspace-shell">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="dashboard-head">
                <div class="dashboard-title">AI-OCR Dashboard</div>
                <div class="dashboard-copy">Real-time performance metrics, processing history, and activity tracking for your handwriting recognition operations.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        a, b, c = st.columns(3)
        with a:
            render_stat_card("Processed Docs", f"{stats['processed_docs']:,}", stats["processed_change"], "#c9f5db", "#1f9a62")
        with b:
            render_stat_card("Successful OCR", f"{stats['successful_ocr']:,}", stats["successful_change"], "#c9f5db", "#1f9a62")
        with c:
            render_stat_card("Errors", f"{stats['errors']:,}", stats["errors_change"], "#ffe2e4", "#d5585f")

        left_col, right_col = st.columns([1.2, 1])
        with left_col:
            st.markdown("### OCR Processing Volume")
            chart_df = build_chart_data(data)
            if not chart_df.empty:
                st.caption("The chart adapts to available OCR records and updates automatically as new files are processed.")
                st.line_chart(chart_df, height=280, use_container_width=True)
            else:
                render_empty_state("No processing data yet. Run OCR once and the chart will appear here.")

        with right_col:
            st.markdown("### Recent Documents")
            if data["recent_documents"]:
                docs_df = pd.DataFrame(
                    data["recent_documents"],
                    columns=["document", "size", "status", "processed_time"],
                )
                docs_df.columns = ["Document", "Size", "Status", "Processed Time"]
                st.dataframe(docs_df, use_container_width=True, hide_index=True)
            else:
                render_empty_state("No documents processed yet.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_upload_page(provider, model, api_key, use_streaming):
    nav_col, content_col = st.columns([0.9, 3.4], gap="large")
    with nav_col:
        render_side_nav()

    with content_col:
        st.markdown('<div class="workspace-shell">', unsafe_allow_html=True)
        provider = "Gemini"
        model = "gemini-2.5-flash"
        use_streaming = False
        if api_key_input:
            api_key = api_key_input.strip()
        else:
            api_key = os.environ.get("GEMINI_API_KEY", "")

        st.markdown(
            """
            <div class="upload-card">
                <div class="upload-card-title">OCR Workspace</div>
                <div class="upload-card-copy">
                    Choose a clear handwritten image to extract and convert the text into digital format.
                </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            help="Supported formats: JPG, JPEG, PNG, BMP, WEBP",
            label_visibility="collapsed",
        )

        st.markdown(
            """
            <div class="upload-tips">
                <span class="tip-pill">Good lighting</span>
                <span class="tip-pill">Clear handwriting</span>
                <span class="tip-pill">Plain background</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if uploaded_file:
            image_bytes = uploaded_file.read()
            mime_type = uploaded_file.type or "image/jpeg"
            st.session_state["uploaded_image_bytes"] = image_bytes
            st.session_state["uploaded_mime_type"] = mime_type

            st.markdown('<div class="preview-frame">', unsafe_allow_html=True)
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, caption=uploaded_file.name, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("Run Recognition", use_container_width=True):
                if not api_key:
                    st.error("Enter your Gemini API key before running the model.")
                else:
                    try:
                        with st.spinner("Analyzing handwriting..."):
                            prompt = build_recognition_prompt(image_bytes)
                            full_text = run_multimodal_text(
                                provider,
                                api_key,
                                model,
                                prompt,
                                image_bytes,
                                mime_type,
                                streaming=False,
                            )

                        st.session_state["last_result"] = full_text
                        st.session_state["last_file"] = uploaded_file.name
                        st.session_state["last_timestamp"] = datetime.now().strftime("%H:%M:%S")
                        st.session_state["reevaluate_mode"] = False
                        st.session_state["reevaluate_feedback"] = ""
                        update_dashboard_after_run(uploaded_file.name, len(image_bytes), "Completed")
                        st.success("Transcription completed successfully.")
                    except Exception as exc:
                        update_dashboard_after_run(uploaded_file.name, len(image_bytes), "Error")
                        st.error(f"Recognition failed: {exc}")
                        st.caption("Check your Gemini API key and verify the selected model is available.")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get("last_result"):
            result_text = st.session_state["last_result"]
            word_count = len(result_text.split())
            char_count = len(result_text)
            timestamp = st.session_state.get("last_timestamp", "--:--:--")

            st.markdown('<div class="result-wrap">', unsafe_allow_html=True)
            st.markdown(
                """
                <div class="result-card">
                    <div class="section-title">Transcription Result</div>
                    <div class="status-note">Generated text from the most recently processed image.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div class="notice-card">
                    <div class="notice-title">Disclaimer</div>
                    This transcription is generated by an AI system and should be reviewed before final use.
                    Although the model is designed to read handwriting accurately, it may occasionally
                    misinterpret words, characters, or formatting.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="result-text">{html.escape(result_text)}</div>',
                unsafe_allow_html=True,
            )

            st.markdown('<div class="metric-strip">', unsafe_allow_html=True)
            metric_a, metric_b, metric_c = st.columns(3)
            metric_a.metric("Words", word_count)
            metric_b.metric("Characters", char_count)
            metric_c.metric("Processed At", timestamp)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="result-actions">', unsafe_allow_html=True)
            action_left, action_right = st.columns(2)
            with action_left:
                st.download_button(
                    label="Download Transcription",
                    data=result_text,
                    file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with action_right:
                if st.button("Re-evaluate Transcription", use_container_width=True):
                    st.session_state["reevaluate_mode"] = True
            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.get("reevaluate_mode"):
                with st.form("reevaluate_feedback_form", clear_on_submit=False):
                    feedback = st.text_area(
                        "User feedback for re-evaluation",
                        value=st.session_state.get("reevaluate_feedback", ""),
                        placeholder="Example: The lowercase letters after 'Alphabet' are missing. Also verify the numeric row and printed labels.",
                        height=130,
                    )
                    st.session_state["reevaluate_feedback"] = feedback
                    submit_feedback = st.form_submit_button("Submit Feedback & Re-evaluate", use_container_width=True)

                cancel_col, _ = st.columns([1, 1])
                with cancel_col:
                    if st.button("Cancel Re-evaluation", key="cancel_re_evaluate", use_container_width=True):
                        st.session_state["reevaluate_mode"] = False
                        st.session_state["reevaluate_feedback"] = ""
                        st.rerun()

                if submit_feedback:
                    if not api_key:
                        st.error("Enter your Gemini API key before running re-evaluation.")
                    elif not st.session_state.get("uploaded_image_bytes"):
                        st.error("Please upload and process an image before re-evaluating the transcription.")
                    elif not feedback.strip():
                        st.error("Please enter feedback before re-evaluation.")
                    else:
                        try:
                            latest_text = st.session_state.get("last_result", result_text)
                            prompt = build_feedback_prompt(
                                st.session_state["uploaded_image_bytes"],
                                latest_text,
                                feedback.strip(),
                                st.session_state.get("last_file", "Uploaded image"),
                            )
                            with st.spinner("Re-evaluating transcription using user feedback..."):
                                review_result = run_multimodal_text(
                                    provider,
                                    api_key,
                                    model,
                                    prompt,
                                    st.session_state["uploaded_image_bytes"],
                                    st.session_state.get("uploaded_mime_type", "image/jpeg"),
                                )

                            remember_correction(
                                st.session_state.get("last_file", "Uploaded image"),
                                st.session_state["uploaded_image_bytes"],
                                latest_text,
                                feedback.strip(),
                                review_result,
                            )
                            st.session_state["last_result"] = review_result
                            st.session_state["last_timestamp"] = datetime.now().strftime("%H:%M:%S")
                            st.session_state["reevaluate_mode"] = False
                            st.session_state["reevaluate_feedback"] = ""
                            st.success("Re-evaluation completed using your feedback and saved memory.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Re-evaluation failed: {exc}")
            st.markdown("</div>", unsafe_allow_html=True)


init_session_state()
ensure_data_file()
ensure_memory_file()
provider, selected_model, api_key_input, use_streaming = render_sidebar()
if api_key_input:
    api_key = api_key_input.strip()
elif provider == "Gemini":
    api_key = os.environ.get("GEMINI_API_KEY", "")
else:
    api_key = os.environ.get("GROQ_API_KEY", "")
render_navbar()

if st.session_state.page == "home":
    render_home_page()
elif st.session_state.page == "dashboard":
    render_dashboard_page()
else:
    render_upload_page(provider, selected_model, api_key, use_streaming)
