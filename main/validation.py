from openai import AsyncOpenAI
from settings.schemas import ValidationResult
from settings.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())


async def extract_user_value(user_input: str) -> ValidationResult:
    completion = await client.beta.chat.completions.parse(
        model="gpt-4.5-preview-2025-02-27",
        messages=[
            {"role": "system", "content": "You are an expert at extracting key values from user input. Extract the user's key value. you have to analyze the key value of the user and understand whether it is correctly identified or not."},
            {"role": "user", "content": user_input},
        ],
        response_format=ValidationResult,
    )

    return completion.choices[0].message.parsed
