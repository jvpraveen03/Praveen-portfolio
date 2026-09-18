from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import requests

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "praveen_portfolio_secret"
)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

BUCKET_NAME = "videos"

ALLOWED_EXTENSIONS = {"mp4", "webm", "ogg", "mov"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():

    videos = []

    try:
        url = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            headers=headers,
            json={
                "prefix": "",
                "limit": 100,
                "offset": 0
            },
            timeout=30
        )

        print("LIST STATUS:", response.status_code)
        print("LIST RESPONSE:", response.text)

        if response.ok:
            for item in response.json():
                name = item.get("name")

                if name and allowed_file(name):
                    videos.append(name)

    except Exception as e:
        print("LIST ERROR:", repr(e))

    return render_template(
        "index.html",
        videos=videos
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

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

    if video is None or not video.filename:
        return "No video selected"

    if not allowed_file(video.filename):
        return "Invalid video format"

    filename = secure_filename(video.filename)

    try:

        file_data = video.read()

        upload_url = (
            f"{SUPABASE_URL}/storage/v1/object/"
            f"{BUCKET_NAME}/{filename}"
        )

        content_type = video.content_type or "video/mp4"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": str(content_type),
            "x-upsert": "true"
        }

        response = requests.post(
            upload_url,
            headers=headers,
            data=file_data,
            timeout=120
        )

        print("UPLOAD STATUS:", response.status_code)
        print("UPLOAD RESPONSE:", response.text)

        if response.status_code in (200, 201):

            return "Video uploaded successfully! 🎉"

        return (
            "Video upload failed: "
            + response.text
        )

    except Exception as e:

        print("UPLOAD ERROR:", repr(e))

        return (
            "Video upload failed: "
            + str(e)
        )


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    url = (
        f"{SUPABASE_URL}/storage/v1/object/public/"
        f"{BUCKET_NAME}/{filename}"
    )

    return redirect(url)


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
