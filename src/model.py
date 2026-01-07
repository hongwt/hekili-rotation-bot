"""
PixelNet Model Architecture

Custom CNN with residual connections and spatial attention for 24x24 character recognition.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    """
    Residual Block with two convolutional layers.
    """
    
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super(ResidualBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                               stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                               stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # Shortcut connection
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1,
                         stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        out += self.shortcut(identity)
        out = self.relu(out)
        
        return out


class SEBlock(nn.Module):
    """
    Squeeze-and-Excitation Block (Channel Attention)
    
    Lightweight attention mechanism that recalibrates channel-wise features.
    Reference: SENet (Squeeze-and-Excitation Networks)
    """
    
    def __init__(self, channels: int, reduction: int = 16):
        super(SEBlock, self).__init__()
        
        self.squeeze = nn.AdaptiveAvgPool2d(1)
        self.excitation = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid()
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor (B, C, H, W)
        
        Returns:
            Attention-weighted tensor (B, C, H, W)
        """
        b, c, _, _ = x.size()
        
        # Squeeze: Global average pooling
        squeeze = self.squeeze(x).view(b, c)
        
        # Excitation: FC layers
        excitation = self.excitation(squeeze).view(b, c, 1, 1)
        
        # Scale
        return x * excitation.expand_as(x)


class PixelNet(nn.Module):
    """
    PixelNet for 24x24 character recognition.
    
    Architecture:
        - Input: (B, 3, 24, 24)
        - Conv Block: Single Conv layer (64 filters) -> (B, 64, 24, 24)
        - ResBlock 1: 64->128 channels, stride=1 -> (B, 128, 24, 24)
        - ResBlock 2: 128->256 channels, stride=2 -> (B, 256, 12, 12)
        - Attention: SE Block
        - Global Average Pooling -> (B, 256)
        - FC layers (256->128->37)
        - Output: (B, 37)
    """
    
    def __init__(self, num_classes: int = 37, dropout_rate: float = 0.3):
        super(PixelNet, self).__init__()
        
        # Simplified initial convolution (single layer instead of two)
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        
        # Reduced number of residual blocks
        self.res_block1 = ResidualBlock(64, 128, stride=1)   # 24x24 -> 24x24
        self.res_block2 = ResidualBlock(128, 256, stride=2)  # 24x24 -> 12x12
        
        # Attention mechanism (SE Block is hardcoded)
        self.attention = SEBlock(256, reduction=16)
        
        # Global average pooling
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Lighter fully connected layers
        self.dropout = nn.Dropout(p=dropout_rate)
        self.fc1 = nn.Linear(256, 128)
        self.fc2 = nn.Linear(128, num_classes)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor (B, 3, 24, 24)
        
        Returns:
            Logits (B, num_classes)
        """
        # Initial conv block
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        
        # Residual blocks
        x = self.res_block1(x)  # (B, 128, 24, 24)
        x = self.res_block2(x)  # (B, 256, 12, 12)
        
        # Apply attention
        x = self.attention(x)
        
        # Global pooling
        x = self.global_avg_pool(x)  # (B, 256, 1, 1)
        x = torch.flatten(x, 1)  # (B, 256)
        
        # FC layers
        x = self.dropout(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x
    
    def get_num_params(self) -> int:
        """Calculate total number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def create_model(num_classes: int = 37, dropout_rate: float = 0.3) -> PixelNet:
    """
    Factory function to create PixelNet model.
    
    Args:
        num_classes: Number of output classes
        dropout_rate: Dropout probability
    
    Returns:
        PixelNet instance
    """
    model = PixelNet(num_classes=num_classes, dropout_rate=dropout_rate)
    print(f"Created PixelNet with {model.get_num_params():,} parameters")
    return model


if __name__ == '__main__':
    # Test model instantiation and forward pass
    print("Testing PixelNet...")
    model = create_model()
    dummy_input = torch.randn(4, 3, 24, 24)
    output = model(dummy_input)
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    assert output.shape == (4, 37), f"Expected (4, 37), got {output.shape}"
    print("✓ PixelNet test passed\n")
