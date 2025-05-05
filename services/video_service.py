import cv2
import torch
import numpy as np
import os
import tempfile
from services.image_service import detect_image_fraud

def extract_frames(video_path, interval=5):
    """
    Extract frames from video at specified interval
    
    Args:
        video_path (str): Path to video file
        interval (int): Extract 1 frame every N seconds
        
    Returns:
        list: List of extracted frame paths
    """
    # Create temp directory for frames
    temp_dir = tempfile.mkdtemp()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    # Calculate frame indices to extract (1 frame per interval seconds)
    frame_indices = [int(fps * i) for i in range(0, int(duration), interval)]
    
    # Extract frames
    frame_paths = []
    for i, frame_idx in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
    
    # Release video
    cap.release()
    
    return frame_paths

def detect_video_fraud(video_path, device):
    """
    Detect if a video contains deepfakes by analyzing frames
    
    Args:
        video_path (str): Path to video file
        device (torch.device): Device to run inference on
        
    Returns:
        dict: Result with prediction and confidence
    """
    try:
        # Extract frames
        frame_paths = extract_frames(video_path)
        
        if not frame_paths:
            return {
                "error": "No frames could be extracted from the video",
                "prediction": "Error in processing",
                "confidence": 0
            }
        
        # Analyze each frame
        frame_results = []
        fake_count = 0
        
        for frame_path in frame_paths:
            result = detect_image_fraud(frame_path, device)
            frame_results.append(result)
            
            if result.get("is_fake", False):
                fake_count += 1
        
        # Calculate percentage of fake frames
        fake_percentage = (fake_count / len(frame_paths)) * 100
        
        # Determine overall verdict
        is_fake = fake_percentage > 10  # Consider fake if >10% frames are fake
        
        result = {
            "is_fake": is_fake,
            "fake_percentage": round(fake_percentage, 2),
            "frames_analyzed": len(frame_paths),
            "fake_frames": fake_count,
            "prediction": "Likely deepfake" if is_fake else "Genuine",
            "confidence": round(fake_percentage if is_fake else (100 - fake_percentage), 2),
            "frame_results": frame_results
        }
        
        # Clean up temporary files
        for frame_path in frame_paths:
            try:
                os.remove(frame_path)
            except:
                pass
        
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "prediction": "Error in processing",
            "confidence": 0
        }
