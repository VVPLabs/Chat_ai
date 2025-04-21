import operator

from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.base import BaseCheckpointSaver

from llm import llm_model
from tools import tool_node
from context_manager import trim_messages
from searchBuilder import web_search


class State(TypedDict):
    messages: Annotated[list, add_messages]
    question: Annotated[list, operator.add]
    search_answer: str


def chatbot(state: State):
    state["messages"] = trim_messages(state["messages"], max_tokens=4000)
    system_message = """
    You are a friendly and helpful assistant who communicates like a real human — casual, natural, and thoughtful.
    You have access to a variety of tools, including the ability to search the web for real-time information.
    Feel free to use them anytime they can help you give more accurate, current, or complete answers —
    especially when the user’s request involves breaking news, live data, recent updates, current events, or anything time-sensitive.
    Your goal is to be genuinely helpful, grounded, and easy to talk to — like a smart friend who always knows how to find the right info.
       """
    response = llm_model.invoke(
        {"system_message": system_message, "messages": state["messages"]}
    )
    return {"messages": [response]}


def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"
    return END


def compile_graph(saver: BaseCheckpointSaver):
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("search_graph", web_search)

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile(checkpointer=saver)
