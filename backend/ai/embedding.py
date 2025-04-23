import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

from typing import List

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.parsers import TesseractBlobParser
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain.indexes import SQLRecordManager, index
from langchain_pinecone import PineconeVectorStore
from langchain_hyperbrowser import HyperbrowserLoader

from langchain_core.runnables import chain
from langchain_core.documents import Document
from config import settings
from pinecone import Pinecone, ServerlessSpec

# from langchain_google_genai import GoogleGenerativeAIEmbeddings


_ = load_dotenv(find_dotenv())

PINECONE_KEY = settings.PINECONE_KEY
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
HYPERBROWSER_API_KEY = settings.HYPERBROWSER_API_KEY

# embeddings = GoogleGenerativeAIEmbeddings(
#     model="models/embedding-001", google_api_key=SecretStr(GOOGLE_API_KEY)
# )

model_name = "ViT-H-14"
checkpoint = "laion2b_s32b_b79k"

embeddings = OpenCLIPEmbeddings(model_name=model_name, checkpoint=checkpoint)

text_splitter = SemanticChunker(
    OpenCLIPEmbeddings(), breakpoint_threshold_type="gradient"
)

pc = Pinecone(api_key=PINECONE_KEY)
index_name = "gecp"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )


pinecone_index = pc.Index(index_name)
vector_store = PineconeVectorStore(
    index=pinecone_index, embedding=embeddings, pinecone_api_key=PINECONE_KEY
)

namespace = f"pinecone/{index_name}"
record_manager = SQLRecordManager(
    namespace, db_url="sqlite:///record_manager_cache.sql"
)
record_manager.create_schema()


def load_and_embed_documents():
    path = f"sample_data/somatosensory.pdf"
    loader = PyMuPDFLoader(
        file_path=Path(path).resolve(),
        mode="page",
        images_inner_format="html-img",
        images_parser=TesseractBlobParser(),
        extract_tables="markdown",
    )
    documents = loader.load()

    docs = text_splitter.split_documents(documents)

    for i, doc in enumerate(docs):
        doc.metadata["source"] = str(Path(path).name)

    index(
        docs_source=docs,
        record_manager=record_manager,
        vector_store=vector_store,
        cleanup="incremental",
        source_id_key="source",
    )

    print("Documents successfully added to Pinecone.")


def load_and_embed_websites():
    base_url = "https://gecpatan.ac.in/"
    visited = set()
    to_visit = [base_url]
    discovered_urls = []
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyBot/1.0; +http://example.com/bot)"
    }

    while to_visit:
        url = to_visit.pop()
        if url in visited or not url.startswith(base_url):
            continue
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            visited.add(url)
            discovered_urls.append(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                next_url = urljoin(url, a_tag["href"])  # type: ignore
                if next_url.startswith(base_url) and next_url not in visited:
                    to_visit.append(next_url)
            time.sleep(1)

        except Exception as e:
            print(f"Error visiting {url}: {e}")

    print(f"Found {discovered_urls} URLs")

    loader = HyperbrowserLoader(
        urls=discovered_urls,
        api_key=HYPERBROWSER_API_KEY,
    )
    documents = loader.load()

    docs = text_splitter.split_documents(documents)

    for i, doc in enumerate(docs):
        source = doc.metadata.get("sourceURL") or doc.metadata.get("url") or f"doc_{i}"
        doc.metadata["source"] = source

    index(
        docs_source=docs,
        record_manager=record_manager,
        vector_store=vector_store,
        cleanup="incremental",
        source_id_key="source",
    )

    print("Documents successfully added to Pinecone.")


@chain
def retriever(query: str):
    docs, scores = zip(*vector_store.similarity_search_with_score(query))
    for doc, score in zip(docs, scores):
        doc.metadata["score"] = score

    return docs
