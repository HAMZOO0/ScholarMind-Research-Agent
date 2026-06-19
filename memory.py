import warnings
warnings.filterwarnings("ignore")

import os
import atexit
import io
import re
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from mem0 import Memory
from ddgs import DDGS

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

MEM0_CONFIG = {
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "mem0_research_assistant",
            "embedding_model_dims": 384,
            "path": ":memory:",
        },
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dims": 384,
        },
    },
}

SYSTEM_PROMPT_TEMPLATE = """You are an expert research assistant with access to real-time web search and memory of past research sessions.

Your job is to help users research any topic deeply and accurately.

MEMORY CONTEXT FROM PAST SESSIONS:
{memory}

BEHAVIOR:
- Always break complex questions into smaller sub-questions before answering
- Search for the most recent and relevant information
- If you find a relevant arXiv paper ID or URL in web search results, or if the user asks you to read a paper, you MUST use the 'fetch_arxiv_paper' tool to read its full content. Do not summarize it based on web search snippets alone.
- Cross-reference multiple sources before giving a conclusion
- Use the memory context above to build on what the user has already researched
- Never ask the user to repeat context that already exists in memory
- If a topic was researched before, mention it and connect it to the new query
- If memory is empty, treat this as a fresh session

OUTPUT FORMAT:
- Give a clear structured answer with sections
- Always cite your sources with links
- End every response with 3 follow-up questions the user might want to explore
- If the research is complex, summarize key findings at the top

TONE:
- Be precise and factual, not conversational
- Avoid filler phrases
- Be concise but never skip important details

If you do not know something, say so clearly. Never hallucinate facts or sources."""

# --- Init model ---
try:
    model = init_chat_model("groq:llama-3.3-70b-versatile")
    print("SUCCESS: Model initialized")
except Exception as e:
    model = None
    print(f"Model init error: {e}")

# --- Init memory ---
try:
    MEMORY = Memory.from_config(MEM0_CONFIG)
    print("SUCCESS: Memory initialized")
except Exception as e:
    MEMORY = None
    print(f"Memory init error: {e}")


def _format_memories(search_results) -> str:
    items = search_results.get("results", []) if isinstance(search_results, dict) else search_results
    memories = [
        f"- {item['memory']}"
        for item in items
        if isinstance(item, dict) and item.get("memory")
    ]
    return "\n".join(memories) if memories else "(no prior memories yet)"


def _close_memory() -> None:
    if MEMORY is None:
        return
    try:
        MEMORY.vector_store.client.close()
    except Exception:
        pass
    try:
        MEMORY.close()
    except Exception:
        pass

atexit.register(_close_memory)


@tool
def web_search(query: str) -> str:

    """Search the web for the latest information on a topic."""
    print("\n\n\n\n\query:: ",query)
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=2))

    output = []
    for r in results:
        output.append(
            f"""
Title: {r['title']}

URL: {r['href']}

Description:
{r['body']}
"""
        )

    return "\n" + ("-" * 50 + "\n").join(output)


@tool
def fetch_arxiv_paper(arxiv_id_or_url: str) -> str:
    """Download and extract the text content of an arXiv research paper.
    
    This tool is useful when you have an arXiv ID (like '2310.01526') or an arXiv URL (like 'https://arxiv.org/abs/2310.01526')
    and want to read the paper's contents, abstract, introduction, or main findings.
    """
    print("\n\n\n\n\narxiv_id_or_url:: ",arxiv_id_or_url)
    try:
        # Extract the arXiv ID from URL or input
        input_str = arxiv_id_or_url.strip()
        match = re.search(r"arxiv\.org/(?:abs|pdf)/([a-zA-Z0-9./\-]+)", input_str, re.IGNORECASE)
        if match:
            arxiv_id = match.group(1)
            if arxiv_id.endswith(".pdf"):
                arxiv_id = arxiv_id[:-4]
        else:
            arxiv_id = input_str

        url = f"https://arxiv.org/pdf/{arxiv_id}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        
        doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
        
        text = ""
        for page in doc:
            text += page.get_text()
        
        if not text.strip():
            return f"Error: No text could be extracted from the arXiv paper with ID {arxiv_id}."
            
        # Truncate to a reasonable limit to avoid context window overflow/TPM limits (e.g., 12000 characters)
        max_chars = 12000
        if len(text) > max_chars:
            truncated_text = text[:max_chars]
            return (
                f"--- arXiv Paper ID: {arxiv_id} (Truncated to first {max_chars} characters) ---\n\n"
                f"{truncated_text}\n\n"
                f"--- [End of Truncated Content - Total Paper Length: {len(text)} characters] ---"
            )
            
        return f"--- arXiv Paper ID: {arxiv_id} ---\n\n{text}"
        
    except Exception as e:
        return f"Error downloading or parsing the arXiv paper: {str(e)}"


def chat(user_id: str, user_message: str) -> str:
    if MEMORY is None:
        return "Setup error: could not initialize Mem0."
    if model is None:
        return "Setup error: could not initialize model."

    try:
        search_results = MEMORY.search(
            query=user_message,
            filters={"user_id": user_id},
            limit=5
        )
        memory_context = _format_memories(search_results)

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(memory=memory_context)

        # Tools
        tools = [web_search, fetch_arxiv_paper]

        # Create agent
        agent_executor = create_react_agent(model, tools=tools, prompt=system_prompt)

        # Invoke
        response = agent_executor.invoke({"messages": [HumanMessage(content=user_message)]})
        reply = response["messages"][-1].content

        MEMORY.add(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": reply},
            ],
            user_id=user_id,
        )

        return reply

    except Exception as exc:
        return f"Error: {exc}"


def getAllMemory(user_id: str):
    if MEMORY is None:
        return []
    try:
        return MEMORY.get_all(filters={"user_id": user_id})
    except Exception as exc:
        return []