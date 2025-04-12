from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.base import BaseCheckpointSaver

from llm import llm_model
from tools import tool_node
from context_manager import trim_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    state["messages"] = trim_messages(state["messages"], max_tokens=4000)
    system_message = "You are a helpful assistant. You are a human being. Talk like a human. You can use tools whenever required if you feel the need for it."
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
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile(checkpointer=saver)
