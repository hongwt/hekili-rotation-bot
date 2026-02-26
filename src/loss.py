"""
Loss functions for PixelAlphabet.

Includes:
- LabelSmoothingCrossEntropy: Standard label smoothing CE (legacy)
- FocalLoss: Standard focal loss (legacy)
- FocalLabelSmoothingLoss: Unified focal + label smoothing with per-class alpha
- ConfusionPairContrastiveLoss: Margin-based contrastive loss for confusable pairs
- CombinedLoss: Integrates FocalLabelSmoothingLoss + optional contrastive loss
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Confusable character pair definitions
# ---------------------------------------------------------------------------

def _char_to_label(char: str) -> int:
    """Convert character to integer label (local helper to avoid circular import)."""
    if char.isdigit():
        return int(char)
    elif char.isalpha() and len(char) == 1:
        return ord(char.upper()) - ord('A') + 10
    else:
        raise ValueError(f"Invalid character: {char}")


# Predefined confusable character pairs
CONFUSED_PAIRS: List[Tuple[str, str]] = [
    ('7', 'T'),
    ('8', 'B'),
    ('0', 'D'),
    ('5', 'S'),
    ('2', 'Z'),
    ('Q', '0'),
    ('1', 'L'),
    ('6', 'G'),
]

# Pre-computed label index pairs for runtime use
CONFUSED_PAIR_INDICES: List[Tuple[int, int]] = [
    (_char_to_label(a), _char_to_label(b)) for a, b in CONFUSED_PAIRS
]

# Characters involved in confusion pairs (unique set)
CONFUSABLE_CHARS: List[str] = sorted(set(
    c for pair in CONFUSED_PAIRS for c in pair
))


def get_confusable_alpha_weights(
    num_classes: int = 36,
    base_weight: float = 1.0,
    confusable_weight: float = 2.0,
) -> torch.Tensor:
    """
    Build a per-class alpha weight vector giving higher weight to confusable classes.

    Args:
        num_classes: Total number of classes.
        base_weight: Weight for non-confusable classes.
        confusable_weight: Weight for confusable classes.

    Returns:
        Tensor of shape (num_classes,).
    """
    alpha = torch.full((num_classes,), base_weight)
    for char in CONFUSABLE_CHARS:
        idx = _char_to_label(char)
        if idx < num_classes:
            alpha[idx] = confusable_weight
    return alpha


# ---------------------------------------------------------------------------
# Legacy loss classes (kept for backward compatibility)
# ---------------------------------------------------------------------------

class LabelSmoothingCrossEntropy(nn.Module):
    """
    Label Smoothing Cross Entropy Loss (legacy).

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
    Focal Loss implementation for handling class imbalance and hard examples (legacy).

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


# ---------------------------------------------------------------------------
# New unified loss classes
# ---------------------------------------------------------------------------

