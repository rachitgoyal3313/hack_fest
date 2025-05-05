from flask import Flask, render_template, request, redirect, url_for, session
import os
import base64
from werkzeug.utils import secure_filename
import torch
from services.text_service import detect_text_fraud, is_model_loading
from services.audio_service import detect_audio_fraud
from services.image_service import detect_image_fraud
from services.video_service import detect_video_fraud

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['SECRET_KEY'] = 'your-secret-key'  # Required for session

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
    # Retrieve results and state from session
    active_tab = session.get('active_tab', 'text')
    text_result = session.get('text_result')
    audio_result = session.get('audio_result')
    image_result = session.get('image_result')
    video_result = session.get('video_result')
    text_input = session.get('text_input', '')
    image_preview = session.get('image_preview')

    # Clear session results to prevent persistent display
    session.pop('text_result', None)
    session.pop('audio_result', None)
    session.pop('image_result', None)
    session.pop('video_result', None)
    session.pop('text_input', None)
    session.pop('image_preview', None)

    return render_template('index.html',
                         active_tab=active_tab,
                         text_result=text_result,
                         audio_result=audio_result,
                         image_result=image_result,
                         video_result=video_result,
                         text_input=text_input,
                         image_preview=image_preview)

@app.route('/detect/text', methods=['POST'])
def detect_text():
    try:
        tab = request.form.get('tab', 'text')
        session['active_tab'] = tab

        # Check if model is currently loading
        if is_model_loading():
            session['text_result'] = {'error': 'Model is currently loading. Please wait a moment and try again.', 'status': 'loading'}
            return redirect(url_for('index'))

        if 'text_input' in request.form and request.form['text_input'].strip():
            # Direct text input
            text = request.form['text_input']
            session['text_input'] = text
            try:
                result = detect_text_fraud(text, device)
                session['text_result'] = result
            except Exception as e:
                app.logger.error(f"Error in text detection: {str(e)}")
                session['text_result'] = {'error': str(e)}
        
        elif 'file' in request.files:
            # File upload
            file = request.files['file']
            if file.filename == '':
                session['text_result'] = {'error': 'No file selected'}
            
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'text', filename)
                try:
                    file.save(filepath)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    if not text.strip():
                        session['text_result'] = {'error': 'The uploaded file is empty'}
                    else:
                        session['text_input'] = text
                        result = detect_text_fraud(text, device)
                        session['text_result'] = result
                except UnicodeDecodeError:
                    session['text_result'] = {'error': 'Invalid file format. Please upload a text file.'}
                except Exception as e:
                    app.logger.error(f"Error processing file: {str(e)}")
                    session['text_result'] = {'error': str(e)}
                finally:
                    # Clean up the uploaded file
                    if os.path.exists(filepath):
                        os.remove(filepath)
        
        else:
            session['text_result'] = {'error': 'No text or file provided'}
        
        return redirect(url_for('index'))
    
    except Exception as e:
        app.logger.error(f"Error in text detection endpoint: {str(e)}")
        session['text_result'] = {'error': str(e)}
        return redirect(url_for('index'))

@app.route('/detect/audio', methods=['POST'])
def detect_audio():
    try:
        tab = request.form.get('tab', 'audio')
        session['active_tab'] = tab

        if 'file' not in request.files:
            session['audio_result'] = {'error': 'No file part'}
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            session['audio_result'] = {'error': 'No file selected'}
            return redirect(url_for('index'))
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'audio', filename)
            file.save(filepath)
            
            try:
                result = detect_audio_fraud(filepath, device)
                session['audio_result'] = result
            except Exception as e:
                app.logger.error(f"Error in audio detection: {str(e)}")
                session['audio_result'] = {'error': str(e)}
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        return redirect(url_for('index'))
    
    except Exception as e:
        app.logger.error(f"Error in audio detection endpoint: {str(e)}")
        session['audio_result'] = {'error': str(e)}
        return redirect(url_for('index'))

@app.route('/detect/image', methods=['POST'])
def detect_image():
    try:
        tab = request.form.get('tab', 'image')
        session['active_tab'] = tab

        if 'file' not in request.files:
            session['image_result'] = {'error': 'No file part'}
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            session['image_result'] = {'error': 'No file selected'}
            return redirect(url_for('index'))
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'image', filename)
            file.save(filepath)
            
            try:
                # Read image for preview
                with open(filepath, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                session['image_preview'] = image_data
                
                result = detect_image_fraud(filepath, device)
                session['image_result'] = result
            except Exception as e:
                app.logger.error(f"Error in image detection: {str(e)}")
                session['image_result'] = {'error': str(e)}
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        return redirect(url_for('index'))
    
    except Exception as e:
        app.logger.error(f"Error in image detection endpoint: {str(e)}")
        session['image_result'] = {'error': str(e)}
        return redirect(url_for('index'))

@app.route('/detect/video', methods=['POST'])
def detect_video():
    try:
        tab = request.form.get('tab', 'video')
        session['active_tab'] = tab

        if 'file' not in request.files:
            session['video_result'] = {'error': 'No file part'}
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            session['video_result'] = {'error': 'No file selected'}
            return redirect(url_for('index'))
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'video', filename)
            file.save(filepath)
            
            try:
                result = detect_video_fraud(filepath, device)
                session['video_result'] = result
            except Exception as e:
                app.logger.error(f"Error in video detection: {str(e)}")
                session['video_result'] = {'error': str(e)}
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        return redirect(url_for('index'))
    
    except Exception as e:
        app.logger.error(f"Error in audio detection endpoint: {str(e)}")
        session['video_result'] = {'error': str(e)}
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)