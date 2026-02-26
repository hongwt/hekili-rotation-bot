"""
PixelNet Model Architecture

Custom CNN with residual connections, position encoding, and attention mechanisms
for 24x24 character recognition.

Key Components:
- CoordConv: Position encoding for spatial awareness
- ResBlockSE: Residual blocks with integrated SE attention
- CBAM: Combined channel and spatial attention
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Literal


class CoordConv(nn.Module):
    """
    CoordConv: Convolution with coordinate channels.
    
    Adds normalized x, y coordinate channels to input before convolution.
    Helps the network learn position-dependent features (important for 6/9, b/d distinction).
    
    Reference: Liu et al., "An Intriguing Failing of Convolutional Neural Networks 
    and the CoordConv Solution" (2018)
    """
    
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3,
                 stride: int = 1, padding: int = 1, bias: bool = False):
        super(CoordConv, self).__init__()
        # +2 for x, y coordinate channels
        self.conv = nn.Conv2d(in_channels + 2, out_channels, kernel_size=kernel_size,
                              stride=stride, padding=padding, bias=bias)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor (B, C, H, W)
        
        Returns:
            Output tensor (B, out_channels, H', W')
        """
        b, _, h, w = x.shape
        device = x.device
        dtype = x.dtype
        
        # Generate normalized coordinate grids [-1, 1]
        xx = torch.linspace(-1, 1, w, device=device, dtype=dtype).view(1, 1, 1, w).expand(b, 1, h, w)
        yy = torch.linspace(-1, 1, h, device=device, dtype=dtype).view(1, 1, h, 1).expand(b, 1, h, w)
        
        # Concatenate coordinates with input
        x = torch.cat([x, xx, yy], dim=1)
        
        return self.conv(x)


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
        
        # Ensure reduced channels is at least 1
        reduced_channels = max(channels // reduction, 1)
        
        self.squeeze = nn.AdaptiveAvgPool2d(1)
        self.excitation = nn.Sequential(
            nn.Linear(channels, reduced_channels, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(reduced_channels, channels, bias=False),
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


class SpatialAttention(nn.Module):
    """
    Spatial Attention Module.
    
    Generates a spatial attention map by aggregating channel information.
    Helps the network focus on important spatial regions (character location).
    """
    
    def __init__(self, kernel_size: int = 7):
        super(SpatialAttention, self).__init__()
        
        padding = kernel_size // 2
        self.conv = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor (B, C, H, W)
        
        Returns:
            Attention-weighted tensor (B, C, H, W)
        """
        # Compute channel-wise statistics
        avg_out = torch.mean(x, dim=1, keepdim=True)  # (B, 1, H, W)
        max_out, _ = torch.max(x, dim=1, keepdim=True)  # (B, 1, H, W)
        
        # Concatenate and compute attention
        attention = torch.cat([avg_out, max_out], dim=1)  # (B, 2, H, W)
        attention = self.sigmoid(self.conv(attention))  # (B, 1, H, W)
        
        return x * attention


class CBAM(nn.Module):
    """
    Convolutional Block Attention Module (CBAM).
    
    Combines channel attention (SE Block) and spatial attention sequentially.
    Reference: Woo et al., "CBAM: Convolutional Block Attention Module" (2018)
    """
    
    def __init__(self, channels: int, reduction: int = 16, spatial_kernel: int = 7):
        super(CBAM, self).__init__()
        
        self.channel_attention = SEBlock(channels, reduction)
        self.spatial_attention = SpatialAttention(spatial_kernel)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor (B, C, H, W)
        
        Returns:
            Attention-weighted tensor (B, C, H, W)
        """
        x = self.channel_attention(x)
        x = self.spatial_attention(x)
        return x


class ResBlockSE(nn.Module):
    """
    Residual Block with integrated SE (Squeeze-and-Excitation) attention.
    
    Applies SE attention after the residual addition for channel recalibration.
    """
    
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1,
                 reduction: int = 16):
        super(ResBlockSE, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                               stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                               stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # SE attention
        self.se = SEBlock(out_channels, reduction)
        
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
        
        # Apply SE attention before residual addition
        out = self.se(out)
        
        out += self.shortcut(identity)
        out = self.relu(out)
        
        return out


class PixelNet(nn.Module):
    """
    PixelNet for 24x24 character recognition.
    
    Optimized Architecture:
        - Input: (B, 3, 24, 24)
        - CoordConv: Position-aware conv (3+2→64) -> (B, 64, 24, 24)
        - ResBlockSE 1: 64->64 channels, stride=1 -> (B, 64, 24, 24)
        - ResBlockSE 2: 64->128 channels, stride=1 -> (B, 128, 24, 24)
        - ResBlockSE 3: 128->256 channels, stride=2 -> (B, 256, 12, 12)
        - CBAM: Channel + Spatial Attention
        - Global Average Pooling -> (B, 256)
        - FC layers with BatchNorm (256->128->36)
        - Output: (B, 36)
    
    Args:
        num_classes: Number of output classes (default: 36)
        dropout_rate: Dropout probability (default: 0.3)
        use_coord_conv: Whether to use CoordConv for position encoding (default: True)
        attention_type: Type of final attention ('cbam', 'se', 'none') (default: 'cbam')
    """
    
    def __init__(self, num_classes: int = 36, dropout_rate: float = 0.3,
                 use_coord_conv: bool = True,
                 attention_type: Literal['cbam', 'se', 'none'] = 'cbam'):
        super(PixelNet, self).__init__()
        
        self.use_coord_conv = use_coord_conv
        self.attention_type = attention_type
        
        # Initial convolution with optional position encoding
        if use_coord_conv:
            self.conv1 = CoordConv(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        else:
            self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        
        # Three residual blocks with integrated SE attention
        self.res_block1 = ResBlockSE(64, 64, stride=1)    # 24x24 -> 24x24
        self.res_block2 = ResBlockSE(64, 128, stride=1)   # 24x24 -> 24x24
        self.res_block3 = ResBlockSE(128, 256, stride=2)  # 24x24 -> 12x12
        
        # Final attention mechanism
        if attention_type == 'cbam':
            self.attention = CBAM(256, reduction=16, spatial_kernel=7)
        elif attention_type == 'se':
            self.attention = SEBlock(256, reduction=16)
        else:
            self.attention = nn.Identity()
        
        # Global average pooling
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Optimized classifier head with BatchNorm
        self.classifier = nn.Sequential(
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(128, num_classes)
        )
    
    def _extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """
        Shared backbone: returns the 256-dim embedding after GAP, before the
        classifier head.

        Args:
            x: Input tensor (B, 3, 24, 24)

        Returns:
            Feature embedding (B, 256)
        """
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)

        x = self.res_block1(x)  # (B, 64, 24, 24)
        x = self.res_block2(x)  # (B, 128, 24, 24)
        x = self.res_block3(x)  # (B, 256, 12, 12)

        x = self.attention(x)

        x = self.global_avg_pool(x)  # (B, 256, 1, 1)
        x = torch.flatten(x, 1)      # (B, 256)
        return x

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor (B, 3, 24, 24)

        Returns:
            Logits (B, num_classes)
        """
        features = self._extract_features(x)
        return self.classifier(features)

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        """
        Return the 256-dimensional embedding vector after Global Average
        Pooling but before the classification head.

        Useful for contrastive loss computation on the feature space.

        Args:
            x: Input tensor (B, 3, 24, 24)

        Returns:
            Feature embedding (B, 256)
        """
        return self._extract_features(x)

    def get_num_params(self) -> int:
        """Calculate total number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def create_model(num_classes: int = 36, dropout_rate: float = 0.3,
                 use_coord_conv: bool = True,
                 attention_type: Literal['cbam', 'se', 'none'] = 'cbam') -> PixelNet:
    """
    Factory function to create PixelNet model.
    
    Args:
        num_classes: Number of output classes
        dropout_rate: Dropout probability
        use_coord_conv: Whether to use CoordConv for position encoding
        attention_type: Type of final attention ('cbam', 'se', 'none')
    
    Returns:
        PixelNet instance
    """
    model = PixelNet(
        num_classes=num_classes,
        dropout_rate=dropout_rate,
        use_coord_conv=use_coord_conv,
        attention_type=attention_type
    )
    print(f"Created PixelNet with {model.get_num_params():,} parameters")
    print(f"  - CoordConv: {use_coord_conv}")
    print(f"  - Attention: {attention_type}")
    return model


if __name__ == '__main__':
    # Test model instantiation and forward pass
    print("Testing PixelNet (Optimized)...")
    print("=" * 50)
    
    # Test default configuration
    model = create_model()
    dummy_input = torch.randn(4, 3, 24, 24)
    output = model(dummy_input)
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    assert output.shape == (4, 36), f"Expected (4, 36), got {output.shape}"
    print("✓ Default PixelNet test passed\n")
    
    # Test without CoordConv
    print("Testing without CoordConv...")
    model_no_coord = create_model(use_coord_conv=False)
    output = model_no_coord(dummy_input)
    assert output.shape == (4, 36)
    print("✓ No CoordConv test passed\n")
    
    # Test with SE attention only
    print("Testing with SE attention...")
    model_se = create_model(attention_type='se')
    output = model_se(dummy_input)
    assert output.shape == (4, 36)
    print("✓ SE attention test passed\n")
    
    # Test with no attention
    print("Testing with no attention...")
    model_none = create_model(attention_type='none')
    output = model_none(dummy_input)
    assert output.shape == (4, 36)
    print("✓ No attention test passed\n")
    
    print("=" * 50)
    print("All tests passed! ✓")
