# Fraud Detector

A Flask-based web application for detecting fraud in text, audio, image, and video using pre-trained models.

## Features

- **Text Fraud Detection**: Detect AI-generated text using RoBERTa OpenAI detector
- **Audio Fraud Detection**: Detect spoofed/fake audio using AASIST model
- **Image Deepfake Detection**: Detect fake images using Deep-Fake-Detector-Model
- **Video Frame Deepfake Detection**: Analyze video frames to detect deepfakes

## Installation

1. Clone the repository:
\`\`\`bash
git clone https://github.com/yourusername/fraud-detector.git
cd fraud-detector
\`\`\`

2. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage

1. Start the Flask application:
\`\`\`bash
python app.py
\`\`\`

2. Open your browser and navigate to `http://127.0.0.1:5000`

3. Use the different tabs to upload and analyze content:
   - Text: Enter text directly or upload a .txt file
   - Audio: Upload a .wav file (16kHz mono)
   - Image: Upload a .jpg or .png file
   - Video: Upload a .mp4 file

## Models

- **Text**: RoBERTa OpenAI detector (`roberta-base-openai-detector`)
- **Audio**: AASIST model (simplified implementation)
- **Image**: Deep-Fake-Detector-Model (`prithivMLmods/Deep-Fake-Detector-Model`)
- **Video**: Frame-by-frame analysis using the image deepfake detector

## Notes

- The AASIST model implementation is simplified for demonstration purposes. In a production environment, you would use the full implementation from the [AASIST repository](https://github.com/clovaai/aasist).
- For video analysis, frames are extracted at 5-second intervals and analyzed individually.
- The application requires a GPU for optimal performance, but will fall back to CPU if no GPU is available.

## License

TEAM NERD HERD