class FocalLabelSmoothingLoss(nn.Module):
    """
    Unified Focal + Label Smoothing Loss.

    Integrates the focal weighting factor (1-p_t)^gamma directly into the
    label-smoothed cross-entropy computation so that every sample's gradient
    contribution is modulated by its difficulty.

    Formula:
        L_FLS = -alpha_t * (1 - p_t)^gamma * sum_c( y_smooth_c * log(p_c) )

    where y_smooth_c is the label-smoothed target distribution.
    """

    def __init__(
        self,
        epsilon: float = 0.1,
        gamma: float = 3.0,
        alpha: Optional[torch.Tensor] = None,
        num_classes: int = 36,
        reduction: str = 'mean',
    ):
        """
        Args:
            epsilon: Label smoothing factor (default: 0.1).
            gamma: Focal focusing parameter (default: 3.0).
            alpha: Per-class weight tensor of shape (num_classes,). If None,
                   uses ``get_confusable_alpha_weights()`` to auto-generate.
            num_classes: Number of classes (used only when alpha is None).
            reduction: 'mean', 'sum', or 'none'.
        """
        super(FocalLabelSmoothingLoss, self).__init__()
        self.epsilon = epsilon
        self.gamma = gamma
        self.reduction = reduction

        if alpha is None:
            alpha = get_confusable_alpha_weights(num_classes)
        self.register_buffer('alpha', alpha)

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred: Prediction logits (B, C).
            target: Ground truth labels (B).

        Returns:
            Loss value.
        """
        n_classes = pred.size(1)

        # Label smoothing: build soft targets
        one_hot = F.one_hot(target, n_classes).float()
        smooth_target = (1 - self.epsilon) * one_hot + self.epsilon / n_classes

        # Log-softmax for numerical stability
        log_prob = F.log_softmax(pred, dim=1)
        prob = torch.exp(log_prob)

        # Per-sample label-smoothed CE (before focal modulation)
        # shape: (B,)
        ce_per_sample = -(smooth_target * log_prob).sum(dim=1)

        # p_t: probability assigned to the true class
        pt = prob.gather(1, target.unsqueeze(1)).squeeze(1)  # (B,)

        # Focal modulation factor
        focal_weight = (1.0 - pt) ** self.gamma  # (B,)

        # Per-class alpha weight
        alpha_t = self.alpha.to(pred.device).gather(0, target)  # (B,)

        # Final loss
        loss = alpha_t * focal_weight * ce_per_sample

        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss


class ConfusionPairContrastiveLoss(nn.Module):
    """
    Margin-based contrastive loss for predefined confusable character pairs.

    For each pair (a, b) present in a training batch, computes the cosine
    distance between the mean feature embedding of class a and class b, then
    penalises if the distance is below a margin threshold.

    L_contrast = sum over pairs: max(0, margin - d(mu_a, mu_b))

    where d is cosine distance = 1 - cosine_similarity.
    """

    def __init__(
        self,
        confused_pairs: Optional[List[Tuple[int, int]]] = None,
        margin: float = 0.5,
        reduction: str = 'mean',
    ):
        """
        Args:
            confused_pairs: List of (label_a, label_b) index tuples. Defaults
                            to ``CONFUSED_PAIR_INDICES``.
            margin: Minimum desired cosine distance between pair centroids.
            reduction: 'mean' over active pairs, 'sum', or 'none'.
        """
        super(ConfusionPairContrastiveLoss, self).__init__()
        if confused_pairs is None:
            confused_pairs = CONFUSED_PAIR_INDICES
        self.confused_pairs = confused_pairs
        self.margin = margin
        self.reduction = reduction

    def forward(
        self,
        features: torch.Tensor,
        targets: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            features: Embedding vectors (B, D) from model.forward_features().
            targets: Ground truth labels (B).

        Returns:
            Contrastive loss (scalar). Zero if no pair is present in the batch.
        """
        losses = []
        for idx_a, idx_b in self.confused_pairs:
            mask_a = targets == idx_a
            mask_b = targets == idx_b

            if mask_a.sum() == 0 or mask_b.sum() == 0:
                continue  # pair not present in this batch

            # Mean embeddings
            mu_a = features[mask_a].mean(dim=0)
            mu_b = features[mask_b].mean(dim=0)

            # Cosine distance = 1 - cosine_similarity
            cos_sim = F.cosine_similarity(mu_a.unsqueeze(0), mu_b.unsqueeze(0))
            cos_dist = 1.0 - cos_sim  # (1,)

            pair_loss = torch.clamp(self.margin - cos_dist, min=0.0)
            losses.append(pair_loss)

        if len(losses) == 0:
            return torch.tensor(0.0, device=features.device, requires_grad=True)

        losses = torch.cat(losses)

        if self.reduction == 'mean':
            return losses.mean()
        elif self.reduction == 'sum':
            return losses.sum()
        else:
            return losses


# ---------------------------------------------------------------------------
# Combined loss (updated)
# ---------------------------------------------------------------------------

