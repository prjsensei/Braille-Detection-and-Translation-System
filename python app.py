from flask import Flask, request, render_template_string, send_file
import os
import cv2
import numpy as np
from PIL import Image
from gtts import gTTS

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Placeholder Braille dictionary (6-dot binary pattern to letter)
BRAILLE_DICT = {
    (1, 0, 0, 0, 0, 0): 'a',
    (1, 1, 0, 0, 0, 0): 'b',
    (1, 0, 0, 1, 0, 0): 'c',
    (1, 0, 0, 1, 1, 0): 'd',
    (1, 0, 0, 0, 1, 0): 'e',
    (1, 1, 0, 1, 0, 0): 'f',
    (1, 1, 0, 1, 1, 0): 'g',
    (1, 1, 0, 0, 1, 0): 'h',
    (0, 1, 0, 1, 0, 0): 'i',
    (0, 1, 0, 1, 1, 0): 'j'
    # Extend as needed
}

def detect_blobs(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)

    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 30
    params.maxArea = 200
    params.filterByCircularity = True
    params.minCircularity = 0.7

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(thresh)

    return keypoints

def mock_braille_to_text(blobs):
    num_chars = len(blobs) // 6
    text = ''
    for i in range(num_chars):
        pattern = tuple(1 if j % 2 == 0 else 0 for j in range(6))  # Fake pattern
        char = BRAILLE_DICT.get(pattern, '?')
        text += char
    return text if text else "No Braille detected"

def text_to_speech(text, out_file):
    tts = gTTS(text=text, lang='en')
    tts.save(out_file)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        if "image" not in request.files:
            return "No image uploaded", 400
        file = request.files["image"]
        if file.filename == "":
            return "No file selected", 400

        img_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(img_path)

        blobs = detect_blobs(img_path)
        result = mock_braille_to_text(blobs)

        audio_path = os.path.join(UPLOAD_FOLDER, "output.mp3")
        text_to_speech(result, audio_path)

        return render_template_string('''
            <h2>Detected Text:</h2>
            <p>{{ text }}</p>
            <audio controls>
              <source src="{{ url_for('audio') }}" type="audio/mpeg">
            </audio>
            <p><a href="{{ url_for('index') }}">Try another image</a></p>
        ''', text=result)

    return '''
    <h1>Braille Image to Speech</h1>
    <form method="post" enctype="multipart/form-data">
      <p><input type="file" name="image" accept="image/*"></p>
      <p><input type="submit" value="Convert"></p>
    </form>
    '''

@app.route("/audio")
def audio():
    return send_file(os.path.join(UPLOAD_FOLDER, "output.mp3"), mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(debug=True)
