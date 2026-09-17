from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "praveen_portfolio_secret")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "videos"

ALLOWED_EXTENSIONS = {"mp4", "webm", "ogg", "mov"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():

    try:
        files = supabase.storage.from_(BUCKET_NAME).list()

        videos = []

        for file in files:
            name = file.get("name")

            if name and allowed_file(name):
                videos.append(name)

    except Exception as e:
        print("Error:", e)
        videos = []

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

    if video is None or video.filename == "":
        return "No video selected"

    if not allowed_file(video.filename):
        return "Invalid video format"

    filename = secure_filename(video.filename)

    try:

        file_data = video.read()

        supabase.storage.from_(BUCKET_NAME).upload(
            filename,
            file_data,
            {
                "content-type": video.content_type
            }
        )

        return "Video uploaded successfully! 🎉"

    except Exception as e:

        print("Upload error:", e)

        return "Video upload failed"


@app.route("/uploads/<filename>")
def uploaded_file(filename):

    url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)

    return redirect(url)


if __name__ == "__main__":
    app.run()
