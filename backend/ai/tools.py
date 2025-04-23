import os

from dotenv import load_dotenv, find_dotenv
from langchain_core.tools import Tool
from langgraph.prebuilt import ToolNode
from langchain_google_community import GmailToolkit
from langchain_experimental.utilities import PythonREPL
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from config import settings

from .searchBuilder import web_search_tool_fn
from langchain_google_community.gmail.utils import (
    get_gmail_credentials,
    build_resource_service,
)

_ = load_dotenv(find_dotenv())
OPENWEATHERMAP_API_KEY = settings.OPENWEATHERMAP_API_KEY


weather = OpenWeatherMapAPIWrapper()

credentials = get_gmail_credentials(
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials/credentials.json",
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)
gmail_tools = toolkit.get_tools()

python_repl = PythonREPL()


tools = []

tools = [
    *gmail_tools,
    Tool(
        name="python_repl",
        description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
        func=python_repl.run,
    ),
    Tool(
        name="OpenWeatherMap",
        func=weather.run,
        description="Useful for getting current weather information for a given location. Input should be a city name.",
    ),
    Tool(
        name="web_search",
        func=web_search_tool_fn,
        description=(
            "Searches the web for up-to-date information using a search engine. "
            "Useful for answering questions about current events, live sports, product availability, etc. "
            "Input should be a plain-text search query."
        ),
    ),
]

tool_node = ToolNode(tools)
