from io import BytesIO
from secrets import token_urlsafe

from bson import ObjectId
from flask import (
    Flask,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    send_file,
)
from pymongo import MongoClient
from gridfs import GridFS

app = Flask(__name__)
app.secret_key = "caf6c365e228accb1fc7bf1977b3a43b4620864b1c874c693f378b45aa8c955f"

client = MongoClient("mongodb://db:27017/?directConnection=true")
db = client.test_database
fs = GridFS(db)


@app.route("/")
def index():
    file_list = fs.list()
    files = [fs.find_one({"filename": file}) for file in file_list]
    return render_template("index.html", files=files)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        if "password" not in request.form:
            flash("No password field")
            return redirect(request.url)
        file = request.files["file"]
        binary_file = file.stream.read()
        fs.put(
            binary_file,
            filename=file.filename,
            content_type=file.content_type,
            password=request.form["password"],
        )
        flash(f"File uploaded {file.filename}")
        return redirect(url_for("index"))
    else:
        return render_template("upload.html")


@app.route("/download/<file_id>", methods=["POST"])
def download_file(file_id):
    if request.method == "POST":
        file = fs.find_one(
            {"_id": ObjectId(file_id), "password": request.form["password"]}
        )
        if file is not None:
            return send_file(
                BytesIO(file.read()),
                as_attachment=True,
                mimetype=file.content_type,
                download_name=file.name,
            )
    flash("Password incorrect or file not found")
    return redirect(url_for("index"))


@app.route("/delete/<file_id>", methods=["POST"])
def delete_file(file_id):
    file = fs.get(ObjectId(file_id))
    flash(f"File deleted {file.name}")
    fs.delete(ObjectId(file_id))
    return redirect(url_for("index"))
