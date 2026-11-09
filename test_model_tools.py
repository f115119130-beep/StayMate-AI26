
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

# 1. 載入 .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

print("STEP 1：程式開始執行", flush=True)

if not all([API_KEY, LLM_API_URL, MODEL_NAME]):
    raise ValueError("缺少 API_KEY、LLM_API_URL 或 MODEL_NAME")

print("STEP 2：環境變數讀取完成", flush=True)
print("模型：", MODEL_NAME, flush=True)
print("API URL：", LLM_API_URL, flush=True)

# 2. 建立 API 客戶端
client = OpenAI(
    api_key=API_KEY,
    base_url=LLM_API_URL,
    timeout=20.0,
    max_retries=0,
)

# 3. 定義測試工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_hotel_info",
            "description": "查詢飯店基本資訊，例如入住與退房時間",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "要查詢的飯店資訊主題",
                    }
                },
                "required": ["topic"],
            },
        },
    }
]

# 4. 定義測試訊息
messages = [
    {
        "role": "system",
        "content": (
            "你是晴旅小屋的 AI 客服助手。"
            "當使用者詢問入住或退房時間時，"
            "必須呼叫 get_hotel_info 工具查詢。"
            "不可自行編造飯店資訊。"
        ),
    },
    {
        "role": "user",
        "content": "請查詢飯店入住時間",
    },
]

# 5. 呼叫 NKUST API
print("STEP 3：準備呼叫 NKUST API", flush=True)
print("Tool Choice：auto", flush=True)

start_time = time.perf_counter()

try:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2,
    )

    elapsed = time.perf_counter() - start_time

    print("\nSTEP 4：API 成功回應", flush=True)
    print(f"執行時間：{elapsed:.2f} 秒")
    print("模型：", response.model)

    choice = response.choices[0]
    message = choice.message

    print("結束原因：", choice.finish_reason)
    print("文字回覆：", message.content)

    if message.tool_calls:
        print("\nTool Calling 測試成功！")

        for tool_call in message.tool_calls:
            print("工具名稱：", tool_call.function.name)
            print("工具參數：", tool_call.function.arguments)
            print("工具 ID：", tool_call.id)

        if any(
            call.function.name == "get_hotel_info"
            for call in message.tool_calls
        ):
            print("\n測試結果：PASS")
        else:
            print("\n測試結果：FAIL（呼叫了非預期工具）")
    else:
        print("\n測試結果：未產生工具呼叫")
        print("模型可能沒有選擇工具，或 API 不支援 Tool Calling。")

except Exception as error:
    elapsed = time.perf_counter() - start_time

    print("\nAPI 測試失敗")
    print(f"執行時間：{elapsed:.2f} 秒")
    print("錯誤類型：", type(error).__name__)
    print("錯誤訊息：", str(error))
