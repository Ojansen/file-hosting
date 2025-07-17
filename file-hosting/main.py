from flask import Flask, request, render_template, flash, redirect, url_for
from pymongo import MongoClient
import gridfs

app = Flask(__name__)

client = MongoClient("mongodb://db:27017/?directConnection=true")
db = client.test_database
fs = gridfs.GridFS(db)


@app.route("/")
def hello_world():
    files = fs.list()
    return render_template("index.html", file=files)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        binary_file = file.stream.read()
        fs.put(binary_file, filename=file.filename)
        return redirect(url_for("download_file", file_name=file.filename))
    else:
        return render_template("upload.html")


@app.route("/download/<file_name>")
def download_file(file_name):
    file = fs.find_one({"filename": file_name}).read()
    return render_template("download.html", file=file)
    # return render_template("download.html", file="nooo")
