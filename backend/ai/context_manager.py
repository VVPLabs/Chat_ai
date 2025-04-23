import os


from dotenv import load_dotenv, find_dotenv
from pydantic import SecretStr
from tiktoken import encoding_for_model
# from langchain.schema import Document
# from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
# from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import  BaseMessage




_=load_dotenv(find_dotenv())

GOOGLE_API_KEY=os.environ["GOOGLE_API_KEY"]

# pc= Pinecone(pinecone_api_key=PINECONE_KEY)

# embeddings= GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=SecretStr(GOOGLE_API_KEY))
# index_name="ai-chat"
# index=pc.Index(index_name)

# vector_store= PineconeVectorStore(index=index, embedding=embeddings, pinecone_api_key=PINECONE_KEY)



def count_tokens(messages: list[BaseMessage]) -> int:
    encoding = encoding_for_model("gpt-3.5-turbo")
    num_tokens = 0
    for message in messages:
        num_tokens += len(encoding.encode(str(message.content)))
        num_tokens += 4  # Approximate overhead per message
    return num_tokens

def trim_messages(messages: list[BaseMessage], max_tokens: int = 4000) -> list[BaseMessage]:
    if not messages:
        return messages

    # Always keep the system message if it exists
    system_message = None
    chat_messages = messages.copy()

    if messages[0].type == "system":
        system_message = chat_messages.pop(0)

    current_tokens = count_tokens(chat_messages)

    while current_tokens > max_tokens and len(chat_messages) > 1:
        chat_messages.pop(0)
        current_tokens = count_tokens(chat_messages)

    if system_message:
        chat_messages.insert(0, system_message)

    for message in chat_messages:
        print(message)

    return chat_messages