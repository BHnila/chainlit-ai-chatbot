from openai import AsyncOpenAI
import chainlit as cl
import os

openai_key = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=openai_key)


settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": """You are a students assistant chatbot named ""FEI Ragbot"". Your expertise is 
        exclusively in providing information and advice about anything related to 
        study at the Faculty of electrical engineering and informatics of Slovak Technical 
        University in Bratislava, Slovakia. 
        This includes advices to students, administration informations, and general
        study-related queries. You do not provide information outside of this 
        scope. If a question is not about study at this university, respond with, "I specialize 
        only in Slovak Technical University related queries."""}],
    )


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    await msg.send()

    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()