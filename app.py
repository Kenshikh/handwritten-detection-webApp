"""
Handwritten Character Recognition - Streamlit App
Professional two-step UI for college project presentation
"""

import base64
import html
import io
import os
from datetime import datetime

import streamlit as st
from groq import Groq
from PIL import Image


st.set_page_config(
    page_title="Handwriting Recognition",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Source+Sans+3:wght@400;600&display=swap');

        :root {
            --bg: #f4f7fb;
            --surface: #ffffff;
            --surface-soft: #eef3f9;
            --text: #14213d;
            --muted: #5c6b82;
            --line: #d9e2ef;
            --primary: #0f4c81;
            --primary-strong: #08365c;
            --accent: #e7f0fa;
            --success: #1f7a5c;
            --shadow: 0 18px 48px rgba(15, 36, 66, 0.10);
            --radius: 22px;
        }

        html, body, [class*="css"] {
            font-family: 'Source Sans 3', sans-serif;
            color: var(--text);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(77, 145, 214, 0.14), transparent 28%),
                radial-gradient(circle at top right, rgba(15, 76, 129, 0.09), transparent 22%),
                linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 2rem;
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
            margin-top: 1.1rem;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: var(--primary) !important;
            background: #f4f8fd;
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
            background: linear-gradient(135deg, var(--primary) 0%, #1b6ca8 100%) !important;
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
            border: 1px solid #bdd0e3 !important;
        }

        .nav-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .brand {
            font-family: 'Manrope', sans-serif;
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--primary-strong);
        }

        .brand-sub {
            font-size: 0.9rem;
            color: var(--muted);
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(237,244,252,0.96));
            border: 1px solid rgba(181, 200, 222, 0.7);
            border-radius: 30px;
            padding: 2.5rem;
            box-shadow: var(--shadow);
            overflow: hidden;
            position: relative;
            max-width: 860px;
            margin: 3rem auto 0;
        }

        .hero-card::after {
            content: "";
            position: absolute;
            inset: auto -60px -80px auto;
            width: 230px;
            height: 230px;
            background: radial-gradient(circle, rgba(15, 76, 129, 0.10), transparent 70%);
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
            margin: 0;
            max-width: 720px;
        }

        .hero-copy {
            font-size: 1.1rem;
            color: var(--muted);
            line-height: 1.8;
            max-width: 700px;
            margin-top: 1rem;
        }

        .info-card, .feature-card, .upload-card, .result-card {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 1.35rem;
            box-shadow: 0 8px 24px rgba(16, 39, 71, 0.05);
        }

        .card-title {
            font-family: 'Manrope', sans-serif;
            font-size: 1.08rem;
            font-weight: 800;
            margin-bottom: 0.55rem;
        }

        .card-copy {
            color: var(--muted);
            line-height: 1.7;
            font-size: 0.99rem;
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

        .steps-list {
            margin: 0;
            padding-left: 1.15rem;
            color: var(--muted);
            line-height: 1.9;
        }

        .status-note {
            font-size: 0.94rem;
            color: var(--muted);
            margin-top: 0.6rem;
        }

        .home-copy {
            max-width: 640px;
            color: var(--muted);
            line-height: 1.9;
            font-size: 1.05rem;
            margin-top: 1rem;
        }

        .home-actions {
            max-width: 220px;
            margin-top: 2rem;
        }

        .page-toolbar {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1.25rem;
        }

        .upload-card {
            max-width: 760px;
            margin: 0 auto;
            padding: 1.75rem;
        }

        .upload-card-title {
            font-family: 'Manrope', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.45rem;
        }

        .upload-card-copy {
            color: var(--muted);
            line-height: 1.7;
            font-size: 1rem;
            margin-bottom: 1.25rem;
        }

        .upload-tips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 1rem;
        }

        .tip-pill {
            background: #f3f7fc;
            border: 1px solid #d9e2ef;
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            color: var(--muted);
            font-size: 0.92rem;
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
            max-width: 760px;
            margin: 1.5rem auto 0;
        }

        @media (max-width: 900px) {
            .hero-card {
                padding: 2rem 1.2rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


class Config:
    MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    TEMPERATURE = 0.2
    MAX_TOKENS = 2048


def encode_image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def recognize_text(client, image_bytes, mime_type="image/jpeg", streaming=True):
    base64_image = encode_image_to_base64(image_bytes)

    prompt = """Please carefully read and transcribe ALL handwritten text from this image.

Instructions:
1. Extract every word, number, and character you can see
2. Maintain the original line breaks and structure
3. If text is unclear, make your best guess and mark it with [unclear]
4. Only return the transcribed text, no additional commentary
5. Preserve capitalization as written

Transcription:"""

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
            model=Config.MODEL,
            messages=messages,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            top_p=1,
            stream=True,
        )

    completion = client.chat.completions.create(
        model=Config.MODEL,
        messages=messages,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content.strip()


def reevaluate_text(client, image_bytes, generated_text, mime_type="image/jpeg"):
    base64_image = encode_image_to_base64(image_bytes)

    prompt = f"""You are reviewing a handwritten text transcription generated by an AI system.

Compare the handwritten image with the current transcription.
If the transcription contains an error, return only the corrected transcription.
If the transcription is already accurate, reply with exactly: The transcription is correct.
Do not include explanations, notes, or any extra commentary.

Current transcription:
{generated_text}
"""

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

    completion = client.chat.completions.create(
        model=Config.MODEL,
        messages=messages,
        temperature=0,
        max_tokens=Config.MAX_TOKENS,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content.strip()


def init_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "uploaded_image_bytes" not in st.session_state:
        st.session_state.uploaded_image_bytes = None
    if "uploaded_mime_type" not in st.session_state:
        st.session_state.uploaded_mime_type = None


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
        api_key_input = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get your key from console.groq.com/keys",
        )
        use_streaming = st.toggle("Stream output", value=True)
        st.markdown("### Input Tips")
        st.markdown(
            """
            - Use a clear image with good lighting
            - Keep the handwritten text centered
            - Prefer dark ink on a plain background
            - JPG, PNG, BMP, and WEBP are supported
            """
        )
    return api_key_input, use_streaming


def render_home_page():
    st.markdown(
        """
        <div class="hero-card">
            <h1 class="hero-title">Handwriting Recognition System</h1>
            <div class="home-copy">
                This project reads handwritten text from an uploaded image.
                It uses an AI vision model to convert notes into digital text.
                Click start to upload an image and generate the transcription.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1.4, 1, 1.4])
    with center_col:
        st.markdown('<div class="home-actions">', unsafe_allow_html=True)
        if st.button("Start", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_upload_page(api_key, use_streaming):
    st.markdown('<div class="page-toolbar">', unsafe_allow_html=True)
    left_spacer, toolbar_right = st.columns([4, 1])
    with toolbar_right:
        if st.button("Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="upload-card">
            <div class="upload-card-title">Upload Handwritten Image</div>
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
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, caption=uploaded_file.name, use_container_width=True)

        if st.button("Run Recognition", use_container_width=True):
            if not api_key:
                st.error("Enter your Groq API key in the sidebar before running the model.")
            else:
                try:
                    client = Groq(api_key=api_key)
                    with st.spinner("Analyzing handwriting..."):
                        if use_streaming:
                            placeholder = st.empty()
                            full_text = ""
                            completion = recognize_text(client, image_bytes, mime_type, streaming=True)
                            for chunk in completion:
                                delta = chunk.choices[0].delta.content or ""
                                full_text += delta
                                safe_text = html.escape(full_text + "▌")
                                placeholder.markdown(
                                    f'<div class="result-text">{safe_text}</div>',
                                    unsafe_allow_html=True,
                                )
                            placeholder.markdown(
                                f'<div class="result-text">{html.escape(full_text)}</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            full_text = recognize_text(client, image_bytes, mime_type, streaming=False)

                    st.session_state["last_result"] = full_text
                    st.session_state["last_file"] = uploaded_file.name
                    st.session_state["last_timestamp"] = datetime.now().strftime("%H:%M:%S")
                    st.success("Transcription completed successfully.")
                except Exception as exc:
                    st.error(f"Recognition failed: {exc}")
                    st.caption("Check the API key and verify the selected model is available.")
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
                <div class="card-title">Transcription Result</div>
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

        metric_a, metric_b, metric_c = st.columns(3)
        metric_a.metric("Words", word_count)
        metric_b.metric("Characters", char_count)
        metric_c.metric("Processed At", timestamp)

        st.download_button(
            label="Download Transcription",
            data=result_text,
            file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=False,
        )
        if st.button("Re-evaluate Transcription"):
            if not api_key:
                st.error("Enter your Groq API key in the sidebar before running re-evaluation.")
            elif not st.session_state.get("uploaded_image_bytes"):
                st.error("Please upload and process an image before re-evaluating the transcription.")
            else:
                try:
                    client = Groq(api_key=api_key)
                    with st.spinner("Re-evaluating transcription..."):
                        review_result = reevaluate_text(
                            client,
                            st.session_state["uploaded_image_bytes"],
                            result_text,
                            st.session_state.get("uploaded_mime_type", "image/jpeg"),
                        )

                    if review_result.strip() == "The transcription is correct.":
                        st.info("Verification result: The transcription is correct.")
                    else:
                        st.session_state["last_result"] = review_result
                        st.success("Verification result: The transcription was reviewed and corrected.")
                        st.rerun()
                except Exception as exc:
                    st.error(f"Re-evaluation failed: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)


init_session_state()
render_navbar()
api_key_input, use_streaming = render_sidebar()
api_key = api_key_input.strip() if api_key_input else os.environ.get("GROQ_API_KEY", "")

if st.session_state.page == "home":
    render_home_page()
else:
    render_upload_page(api_key, use_streaming)
