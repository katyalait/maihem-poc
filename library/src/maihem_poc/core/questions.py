import uuid

import pandas as pd

from maihem_poc.core.ai import ask_llm_to_create_question, ask_llm_to_create_answer, ask_llm_to_assess_answer, send_message
from maihem_poc.data.db import get_vector_db


def generate_question(chunk: str, model: str):
    return ask_llm_to_create_question(
        message=f"Generate a question that the contents of this text can answer: {chunk}", model=model
    )


def generate_answer(question: str, chunk: str, model: str):
    return ask_llm_to_create_answer(
        message=f"Generate the answer to this question {question} from the content of this text: {chunk}", model=model
    )


def get_questions(filename: str):
    try:
        return pd.read_csv(f"{filename}_questions.csv")
    except FileNotFoundError:
        return None


def create_questions(filename: str, model: str):
    vectordb = get_vector_db(filename)
    df = _create_questions(vectordb, model)
    df.to_csv(f"{filename}_questions.csv", index=False)
    return df


def _create_questions(data: pd.DataFrame, model: str) -> pd.DataFrame:
    questions = []
    for idx, row in data.iterrows():
        # can optionally create different questions by putting in previous question
        text = row["text"]
        question = generate_question(text, model)
        answer = generate_answer(question, text, model)
        questions.append([question, answer, text])
        if idx == 12:
            return pd.DataFrame(questions, columns=["question", "answer", "source"])


def start_questions_test(filename: str, model: str):
    questions_df = get_questions(filename)
    if questions_df is None:
        return None
    else:
        results = ask_questions(questions_df, model)
        results.to_csv(f"{filename}_questions_test.csv", index=False)
        return results


def get_latest_test_result(filename: str):
    try:
        return pd.read_csv(f"{filename}_questions_test.csv")
    except FileNotFoundError:
        return None


def ask_questions(question_data: pd.DataFrame, model: str) -> pd.DataFrame:
    results = []
    for idx, row in question_data.iterrows():
        chatbot_answer = run_chatbot_test(row['question'])
        assessment = assess_chatbot_answer(chatbot_answer, row["question"], row['answer'], row['source'], model)
        results.append([row['question'],
                        chatbot_answer,
                        assessment,
                        row['answer'],
                        row['source']
                        ])
    return pd.DataFrame(results, columns=["question", "answer", "assessment", "expected_answer", "source"])


def run_chatbot_test(question: str):
    conversation_id = str(uuid.uuid4())
    return send_message(conversation_id, question)["response"]


def assess_chatbot_answer(chatbot_answer: str, question: str, expected_answer: str, reference_text: str, model: str):
    print(chatbot_answer)
    answer = ask_llm_to_assess_answer(
        message=f"The question was: {question}\n"
        f"The expected answer is: {expected_answer}\n"
        f"The reference text is: {reference_text}\n"
        f"The LLM given answer is: {chatbot_answer}\n"
        f"Is the question answered correctly?", model=model)
    return answer
