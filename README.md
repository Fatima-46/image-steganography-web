# 🖼️ Image Steganography — Web App (Flask)

A live web version of the LSB image steganography tool. Upload a PNG
and a secret message, download an image with the message hidden
inside — or upload an encoded image to reveal what's hidden in it.

**Live demo:** _add your PythonAnywhere link here after deploying_

## Features
- **Hide a Message:** upload a PNG + type text → download the encoded image
- **Reveal a Message:** upload an encoded PNG → see the hidden text
- Same tested Least Significant Bit (LSB) logic as the command-line version

## Project structure
```
steganography-web/
├── app.py              # Flask routes (/, /encode, /decode)
├── steganography.py    # Core LSB encode/decode logic
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── encode.html
│   └── decode.html
├── static/
│   └── cover.png        # sample image to try it with
├── uploads/              # temporary storage for uploaded/generated images
└── requirements.txt
```

## Run it locally
```bash
git clone https://github.com/YOUR-USERNAME/image-steganography-web.git
cd image-steganography-web
pip install -r requirements.txt
python3 app.py
```
Then open `http://127.0.0.1:5000` in your browser.

## How it works
Same core idea as the CLI version: every pixel's Red/Green/Blue value
has a "least significant bit" that can be changed without any visible
color difference. The message is converted to binary and one bit is
hidden per color channel per pixel. Flask just adds a web form on top
so anyone can use it from a browser instead of a terminal.

## Deployment
Deployed free on [PythonAnywhere](https://www.pythonanywhere.com) —
see the main project notes for exact setup steps.

## Notes
- PNG images only (JPG compression corrupts the hidden bits)
- Uploaded/generated images are temporary — this is a demo tool, not
  meant for storing sensitive data long-term
