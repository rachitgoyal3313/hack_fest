from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import numpy as np
import logging
import threading
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model and tokenizer once at module level
model_name = "austinb/fraud_text_detection"
tokenizer = None
model = None
model_loading = False
model_load_lock = threading.Lock()

def is_model_loading():
    global model_loading
    return model_loading

def load_model(device):
    global tokenizer, model, model_loading
    
    # Check if model is already loaded
    if tokenizer is not None and model is not None:
        return tokenizer, model
        
    with model_load_lock:
        # Double-check after acquiring lock
        if tokenizer is not None and model is not None:
            return tokenizer, model
            
        try:
            if not model_loading:
                model_loading = True
                logger.info(f"Loading model {model_name}...")
                tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=False)
                model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=False).to(device)
                logger.info("Model loaded successfully")
                model_loading = False
            else:
                # Wait for model to load with timeout
                start_time = time.time()
                while model_loading:
                    if time.time() - start_time > 30:  # 30 second timeout
                        raise Exception("Model loading timeout")
                    time.sleep(0.5)
                
        except Exception as e:
            model_loading = False
            logger.error(f"Error loading model: {str(e)}")
            raise Exception(f"Failed to load model: {str(e)}")
            
    return tokenizer, model

def detect_text_fraud(text, device):
    """
    Detect if text is AI-generated using austinb/fraud_text_detection model
    
    Args:
        text (str): Input text to analyze
        device (torch.device): Device to run inference on
        
    Returns:
        dict: Result with prediction and confidence
    """
    try:
        if not text or not text.strip():
            raise ValueError("Empty text provided")

        if is_model_loading():
            raise Exception("Model is currently loading. Please try again in a moment.")

        tokenizer, model = load_model(device)
        
        # Truncate text if it's too long
        max_length = tokenizer.model_max_length
        if len(text) > max_length * 4:  # Rough character estimate
            logger.warning(f"Text length ({len(text)}) exceeds maximum. Truncating...")
            text = text[:max_length * 4]  # Truncate to avoid tokenizer errors
        
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length).to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
        
        # Get prediction (0: human, 1: AI)
        prediction = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][prediction].item() * 100
        
        result = {
            "is_ai_generated": bool(prediction),
            "confidence": round(confidence, 2),
            "prediction": "AI-generated" if prediction else "Human-written",
            "raw_scores": {
                "human_score": float(probabilities[0][0]),
                "ai_score": float(probabilities[0][1])
            }
        }
        print (result)
        return result
    except Exception as e:
        logger.error(f"Error during text detection: {str(e)}")
        raise Exception(f"Text detection failed: {str(e)}")
