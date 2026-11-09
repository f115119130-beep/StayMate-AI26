"""會員中心：頁面說明與可重用標題。

現有 Gradio UI 事件綁定暫時保留在 app.py，避免拆分造成失效。
"""
TITLE = '會員中心'
DESCRIPTION = '註冊、登入、登出'

def render_heading(gr):
    return gr.Markdown(f"## {TITLE}\n{DESCRIPTION}")
