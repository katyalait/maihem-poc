import datetime
import uuid
import random

import pandas as pd

from maihem_poc.core.ai import ask_llm_to_create_question, ask_llm_to_create_answer, ask_llm_to_assess_answer, send_message
from maihem_poc.data.db import get_vector_db, load_file, save_file, load_scope


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
        return load_file(filename, 'questions')
    except FileNotFoundError:
        return None


def create_questions(filename: str, model: str, limit: int):
    vectordb = get_vector_db(filename)
    df = _create_questions(vectordb, model, limit)
    save_file(df, filename, 'questions')
    return df


def _create_questions(data: pd.DataFrame, model: str, limit: int) -> pd.DataFrame:
    questions = []
    number_of_rows = data.shape[0]
    chosen_rows = []
    if limit is None or number_of_rows < limit:
        limit = number_of_rows
    # randomly pick a row
    for _ in range(limit):
        if len(chosen_rows) == number_of_rows:
            break
        while True:
            random_int = random.randint(1, number_of_rows) - 1
            if random_int not in chosen_rows:
                chosen_rows.append(random_int)
            text = data.iloc[random_int-1]["text"]
            if len(text) >= 250:  # rough limit for generating good questions
                question = generate_question(text, model)
                answer = generate_answer(question, text, model)
                questions.append([question, answer, text])
                break
            if len(chosen_rows) == number_of_rows:
                break
    return pd.DataFrame(questions, columns=["question", "answer", "source"])


def start_questions_test(filename: str, model: str, endpoint):
    questions_df = get_questions(filename)
    if questions_df is None:
        return None
    else:
        results = ask_questions(questions_df, model, endpoint)
        # save results with date
        save_file(results, filename, 'results', datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        # save as latest results
        save_file(results, filename, 'results')
        return results


def get_test_result(filename: str, direct: bool = False):
    try:
        return load_file(filename, 'results', direct)
    except FileNotFoundError:
        return None


def get_all_results(filename: str):
    return load_scope('results', filename)


def ask_questions(question_data: pd.DataFrame, model: str, endpoint) -> pd.DataFrame:
    results = []
    for idx, row in question_data.iterrows():
        chatbot_answer = run_chatbot_test(row['question'], endpoint)
        assessment = assess_chatbot_answer(chatbot_answer, row["question"], row['answer'], row['source'], model)
        results.append([row['question'],
                        chatbot_answer,
                        assessment,
                        row['answer'],
                        row['source']
                        ])
    return pd.DataFrame(results, columns=["question", "answer", "assessment", "expected_answer", "source"])


def run_chatbot_test(question: str, endpoint: str):
    conversation_id = str(uuid.uuid4())
    return send_message(conversation_id, question, endpoint)["response"]


def assess_chatbot_answer(chatbot_answer: str, question: str, expected_answer: str, reference_text: str, model: str):
    print(chatbot_answer)
    answer = ask_llm_to_assess_answer(
        message=f"The question was: {question}\n"
        f"The expected answer is: {expected_answer}\n"
        f"The reference text is: {reference_text}\n"
        f"The LLM given answer is: {chatbot_answer}\n"
        f"Is the question answered correctly?", model=model)
    return answer
