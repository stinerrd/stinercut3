"""
Inference functions for Skydiving Frame Classifier.
Simplified from neurostiner project for detection use only.
"""
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import cv2 as cv
import tensorflow as tf

from .config import CATEGORIES, MODEL_PATH, INPUT_SIZE
from .models.losses import FocalLoss


def load_model(model_path=None):
    """
    Load the trained model.

    Args:
        model_path: Path to model file. Defaults to MODEL_PATH from config.

    Returns:
        Loaded Keras model
    """
    if model_path is None:
        model_path = MODEL_PATH

    model_path = str(model_path)

    # Ensure .keras extension (required by Keras 3)
    if not model_path.endswith('.keras'):
        model_path = model_path.rsplit('.', 1)[0] + '.keras'

    model = tf.keras.models.load_model(
        model_path,
        custom_objects={'FocalLoss': FocalLoss}
    )
    return model


def preprocess_image(image_path):
    """
    Load and preprocess a single image for prediction.

    Args:
        image_path: Path to image file

    Returns:
        Preprocessed image array ready for prediction
    """
    # Read image
    img = cv.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Convert BGR to RGB
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    # Resize to model input size
    img = cv.resize(img, (INPUT_SIZE, INPUT_SIZE), interpolation=cv.INTER_AREA)

    # Convert to float32 [0, 255] - EfficientNet handles its own normalization
    img = img.astype(np.float32)

    # Add batch dimension
    img = np.expand_dims(img, axis=0)

    return img


def preprocess_frame(frame):
    """
    Preprocess an OpenCV frame (numpy array) for prediction.

    Args:
        frame: OpenCV frame in BGR format (numpy array)

    Returns:
        Preprocessed image array ready for prediction
    """
    # Convert BGR to RGB
    img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # Resize to model input size
    img = cv.resize(img, (INPUT_SIZE, INPUT_SIZE), interpolation=cv.INTER_AREA)

    # Convert to float32 [0, 255] - EfficientNet handles its own normalization
    img = img.astype(np.float32)

    # Add batch dimension
    img = np.expand_dims(img, axis=0)

    return img


def predict_single(model, image_path):
    """
    Predict category for a single image.

    Args:
        model: Loaded Keras model
        image_path: Path to image

    Returns:
        Tuple of (category_name, confidence, all_probabilities)
    """
    img = preprocess_image(image_path)
    predictions = model.predict(img, verbose=0)[0]

    category_idx = np.argmax(predictions)
    category_name = CATEGORIES[category_idx]
    confidence = predictions[category_idx]

    return category_name, confidence, predictions


def predict_frame(model, frame):
    """
    Predict category for an OpenCV frame.

    Args:
        model: Loaded Keras model
        frame: OpenCV frame in BGR format (numpy array)

    Returns:
        Tuple of (category_name, confidence, all_probabilities)
    """
    img = preprocess_frame(frame)
    predictions = model.predict(img, verbose=0)[0]

    category_idx = np.argmax(predictions)
    category_name = CATEGORIES[category_idx]
    confidence = predictions[category_idx]

    return category_name, confidence, predictions
