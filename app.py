from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Secret key
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "praveen_portfolio_secret"
)

# Supabase settings
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

BUCKET_NAME = "videos"

# Allowed video formats
ALLOWED_EXTENSIONS = {
    "mp4",
    "webm",
    "ogg",
    "mov"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================
# HOME PAGE
# =========================

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

        print("List error:", repr(e))

        videos = []

    return render_template(
        "index.html",
        videos=videos
    )


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "Admin@123":

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )

        return "Invalid username or password"

    return render_template("login.html")


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )

    return render_template("admin.html")


# =========================
# UPLOAD VIDEO
# =========================

@app.route("/upload", methods=["POST"])
def upload():

    # Check admin login
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )

    # Get uploaded file
    video = request.files.get("video")

    if video is None or video.filename == "":

        return "No video selected"

    # Check file type
    if not allowed_file(video.filename):

        return "Invalid video format"

    # Secure filename
    filename = secure_filename(
        video.filename
    )

    try:

        # Read video
        file_data = video.read()

        # Upload to Supabase
        result = supabase.storage.from_(
            BUCKET_NAME
        ).upload(
            filename,
            file_data,
            file_options={
                "content-type": (
                    video.content_type
                    or "video/mp4"
                ),
                "upsert": True
            }
        )

        print(
            "UPLOAD RESULT:",
            result
        )

        return (
            "Video uploaded successfully! 🎉"
        )

    except Exception as e:

        print(
            "Upload error:",
            repr(e)
        )

        return (
            f"Video upload failed: {str(e)}"
        )


# =========================
# VIDEO URL
# =========================

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    try:

        url = supabase.storage.from_(
            BUCKET_NAME
        ).get_public_url(filename)

        return redirect(url)

    except Exception as e:

        print(
            "URL error:",
            repr(e)
        )

        return "Video URL error"


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )
