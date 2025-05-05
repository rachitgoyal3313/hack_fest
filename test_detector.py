import torch
from services.text_service import detect_text_fraud

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Test text
text = "This is a test text to analyze whether it is AI-generated or human-written."

# Detect if the text is AI-generated
try:
    result = detect_text_fraud(text, device)
    print("Result:", result)
except Exception as e:
    print(f"Error occurred: {str(e)}")