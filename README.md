# StayMate-AI26 — Sunny Stay 晴旅小屋 (V2.2)

本機課程示範：**LLM + Agent (Tool Calling) + RAG (TF-IDF)**，加上會員登入、查房、SQLite 訂房、會員個人訂單與全站浮動 AI 客服。

## 本機執行

1. 使用 Python 3.10+，在虛擬環境中執行 `pip install -r requirements.txt`。
2. 複製 `.env.example` 為 `.env`，只在自己的電腦填入學校提供的 `MODEL_NAME`、`API_KEY`、`LLM_API_URL`。**不要將 `.env` 上傳 GitHub。**
3. 執行 `python app.py`，瀏覽 `http://127.0.0.1:7860`。
4. 免登入可使用「AI 客服」及右下角浮動 AI。註冊會員後可查房並建立模擬訂單，再問 AI「我的訂單有哪些？」。

## AI 三大技術

- **LLM**：透過學校 OpenAI-compatible API 呼叫 `MODEL_NAME`。
- **Agent**：`run_agent` 根據需求呼叫 `list_rooms`、`check_room_availability`、`get_my_bookings` 等工具，並顯示 Tool Trace。
- **RAG**：`rag_tfidf.py` 以 TF-IDF 從 `hotel_rules.txt` 搜尋相關政策，再提供給 LLM。

## 訂房與安全

- 訪客可查詢房型與模擬庫存，但只有已登入會員能建立、查詢或取消自己的訂單。
- `prepare_booking` 只建立建議草稿；正式訂單由顧客在訂房頁按下確認後才寫入 SQLite。
- 會員查詢工具從伺服器驗證的 session 取得身分，AI 不可指定 user_id。
- 訂房以 SQLite `BEGIN IMMEDIATE` 交易重新檢查每晚庫存，避免超額訂房。
- `hotel_app.db` 與 `bookings.db` 均為本機產生，不上傳 GitHub。
- 這是虛構飯店與模擬訂單，不含真實付款、真實房間庫存或商用登入安全保證。登入工作階段保存在本機記憶體，重新啟動後須重新登入。

## GitHub


## 測試


## 模組化目錄說明

- `services/booking_service.py` 是實際使用的會員、庫存及訂房邏輯；`booking_backend.py` 是舊版匯入相容層。
- `services/auth_service.py`、`services/room_service.py`、`database/connection.py` 提供可重用介面。
- `tools/booking_tools.py` 提供獨立查房與個人訂單查詢介面。
- `pages/*.py` 目前是頁面元件的起點；**完整的 Gradio 頁面與 AI Agent 事件綁定仍在 `app.py`**，尚未完成全部 UI 拆分。
- `rag_tfidf.py` 是 RAG 實作；`app.py` 保留 LLM Agent Tool Calling。

此版本重點是保持原有可執行的展示程式，同時建立後續拆分目錄；不要把目錄存在誤認為所有程式已完成分層。
