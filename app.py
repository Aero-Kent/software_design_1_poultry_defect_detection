import time
from flask import Flask, render_template, request, redirect, url_for
from ultralytics import YOLO
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'

model = YOLO('model/best.pt')

def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route('/')
def index(): return render_template('index.html', uploaded_images = [])

# main code for the model prediction...
@app.route('/upload', methods=['POST'])
def upload():
  # code in order to save images.
  uploaded_files = request.files.getlist('user_images')
  saved_paths = []
  output_paths = []

  if len(uploaded_files) > 10 or len(uploaded_files) == 0:
    return render_template('index.html', uploaded_images = [], error = "Maximum 10 files allowed.")

  # main loop in order to run the model, change nalang this later for retina and r-cnn
  # models for the metrics.
  start_time = time.time()
  for file in uploaded_files:
    if file and file.filename != '' and allowed_file(file.filename):
        
      # save first the raw images, hindi ko alam pano mapagana ng hindi invalid filetype
      # kaya sinasave ko muna sa isang folder tapos retrieve ko nalang dun for model prediction+output...
      filename = file.filename
      file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)          
      file.save(file_path)
      saved_paths.append(url_for('static', filename=f'uploads/{filename}'))

      # Model Predicions here... eto mainly yung iibahin for the retina and r-cnn
      for file_path in [os.path.join(app.root_path, 'static/uploads', os.path.basename(p)) for p in saved_paths]:
        results = model.predict(source = file_path, device = 'cpu', conf=0.25, save=False)

        for r in results:
          result_img = r.plot()
          out_name = os.path.basename(file_path)
          out_path = os.path.join(app.config['OUTPUT_FOLDER'], out_name)
          
          Image.fromarray(result_img).save(out_path)
          output_paths.append(url_for('static', filename=f'outputs/{out_name}'))

  detection_time = round(time.time() - start_time, 2)
  return render_template('index.html', uploaded_images = output_paths, detection_time = detection_time)

@app.route('/clear_outputs', methods=['POST'])
def clear_outputs():
  folders_to_clear = [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]

  for folder in folders_to_clear:
    for file in os.listdir(folder):
      file_path = os.path.join(folder, file)
      try:
        if os.path.isfile(file_path):
          os.remove(file_path)
      except Exception as e:
        print(f"Error deleting {file_path}: {e}")

  return redirect(url_for('index'))

if __name__ == '__main__':
  os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok = True)
  os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok = True)
  app.run(debug=True)