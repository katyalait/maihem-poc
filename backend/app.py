import os
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for
from maihem_poc.core.questions import create_questions, start_questions_test, get_test_result, get_all_results
from maihem_poc.data.db import get_vector_db
from maihem_poc.data.vectoriser import create_vectordb

MODEL = os.getenv("MODEL")
CHATBOT_ENDPOINT_1 = os.getenv("CHATBOT_ENDPOINT_1")
CHATBOT_ENDPOINT_2 = os.getenv("CHATBOT_ENDPOINT_2")

app = Flask(__name__)


def file_filter(filename):
    """
    Filters out hidden files that start with a dot.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file is not hidden, False otherwise.
    """
    return not filename.startswith(".")


def get_file_location(filename):
    """
    Constructs the full file path for the given filename in the uploads directory.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The full path to the file.
    """
    return os.path.join(app.root_path, "uploads", filename)


@app.route("/test/")
def test_file():
    """
    Displays the testing suite page, showing data from a specified file.

    Query Parameters:
        filename (str, optional): The name of the file to be processed.
        data (str, optional): The path to the data file, typically a .csv file.

    Returns:
        Response: Renders the 'testing_suite.html' template with the file name, data,
                  message, and column names.
    """
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
    """
    Displays the main upload page.

    Query Parameters:
        message (str, optional): A message to display on the upload page.

    Returns:
        Response: Renders the 'upload.html' template with a list of files in the 'uploads'
                  directory and an optional message.
    """
    message = request.args.get("message")
    files = filter(file_filter, os.listdir("uploads"))
    return render_template("upload.html", files=files, message=message)


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handles file upload and saves the uploaded file to the 'uploads' directory.

    Form Data:
        file: The uploaded file.

    Returns:
        str: A message indicating the status of the upload.
        Redirect: Redirects to the index page with a success message if the file is uploaded successfully.
    """
    if "file" not in request.files:
        return "No file part"
    file = request.files["file"]
    if file.filename == "":
        return "No selected file"
    if file:
        file.save(f"uploads/{file.filename}")
        return redirect(
            url_for(".index", message=f"File {file.filename} saved successfully!")
        )


@app.route("/create_vectordb")
def create_db():
    """
    Creates a vector database from the specified file.

    Query Parameters:
        filename (str): The name of the file to create the vector database from.

    Returns:
        Redirect: Redirects to the test file page with a success message.
    """
    filename = request.args.get("filename")
    create_vectordb(
        get_file_location(filename),
    )
    return redirect(
        url_for(".test_file", filename=filename, data="Vector DB created successfully!")
    )


@app.route("/get_chunks")
def chunks():
    """
    Retrieves chunks from the vector database and saves them as a CSV file.

    Query Parameters:
        filename (str): The name of the file to retrieve chunks from.

    Returns:
        Redirect: Redirects to the test file page with the chunks CSV file or an error message.
    """
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
    """
    Generates questions from the specified file and saves them as a CSV file.

    Query Parameters:
        filename (str): The name of the file to generate questions from.
        limit (int, optional): The maximum number of questions to generate (default is 15).

    Returns:
        Redirect: Redirects to the test file page with the questions CSV file.
    """
    filename = request.args.get("filename")
    limit = request.args.get("limit", 15)
    question_df = create_questions(get_file_location(filename), model=MODEL, limit=limit)
    question_df.to_csv("questions.csv", index=False)
    data = "questions.csv"
    return redirect(url_for(".test_file", filename=filename, data=data))


@app.route("/run_test")
def run_test():
    """
    Runs a test using the questions generated from the specified file and saves the results as a CSV file.

    Query Parameters:
        filename (str): The name of the file to run the test on.

    Returns:
        Redirect: Redirects to the test file page with the test results CSV file or an error message.
    """
    filename = request.args.get("filename")
    endpoint = request.args.get("str", 'CHATBOT_ENDPOINT_1')
    endpoint = os.getenv(endpoint)
    results = start_questions_test(get_file_location(filename), model=MODEL, endpoint=endpoint)
    if results is None:
        data = "Error running test, check if you have generated the questions first!"
    else:
        results.to_csv("results.csv", index=False)
        data = "results.csv"
    return redirect(url_for(".test_file", filename=filename, data=data))


@app.route("/show_latest_result")
def show_latest_result():
    """
    Displays the latest test results from the specified file and saves them as a CSV file.

    Query Parameters:
        filename (str): The name of the file to retrieve the latest test results from.

    Returns:
        Redirect: Redirects to the test file page with the latest test results CSV file or an error message.
    """
    filename = request.args.get("filename")
    results = get_test_result(get_file_location(filename))
    if results is None:
        data = "No results found, please run the tests first"
    else:
        results.to_csv("results.csv", index=False)
        data = "results.csv"
    return redirect(url_for(".test_file", filename=filename, data=data))


@app.route("/view_results_for")
def view_results_for():
    """
    Displays a test results from a specified file and saves them as a CSV file.

    Query Parameters:
        filename (str): The name of the file to retrieve the latest test results from.

    Returns:
        Redirect: Redirects to the test file page with the test results CSV file or an error message.
    """
    filename = request.args.get("filename")
    results_file = request.args.get("results_file")
    results = get_test_result(results_file, direct=True)
    if results is None:
        data = "No results found, please run the tests first"
    else:
        results.to_csv("results.csv", index=False)
        data = "results.csv"
    return redirect(url_for(".test_file", filename=filename, data=data))


@app.route("/show_all_results")
def show_all_results():
    """
    Displays all the test results from the specified file and saves them as a CSV file.

    Query Parameters:
        filename (str): The name of the file to retrieve the test results from.

    Returns:
        Redirect: Redirects to the test file page with the all test results CSV file or an error message.
    """
    def create_hyper_link(filename: str, results_file: str):
        return "<a href=\"/view_results_for?filename={filename}&results_file={results_file}\">View</a>".format(filename=filename, results_file=results_file)
    filename = request.args.get("filename")
    results = get_all_results(get_file_location(filename))
    if results is None:
        data = "No results found, please run the tests first"
    else:
        table = pd.DataFrame([[file.rsplit('.csv')[0], create_hyper_link(filename, file)] for file in results],
                             columns=['filename', 'results'])
        table.to_csv("results_table.csv", index=False)
        data = "results_table.csv"
    return redirect(url_for(".test_file", filename=filename, data=data))


if __name__ == "__main__":
    app.run(debug=True)
