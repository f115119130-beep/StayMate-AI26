"""AI 客服：頁面說明與可重用標題。

現有 Gradio UI 事件綁定暫時保留在 app.py，避免拆分造成失效。
"""
TITLE = 'AI 客服'
DESCRIPTION = 'LLM + Agent + RAG，免登入可聊天'

def render_heading(gr):
    return gr.Markdown(f"## {TITLE}\n{DESCRIPTION}")
