import torch
import torch.nn as nn
import torchaudio
import numpy as np
import os
import sys
from urllib.request import urlretrieve
import zipfile
import soundfile as sf
import resampy

# AASIST model implementation
class AASIST(nn.Module):
    def __init__(self):
        super(AASIST, self).__init__()
        # Simplified AASIST model architecture
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(64 * 32 * 32, 512)
        self.fc2 = nn.Linear(512, 2)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # Simple forward pass
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 64 * 32 * 32)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Model singleton
aasist_model = None

def download_aasist_model():
    """Download AASIST model weights if not present"""
    model_dir = os.path.join('models', 'aasist')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'model.pth')
    
    if not os.path.exists(model_path):
        print("Downloading AASIST model weights...")
        # Note: In a real implementation, you would download the actual model weights
        # For this example, we'll create a dummy model
        model = AASIST()
        torch.save(model.state_dict(), model_path)
        print(f"Model saved to {model_path}")
    
    return model_path

def load_model(device):
    """Load AASIST model"""
    global aasist_model
    
    if aasist_model is None:
        model_path = download_aasist_model()
        aasist_model = AASIST().to(device)
        aasist_model.load_state_dict(torch.load(model_path, map_location=device))
        aasist_model.eval()
    
    return aasist_model

def preprocess_audio(audio_path):
    """Preprocess audio file to 16kHz mono"""
    # Load audio
    data, sample_rate = sf.read(audio_path)
    
    # Convert to mono if stereo
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    # Resample to 16kHz if needed
    if sample_rate != 16000:
        data = resampy.resample(data, sample_rate, 16000)
        sample_rate = 16000
    
    # Normalize
    data = data / np.max(np.abs(data))
    
    return data, sample_rate

def detect_audio_fraud(audio_path, device):
    """
    Detect if audio is spoofed/fake using AASIST
    
    Args:
        audio_path (str): Path to audio file
        device (torch.device): Device to run inference on
        
    Returns:
        dict: Result with prediction and confidence
    """
    try:
        # Load model
        model = load_model(device)
        
        # Preprocess audio
        audio_data, sample_rate = preprocess_audio(audio_path)
        
        # Convert to spectrogram (simplified for example)
        # In a real implementation, you would use the proper feature extraction
        audio_tensor = torch.from_numpy(audio_data).float().to(device)
        
        # Ensure proper shape for model input (batch, channel, height, width)
        # This is a simplified example - real implementation would use proper spectrograms
        spectrogram = torch.stft(
            audio_tensor[:16000*5] if len(audio_tensor) > 16000*5 else audio_tensor, 
            n_fft=512, 
            hop_length=256, 
            return_complex=False
        )
        
        # Get magnitude
        spectrogram = torch.sqrt(spectrogram[..., 0]**2 + spectrogram[..., 1]**2)
        
        # Reshape for CNN input (batch, channel, height, width)
        spectrogram = spectrogram.unsqueeze(0).unsqueeze(0)
        
        # Resize to expected dimensions (simplified)
        spectrogram = nn.functional.interpolate(
            spectrogram, 
            size=(64, 64), 
            mode='bilinear', 
            align_corners=False
        )
        
        # Run inference
        with torch.no_grad():
            outputs = model(spectrogram)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
        
        # Get prediction (0: genuine, 1: spoofed)
        prediction = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][prediction].item() * 100
        
        result = {
            "is_spoofed": bool(prediction),
            "confidence": round(confidence, 2),
            "prediction": "Spoofed/Fake" if prediction else "Genuine",
            "raw_scores": {
                "genuine_score": float(probabilities[0][0]),
                "spoofed_score": float(probabilities[0][1])
            }
        }
        
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "prediction": "Error in processing",
            "confidence": 0
        }
