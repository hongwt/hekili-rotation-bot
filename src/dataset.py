"""
PixelAlphabet Dataset Module

Handles loading and augmentation of 24x24 character images.
"""
import os
from typing import Tuple, Optional, Callable
from pathlib import Path

import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
import numpy as np


# Label mapping: 0-9 -> '0'-'9', 10-35 -> 'A'-'Z' (36 classes total)
def label_to_char(label: int) -> str:
    """Convert integer label to character."""
    if 0 <= label <= 9:
        return str(label)
    elif 10 <= label <= 35:
        return chr(ord('A') + label - 10)
    else:
        raise ValueError(f"Invalid label: {label}")


def char_to_label(char: str) -> int:
    """Convert character to integer label."""
    if char.isdigit():
        return int(char)
    elif char.isalpha() and len(char) == 1:
        return ord(char.upper()) - ord('A') + 10
    else:
        raise ValueError(f"Invalid character: {char}")


class PixelDataset(Dataset):
    """
    Dataset for 24x24 character images.
    
    Expected directory structure:
        data_root/
            0/
                img001.png
                img002.png
            1/
            ...
            A/
            B/
            ...
            Z/
    """
    
    def __init__(
        self,
        data_root: str,
        split: str = 'train',
        transform: Optional[Callable] = None,
        augmentation: bool = True
    ):
        """
        Args:
            data_root: Path to dataset root directory
            split: 'train', 'val', or 'test'
            transform: Optional custom transform
            augmentation: Whether to apply data augmentation (only for training)
        """
        self.data_root = Path(data_root)
        self.split = split
        self.augmentation = augmentation and (split == 'train')
        
        # Collect all image paths and labels
        self.samples = []
        self._load_samples()
        
        # Define transforms
        if transform is not None:
            self.transform = transform
        else:
            self.transform = self._get_default_transform()
    
    def _load_samples(self):
        """Scan directory and collect (image_path, label) pairs."""
        split_dir = self.data_root / self.split
        
        if not split_dir.exists():
            raise FileNotFoundError(f"Split directory not found: {split_dir}")
        
        # Iterate through class directories
        for class_dir in sorted(split_dir.iterdir()):
            if not class_dir.is_dir():
                continue
            
            class_name = class_dir.name
            try:
                label = char_to_label(class_name)
            except ValueError:
                print(f"Warning: Skipping unknown class '{class_name}'")
                continue
            
            # Collect all images in this class
            for img_path in class_dir.glob('*.png'):
                self.samples.append((str(img_path), label))
        
        if len(self.samples) == 0:
            raise RuntimeError(f"No samples found in {split_dir}")
        
        print(f"Loaded {len(self.samples)} samples for split '{self.split}'")
    
    def _get_default_transform(self):
        """Build transformation pipeline."""
        transform_list = []
        
        if self.augmentation:
            # Data augmentation for training - enhanced diversity
            transform_list.extend([
                # Expanded color jitter for better robustness
                transforms.ColorJitter(
                    brightness=0.4,  # ±40%
                    contrast=0.4,    # ±40%
                    saturation=0.3,  # ±30%
                    hue=0.15         # ±15%
                ),
                # Random blur to simulate different image quality
                transforms.RandomApply([
                    transforms.GaussianBlur(kernel_size=3, sigma=(0.5, 1.0))
                ], p=0.3),
                # Random sharpness adjustment
                transforms.RandomApply([
                    transforms.RandomAdjustSharpness(sharpness_factor=2.0)
                ], p=0.2),
                # Geometric transformations
                transforms.RandomAffine(
                    degrees=5,
                    translate=(0.08, 0.08),  # ~2 pixels for 24x24
                    scale=(0.9, 1.1),
                    fill=0
                ),
                # Random Gaussian noise will be applied in __getitem__
            ])
        
        # Common transforms for all splits
        transform_list.extend([
            transforms.ToTensor(),  # Converts to [0, 1] and CHW format
            # No normalization with ImageNet stats since our domain is different
        ])
        
        if self.augmentation:
            # Random Erasing works on Tensors, so it must proceed ToTensor
            transform_list.append(
                transforms.RandomErasing(
                    p=0.1, 
                    scale=(0.02, 0.15), 
                    ratio=(0.3, 3.3), 
                    value=0
                )
            )
        
        return transforms.Compose(transform_list)
    
    def _add_gaussian_noise(self, tensor: torch.Tensor, sigma: float = 0.02) -> torch.Tensor:
        """Add Gaussian noise to tensor."""
        if self.augmentation:
            noise = torch.randn_like(tensor) * sigma
            tensor = tensor + noise
            tensor = torch.clamp(tensor, 0.0, 1.0)
        return tensor
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Returns:
            image: Tensor of shape (3, 24, 24) in range [0, 1]
            label: Integer label
        """
        img_path, label = self.samples[idx]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        # Apply transforms
        image = self.transform(image)
        
        # Add Gaussian noise (only during training)
        image = self._add_gaussian_noise(image)
        
        return image, label


def get_dataloader(
    data_root: str,
    split: str,
    batch_size: int,
    shuffle: bool = True,
    num_workers: int = 4
):
    """
    Convenience function to create DataLoader.
    
    Args:
        data_root: Path to dataset
        split: 'train', 'val', or 'test'
        batch_size: Batch size
        shuffle: Whether to shuffle data
        num_workers: Number of worker processes
    
    Returns:
        DataLoader instance
    """
    dataset = PixelDataset(
        data_root=data_root,
        split=split,
        augmentation=(split == 'train')
    )
    
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return dataloader
