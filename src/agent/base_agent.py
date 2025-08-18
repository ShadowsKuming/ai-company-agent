# src/agent/base_agent.py
from smolagents import CodeAgent
from src.config import llm

def build_base_agent():
    return CodeAgent(
        model=llm,
        tools=[],
        max_steps=3
    )

