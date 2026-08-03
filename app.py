"""
Flask Web App for Image Steganography
---------------------------------------
This wraps our existing steganography.py logic (encode_image / decode_image)
in a simple website with two pages:
  /encode  -> upload an image + type a message -> download the new image
  /decode  -> upload an encoded image -> see the hidden message

Nothing about the core LSB logic changes here - this file is just the
"front door" (web forms) that calls the functions we already built and
tested.
"""

import os
import uuid
from flask import Flask, request, render_template, send_file, flash, redirect

import steganography as steg  # our existing, already-tested module

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # needed for flash messages

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/encode", methods=["GET", "POST"])
def encode():
    if request.method == "GET":
        return render_template("encode.html")

    # POST: user submitted the form
    image_file = request.files.get("image")
    message = request.form.get("message", "").strip()

    if not image_file or image_file.filename == "":
        flash("Please choose a PNG image.")
        return redirect("/encode")

    if not allowed_file(image_file.filename):
        flash("Only PNG images are supported (JPG compression breaks the hidden data).")
        return redirect("/encode")

    if not message:
        flash("Please enter a message to hide.")
        return redirect("/encode")

    # Save the uploaded image with a unique name so multiple users
    # don't overwrite each other's files
    unique_id = uuid.uuid4().hex
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}_input.png")
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}_encoded.png")
    image_file.save(input_path)

    try:
        steg.encode_image(input_path, message, output_path)
    except ValueError as e:
        flash(str(e))
        return redirect("/encode")

    return send_file(output_path, as_attachment=True, download_name="encoded_image.png")


@app.route("/decode", methods=["GET", "POST"])
def decode():
    if request.method == "GET":
        return render_template("decode.html")

    image_file = request.files.get("image")

    if not image_file or image_file.filename == "":
        flash("Please choose an encoded PNG image.")
        return redirect("/decode")

    if not allowed_file(image_file.filename):
        flash("Only PNG images are supported.")
        return redirect("/decode")

    unique_id = uuid.uuid4().hex
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}_decode.png")
    image_file.save(input_path)

    hidden_message = steg.decode_image(input_path)

    return render_template("decode.html", hidden_message=hidden_message)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
