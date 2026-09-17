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
            path=filename,
            file=file_data,
            file_options={
                "content-type": video.content_type,
                "upsert": "true"
            }
        )

        return "Video uploaded successfully! 🎉"

    except Exception as e:

        print("Upload error:", repr(e))

        return f"Video upload failed: {str(e)}"
