from operator import itemgetter

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableLambda
from langchain.schema.runnable.config import RunnableConfig
from langchain.memory import ConversationBufferMemory

from chainlit.types import ThreadDict
import chainlit.data as cl_data
import chainlit as cl
import os

import chainlit.data as cl_data
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from sqlalchemy.ext.asyncio import create_async_engine

from pathlib import Path


#A very simple storage client for a demo app data manipulation
class LocalStorageClient:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, data: bytes) -> str:
        file_path = self.base_path / filename
        with open(file_path, 'wb') as f:
            f.write(data)
        return str(file_path)

    def load(self, filename: str) -> bytes:
        file_path = self.base_path / filename
        with open(file_path, 'rb') as f:
            return f.read()

    def delete(self, filename: str):
        file_path = self.base_path / filename
        if file_path.exists():
            file_path.unlink()


# Define the connection string to your PostgreSQL database
conninfo = os.getenv("POSTGRES_CONNINFO")

# Create the SQLAlchemy async engine for PostgreSQL
engine = create_async_engine(conninfo, echo=True)

# Initialize the local storage client
local_storage_client = LocalStorageClient('/DATA')

# Replace the AzureStorageClient with a connection to PostgreSQL
cl_data._data_layer = SQLAlchemyDataLayer(
    conninfo=conninfo,
    ssl_require=False,
    storage_provider=local_storage_client,  
    user_thread_limit=100
)


#Function to setup langchain LLM connection
def setup_runnable():
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    model = ChatOpenAI(streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            You are a student's assistant chatbot named "FEI Ragbot". Your expertise is 
            exclusively in providing information and advice about anything related to 
            study at the Faculty of electrical engineering and informatics of Slovak Technical 
            University in Bratislava, Slovakia. 
            This includes advices to students, administration informations, and general
            study-related queries. You do not provide information outside of this 
            scope. If a question is not about study at this university, respond with, "I specialize 
            only in Slovak Technical University related queries."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    runnable = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | model
        | StrOutputParser()
    )
    cl.user_session.set("runnable", runnable)


#Mock auth flow
@cl.password_auth_callback
def auth():
    return cl.User(identifier="test")


#Function that sets four starters for welcome screen
@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Morning routine ideation",
            message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
            icon="/public/terminal.svg",
            ),

        cl.Starter(
            label="Explain superconductors",
            message="Explain superconductors like I'm five years old.",
            icon="/public/terminal.svg",
            ),
        cl.Starter(
            label="Python script for daily email reports",
            message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up.",
            icon="/public/terminal.svg",
            ),
        cl.Starter(
            label="Text inviting friend to Klub 39",
            message="Write a text asking a friend to be my plus-one at a wedding next month. I want to keep it super short and casual, and offer an out.",
            icon="/public/terminal.svg",
            )
        ]


#Set app environment before start
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    setup_runnable()


#What to do when chat is resumed from chat history
@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])

    cl.user_session.set("memory", memory)

    setup_runnable()


#Handle user prompt and LLM response
@cl.on_message
async def on_message(message: cl.Message):
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory

    runnable = cl.user_session.get("runnable")  # type: Runnable

    res = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await res.stream_token(chunk)

    await res.send()

    memory.chat_memory.add_user_message(message.content)
    memory.chat_memory.add_ai_message(res.content)