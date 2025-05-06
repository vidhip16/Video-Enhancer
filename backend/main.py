# Main Flask API to handle video uploads and processing
from flask import Flask, request, jsonify, render_template, url_for, redirect, send_from_directory
import os
import uuid
import sys

# Get absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
frontend_dir = os.path.join(project_root, 'frontend')
static_dir = os.path.join(project_root, 'static')

# Add the current directory to the path so Python can find our modules
sys.path.append(current_dir)

from werkzeug.utils import secure_filename
from video_processing import VideoProcessor

# Update your Flask app initialization with absolute paths
app = Flask(__name__, 
            static_folder=static_dir, 
            template_folder=frontend_dir)

# Configuration with absolute paths
UPLOAD_FOLDER = os.path.join(static_dir, 'uploads')
OUTPUT_FOLDER = os.path.join(static_dir, 'output')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload size

# Initialize the video processor - no API key needed
processor = VideoProcessor(OUTPUT_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser submits an empty file without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique filename to avoid conflicts
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the uploaded file
        file.save(filepath)
        
        # Get parameters from form
        position = request.form.get('position', 'bottom')
        extension_ratio = float(request.form.get('extension_ratio', 1.0))
        use_keyframes = request.form.get('use_keyframes', 'false') == 'true'
        keyframe_interval = int(request.form.get('keyframe_interval', 24))
        sample_rate = int(request.form.get('sample_rate', 1))
        
        # Process the video
        try:
            if use_keyframes:
                output_path = processor.process_video_keyframes(
                    filepath, position, extension_ratio, keyframe_interval
                )
            else:
                output_path = processor.process_video(
                    filepath, position, extension_ratio, None, sample_rate
                )
            
            # Get relative path for the frontend
            relative_output = os.path.relpath(output_path, static_dir)
            
            return jsonify({
                'success': True,
                'output_video': f'/static/{relative_output}',
                'message': 'Video processed successfully!'
            }), 200
        
        except Exception as e:
            return jsonify({
                'error': f'Error processing video: {str(e)}'
            }), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(static_dir, filename)

@app.route('/api/stats')
def get_stats():
    # Count number of videos processed
    output_files = [f for f in os.listdir(OUTPUT_FOLDER) if os.path.isfile(os.path.join(OUTPUT_FOLDER, f))]
    
    return jsonify({
        'videos_processed': len(output_files)
    })

if __name__ == '__main__':
    print(f"Frontend directory: {frontend_dir}")
    print(f"Static directory: {static_dir}")
    app.run(debug=True, host='0.0.0.0', port=5001)