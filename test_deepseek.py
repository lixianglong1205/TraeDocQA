import getpass
import os
from dotenv import load_dotenv

load_dotenv()
# Set API key if not already in environment
if not os.environ.get("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for DeepSeek: ")

from langchain.chat_models import init_chat_model

from langchain_core.prompts import ChatPromptTemplate

llm = init_chat_model(
    "deepseek-chat",
    model_provider="deepseek",
    temperature=0.1  # Matches your original temperature
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个FAQ提取助手。请从用户问题中提取相关的问题-答案对。"),
    ("human", "1+2**=?")
])

chain = prompt | llm

# print(llm.invoke("你好").content)

print(chain.invoke({}).content)