class CombinedLoss(nn.Module):
    """
    Combined Loss function that integrates multiple loss components.

    Default configuration (updated):
        Base loss: FocalLabelSmoothingLoss (replaces old CE+Focal additive)
        Auxiliary: ConfusionPairContrastiveLoss (optional)

    Total Loss = L_FLS + lambda_contrastive * L_contrast

    Legacy mode: when ``use_focal`` / ``use_label_smoothing`` / ``lambda_focal``
    are passed explicitly, falls back to the old additive behaviour for backward
    compatibility.
    """

    def __init__(
        self,
        # --- new unified API ---
        smoothing: float = 0.1,
        focal_gamma: float = 3.0,
        alpha_weights: Optional[torch.Tensor] = None,
        num_classes: int = 36,
        use_contrastive: bool = True,
        lambda_contrastive: float = 0.3,
        contrastive_margin: float = 0.5,
        # --- legacy API (kept for backward compat) ---
        use_focal: bool = True,
        use_label_smoothing: bool = True,
        focal_alpha: float = 1.0,
        lambda_focal: float = 0.5,
    ):
        """
        Args:
            smoothing: Label smoothing epsilon.
            focal_gamma: Focal loss gamma parameter.
            alpha_weights: Per-class weight tensor (num_classes,). Auto-generated
                           if None.
            num_classes: Number of classes.
            use_contrastive: Whether to include contrastive loss.
            lambda_contrastive: Weight for contrastive loss component.
            contrastive_margin: Margin for contrastive loss.
            use_focal: (legacy) kept for backward compatibility.
            use_label_smoothing: (legacy) kept for backward compatibility.
            focal_alpha: (legacy) scalar alpha for old FocalLoss.
            lambda_focal: (legacy) weight for old additive focal.
        """
        super(CombinedLoss, self).__init__()

        # Use the new unified FocalLabelSmoothingLoss as base
        self.base_loss = FocalLabelSmoothingLoss(
            epsilon=smoothing,
            gamma=focal_gamma,
            alpha=alpha_weights,
            num_classes=num_classes,
        )

        # Optional contrastive loss
        self.contrastive_loss: Optional[ConfusionPairContrastiveLoss] = None
        self.lambda_contrastive = lambda_contrastive
        if use_contrastive:
            self.contrastive_loss = ConfusionPairContrastiveLoss(
                margin=contrastive_margin,
            )

    def forward(
        self,
        pred: torch.Tensor,
        target: torch.Tensor,
        features: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Args:
            pred: Prediction logits (B, C).
            target: Ground truth labels (B).
            features: Optional embedding vectors (B, D) for contrastive loss.
                      If None and contrastive loss is enabled, the contrastive
                      component is skipped for this call.

        Returns:
            Combined loss value.
        """
        loss = self.base_loss(pred, target)

        if self.contrastive_loss is not None and features is not None:
            contrast = self.contrastive_loss(features, target)
            loss = loss + self.lambda_contrastive * contrast

        return loss


def create_loss_function(loss_type: str = 'combined', **kwargs):
    """
    Factory function to create loss function.

    Args:
        loss_type: Type of loss:
            - 'ce': Standard CrossEntropyLoss
            - 'focal': FocalLoss (legacy)
            - 'label_smoothing': LabelSmoothingCrossEntropy (legacy)
            - 'focal_label_smoothing': FocalLabelSmoothingLoss (new)
            - 'combined': CombinedLoss (FocalLabelSmoothing + contrastive)
        **kwargs: Additional arguments forwarded to the loss constructor.

    Returns:
        Loss function instance.
    """
    if loss_type == 'ce':
        return nn.CrossEntropyLoss()
    elif loss_type == 'focal':
        return FocalLoss(**kwargs)
    elif loss_type == 'label_smoothing':
        return LabelSmoothingCrossEntropy(**kwargs)
    elif loss_type == 'focal_label_smoothing':
        return FocalLabelSmoothingLoss(**kwargs)
    elif loss_type == 'combined':
        return CombinedLoss(**kwargs)
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")


if __name__ == '__main__':
    # Test loss functions
    print("Testing loss functions...")

    # Dummy data
    batch_size = 8
    num_classes = 36
    pred = torch.randn(batch_size, num_classes)
    target = torch.randint(0, num_classes, (batch_size,))
    features = torch.randn(batch_size, 256)

    # Test Label Smoothing Cross Entropy (legacy)
    print("\n1. Label Smoothing Cross Entropy:")
    ls_loss = LabelSmoothingCrossEntropy(epsilon=0.1)
    loss_val = ls_loss(pred, target)
    print(f"   Loss: {loss_val.item():.4f}")

    # Test Focal Loss (legacy)
    print("\n2. Focal Loss:")
    focal_loss = FocalLoss(gamma=2.0)
    loss_val = focal_loss(pred, target)
    print(f"   Loss: {loss_val.item():.4f}")

    # Test FocalLabelSmoothingLoss (new)
    print("\n3. FocalLabelSmoothingLoss:")
    fls = FocalLabelSmoothingLoss(epsilon=0.1, gamma=3.0)
    loss_val = fls(pred, target)
    print(f"   Loss: {loss_val.item():.4f}")

    # Test ConfusionPairContrastiveLoss (new)
    print("\n4. ConfusionPairContrastiveLoss:")
    cpcl = ConfusionPairContrastiveLoss(margin=0.5)
    loss_val = cpcl(features, target)
    print(f"   Loss: {loss_val.item():.4f}")

    # Test Combined Loss (updated)
    print("\n5. Combined Loss (updated):")
    combined_loss = CombinedLoss()
    loss_val = combined_loss(pred, target, features)
    print(f"   Loss: {loss_val.item():.4f}")

    # Test factory function
    print("\n6. Factory function:")
    loss_fn = create_loss_function('combined')
    loss_val = loss_fn(pred, target)
    print(f"   Loss: {loss_val.item():.4f}")

    # Test confusable alpha weights
    print("\n7. Confusable alpha weights:")
    alpha = get_confusable_alpha_weights()
    print(f"   Shape: {alpha.shape}")
    print(f"   Confusable chars: {CONFUSABLE_CHARS}")
    print(f"   Sample weights: 'W'={alpha[_char_to_label('W')]:.1f}, "
          f"'8'={alpha[_char_to_label('8')]:.1f}, "
          f"'B'={alpha[_char_to_label('B')]:.1f}")

    print("\n✓ All loss function tests passed")

