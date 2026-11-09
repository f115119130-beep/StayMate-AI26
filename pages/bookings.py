"""我的訂單：頁面說明與可重用標題。

現有 Gradio UI 事件綁定暫時保留在 app.py，避免拆分造成失效。
"""
TITLE = '我的訂單'
DESCRIPTION = '登入後查看與取消個人訂單'

def render_heading(gr):
    return gr.Markdown(f"## {TITLE}\n{DESCRIPTION}")
