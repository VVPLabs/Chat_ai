import os

from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import SecretStr
from config import settings
from .tools import tools


_ = load_dotenv(find_dotenv())

GOOGLE_API_KEY = settings.GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", api_key=SecretStr(GOOGLE_API_KEY), temperature=0
)

llm_with_tools = llm.bind_tools(tools)
prompt_template = ChatPromptTemplate.from_messages(
    [("system", "{system_message}"), MessagesPlaceholder("messages")]
)

llm_model = prompt_template | llm_with_tools
