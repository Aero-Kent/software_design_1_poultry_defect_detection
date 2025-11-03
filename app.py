from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route('/')
def index():
  return render_template('index.html', uploaded_images=[])

@app.route('/upload', methods=['POST'])
def upload():
    # Get the list of files from the form input named 'user_images'
    uploaded_files = request.files.getlist('user_images')
    saved_paths = []

    if len(uploaded_files) > 10:
      return render_template('index.html', uploaded_images = [], error = "Maximum 10 files allowed.")

    for file in uploaded_files:
        if file and file.filename != '' and allowed_file(file.filename):
            # temporary muna na sasave, dapat na dedelete mga images after each run dapat...
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)          
            file.save(file_path)
            saved_paths.append(url_for('static', filename=f'uploads/{filename}'))
            
            # Later: Run DL model inference here...

    return render_template('index.html', uploaded_images=saved_paths)

if __name__ == '__main__':
  os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
  app.run(debug=True)