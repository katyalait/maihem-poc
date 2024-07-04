import os

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


def file_filter(filename):
    return not filename.startswith(".")


@app.route("/test?<filename>")
def test_file(filename: str):
    return render_template("testing_suite.html", filename=filename)


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


if __name__ == "__main__":
    app.run(debug=True)
