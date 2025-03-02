import openai
import asyncio
from settings.config import settings

client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())


async def create_value_saver_assistant():
    assistant = await client.beta.assistants.create(
        name="Value Saver Assistant",
        instructions="""
        You are a personal assistant that helps users save their key values to the database.
        When you receive a key value, use the save_value function to save it.
        """,
        tools=[{
            "type": "function",
            "function": {
                "name": "save_value",
                "description": "Save the user's key value to the database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "string",
                            "description": "The key value of the user."
                        },
                        "user_id": {
                            "type": "integer",
                            "description": "The ID of the user."
                        }
                    },
                    "required": ["value", "user_id"]
                }
            }
        }],
        model="gpt-4-turbo"
    )
    return assistant.id


async def main():
    assistant_id = await create_value_saver_assistant()
    print("Assistant ID:", assistant_id)

asyncio.run(main())
