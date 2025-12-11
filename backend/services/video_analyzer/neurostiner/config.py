"""
Configuration for Skydiving Frame Classifier - Detection Only.
Simplified from neurostiner project for inference use.
"""
from pathlib import Path

# Model path (relative to this file)
MODEL_PATH = Path(__file__).parent / 'efficientnet.keras'

# Categories (must match training order)
CATEGORIES = ['boden', 'canopy', 'freefall', 'in_plane']
NUM_CLASSES = len(CATEGORIES)

# Input configuration
INPUT_SIZE = 224  # EfficientNetB0 native resolution
INPUT_SHAPE = (INPUT_SIZE, INPUT_SIZE, 3)

# Focal loss parameters (needed for model deserialization)
FOCAL_GAMMA = 2.0
FOCAL_ALPHA = [0.85, 0.60, 2.08, 0.54]  # Normalized class weights
