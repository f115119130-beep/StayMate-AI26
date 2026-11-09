"""查房訂房：頁面說明與可重用標題。

現有 Gradio UI 事件綁定暫時保留在 app.py，避免拆分造成失效。
"""
TITLE = '查房訂房'
DESCRIPTION = '日期、人數、模擬庫存與確認訂房'

def render_heading(gr):
    return gr.Markdown(f"## {TITLE}\n{DESCRIPTION}")
