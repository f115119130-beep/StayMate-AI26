"""首頁：頁面說明與可重用標題。

現有 Gradio UI 事件綁定暫時保留在 app.py，避免拆分造成失效。
"""
TITLE = '首頁'
DESCRIPTION = '飯店介紹、快速查房、免登入 AI'

def render_heading(gr):
    return gr.Markdown(f"## {TITLE}\n{DESCRIPTION}")
