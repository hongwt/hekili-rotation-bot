"""
Inference Module for PixelNet

Load trained model and perform character recognition on 24x24 images.
"""
from typing import Union, Tuple
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
import numpy as np

from model import create_model
from dataset import label_to_char

class CharacterPredictor:
    """
    Wrapper class for character recognition inference.
    """
    
    def __init__(self, checkpoint_path: str, device: str = 'auto'):
        """
        Initialize predictor with trained model.
        
        Args:
            checkpoint_path: Path to model checkpoint (.pth file)
            device: 'cuda', 'cpu', or 'auto' (auto-detect)
        """
        self.checkpoint_path = Path(checkpoint_path)
        
        # Setup device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        print(f"Using device: {self.device}")
        
        # Load model
        self.model = self._load_model()
        
        # Define preprocessing transform
        self.transform = transforms.Compose([
            transforms.ToTensor(),
        ])
    
    def _load_model(self) -> torch.nn.Module:
        """Load model from checkpoint."""
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")
        
        # Create model
        model = create_model(num_classes=37, dropout_rate=0.4)
        
        # Load weights
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        
        model.to(self.device)
        model.eval()
        
        print(f"✓ Loaded model from {self.checkpoint_path}")
        if 'val_acc' in checkpoint:
            print(f"  Model validation accuracy: {checkpoint['val_acc']:.2f}%")
        
        return model
    
    @torch.no_grad()
    def predict(
        self,
        image: Union[str, Path, Image.Image, np.ndarray, torch.Tensor],
        return_confidence: bool = True
    ) -> Union[str, Tuple[str, float]]:
        """
        Predict character from image.
        
        Args:
            image: Input image (file path, PIL Image, numpy array, or tensor)
            return_confidence: Whether to return confidence score
        
        Returns:
            Predicted character (and confidence if requested)
        """
        # Preprocess image
        image_tensor = self._preprocess_image(image)
        image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
        image_tensor = image_tensor.to(self.device)
        
        # Forward pass
        logits = self.model(image_tensor)
        probabilities = F.softmax(logits, dim=1)
        
        # Get prediction
        confidence, predicted_label = torch.max(probabilities, dim=1)
        confidence = confidence.item()
        predicted_label = predicted_label.item()
        
        # Convert to character
        predicted_char = label_to_char(predicted_label)
        
        if return_confidence:
            return predicted_char, confidence
        else:
            return predicted_char
    
    @torch.no_grad()
    def predict_batch(
        self,
        images: list,
        return_confidence: bool = True
    ) -> list:
        """
        Predict characters for a batch of images.
        
        Args:
            images: List of images (same formats as predict())
            return_confidence: Whether to return confidence scores
        
        Returns:
            List of predictions (characters or (character, confidence) tuples)
        """
        # Preprocess all images
        image_tensors = [self._preprocess_image(img) for img in images]
        batch_tensor = torch.stack(image_tensors).to(self.device)
        
        # Forward pass
        logits = self.model(batch_tensor)
        probabilities = F.softmax(logits, dim=1)
        
        # Get predictions
        confidences, predicted_labels = torch.max(probabilities, dim=1)
        
        results = []
        for conf, label in zip(confidences.cpu().numpy(), predicted_labels.cpu().numpy()):
            char = label_to_char(int(label))
            if return_confidence:
                results.append((char, float(conf)))
            else:
                results.append(char)
        
        return results
    
    def _preprocess_image(
        self,
        image: Union[str, Path, Image.Image, np.ndarray, torch.Tensor]
    ) -> torch.Tensor:
        """
        Preprocess image to model input format.
        
        Args:
            image: Input in various formats
        
        Returns:
            Tensor of shape (3, 24, 24)
        """
        # Convert to PIL Image
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image).convert('RGB')
        elif isinstance(image, torch.Tensor):
            # Already a tensor, just ensure correct format
            if image.dim() == 2:  # (H, W)
                image = image.unsqueeze(0).repeat(3, 1, 1)
            return image
        elif not isinstance(image, Image.Image):
            raise TypeError(f"Unsupported image type: {type(image)}")
        
        # Ensure 24x24 size
        if image.size != (24, 24):
            print(f"Warning: Resizing image from {image.size} to (24, 24)")
            image = image.resize((24, 24), Image.BILINEAR)
        
        # Apply transform
        tensor = self.transform(image)
        
        return tensor


def predict(
    checkpoint_path: str,
    image_path: str,
    device: str = 'auto'
) -> Tuple[str, float]:
    """
    Convenience function for single prediction.
    
    Args:
        checkpoint_path: Path to model checkpoint
        image_path: Path to input image
        device: Device to use
    
    Returns:
        (predicted_character, confidence)
    """
    predictor = CharacterPredictor(checkpoint_path, device)
    return predictor.predict(image_path, return_confidence=True)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Character recognition inference')
    parser.add_argument('--checkpoint', type=str, required=True,
                        help='Path to model checkpoint')
    parser.add_argument('--image', type=str, required=True,
                        help='Path to input image')
    parser.add_argument('--device', type=str, default='auto',
                        choices=['auto', 'cuda', 'cpu'],
                        help='Device to use')
    
    args = parser.parse_args()
    
    # Run prediction
    char, confidence = predict(args.checkpoint, args.image, args.device)
    print(f"\nPrediction: '{char}' (confidence: {confidence:.4f})")
