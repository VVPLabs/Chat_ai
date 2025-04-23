import os
import logging
import traceback

from fastapi import APIRouter, FastAPI, HTTPException, Response
from contextlib import asynccontextmanager
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from fastapi.middleware.cors import CORSMiddleware

from ai.graph import compile_graph

logging.basicConfig(level=logging.INFO)

_ = load_dotenv(find_dotenv())

ai_router = APIRouter(prefix="/ai", tags=["AI"])
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database_connection_pool.open()
    logging.info("Database connection pool opened.")
    yield
    await database_connection_pool.close()
    logging.info("Database connection pool closed.")


class ChatInput(BaseModel):
    messages: list[str]
    thread_id: str


@ai_router.get("/")
async def welcome():
    return Response(content="Hello")


@ai_router.post("/chat")
async def chat(input: ChatInput):
    global graph
    try:
        async with database_connection_pool.connection() as conn:
            saver = AsyncPostgresSaver(conn)
            await saver.setup()
            graph = compile_graph(saver)

        response = await graph.ainvoke(  # type: ignore
            {"messages": input.messages},
            config={"configurable": {"thread_id": input.thread_id}},
        )
        logging.info(f"Response: {response['messages']}")
        return response["messages"][-1].content
    except Exception as e:
        logging.error(f"Error processing chat: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


app.include_router(ai_router)
