"""AI service contract.

The LLM + agent execution remains implemented in app.py for compatibility
with the existing Gradio event handlers; refactor it here in the next phase.
"""
AI_FEATURES = ("LLM", "Agent tool calling", "TF-IDF RAG")
