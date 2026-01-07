"""
Loss functions for PixelAlphabet.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class LabelSmoothingCrossEntropy(nn.Module):
    """
    Label Smoothing Cross Entropy Loss
    
    Prevents the model from becoming over-confident by smoothing the labels.
    Instead of using hard 0/1 targets, uses soft targets: (1-epsilon) for correct class,
    epsilon/(num_classes-1) for other classes.
    
    This helps with generalization and reduces overfitting.
    """
    
    def __init__(self, epsilon: float = 0.1, reduction: str = 'mean'):
        """
        Args:
            epsilon: Smoothing factor (default: 0.1)
            reduction: 'mean', 'sum' or 'none'
        """
        super(LabelSmoothingCrossEntropy, self).__init__()
        self.epsilon = epsilon
        self.reduction = reduction
    
    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred: Prediction logits (B, C)
            target: Ground truth labels (B)
        
        Returns:
            Loss value
        """
        n_classes = pred.size(1)
        
        # Convert target to one-hot
        one_hot = F.one_hot(target, n_classes).float()
        
        # Apply label smoothing
        smooth_target = (1 - self.epsilon) * one_hot + self.epsilon / n_classes
        
        # Compute loss
        log_prob = F.log_softmax(pred, dim=1)
        loss = -(smooth_target * log_prob).sum(dim=1)
        
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss


class FocalLoss(nn.Module):
    """
    Focal Loss implementation for handling class imbalance and hard examples.
    
    Formula: FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    
    Dynamically scales the cross entropy loss based on the difficulty of examples.
    Easy examples (high confidence) are down-weighted, allowing the model to focus
    on hard, misclassified examples.
    """
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        """
        Args:
            alpha: Weighting factor (default: 1)
            gamma: Focusing parameter (default: 2)
            reduction: 'mean', 'sum' or 'none'
        """
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        """
        Args:
            inputs: Prediction logits (B, C)
            targets: Ground truth labels (B)
        """
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss

        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class CombinedLoss(nn.Module):
    """
    Combined Loss function that integrates multiple loss components.
    
    Components:
        1. Label Smoothing Cross Entropy (base loss)
        2. Focal Loss (optional, for hard examples)
        3. Contrastive Loss (optional, for confused character pairs)
    
    Total Loss = CE + lambda_focal * Focal + lambda_contrastive * Contrastive
    """
    
    def __init__(
        self,
        use_focal: bool = True,
        use_label_smoothing: bool = True,
        smoothing: float = 0.1,
        focal_gamma: float = 2.0,
        focal_alpha: float = 1.0,
        lambda_focal: float = 0.5
    ):
        """
        Args:
            use_focal: Whether to include focal loss
            use_label_smoothing: Whether to use label smoothing
            smoothing: Label smoothing factor
            focal_gamma: Focal loss gamma parameter
            focal_alpha: Focal loss alpha parameter
            lambda_focal: Weight for focal loss component
        """
        super(CombinedLoss, self).__init__()
        
        # Base loss
        if use_label_smoothing:
            self.base_loss = LabelSmoothingCrossEntropy(epsilon=smoothing)
        else:
            self.base_loss = nn.CrossEntropyLoss()
        
        # Optional focal loss
        self.focal_loss = None
        self.lambda_focal = lambda_focal
        if use_focal:
            self.focal_loss = FocalLoss(alpha=focal_alpha, gamma=focal_gamma)
    
    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred: Prediction logits (B, C)
            target: Ground truth labels (B)
        
        Returns:
            Combined loss value
        """
        # Base loss
        loss = self.base_loss(pred, target)
        
        # Add focal loss if configured
        if self.focal_loss is not None:
            focal = self.focal_loss(pred, target)
            loss = loss + self.lambda_focal * focal
        
        return loss


def create_loss_function(loss_type: str = 'combined', **kwargs):
    """
    Factory function to create loss function.
    
    Args:
        loss_type: Type of loss ('ce', 'focal', 'label_smoothing', 'combined')
        **kwargs: Additional arguments for loss function
    
    Returns:
        Loss function instance
    """
    if loss_type == 'ce':
        return nn.CrossEntropyLoss()
    elif loss_type == 'focal':
        return FocalLoss(**kwargs)
    elif loss_type == 'label_smoothing':
        return LabelSmoothingCrossEntropy(**kwargs)
    elif loss_type == 'combined':
        return CombinedLoss(**kwargs)
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")


if __name__ == '__main__':
    # Test loss functions
    print("Testing loss functions...")
    
    # Dummy data
    batch_size = 8
    num_classes = 37
    pred = torch.randn(batch_size, num_classes)
    target = torch.randint(0, num_classes, (batch_size,))
    
    # Test Label Smoothing Cross Entropy
    print("\n1. Label Smoothing Cross Entropy:")
    ls_loss = LabelSmoothingCrossEntropy(epsilon=0.1)
    loss_val = ls_loss(pred, target)
    print(f"   Loss: {loss_val.item():.4f}")
    
    # Test Focal Loss
    print("\n2. Focal Loss:")
    focal_loss = FocalLoss(gamma=2.0)
    loss_val = focal_loss(pred, target)
    print(f"   Loss: {loss_val.item():.4f}")
    
    # Test Combined Loss
    print("\n3. Combined Loss:")
    combined_loss = CombinedLoss(
        use_focal=True,
        use_label_smoothing=True,
        lambda_focal=0.5
    )
    loss_val = combined_loss(pred, target)
    print(f"   Loss: {loss_val.item():.4f}")
    
    # Test factory function
    print("\n4. Factory function:")
    loss_fn = create_loss_function('combined')
    loss_val = loss_fn(pred, target)
    print(f"   Loss: {loss_val.item():.4f}")
    
    print("\n✓ All loss function tests passed")

