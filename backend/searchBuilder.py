from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.utilities import GoogleSerperAPIWrapper
from typing_extensions import TypedDict
from typing import List
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())


search = GoogleSerperAPIWrapper(gl="in", hl="en")


class OptimizedWebSearchState(TypedDict):
    question: List[str]
    optimized_web_request: str
    documents: List[str]
    search_links: List[str]
    scraped_pages: List[str]
    final_answer: str


def optimize_queries(state: OptimizedWebSearchState):
    from llm import llm_with_tools

    print("\n[OPTIMIZE QUERIES] Input state:", state)

    system_message = """
    You are a helpful assistant that improves user questions to make them clearer and more specific for web search.

    You will receive a user message that may be vague, conversational, or casually phrased.
    Your job is to rewrite it into a focused, search-friendly statement that captures the user’s intent in a way that search engines will understand.

    Guidelines:
    - Keep the original meaning, but improve clarity and focus.
    - Convert casual or question-style messages into fact-based search phrases.
    - Avoid vague or opinion-based words like “should”, “could”, “best”, or “is it good to”.
    - Do NOT add any details the user didn't mention.
    - Use natural, simple language—but make sure the query is complete and informative.
    - If the user asks about current events, sports, news, tools, etc., make sure the phrasing helps fetch **live or real-time** results.
    - NEVER return just a single word or ultra-short phrase—your output should be clear, structured, and useful.

    Only return the improved query as plain text. No extra formatting, explanations, or responses—just the rewritten query.
    """

    human_message = HumanMessage(content=(f"user_request: {state['question'][0]}"))

    optimized_response = llm_with_tools.invoke([system_message, human_message])
    optimized_web_request = optimized_response.content
    print("[OPTIMIZE QUERIES] Optimized request:", optimized_web_request)

    return {**state, "optimized_web_request": optimized_web_request}


def search_web(state: OptimizedWebSearchState):

    print("\n[SEARCH WEB] Optimized query:", state["optimized_web_request"])

    response = search.results(state["optimized_web_request"])
    print("[SEARCH WEB] Raw search response:", response)

    if isinstance(response, str):
        return {**state, "documents": [response], "search_links": []}

    organic_results = response.get("organic", [])
    links = []
    snippets = []

    for result in organic_results:
        if "link" in result:
            links.append(result["link"])
        if "snippet" in result:
            snippets.append(result["snippet"])
        for sitelink in result.get("sitelinks", []):
            if "link" in sitelink:
                links.append(sitelink["link"])

    combined_snippets = "\n\n".join(snippets)
    print("[SEARCH WEB] Extracted snippets:", combined_snippets[:500])
    print("[SEARCH WEB] Top links:", links[:3])

    return {**state, "documents": [combined_snippets], "search_links": links[:3]}


def generate_answer(state: OptimizedWebSearchState):
    from llm import llm

    print("\n[GENERATE ANSWER] Generating answer from content...")

    system_message = SystemMessage(
        content="You are a helpful assistant. Use the provided web content to answer the user's question clearly and accurately."
    )

    combined_docs = "\n\n".join(state["scraped_pages"] + state["documents"])

    human_message = HumanMessage(
        content=f"""User's original question: {state['question'][0]}
        Documents:{combined_docs}
        Answer the user's question based only on the information above. If the documents don't help, say so clearly."""
    )

    response = llm.invoke([system_message, human_message])
    print("[GENERATE ANSWER] Final answer:", response.content)

    return {**state, "final_answer": response.content}


# Define and compile the graph
optimized_web_search_builder = StateGraph(OptimizedWebSearchState)
optimized_web_search_builder.add_node("optimize_queries", optimize_queries)
optimized_web_search_builder.add_node("search_web", search_web)
optimized_web_search_builder.add_node("generate_answer", generate_answer)

optimized_web_search_builder.add_edge(START, "optimize_queries")
optimized_web_search_builder.add_edge("optimize_queries", "search_web")
optimized_web_search_builder.add_edge("search_web", "generate_answer")
optimized_web_search_builder.add_edge("generate_answer", END)

web_search = optimized_web_search_builder.compile()


def web_search_tool_fn(query: str) -> str:
    state = {
        "question": [query],
        "optimized_web_request": "",
        "documents": [],
        "search_links": [],
        "scraped_pages": [],
        "final_answer": "",
    }
    result = web_search.invoke(state)
    return result["final_answer"]
