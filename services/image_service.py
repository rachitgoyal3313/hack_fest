from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch
import numpy as np

# Load model and feature extractor once at module level
model_name = "prithivMLmods/Deep-Fake-Detector-Model"
feature_extractor = None
model = None

def load_model(device):
    global feature_extractor, model
    if feature_extractor is None or model is None:
        feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        model = AutoModelForImageClassification.from_pretrained(model_name).to(device)
    return feature_extractor, model

def detect_image_fraud(image_path, device):
    """
    Detect if an image is a deepfake using the Deep-Fake-Detector-Model
    
    Args:
        image_path (str): Path to image file
        device (torch.device): Device to run inference on
        
    Returns:
        dict: Result with prediction and confidence
    """
    try:
        feature_extractor, model = load_model(device)
        
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        inputs = feature_extractor(images=image, return_tensors="pt").to(device)
        
        # Run inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
        
        # Get prediction (model-specific labels)
        prediction_idx = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][prediction_idx].item() * 100
        
        # Map prediction index to label (check model documentation for exact mapping)
        # Assuming 0: real, 1: fake
        is_fake = prediction_idx == 1
        label = "Fake" if is_fake else "Real"
        
        result = {
            "is_fake": is_fake,
            "confidence": round(confidence, 2),
            "prediction": label,
            "raw_scores": {
                "real_score": float(probabilities[0][0]),
                "fake_score": float(probabilities[0][1]) if probabilities.shape[1] > 1 else 0
            }
        }
        print(result)
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "prediction": "Error in processing",
            "confidence": 0
        }
