import os
import json
import atexit
from pathlib import Path

MEMORY_DIR = Path("./user_memories")
MEMORY_INIT_ERROR = None

try:
    MEMORY_DIR.mkdir(exist_ok=True)
    MEMORY = True  # truthy = system online
    print("SUCCESS: Memory initialized (local JSON store)")
except Exception as e:
    MEMORY = None
    MEMORY_INIT_ERROR = str(e)
    print(f"Memory init error: {e}")

_EXTRACT_SYSTEM = (
    "Extract 0-3 personal facts about the user from the message. "
    "Only extract clear facts: name, location, profession, interests, goals. "
    "Return a JSON array of strings only. If nothing factual, return [].\n"
    'Example output: ["Name is Hamza", "From Pakistan", "Software engineer"]'
)


def _load(user_id: str) -> list:
    f = MEMORY_DIR / f"{user_id}.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(user_id: str, memories: list) -> None:
    f = MEMORY_DIR / f"{user_id}.json"
    f.write_text(json.dumps(memories, indent=2, ensure_ascii=False), encoding="utf-8")


# Models tried in order for extraction — separate from chat cascade to avoid competing rate limits
_EXTRACT_MODELS = [
    "groq:llama-3.3-70b-versatile",
    "groq:qwen/qwen3-32b",
    "groq:qwen/qwen3.6-27b",
]


def _extract_facts(user_message: str) -> list:
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import HumanMessage, SystemMessage

    for model_id in _EXTRACT_MODELS:
        try:
            model = init_chat_model(model_id)
            resp = model.invoke([
                SystemMessage(_EXTRACT_SYSTEM),
                HumanMessage(user_message[:400]),
            ])
            raw = resp.content.strip()
            start, end = raw.find("["), raw.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(raw[start:end])
            return []
        except Exception as e:
            print(f"Memory extraction failed with {model_id}: {e}")
    return []


def add_memory(user_id: str, user_message: str, assistant_reply: str) -> None:
    if MEMORY is None:
        return
    try:
        facts = _extract_facts(user_message)
        if facts and isinstance(facts, list):
            existing = _load(user_id)
            existing.extend(str(f) for f in facts)
            _save(user_id, existing)
            print(f"Memory saved: {facts}")
        else:
            print("Memory: no new facts in this message")
    except Exception as e:
        print(f"Memory add failed: {e}")


def get_memories(query: str, user_id: str, limit: int = 5) -> str:
    if MEMORY is None:
        return "(memory system unavailable)"
    memories = _load(user_id)
    if not memories:
        return "(no prior memories yet)"
    # Keyword relevance: prefer memories that share words with the query
    query_words = set(query.lower().split())
    scored = sorted(memories, key=lambda m: len(query_words & set(m.lower().split())), reverse=True)
    return "\n".join(f"- {m}" for m in scored[:limit])


def getAllMemory(user_id: str) -> list:
    if MEMORY is None:
        return []
    return [{"memory": m} for m in _load(user_id)]


atexit.register(lambda: None)  # no Qdrant to close
