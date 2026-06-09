"""
ResearchAI — Multi-Agent Company Research Assistant
Built with CrewAI + Streamlit
"""

import streamlit as st
import os
import sys
import io
import threading
import time
import queue
from datetime import datetime
from dotenv import load_dotenv

# ── Must be the very first Streamlit call ────────────────────────────────────
st.set_page_config(
    page_title="ResearchAI — Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

# ── Injected CSS — Premium Dark Theme ────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0a0a0f;
    color: #e2e8f0;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f1a; }
::-webkit-scrollbar-thumb { background: #3b3b5c; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #6366f1; }

/* ── Hero Header ── */
.hero-header {
    background: linear-gradient(135deg, #0f0f1a 0%, #13131f 50%, #0a0a0f 100%);
    border: 1px solid #1e1e35;
    border-radius: 20px;
    padding: 2.5rem 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -60px; left: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-header::after {
    content: '';
    position: absolute;
    bottom: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(168,85,247,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.35);
    color: #a5b4fc;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0 0%, #a5b4fc 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin: 0 0 0.6rem 0;
}
.hero-subtitle {
    color: #64748b;
    font-size: 1rem;
    font-weight: 400;
    margin: 0;
    max-width: 540px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d0d18 !important;
    border-right: 1px solid #1e1e35 !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid #1e1e35;
}
.sidebar-logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.sidebar-logo-text {
    font-weight: 700; font-size: 1.1rem;
    background: linear-gradient(135deg, #a5b4fc, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.sidebar-section-title {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin: 1.2rem 0 0.6rem 0;
}
.api-key-note {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 0.75rem;
    font-size: 0.78rem;
    color: #94a3b8;
    line-height: 1.5;
    margin-top: 0.5rem;
}
.api-key-note a { color: #a5b4fc; text-decoration: none; }
.api-key-note a:hover { text-decoration: underline; }
.agent-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid #1e1e35;
    border-radius: 12px;
    padding: 0.85rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s;
}
.agent-card:hover { border-color: #3b3b5c; }
.agent-card-title {
    font-size: 0.82rem; font-weight: 600; color: #a5b4fc;
    margin-bottom: 0.25rem;
}
.agent-card-desc {
    font-size: 0.73rem; color: #475569; line-height: 1.4;
}
.agent-tool-badge {
    display: inline-block;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.25);
    color: #818cf8;
    font-size: 0.62rem;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    margin-top: 0.4rem;
}

/* ── Input Area ── */
.input-card {
    background: #0d0d18;
    border: 1px solid #1e1e35;
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
}
.input-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 0.5rem;
    letter-spacing: 0.02em;
}
[data-testid="stTextInput"] input {
    background: #13131f !important;
    border: 1px solid #2a2a45 !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 1rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: #3b3b5c !important; }

/* ── Launch Button ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3) !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    opacity: 0.92 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button:disabled {
    opacity: 0.4 !important;
    transform: none !important;
    cursor: not-allowed !important;
}

/* ── Status Cards ── */
.status-running {
    background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(168,85,247,0.08));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.status-dot {
    width: 10px; height: 10px;
    background: #6366f1;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(99,102,241,0.4); }
    50% { opacity: 0.7; transform: scale(1.1); box-shadow: 0 0 0 6px rgba(99,102,241,0); }
}
.status-text { font-size: 0.9rem; color: #a5b4fc; font-weight: 500; }
.status-subtext { font-size: 0.78rem; color: #475569; margin-top: 0.1rem; }

/* ── Pipeline Steps ── */
.pipeline-container {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    margin: 1rem 0;
}
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    border: 1px solid transparent;
    transition: all 0.3s;
}
.pipeline-step.pending {
    background: rgba(255,255,255,0.02);
    border-color: #1e1e35;
    color: #3b3b5c;
}
.pipeline-step.active {
    background: rgba(99,102,241,0.08);
    border-color: rgba(99,102,241,0.35);
    color: #a5b4fc;
}
.pipeline-step.done {
    background: rgba(34,197,94,0.06);
    border-color: rgba(34,197,94,0.25);
    color: #4ade80;
}
.step-icon { font-size: 1rem; min-width: 24px; text-align: center; }
.step-label { font-size: 0.85rem; font-weight: 500; }

/* ── Log Container ── */
.log-container {
    background: #08080f;
    border: 1px solid #1a1a2e;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    line-height: 1.7;
    color: #64748b;
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}
.log-line-agent { color: #818cf8; }
.log-line-task  { color: #34d399; }
.log-line-tool  { color: #fbbf24; }
.log-line-done  { color: #4ade80; font-weight: 600; }

/* ── Report Output ── */
.report-wrapper {
    background: #0d0d18;
    border: 1px solid #1e1e35;
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-top: 1.5rem;
    position: relative;
    overflow: hidden;
}
.report-wrapper::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
    border-radius: 20px 20px 0 0;
}
.report-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #1e1e35;
}
.report-title-text {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
}
.report-meta {
    font-size: 0.72rem;
    color: #475569;
}
.report-content h2 {
    color: #a5b4fc !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    margin-top: 1.8rem !important;
    margin-bottom: 0.6rem !important;
    padding-bottom: 0.4rem !important;
    border-bottom: 1px solid #1e1e35 !important;
}
.report-content h3 {
    color: #c084fc !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    margin-top: 1rem !important;
}
.report-content p { color: #94a3b8 !important; line-height: 1.75 !important; }
.report-content ul, .report-content ol {
    color: #94a3b8 !important;
    line-height: 1.8 !important;
}
.report-content li { margin-bottom: 0.2rem !important; }
.report-content strong { color: #e2e8f0 !important; }
.report-content a { color: #818cf8 !important; }
.report-content code {
    background: #13131f !important;
    border: 1px solid #2a2a45 !important;
    border-radius: 4px !important;
    padding: 0.1rem 0.4rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82em !important;
    color: #c084fc !important;
}
.report-content blockquote {
    border-left: 3px solid #6366f1 !important;
    background: rgba(99,102,241,0.06) !important;
    padding: 0.6rem 1rem !important;
    border-radius: 0 8px 8px 0 !important;
    color: #94a3b8 !important;
}

/* ── Success / Error Banners ── */
.success-banner {
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    color: #4ade80;
    font-weight: 500;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.error-banner {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    color: #f87171;
    font-size: 0.88rem;
    line-height: 1.5;
}

/* ── Metric Cards ── */
.metrics-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    flex: 1;
    background: rgba(255,255,255,0.02);
    border: 1px solid #1e1e35;
    border-radius: 14px;
    padding: 1.1rem;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #3b3b5c; }
.metric-value {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a5b4fc, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-label {
    font-size: 0.72rem;
    color: #475569;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 0.2rem;
}

/* ── Selectbox / Checkbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #13131f !important;
    border: 1px solid #2a2a45 !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
[data-testid="stCheckbox"] label { color: #94a3b8 !important; font-size: 0.85rem !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0d0d18 !important;
    border: 1px solid #1e1e35 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: rgba(99,102,241,0.1) !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    color: #a5b4fc !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(99,102,241,0.2) !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.2) !important;
}

/* ── Divider ── */
hr { border-color: #1e1e35 !important; margin: 1.2rem 0 !important; }

</style>
""",
    unsafe_allow_html=True,
)


# ── Session State ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "running": False,
        "report": None,
        "error": None,
        "elapsed": 0,
        "log_lines": [],
        "company_searched": "",
        "run_count": 0,
        "last_run_time": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ── Stdout Capture Helper ─────────────────────────────────────────────────────
class StreamCapture(io.StringIO):
    """Captures stdout and pushes lines into a thread-safe queue."""
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self._queue = log_queue

    def write(self, text: str):
        if text and text.strip():
            self._queue.put(text)
        return len(text)

    def flush(self):
        pass


# ── Crew Runner ───────────────────────────────────────────────────────────────
def run_crew_thread(company: str, result_container: dict, log_queue: queue.Queue):
    """Runs in a background thread so Streamlit can stay responsive."""
    old_stdout = sys.stdout
    sys.stdout = StreamCapture(log_queue)
    try:
        from crew import create_research_crew
        research_crew = create_research_crew(company)
        result = research_crew.kickoff(inputs={"company_name": company})
        # CrewAI may return CrewOutput; convert to string
        result_container["output"] = str(result) if result else "No output returned."
        result_container["error"] = None
    except Exception as exc:
        result_container["output"] = None
        result_container["error"] = str(exc)
    finally:
        sys.stdout = old_stdout
        log_queue.put("__DONE__")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">🔬</div>
            <div class="sidebar-logo-text">ResearchAI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('\u003cdiv class="sidebar-section-title"\u003e🔑 LLM Provider\u003c/div\u003e', unsafe_allow_html=True)

    llm_provider = st.radio(
        "Choose your AI provider",
        ["🟢 OpenAI", "🔵 Google Gemini"],
        index=0,
        help="Pick one — you only need one API key.",
        label_visibility="collapsed",
    )

    if llm_provider == "🟢 OpenAI":
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Get yours at platform.openai.com",
        )
        gemini_key = ""
        st.markdown(
            '<div class="api-key-note">💡 Get a key at '
            '<a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com</a>'
            "</div>",
            unsafe_allow_html=True,
        )
        openai_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
        model_choice = st.selectbox("Model", openai_models, index=0, help="gpt-4o-mini is fastest & cheapest.")
    else:
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Get yours at aistudio.google.com — free!",
        )
        openai_key = ""
        st.markdown(
            '<div class="api-key-note">💡 Free tier available at '
            '<a href="https://aistudio.google.com" target="_blank">aistudio.google.com</a>'
            "</div>",
            unsafe_allow_html=True,
        )
        gemini_models = ["gemini/gemini-2.0-flash", "gemini/gemini-1.5-flash", "gemini/gemini-1.5-pro"]
        model_choice = st.selectbox("Model", gemini_models, index=0, help="gemini-2.0-flash is fastest & free.")

    st.markdown('\u003cdiv class="sidebar-section-title"\u003e🔑 Search Key\u003c/div\u003e', unsafe_allow_html=True)
    serper_key = st.text_input(
        "Serper API Key",
        type="password",
        placeholder="Your Serper key",
        value=os.getenv("SERPER_API_KEY", ""),
        help="Required for web search. Free tier at serper.dev",
    )
    st.markdown(
        '<div class="api-key-note">💡 Free tier at '
        '<a href="https://serper.dev" target="_blank">serper.dev</a></div>',
        unsafe_allow_html=True,
    )

    show_logs = st.checkbox("Show agent logs", value=True)

    # Save keys to environment for this session
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ.pop("GEMINI_API_KEY", None)  # clear other provider
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
        os.environ.pop("OPENAI_API_KEY", None)  # clear other provider
    if serper_key:
        os.environ["SERPER_API_KEY"] = serper_key


    st.markdown('<div class="sidebar-section-title">🤖 Agent Pipeline</div>', unsafe_allow_html=True)

    agents_info = [
        ("🔍", "Web Researcher", "Searches the web for news, financials & product info.", "SerperDevTool"),
        ("🕷️", "Data Extractor", "Scrapes company websites & articles via Jina.ai.", "Jina.ai Scraper"),
        ("📝", "Report Editor", "Synthesises findings into a structured report.", "LLM Synthesis"),
    ]
    for icon, title, desc, tool_badge in agents_info:
        st.markdown(
            f"""
            <div class="agent-card">
                <div class="agent-card-title">{icon} {title}</div>
                <div class="agent-card-desc">{desc}</div>
                <div class="agent-tool-badge">{tool_badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.session_state.run_count > 0:
        st.markdown(
            f"""
            <div style="font-size:0.72rem; color:#3b3b5c; text-align:center;">
            ✅ {st.session_state.run_count} research run{"s" if st.session_state.run_count != 1 else ""} completed
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-badge">✦ Multi-Agent AI Research</div>
        <h1 class="hero-title">ResearchAI</h1>
        <p class="hero-subtitle">
            A three-agent CrewAI system that autonomously searches the web,
            scrapes sources, and compiles a professional intelligence report
            on any company or product — in minutes.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Metrics Row ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="metrics-row">
        <div class="metric-card">
            <div class="metric-value">3</div>
            <div class="metric-label">AI Agents</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">3</div>
            <div class="metric-label">Tasks</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">2</div>
            <div class="metric-label">Web Tools</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">∞</div>
            <div class="metric-label">Companies</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input Card ────────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown('<div class="input-label">🏢 Enter company or product name</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([3, 1])
with col_input:
    company_input = st.text_input(
        label="company",
        label_visibility="collapsed",
        placeholder="e.g.  OpenAI,  Tesla,  Notion,  Stripe ...",
        disabled=st.session_state.running,
        key="company_input_field",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)

llm_key_ok = bool(os.getenv("OPENAI_API_KEY")) or bool(os.getenv("GEMINI_API_KEY"))
keys_ok = llm_key_ok and bool(os.getenv("SERPER_API_KEY"))
launch_btn = st.button(
    "🚀  Launch Research Crew",
    disabled=st.session_state.running or not company_input.strip() or not keys_ok,
    use_container_width=True,
)

if not keys_ok:
    if not llm_key_ok:
        st.markdown(
            '<div style="font-size:0.78rem; color:#f87171; margin-top:0.5rem;">'
            "⚠️  Please enter an OpenAI <strong>or</strong> Gemini API key in the sidebar."
            "</div>",
            unsafe_allow_html=True,
        )
    elif not os.getenv("SERPER_API_KEY"):
        st.markdown(
            '<div style="font-size:0.78rem; color:#f87171; margin-top:0.5rem;">'
            "⚠️  Please enter your Serper API key in the sidebar before running."
            "</div>",
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)


# ── Launch Logic ──────────────────────────────────────────────────────────────
if launch_btn and company_input.strip() and keys_ok:
    # Pass selected model to crew via env
    os.environ["RESEARCH_MODEL_NAME"] = model_choice

    # Reset state
    st.session_state.running = True
    st.session_state.report = None
    st.session_state.error = None
    st.session_state.log_lines = []
    st.session_state.company_searched = company_input.strip()
    st.session_state.start_time = time.time()

    # Shared containers for thread results
    result_container: dict = {"output": None, "error": None}
    log_queue: queue.Queue = queue.Queue()

    # Start crew in background thread
    t = threading.Thread(
        target=run_crew_thread,
        args=(company_input.strip(), result_container, log_queue),
        daemon=True,
    )
    t.start()

    # ── Live Progress UI ──────────────────────────────────────────────────────
    status_ph = st.empty()
    pipeline_ph = st.empty()
    log_ph = st.empty() if show_logs else None
    timer_ph = st.empty()

    pipeline_stages = [
        ("🔍", "Web Researcher", "Searching the internet..."),
        ("🕷️", "Data Extractor", "Scraping websites & articles..."),
        ("📝", "Report Editor", "Compiling intelligence report..."),
    ]

    def render_pipeline(active_idx: int, done_indices: list[int]):
        html = '<div class="pipeline-container">'
        for i, (icon, label, sub) in enumerate(pipeline_stages):
            if i in done_indices:
                cls, step_icon = "done", "✅"
            elif i == active_idx:
                cls, step_icon = "active", "⏳"
            else:
                cls, step_icon = "pending", "○"
            html += (
                f'<div class="pipeline-step {cls}">'
                f'<span class="step-icon">{step_icon}</span>'
                f'<span class="step-label">{icon} {label}</span>'
                f"</div>"
            )
        html += "</div>"
        return html

    elapsed = 0
    active_stage = 0
    done_stages: list[int] = []
    all_logs: list[str] = []
    stage_keywords = [
        ["researcher", "searching", "search agent"],
        ["extractor", "scraping", "scrape", "website"],
        ["editor", "compiling", "report", "writing"],
    ]

    while t.is_alive() or not log_queue.empty():
        elapsed = time.time() - st.session_state.start_time
        mins, secs = divmod(int(elapsed), 60)

        # Drain log queue
        while not log_queue.empty():
            try:
                line = log_queue.get_nowait()
                if line == "__DONE__":
                    break
                all_logs.append(line)
                # Detect stage progression
                lower = line.lower()
                for si, kws in enumerate(stage_keywords):
                    if any(kw in lower for kw in kws):
                        if si > active_stage and si - 1 not in done_stages:
                            done_stages.append(active_stage)
                            active_stage = si
                        break
            except queue.Empty:
                break

        # Status header
        status_ph.markdown(
            f"""
            <div class="status-running">
                <div class="status-dot"></div>
                <div>
                    <div class="status-text">
                        Agents are working on: <strong>{st.session_state.company_searched}</strong>
                    </div>
                    <div class="status-subtext">
                        Elapsed: {mins:02d}:{secs:02d} — This usually takes 2–5 minutes
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Pipeline
        pipeline_ph.markdown(render_pipeline(active_stage, done_stages), unsafe_allow_html=True)

        # Logs
        if log_ph and all_logs:
            recent = all_logs[-60:]  # last 60 lines
            log_text = "\n".join(recent)
            log_ph.markdown(
                f'<div class="log-container">{log_text}</div>',
                unsafe_allow_html=True,
            )

        time.sleep(1.2)

    # Thread finished
    t.join(timeout=5)

    # Clear live widgets
    status_ph.empty()
    pipeline_ph.empty()
    if log_ph:
        log_ph.empty()
    timer_ph.empty()

    st.session_state.running = False
    st.session_state.elapsed = time.time() - st.session_state.start_time
    st.session_state.last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if result_container["error"]:
        st.session_state.error = result_container["error"]
    else:
        st.session_state.report = result_container["output"]
        st.session_state.run_count += 1
        st.session_state.log_lines = all_logs

    st.rerun()


# ── Display Results ───────────────────────────────────────────────────────────
if st.session_state.error:
    st.markdown(
        f"""
        <div class="error-banner">
            ❌ <strong>Research failed:</strong><br><br>
            {st.session_state.error}
            <br><br>
            <strong>Common fixes:</strong><br>
            • Verify your API keys are correct (OpenAI or Gemini + Serper)<br>
            • Make sure you selected the right model for the key you provided<br>
            • Check you have API credits remaining<br>
            • Try again — web requests occasionally time out
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.report:
    mins, secs = divmod(int(st.session_state.elapsed), 60)

    st.markdown(
        f"""
        <div class="success-banner">
            ✅ Research complete for <strong>{st.session_state.company_searched}</strong>
            &nbsp;·&nbsp; Finished in {mins}m {secs}s
            &nbsp;·&nbsp; {st.session_state.last_run_time}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Report Card ───────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="report-wrapper">
            <div class="report-header">
                <div class="report-title-text">
                    📊 Intelligence Report — {st.session_state.company_searched}
                </div>
                <div class="report-meta">
                    Generated {st.session_state.last_run_time} &nbsp;·&nbsp; CrewAI v3
                </div>
            </div>
            <div class="report-content">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(st.session_state.report)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Actions Row ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_dl_md, col_dl_txt, col_new = st.columns([1, 1, 2])
    with col_dl_md:
        st.download_button(
            label="⬇️  Download Markdown",
            data=st.session_state.report,
            file_name=f"research_{st.session_state.company_searched.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_dl_txt:
        st.download_button(
            label="⬇️  Download TXT",
            data=st.session_state.report,
            file_name=f"research_{st.session_state.company_searched.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with col_new:
        if st.button("🔄  Start New Research", use_container_width=True):
            st.session_state.report = None
            st.session_state.error = None
            st.session_state.log_lines = []
            st.rerun()

    # ── Agent Log Expander ────────────────────────────────────────────────────
    if show_logs and st.session_state.log_lines:
        with st.expander("🔎 View Full Agent Log", expanded=False):
            st.markdown(
                f'<div class="log-container">{"".join(st.session_state.log_lines)}</div>',
                unsafe_allow_html=True,
            )


# ── Empty State ───────────────────────────────────────────────────────────────
if not st.session_state.report and not st.session_state.error and not st.session_state.running:
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 3.5rem 2rem;
            color: #3b3b5c;
            border: 1px dashed #1e1e35;
            border-radius: 16px;
            margin-top: 0.5rem;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔬</div>
            <div style="font-size: 1.05rem; font-weight: 600; color: #475569; margin-bottom: 0.5rem;">
                Ready to research
            </div>
            <div style="font-size: 0.85rem; color: #334155; max-width: 340px; margin: 0 auto; line-height: 1.6;">
                Enter any company or product name above, add your API keys in the sidebar,
                then click <strong style="color:#6366f1;">Launch Research Crew</strong>.
            </div>
            <div style="margin-top: 1.5rem; display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap;">
                <span style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
                    color:#6366f1;font-size:0.78rem;padding:0.3rem 0.8rem;border-radius:999px;">OpenAI</span>
                <span style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
                    color:#6366f1;font-size:0.78rem;padding:0.3rem 0.8rem;border-radius:999px;">Tesla</span>
                <span style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
                    color:#6366f1;font-size:0.78rem;padding:0.3rem 0.8rem;border-radius:999px;">Notion</span>
                <span style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
                    color:#6366f1;font-size:0.78rem;padding:0.3rem 0.8rem;border-radius:999px;">Stripe</span>
                <span style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);
                    color:#6366f1;font-size:0.78rem;padding:0.3rem 0.8rem;border-radius:999px;">Anthropic</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
