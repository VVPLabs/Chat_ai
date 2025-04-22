import json


from langchain_core.messages import HumanMessage, SystemMessage
from typing_extensions import TypedDict
from typing import List
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())


class OptimizedWebSearchState(TypedDict):
    input: str
    task_goal: Optional[str]
    subtasks: Optional[List[str]]
    plan: Optional[str]
    tools_used: Optional[List[str]]
    feedback: Optional[str]


from langchain_core.runnables import RunnableLambda
from typing import TypedDict, List, Optional


class SubTask(TypedDict):
    goal: str
    deadlines: str
    priority: str


class TaskPlannerState(TypedDict):
    input: str
    goal: Optional[str]
    subtasks: Optional[List[SubTask]]
    conflicts: Optional[bool]
    approval: Optional[bool]
    changes: Optional[str]
    task_added: Optional[bool]


def ExtractGoalNode(state: TaskPlannerState) -> TaskPlannerState:
    from llm import llm_with_tools

    user_input = state["input"]

    system_message = """You are a smart task planning assistant.
    Your job is to extract the **main goal** the user wants to accomplish, based on their input.
    - The goal should be a single sentence describing the primary task or objective.
    - If the user mentions a **specific deadline or date**, include it in the goal.
    - Do NOT include step-by-step instructions or unrelated details.
    - The response should be concise, focused, and no more than 20 words.
    """

    messages = [
        SystemMessage(content=system_message),
        HumanMessage(
            content=f'The user said: "{user_input}"\n What is their main goal?'
        ),
    ]

    response = llm_with_tools.invoke(messages)
    goal = response.content.strip()  # type: ignore
    return {**state, "goal": goal}


def BreakIntoSubtasksNode(state: TaskPlannerState) -> TaskPlannerState:
    from llm import llm_with_tools

    goal = state["goal"]

    system_message = """You are a task planning assistant.
    Your job is to break down a high-level goal into 3 to 6 clear subtasks.
    Each subtask must include:
    - a short description (`goal`)
    - a realistic deadline with time (in natural language or ISO format)
    - a priority (high, medium, or low)

    Ensure deadlines make sense given the overall goal.
    Return the subtasks in the following format:
    [
    {"goal": "...", "deadline": "...", "priority": "..."},
    ]"""

    user_prompt = f"The main goal is: {goal}\n Break it into subtasks."

    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=user_prompt),
    ]

    response = llm_with_tools.invoke(messages)
    subtasks = eval(response.content.strip())  # type: ignore
    return {**state, "subtasks": subtasks}


def ConflictCheckNode():
    pass


def RequestApprovalNode(state: TaskPlannerState):
    pass


def check_conflicts(state: TaskPlannerState) -> TaskPlannerState:
    # Mock calendar conflict check
    conflicts = False  # Imagine checking with Google Calendar here
    return {**state, "conflicts": conflicts}


def ask_human_approval(state: TaskPlannerState) -> TaskPlannerState:
    # Simulate human approval
    print("Prompting user: Add to task manager?")
    approval = True  # Replace with FastAPI endpoint for real-time approval
    return {**state, "approval": approval}


def add_task(state: TaskPlannerState) -> TaskPlannerState:
    added = state["approval"] and not state["conflicts"]
    return {**state, "task_added": added}


# ExtractGoalNode: Parse input to get the goal.

# BreakIntoSubtasksNode: Create subtasks with deadline and priority.

# ConflictCheckNode: Evaluate subtasks against existing schedules → set conflicts.

# RequestApprovalNode: Ask user for confirmation or edits → set approval and possibly changes.

# ApplyChangesNode (optional): Apply changes if any.

# FinalizeTaskNode: If approval, mark task_added = True.


# def human_review_node(state) -> Command[Literal["call_llm", "run_tool"]]:
#     last_message = state["messages"][-1]
#     tool_call = last_message.tool_calls[-1]

#     human_review = interrupt({
#         "question": "Is this correct?",
#         "tool_call": tool_call,
#     })

#     review_action = human_review["action"]
#     review_data = human_review.get("data")

#     if review_action == "continue":
#         return Command(goto="run_tool")

#     elif review_action == "update":
#         updated_message = {
#             "role": "ai",
#             "content": last_message.content,
#             "tool_calls": [
#                 {
#                     "id": tool_call["id"],
#                     "name": tool_call["name"],
#                     "args": review_data,
#                 }
#             ],
#             "id": last_message.id,
#         }
#         return Command(goto="run_tool", update={"messages": [updated_message]})

#     elif review_action == "feedback":
#         tool_message = {
#             "role": "tool",
#             "content": review_data,
#             "name": tool_call["name"],
#             "tool_call_id": tool_call["id"],
#         }
#         return Command(goto="call_llm", update={"messages": [tool_message]})
