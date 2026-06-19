try:
    from langchain.agents import create_agent
    print("SUCCESS: imported create_agent from langchain.agents")
except ImportError as e:
    print(f"FAILED: {e}")

try:
    from langgraph.prebuilt import create_react_agent
    print("SUCCESS: imported create_react_agent from langgraph.prebuilt")
except ImportError as e:
    print(f"FAILED: {e}")
