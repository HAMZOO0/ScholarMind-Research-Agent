import streamlit as st
import json
from src import chat, getAllMemory, MEMORY, MEMORY_INIT_ERROR

st.set_page_config(page_title="ScholarMind", page_icon="🔬", layout="wide")

# Injecting Claude Code-style dark grey theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    .stApp {
        background: #111111;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #161616 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }

    .panel-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #d4d4d4 0%, #a3a3a3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }

    .dashboard-card {
        background: #1a1a1a;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
        position: relative;
        overflow: hidden;
    }

    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
    }

    .dashboard-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }

    .youtube-card:hover {
        border-color: rgba(239, 68, 68, 0.35);
        box-shadow: 0 8px 24px rgba(239, 68, 68, 0.1);
    }

    .card-title-link {
        text-decoration: none !important;
        font-weight: 600;
        color: #e5e5e5;
        transition: color 0.2s ease;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.35;
        font-size: 0.92rem;
        margin-bottom: 0.3rem;
    }

    .card-title-link:hover {
        color: #ffffff !important;
    }

    .youtube-card .card-title-link:hover {
        color: #fca5a5 !important;
    }

    .card-badge-row {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        margin: 0.25rem 0 0.4rem 0;
        flex-wrap: wrap;
    }

    .badge {
        padding: 0.15rem 0.45rem;
        border-radius: 9999px;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
    }

    .badge-stars {
        background-color: rgba(255, 255, 255, 0.06);
        color: #d4d4d4;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .badge-yt {
        background-color: rgba(239, 68, 68, 0.08);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }

    .badge-topic {
        background-color: rgba(255, 255, 255, 0.05);
        color: #a3a3a3;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .card-desc-text {
        font-size: 0.875rem;
        color: #737373;
        line-height: 1.5;
        margin-bottom: 0.8rem;
    }

    .action-btn-link {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.82rem;
        font-weight: 600;
        color: #d4d4d4;
        text-decoration: none !important;
        transition: all 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 0.3rem 0.65rem;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.04);
    }

    .action-btn-link:hover {
        color: #ffffff !important;
        background-color: #2d2d2d;
        border-color: rgba(255, 255, 255, 0.22);
        transform: translateX(2px);
    }

    .youtube-card .action-btn-link {
        color: #f87171;
        border-color: rgba(239, 68, 68, 0.2);
        background-color: rgba(239, 68, 68, 0.04);
    }

    .youtube-card .action-btn-link:hover {
        color: #ffffff !important;
        background-color: #b91c1c;
        border-color: #b91c1c;
    }

    /* Custom tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #1a1a1a;
        padding: 5px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 7px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #737373;
        background-color: transparent;
        transition: all 0.2s ease;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #e5e5e5;
        background-color: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Streamlit container video override */
    .element-container iframe {
        border-radius: 10px !important;
    }

    /* Buttons styling */
    div.stButton > button:first-child {
        background: #242424;
        color: #e5e5e5;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background: #2e2e2e;
        border-color: rgba(255, 255, 255, 0.2);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }

    /* Plus button styling */
    div[data-testid="stPopover"] button {
        background-color: #1e1e1e !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #a3a3a3 !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.35rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        margin-top: 5px !important;
    }
    div[data-testid="stPopover"] button:hover {
        background-color: #2a2a2a !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }

    /* Clamp heading sizes inside chat bubbles so ## doesn't render huge */
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2 {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #e5e5e5 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.25rem !important;
        letter-spacing: 0.01em;
    }
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] h4 {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #d4d4d4 !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.2rem !important;
    }
    [data-testid="stChatMessage"] p {
        font-size: 0.9rem !important;
        line-height: 1.65 !important;
        color: #c4c4c4 !important;
    }
    [data-testid="stChatMessage"] li {
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
        color: #c4c4c4 !important;
    }
    [data-testid="stChatMessage"] a {
        color: #818cf8 !important;
        text-decoration: underline !important;
        text-underline-offset: 2px;
    }
    [data-testid="stChatMessage"] a:hover {
        color: #a5b4fc !important;
    }
    [data-testid="stChatMessage"] code {
        font-size: 0.82rem !important;
        background: #2a2a2a !important;
        color: #a3e635 !important;
        padding: 0.1rem 0.35rem !important;
        border-radius: 4px !important;
    }
    [data-testid="stChatMessage"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 0.75rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    USER_ID = st.text_input("Your User ID", value="user_01", placeholder="Enter your user ID...")
# --- Init session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_model" not in st.session_state:
    st.session_state.last_model = None

# --- Sidebar ---
with st.sidebar:
    st.title("ScholarMind")
    st.caption("Powered by Groq + Mem0 + LangChain + MCP Server")
    st.divider()

    # Active model indicator
    st.subheader("Active Model")
    if st.session_state.last_model:
        model_name = st.session_state.last_model
        # Shorten display name
        label_map = {
            "openai/gpt-oss-120b":      ("GPT-OSS 120B", "#6366f1"),
            "qwen/qwen3.6-27b":         ("Qwen 3.6-27B", "#0ea5e9"),
            "llama-3.3-70b-versatile":  ("LLaMA 3.3-70B", "#10b981"),
            "qwen/qwen3-32b":           ("Qwen 3-32B",    "#f59e0b"),
            "openai/gpt-oss-20b":       ("GPT-OSS 20B",   "#ef4444"),
        }
        display, color = label_map.get(model_name, (model_name, "#737373"))
        st.markdown(f"""
        <div style="background:{color}18;border:1px solid {color}55;border-radius:8px;
                    padding:0.5rem 0.75rem;display:flex;align-items:center;gap:0.5rem;">
            <span style="width:8px;height:8px;border-radius:50%;background:{color};
                         display:inline-block;box-shadow:0 0 6px {color};"></span>
            <span style="color:{color};font-weight:600;font-size:0.85rem;">{display}</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"`{model_name}`")
    else:
        st.caption("No request yet.")
    st.divider()

    st.subheader("Memory")
    # Memory system health indicator
    if MEMORY is not None:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.5rem;">
            <span style="width:8px;height:8px;border-radius:50%;background:#10b981;
                         display:inline-block;box-shadow:0 0 5px #10b981;"></span>
            <span style="color:#10b981;font-size:0.78rem;font-weight:600;">Memory system online</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.5rem;">
            <span style="width:8px;height:8px;border-radius:50%;background:#ef4444;
                         display:inline-block;"></span>
            <span style="color:#ef4444;font-size:0.78rem;font-weight:600;">Memory system offline</span>
        </div>""", unsafe_allow_html=True)
        if MEMORY_INIT_ERROR:
            with st.expander("Show error"):
                st.code(MEMORY_INIT_ERROR, language="text")

    if st.button("View all memories", use_container_width=True):
        memories = getAllMemory(USER_ID)
        items = memories.get("results", []) if isinstance(memories, dict) else memories
        if items:
            for item in items:
                if isinstance(item, dict) and item.get("memory"):
                    st.info(item["memory"])
        else:
            if MEMORY is None:
                st.error("Memory system failed to initialize. Check the error above.")
            else:
                st.caption("No memories stored yet for this user ID.")

    st.divider()
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Area (GPT-style Single Column) ---
st.title("ScholarMind")
st.caption("Ask questions, explore papers, search code, and find videos in one unified chat.")

# Message container
_hist_label_map = {
    "openai/gpt-oss-120b":     ("GPT-OSS 120B", "#6366f1"),
    "qwen/qwen3.6-27b":        ("Qwen 3.6-27B", "#0ea5e9"),
    "llama-3.3-70b-versatile": ("LLaMA 3.3-70B", "#10b981"),
    "qwen/qwen3-32b":          ("Qwen 3-32B",    "#f59e0b"),
    "openai/gpt-oss-20b":      ("GPT-OSS 20B",   "#ef4444"),
}
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("model_used"):
            m = msg["model_used"]
            disp, col = _hist_label_map.get(m, (m, "#737373"))
            st.markdown(f"""
            <div style="margin-top:0.4rem;display:flex;align-items:center;gap:0.4rem;">
                <span style="width:7px;height:7px;border-radius:50%;background:{col};
                             display:inline-block;"></span>
                <span style="color:{col};font-size:0.75rem;font-weight:600;opacity:0.8;">{disp}</span>
            </div>""", unsafe_allow_html=True)
        
        # Render YouTube results inline for the assistant
        if msg.get("youtube_results"):
            st.markdown('<div class="panel-header" style="font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem;">YouTube Insights</div>', unsafe_allow_html=True)
            for yt in msg["youtube_results"]:
                vid = yt.get('video_id', '')
                thumb = f"https://img.youtube.com/vi/{vid}/mqdefault.jpg" if vid else ""
                st.markdown(f"""
                <div class="dashboard-card youtube-card" style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <a href="{yt.get('url')}" target="_blank" style="flex-shrink:0;">
                        <img src="{thumb}" style="width:110px;height:62px;object-fit:cover;border-radius:6px;" onerror="this.style.display='none'"/>
                    </a>
                    <div style="flex:1;min-width:0;">
                        <a href="{yt.get('url')}" target="_blank" class="card-title-link">{yt.get('title', 'Video')}</a>
                        <div class="card-badge-row">
                            <span class="badge badge-yt">YouTube</span>
                        </div>
                        <a href="{yt.get('url')}" target="_blank" class="action-btn-link">Watch ➜</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Render GitHub results inline for the assistant
        if msg.get("github_results"):
            st.markdown('<div class="panel-header" style="font-size:0.95rem;margin-top:0.75rem;margin-bottom:0.35rem;">GitHub Repositories</div>', unsafe_allow_html=True)
            for repo in msg["github_results"]:
                st.markdown(f"""
                <div class="dashboard-card">
                    <a href="{repo.get('url')}" target="_blank" class="card-title-link">{repo.get('name')}</a>
                    <div class="card-badge-row">
                        <span class="badge badge-stars">★ {repo.get('stars', 0):,}</span>
                        <span class="badge badge-topic">GitHub</span>
                    </div>
                    <div class="card-desc-text">{repo.get('desc')}</div>
                    <a href="{repo.get('url')}" target="_blank" class="action-btn-link">View Repo ➜</a>
                </div>
                """, unsafe_allow_html=True)

# --- Tool configurations popover (GPT-style plus button selector) ---
col_pop, col_space = st.columns([1, 10])
with col_pop:
    with st.popover("+", help="Configure active skills"):
        st.markdown("Toggle active skills for this query:")
        tool_options = {
            "Web Search": "web_search",
            "arXiv Paper Search": "arxiv_search",
            "arXiv Paper Reader": "fetch_arxiv_paper",
            "PubMed Medical Search": "pubmed_search",
            "GitHub Repo Search": "github_search",
            "YouTube Video Search": "youtube_search",
        }
        enabled_tools = []
        for label, tool_id in tool_options.items():
            if st.checkbox(label, value=True):
                enabled_tools.append(tool_id)
                # Auto-enable transcript tool when youtube search is active
                if tool_id == "youtube_search":
                    enabled_tools.append("youtube_transcript")
        
        st.divider()
        st.markdown("""
        **Slash Commands:**
        - `/search <query>` — Web Search
        - `/papers <topic>` — arXiv Paper Search
        - `/paper <id>` — Read arXiv Paper by ID
        - `/pubmed <topic>` — PubMed Medical Search
        - `/git <query>` — GitHub Search
        - `/yt <query>` — YouTube Search
        - `/sub <video_id>` — YouTube Transcript
        """)

# --- Chat Input ---
if prompt := st.chat_input("Ask anything or use command (e.g. /yt, /git)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            res = chat(user_id=USER_ID, user_message=prompt, enabled_tools=enabled_tools)
        
        reply = res.get("reply", "No response generated.")
        model_used = res.get("model_used", "")
        st.markdown(reply)

        # Model badge under the reply
        if model_used:
            st.session_state.last_model = model_used
            label_map = {
                "openai/gpt-oss-120b":     ("GPT-OSS 120B", "#6366f1"),
                "qwen/qwen3.6-27b":        ("Qwen 3.6-27B", "#0ea5e9"),
                "llama-3.3-70b-versatile": ("LLaMA 3.3-70B", "#10b981"),
                "qwen/qwen3-32b":          ("Qwen 3-32B",    "#f59e0b"),
                "openai/gpt-oss-20b":      ("GPT-OSS 20B",   "#ef4444"),
            }
            display, color = label_map.get(model_used, (model_used, "#737373"))
            st.markdown(f"""
            <div style="margin-top:0.5rem;display:flex;align-items:center;gap:0.4rem;">
                <span style="width:7px;height:7px;border-radius:50%;background:{color};
                             display:inline-block;box-shadow:0 0 5px {color};"></span>
                <span style="color:{color};font-size:0.75rem;font-weight:600;opacity:0.85;">
                    {display}
                </span>
            </div>
            """, unsafe_allow_html=True)

        yt_data = res.get("youtube_results", [])
        gh_data = res.get("github_results", [])
        
        if yt_data:
            st.markdown('<div class="panel-header" style="font-size:0.95rem;margin-top:0.75rem;margin-bottom:0.35rem;">YouTube Insights</div>', unsafe_allow_html=True)
            for yt in yt_data:
                vid = yt.get('video_id', '')
                thumb = f"https://img.youtube.com/vi/{vid}/mqdefault.jpg" if vid else ""
                st.markdown(f"""
                <div class="dashboard-card youtube-card" style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <a href="{yt.get('url')}" target="_blank" style="flex-shrink:0;">
                        <img src="{thumb}" style="width:110px;height:62px;object-fit:cover;border-radius:6px;" onerror="this.style.display='none'"/>
                    </a>
                    <div style="flex:1;min-width:0;">
                        <a href="{yt.get('url')}" target="_blank" class="card-title-link">{yt.get('title', 'Video')}</a>
                        <div class="card-badge-row">
                            <span class="badge badge-yt">YouTube</span>
                        </div>
                        <a href="{yt.get('url')}" target="_blank" class="action-btn-link">Watch ➜</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if gh_data:
            st.markdown('<div class="panel-header" style="font-size:0.95rem;margin-top:0.75rem;margin-bottom:0.35rem;">GitHub Repositories</div>', unsafe_allow_html=True)
            for repo in gh_data:
                st.markdown(f"""
                <div class="dashboard-card">
                    <a href="{repo.get('url')}" target="_blank" class="card-title-link">{repo.get('name')}</a>
                    <div class="card-badge-row">
                        <span class="badge badge-stars">★ {repo.get('stars', 0):,}</span>
                        <span class="badge badge-topic">GitHub</span>
                    </div>
                    <div class="card-desc-text">{repo.get('desc')}</div>
                    <a href="{repo.get('url')}" target="_blank" class="action-btn-link">View Repo ➜</a>
                </div>
                """, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "youtube_results": yt_data,
        "github_results": gh_data,
        "model_used": model_used,
    })
    st.rerun()