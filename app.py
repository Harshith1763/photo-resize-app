from flask import Flask, request, render_template, send_file, redirect, url_for
from PIL import Image, ImageFilter
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Platform dimensions (width, height) and recommended sizes
PLATFORM_DIMENSIONS = {
    "WhatsApp": (800, 800),
    "Instagram": (1080, 1080),
    "Twitter (X)": (1200, 675),
    "Reddit": (1200, 628),
}

# Recommended sizes for display
RECOMMENDED_SIZES = {
    "WhatsApp": "800x800 pixels",
    "Instagram": "1080x1080 pixels",
    "Twitter (X)": "1200x675 pixels",
    "Reddit": "1200x628 pixels",
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def resize_image(image_path, platform):
    img = Image.open(image_path)
    width, height = PLATFORM_DIMENSIONS[platform]
    img = img.resize((width, height), Image.Resampling.LANCZOS)  # Updated here
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"resized_{platform}.jpg")
    img.save(output_path, "JPEG")
    return output_path

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Save the uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Get uploaded image size
            img = Image.open(file_path)
            uploaded_size = f"{img.width}x{img.height} pixels"

            # Resize for the selected platform
            platform = request.form["platform"]
            resized_file = resize_image(file_path, platform)

            # Render the result page
            return render_template(
                "result.html",
                platform=platform,
                uploaded_size=uploaded_size,
                resized_file=resized_file,
                recommended_sizes=RECOMMENDED_SIZES,
            )

    # Render the upload form for GET requests
    return render_template("index.html", platforms=PLATFORM_DIMENSIONS.keys(), recommended_sizes=RECOMMENDED_SIZES)

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)