# Example: reuse your existing OpenAI setup
import os
import uuid
from functools import partial

import requests

from openai import OpenAI

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
CHATBOT_ENDPOINT = os.getenv("CHATBOT_ENDPOINT")
CHATBOT_API_TOKEN = os.getenv("CHATBOT_API_TOKEN")


def ask_llm(system_message: str, message: str, model: str):
    """"""
    # Point to the local server
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {"role": "user", "content": message},
        ],
        temperature=0.1,
    )
    return completion.choices[0].message.content


def send_message(conversation_id, message):
    headers = {
        "Authorization": f"Bearer {CHATBOT_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "conversation_id": conversation_id,
        "message": message,
    }

    response = requests.post(CHATBOT_ENDPOINT, headers=headers, json=payload)
    return response.json()


ask_llm_to_create_question = partial(ask_llm, system_message="You are an expert question generator. When given some text, you create some questions about it. Return only the question and nothing else.")
ask_llm_to_create_answer = partial(ask_llm, system_message="You are an expert answer generator. When given some text, you create an answer to a question about the text. Return only the answer and nothing else.")
ask_llm_to_assess_answer = partial(ask_llm, system_message="You are an expert fact checker. When presented with a question, the answer and reference text, you state YES/NO if the question has been answered correctly.")

