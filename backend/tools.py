from dotenv import load_dotenv, find_dotenv
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.prebuilt import ToolNode
from langchain_google_community import GmailToolkit
from langchain_experimental.utilities import PythonREPL
from langchain_google_community.gmail.utils import (
    get_gmail_credentials,
    build_resource_service,
)

load_dotenv(find_dotenv())
search = GoogleSerperAPIWrapper(gl="in", hl="en")

toolkit = GmailToolkit()
credentials = get_gmail_credentials(
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json",
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)

gmail_tools = toolkit.get_tools()

python_repl = PythonREPL()

tools = [
    *gmail_tools,
    Tool(
        name="search",
        func=search.run,
        description="useful for when you need to ask with search",
    ),
    Tool(
        name="python_repl",
        description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
        func=python_repl.run,
    ),
]

tool_node = ToolNode(tools)
