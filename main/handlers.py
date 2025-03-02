import os
from aiogram import Bot
from aiogram.types import Message
from utils import (
    download_voice,
    transcribe_audio,
    text_to_speech,
    create_thread,
    generate_question,
    analyze_user_response,
    get_assistant_response,
    save_value,
)
from aiogram.types import FSInputFile

user_states = {}


async def process_voice(bot: Bot, message: Message, language: str):
    file_path = await download_voice(bot, message)
    text = await transcribe_audio(file_path)
    response_text = await get_assistant_response(text)
    audio_path = await text_to_speech(response_text, language)

    await message.answer(f"You ask: {text}")
    voice_file = FSInputFile(audio_path)
    await message.answer_voice(voice=voice_file)

    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(audio_path):
        os.remove(audio_path)


async def start_value_dialogue(user_id: int, message: Message):
    thread = await create_thread()
    user_states[user_id] = {"thread_id": thread.id}

    initial_question = "What is most important to you in life?"

    await message.reply(initial_question)


async def handle_user_value(user_id: int, user_input: str, message: Message):
    if user_id not in user_states:
        response = await get_assistant_response(user_input)
        await message.reply(response)
        return

    thread_id = user_states[user_id]["thread_id"]
    validation_result = await analyze_user_response(thread_id, user_input)

    if validation_result and validation_result.is_valid:
        await save_value(validation_result.value, user_id)

        await message.reply(f"Your key value has been identified: '{validation_result.value}'. It has been saved!")

    question = await generate_question(thread_id, user_input)
    await message.reply(question)
