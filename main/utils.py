import os
import uuid
import openai
import aiofiles
import json
from aiogram import Bot
from aiogram.types import Message
from settings.config import settings
from settings.models import SessionLocal, UserValue
from validation import extract_user_value

openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())


async def download_voice(bot: Bot, message: Message) -> str:
    file = await bot.get_file(message.voice.file_id)
    unique_id = uuid.uuid4()

    downloads_dir = os.path.join(os.path.dirname(__file__), "..", "data", "downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    file_path = os.path.join(downloads_dir, f"{unique_id}.ogg")

    await bot.download_file(file.file_path, file_path)

    return file_path


async def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        response = await openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return response.text


async def get_assistant_response(prompt: str) -> str:
    assistant_id = settings.ASSISTANT_DEFAULT_API_KEY.get_secret_value()

    thread = await openai_client.beta.threads.create()

    await openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Answer a question: {prompt}"
    )

    run = await openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    if run.status == "completed":
        messages = await openai_client.beta.threads.messages.list(
            thread_id=thread.id
        )
        return messages.data[0].content[0].text.value
    else:
        raise Exception(f"Run did not complete successfully. Status: {run.status}")


async def text_to_speech(text: str, language: str) -> str:
    voice = {
        "English": "alloy",
        "Russian": "onyx"
    }.get(language, "alloy")

    response = await openai_client.audio.speech.create(
        model="tts-1",
        input=text,
        voice=voice
    )

    audio_responses_dir = os.path.join(os.path.dirname(__file__), "..", "data", "audio_responses")
    os.makedirs(audio_responses_dir, exist_ok=True)

    unique_id = uuid.uuid4()
    file_path = os.path.join(audio_responses_dir, f"output_{unique_id}.mp3")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(response.content)

    return file_path


async def create_thread():
    return await openai_client.beta.threads.create()


async def send_message_to_thread(thread_id: str, content: str):
    await openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )


async def run_assistant(thread_id: str, assistant_id: str):
    run = await openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run


async def get_thread_messages(thread_id: str):
    messages = await openai_client.beta.threads.messages.list(
        thread_id=thread_id
    )
    return messages.data[0].content[0].text.value


async def generate_question(thread_id: str, user_input: str):
    await send_message_to_thread(thread_id, user_input)

    run = await run_assistant(thread_id, settings.ASSISTANT_VALUES_API_KEY.get_secret_value())

    if run.status == "completed":
        question = await get_thread_messages(thread_id)
        return question
    else:
        raise Exception(f"Run did not complete successfully. Status: {run.status}")


async def analyze_user_response(thread_id: str, user_input: str):

    await send_message_to_thread(thread_id, user_input)

    run = await run_assistant(thread_id, settings.ASSISTANT_VALUES_API_KEY.get_secret_value())

    if run.status == "completed":
        messages = await openai_client.beta.threads.messages.list(thread_id=thread_id)

        for message in messages.data:
            if message.role == "assistant":
                response_text = message.content[0].text.value
                value = await extract_user_value(response_text)
                return value

    # if run.status == "requires_action":
    #     tool_outputs = []
    #
    #     for tool_call in run.required_action.submit_tool_outputs.tool_calls:
    #         if tool_call.function.name == "save_value":
    #             arguments = json.loads(tool_call.function.arguments)
    #             value = arguments.get("value")
    #             user_id = arguments.get("user_id")
    #
    #             validation_result = await analyze_user_response(thread_id, user_input)
    #
    #             if validation_result and validation_result.is_valid:
    #                 await save_value(validation_result.value, user_id)
    #                 tool_outputs.append({
    #                     "tool_call_id": tool_call.id,
    #                     "output": "Value saved successfully"
    #                 })
    #             else:
    #                 tool_outputs.append({
    #                     "tool_call_id": tool_call.id,
    #                     "output": "Invalid value, please ask user more questions"
    #                 })
    #
    #     await openai_client.beta.threads.runs.submit_tool_outputs(
    #         thread_id=thread_id,
    #         run_id=run.id,
    #         tool_outputs=tool_outputs,
    #     )
    #
    #     return validation_result if validation_result.is_valid else None

    return None


async def save_value(value: str, user_id: int):

    async with SessionLocal() as session:
        new_value = UserValue(user_id=user_id, value=value)
        session.add(new_value)
        await session.commit()
