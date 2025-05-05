from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import torch
from services.text_service import detect_text_fraud, is_model_loading
from services.audio_service import detect_audio_fraud
from services.image_service import detect_image_fraud
from services.video_service import detect_video_fraud

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Ensure upload directories exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'text'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'audio'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'image'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'video'), exist_ok=True)

# Check if GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect/text', methods=['POST'])
def detect_text():
    try:
        # Check if model is currently loading
        if is_model_loading():
            return jsonify({
                'error': 'Model is currently loading. Please wait a moment and try again.',
                'status': 'loading'
            }), 503

        if 'text_input' in request.form and request.form['text_input'].strip():
            # Direct text input
            text = request.form['text_input']
            try:
                result = detect_text_fraud(text, device)
                return jsonify(result)
            except Exception as e:
                app.logger.error(f"Error in text detection: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        elif 'file' in request.files:
            # File upload
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'text', filename)
                try:
                    file.save(filepath)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    if not text.strip():
                        return jsonify({'error': 'The uploaded file is empty'}), 400
                    
                    result = detect_text_fraud(text, device)
                    return jsonify(result)
                except UnicodeDecodeError:
                    return jsonify({'error': 'Invalid file format. Please upload a text file.'}), 400
                except Exception as e:
                    app.logger.error(f"Error processing file: {str(e)}")
                    return jsonify({'error': str(e)}), 500
                finally:
                    # Clean up the uploaded file
                    if os.path.exists(filepath):
                        os.remove(filepath)
        
        return jsonify({'error': 'No text or file provided'}), 400
    except Exception as e:
        app.logger.error(f"Error in text detection endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/detect/audio', methods=['POST'])
def detect_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'audio', filename)
        file.save(filepath)
        
        result = detect_audio_fraud(filepath, device)
        return jsonify(result)

@app.route('/detect/image', methods=['POST'])
def detect_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'image', filename)
        file.save(filepath)
        
        result = detect_image_fraud(filepath, device)
        return jsonify(result)

@app.route('/detect/video', methods=['POST'])
def detect_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'video', filename)
        file.save(filepath)
        
        result = detect_video_fraud(filepath, device)
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
