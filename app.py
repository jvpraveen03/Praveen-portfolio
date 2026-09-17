from flask import Flask, render_template, request, redirect, url_for, session , send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "praveen_portfolio_secret"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp4", "webm", "ogg", "mov"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

@app.route("/")
def home():
    videos = os.listdir(UPLOAD_FOLDER)
    return render_template("index.html", videos=videos)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "Admin@123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    return render_template("admin.html")

@app.route("/upload", methods=["POST"])
def upload():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    video = request.files.get("video")

    if video is None:
        return "No video selected"

    if video.filename == "":
        return "No video selected"

    if not allowed_file(video.filename):
        return "Invalid video format"

    filename = secure_filename(video.filename)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    video.save(file_path)

    return "Video uploaded successfully! 🎉"

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    video = request.files.get("video")

    if video and allowed_file(video.filename):

        filename = secure_filename(video.filename)

        video.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)