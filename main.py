import chainlit as cl
import os

from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.memory.buffer import ConversationBufferMemory
from langchain.prompts import PromptTemplate

conversation_memory = ConversationBufferMemory(memory_key="chat_history",
                                               max_len=50,
                                               return_messages=True,
                                                   )

ice_cream_assistant_template = """
        You are a students assistant chatbot named "FEI Ragbot". Your expertise is 
        exclusively in providing information and advice about anything related to 
        study at the Faculty of electrical engineering and informatics of Slovak Technical 
        University in Bratislava, Slovakia. 
        This includes advices to students, administration informations, and general
        study-related queries. You do not provide information outside of this 
        scope. If a question is not about study at this university, respond with, "I specialize 
        only in Slovak Technical University related queries."
        Chat History: {chat_history}
        Question: {question}
        Answer:
        """

ice_cream_assistant_prompt_template = PromptTemplate(
    input_variables=["chat_history", "question"],
    template=ice_cream_assistant_template
)

openai_api_key = os.getenv("OPENAI_API_KEY")

@cl.on_chat_start
def quey_llm():
    llm = OpenAI(model='gpt-3.5-turbo-instruct',
                 temperature=0,openai_api_key=openai_api_key)
    
    conversation_memory = ConversationBufferMemory(memory_key="chat_history",
                                                   max_len=50,
                                                   return_messages=True,
                                                   )
    llm_chain = LLMChain(llm=llm, 
                         prompt=ice_cream_assistant_prompt_template,
                         memory=conversation_memory)
    
    cl.user_session.set("llm_chain", llm_chain)


@cl.on_message
async def query_llm(message: cl.Message):
    llm_chain = cl.user_session.get("llm_chain")
    
    response = await llm_chain.acall(message.content, 
                                     callbacks=[
                                         cl.AsyncLangchainCallbackHandler()])
    
    await cl.Message(response["text"]).send()