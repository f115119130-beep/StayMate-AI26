
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("LLM_API_URL"),
    timeout=60.0,
    max_retries=0,
)

print("開始測試基本聊天 API...", flush=True)
start = time.perf_counter()

try:
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "user", "content": "你好，請回答 OK"}
        ],
        max_tokens=30,
    )

    print("API 成功回應")
    print("耗時：", round(time.perf_counter() - start, 2), "秒")
    print("內容：", response.choices[0].message.content)

except Exception as e:
    print("測試失敗：", type(e).__name__)
    print("耗時：", round(time.perf_counter() - start, 2), "秒")
    print("錯誤：", str(e))
