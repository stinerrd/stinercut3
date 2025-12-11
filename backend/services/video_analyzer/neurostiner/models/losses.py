"""
Custom loss functions for handling class imbalance.
Required for model deserialization.
"""
import tensorflow as tf
from tensorflow.keras import backend as K

from ..config import FOCAL_GAMMA, FOCAL_ALPHA


class FocalLoss(tf.keras.losses.Loss):
    """
    Focal Loss for multi-class classification with class imbalance.

    Focal Loss reduces the relative loss for well-classified examples,
    putting more focus on hard, misclassified examples.

    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)

    where:
    - p_t is the probability of the correct class
    - gamma is the focusing parameter (typically 2.0)
    - alpha is the class balancing parameter

    Reference: Lin et al. "Focal Loss for Dense Object Detection" (2017)
    """

    def __init__(self, gamma=FOCAL_GAMMA, alpha=None,
                 from_logits=False, label_smoothing=0.0, **kwargs):
        """
        Args:
            gamma: Focusing parameter. Higher values = more focus on hard examples.
                   gamma=0 is equivalent to cross-entropy. Default: 2.0
            alpha: Class weights. Can be:
                   - None: No class weighting
                   - List/array: Per-class weights [alpha_0, alpha_1, ...]
            from_logits: Whether predictions are logits or probabilities
            label_smoothing: Label smoothing factor (0-1)
        """
        super().__init__(**kwargs)
        self.gamma = gamma
        self.alpha = alpha if alpha is not None else FOCAL_ALPHA
        self.from_logits = from_logits
        self.label_smoothing = label_smoothing

    def call(self, y_true, y_pred):
        # Convert logits to probabilities if needed
        if self.from_logits:
            y_pred = tf.nn.softmax(y_pred, axis=-1)

        # Clip predictions to prevent log(0)
        epsilon = K.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)

        # Handle sparse labels (integer labels)
        y_true_shape = tf.shape(y_true)
        y_pred_shape = tf.shape(y_pred)

        # If y_true is sparse (1D or 2D with last dim=1), convert to one-hot
        if len(y_true.shape) == 1 or (len(y_true.shape) == 2 and y_true.shape[-1] == 1):
            y_true = tf.squeeze(y_true)
            y_true = tf.cast(y_true, tf.int32)
            num_classes = y_pred_shape[-1]
            y_true = tf.one_hot(y_true, depth=num_classes)

        # Apply label smoothing if specified
        if self.label_smoothing > 0:
            num_classes = tf.cast(y_pred_shape[-1], tf.float32)
            y_true = y_true * (1.0 - self.label_smoothing) + \
                     self.label_smoothing / num_classes

        # Compute cross entropy: -y_true * log(y_pred)
        cross_entropy = -y_true * tf.math.log(y_pred)

        # Compute focal weight: (1 - p_t)^gamma
        # p_t is the probability of the true class
        p_t = tf.reduce_sum(y_true * y_pred, axis=-1, keepdims=True)
        focal_weight = tf.pow(1.0 - p_t, self.gamma)

        # Apply alpha weighting if provided
        if self.alpha is not None:
            alpha_tensor = tf.constant(self.alpha, dtype=tf.float32)
            # Broadcast alpha weights to match y_true shape
            alpha_weight = tf.reduce_sum(y_true * alpha_tensor, axis=-1, keepdims=True)
            focal_weight = focal_weight * alpha_weight

        # Combine focal weight with cross entropy
        focal_loss = focal_weight * cross_entropy

        # Sum over classes, mean over batch
        return tf.reduce_mean(tf.reduce_sum(focal_loss, axis=-1))

    def get_config(self):
        config = super().get_config()
        config.update({
            'gamma': self.gamma,
            'alpha': self.alpha,
            'from_logits': self.from_logits,
            'label_smoothing': self.label_smoothing
        })
        return config
