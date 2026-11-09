import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env")

client = OpenAI(
    api_key=os.getenv("EMBEDDING_API_KEY"),
    base_url=os.getenv("EMBEDDING_API_URL")
)

response = client.embeddings.create(
    model=os.getenv("EMBEDDING_MODEL_NAME"),
    input=["晴旅小屋提供每日早餐服務。"],
    encoding_format="float"
)

vector = response.data[0].embedding

print("Embedding API 測試成功！")
print("向量維度：", len(vector))
print("前五個數值：", vector[:5])