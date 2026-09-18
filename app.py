from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from supabase import create_client
import os
import requests

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "praveen_portfolio_secret"
)

SUPABASE_URL = os.environ.get("SUPABASE_URL","").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

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
        response = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "prefix": "",
                "limit": 100,
                "offset": 0
            }
        )

        response.raise_for_status()

        files = response.json()

        videos = []

        for file in files:
            name = file.get("name")

            if name and allowed_file(name):
                videos.append(name)

    except Exception as e:

        print("List error:", repr(e))
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

        upload_url = (
            f"{SUPABASE_URL}/storage/v1/object/
            {BUCKET_NAME}/{filename}"
        )

        response = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": video.content_type or "application/octet-stream",
                "x-upsert": "true"
            },
            data=file_data
        )

        print("Supabase status:", response.status_code)
        print("Supabase response:", response.text)

        if response.status_code not in (200, 201):
            return f"Upload failed: {response.text}"

        return "Video uploaded successfully! 🎉"

    except Exception as e:

        print("Upload error:", repr(e))

        return f"Video upload failed: {str(e)}"


@app.route("/uploads/<filename>")
def uploaded_file(filename):

    url = (
        f"{SUPABASE_URL}/storage/v1/object/public/"
        f"{BUCKET_NAME}/{filename}"
    )

    return redirect(url)


if __name__ == "__main__":
    app.run()
