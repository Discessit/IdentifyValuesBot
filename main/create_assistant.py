import openai
import asyncio
from settings.config import settings


openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())


async def create_assistant():
    assistant = await openai_client.beta.assistants.create(
        name="Personal Assistant",
        instructions="You are a personal assistant. Please answer the questions in the language you will hear, it's either English or Russian.",
        model="gpt-4-turbo",
    )
    return assistant.id


async def main():
    assistant_id = await create_assistant()
    print("Assistant ID:", assistant_id)

asyncio.run(main())