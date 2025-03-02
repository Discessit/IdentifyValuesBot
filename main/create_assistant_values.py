import openai
import asyncio
from settings.config import settings

client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())


async def create_value_extractor_assistant():
    assistant = await client.beta.assistants.create(
        name="Value Extractor Assistant",
        instructions="""
           You are a personal assistant that helps users identify their key values.
           Your task is to ask the user a series of questions to understand what is most important to them in life.
           Start by asking: "What is most important to you in life?"
           Then, based on their response, ask follow-up questions to dig deeper into their values.
           When you identify a key value, call the 'extract_value' function to pass it to the bot.
           Be concise and ask only relevant questions.
           Do not wait for the user to specify the context — start the conversation immediately.
           """,
        tools=[{
            "type": "function",
            "function": {
                "name": "extract_value",
                "description": "Extract the user's key value from their response.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "string",
                            "description": "The key value of the user."
                        }
                    },
                    "required": ["value"]
                }
            }
        }],
        model="gpt-4.5-preview-2025-02-27"
    )
    return assistant.id


async def main():
    assistant_id = await create_value_extractor_assistant()
    print("Assistant ID:", assistant_id)

asyncio.run(main())