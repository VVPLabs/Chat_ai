import os
import logging
import traceback

from fastapi import FastAPI, HTTPException, Response
from contextlib import asynccontextmanager
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


from graph import compile_graph

logging.basicConfig(level=logging.INFO)

_ = load_dotenv(find_dotenv())

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
    "row_factory": dict_row,
}

database_connection_pool = AsyncConnectionPool(
    conninfo=os.environ["DB_URL"],
    max_size=20,
    open=False,
    kwargs=connection_kwargs,
)

app = FastAPI(lifespan=lambda app: lifespan(app))

graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph
    await database_connection_pool.open()
    try:
        async with database_connection_pool.connection() as conn:
            saver = AsyncPostgresSaver(conn)
            await saver.setup()
            graph = compile_graph(saver)
    except Exception as e:
        logging.error(f"Error setting up database: {type(e).__name__} - {e}")
        raise
    yield
    await database_connection_pool.close()


class ChatInput(BaseModel):
    messages: list[str]
    thread_id: str


@app.get("/")
async def welcome():
    return Response(content="Hello")


@app.post("/chat")
async def chat(input: ChatInput):

    try:
        response = await graph.ainvoke(  # type: ignore
            {"messages": input.messages},
            config={"configurable": {"thread_id": input.thread_id}}
        )
        logging.info(f"Response: {response['messages']}")
        return response["messages"][-1].content
    except Exception as e:
        logging.error(f"Error processing chat: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
