import os
from urllib.parse import quote, unquote

import pandas as pd
from flask import Flask, redirect, render_template, request, session, url_for
from maihem_poc.core.questions import create_questions, start_questions_test, get_latest_test_result
from maihem_poc.data.db import get_vector_db
from maihem_poc.data.vectoriser import create_vectordb

MODEL = os.getenv("MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

app = Flask(__name__)
app.secret_key = (
    "supersecretkey"  # Necessary for using sessions, should be a random secret key
)


def file_filter(filename):
    return not filename.startswith(".")


def get_file_location(filename):
    return os.path.join(app.root_path, "uploads", filename)


@app.route("/test/")
def test_file():
    filename = request.args.get("filename", None)
    data = request.args.get("data", "")
    message = ""
    columns = ""
    if data.endswith(".csv"):
        df = pd.read_csv(data)
        data = df.to_dict(orient="records")  # Convert DataFrame to list of dictionaries
        columns = list(df.columns)
    else:
        message = data
    return render_template(
        "testing_suite.html",
        filename=filename,
        data=data,
        message=message,
        columns=columns,
    )


@app.route("/")
def index():
    message = request.args.get("message")
    files = filter(file_filter, os.listdir("uploads"))
    return render_template("upload.html", files=files, message=message)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part"
    file = request.files["file"]
    if file.filename == "":
        return "No selected file"
    if file:
        # Save the file, for example, to the 'uploads' directory
        file.save(f"uploads/{file.filename}")
        return redirect(
            url_for(".index", message=f"File {file.filename} saved successfully!")
        )


@app.route("/create_vectordb")
def create_db():
    filename = request.args.get("filename")
    create_vectordb(
        get_file_location(filename),
        embedding_function="get_embedding_openai",
        model="nomic-ai/nomic-embed-text-v1.5-GGUF",
    )
    return redirect(
        url_for(".test_file", filename=filename, data="Vector DB created successfully!")
    )


@app.route("/get_chunks")
def chunks():
    filename = request.args.get("filename")
    df = get_vector_db(get_file_location(filename))
    if df is None:
        data = "No chunks found, please run create vector DB"
    else:
        df.to_csv("chunks.csv", index=False)
        data = "chunks.csv"

    return redirect(url_for(".test_file", filename=filename, data=data))


@app.route("/get_questions")
def get_questions():
    filename = request.args.get("filename")
    question_df = create_questions(get_file_location(filename), model=MODEL)
    question_df.to_csv("questions.csv", index=False)
    data = "questions.csv"
    return redirect(url_for(".test_file", filename=filename, data=data))


@app.route("/run_test")
def run_test():
    filename = request.args.get("filename")
    results = start_questions_test(get_file_location(filename), model=MODEL)
    if results is None:
        data = "Error running test, check if yu have generated the questions first!"
    else:
        results.to_csv("results.csv", index=False)
        data = "results.csv"
    return redirect(url_for(".test_file", filename=filename, data=data))


@app.route("/show_latest_result")
def show_latest_result():
    filename = request.args.get("filename")
    results = get_latest_test_result(get_file_location(filename))
    if results is None:
        data = "No results found, please run the tests first"
    else:
        results.to_csv("results.csv", index=False)
        data = "results.csv"
    return redirect(url_for(".test_file", filename=filename, data=data))

if __name__ == "__main__":
    app.run(debug=True)
