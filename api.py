import os
from flask import Flask, render_template, send_file, request, jsonify
from werkzeug import secure_filename
import json
from process import process_cobol_file

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_PATH = os.path.join(app.root_path, 'upload')


@app.route("/")
def home():
    return render_template("Home.html")


@app.route("/process", methods=["GET", "POST"])
def process():
    if request.method == 'POST' and request.files['file']:
        uploaded_file = request.files['file']
        save_file = os.path.join(
            UPLOAD_PATH, secure_filename(uploaded_file.filename))
        uploaded_file.save(save_file)
        print("File saved successfully ")

    response = process_cobol_file(save_file)
    os.remove(save_file)
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
