import torch
from torch.nn import Linear, Module, RMSNorm
import torch.nn.functional as F


def activation_quantization(x, min_val=1e-5):
    """
    Quantize the activations of a linear layer to -127, 0, 127.
    Using the maximum value of the activations to scale the quantization.

    Args:
        x (torch.Tensor): Activations of the linear layer.
        min_val (float): Minimum value to clamp the activations to.

    Returns:
        torch.Tensor: Quantized activations.
    """
    scale = 127.0 / x.abs().max(dim=-1, keepdim=True).values.clamp_(min=min_val)
    y = (x * scale).round().clamp_(-127, 127) / scale
    return y


def weight_quantization(w, min_val=1e-5):
    """
    Quantize the weights of a linear layer to -1, 0, 1.

    Args:
        w (torch.Tensor): Weights of the linear layer.
        min_val (float): Minimum value to clamp the weights to.

    Returns:
        torch.Tensor: Quantized weights.
    """
    scale = 1.0 / w.abs().mean().clamp_(min=min_val)
    y = (w * scale).round().clamp_(-1, 1) / scale
    return y


class BitLinear(Linear):
    def forward(self, x):
        w = self.weight
        x_norm = RMSNorm(x)
        x_quant = x_norm + (activation_quantization(x_norm) - x_norm).detach()
        w_quant = w + (weight_quantization(w) - w).detach()
        return F.linear(x_quant, w_quant)


# replace all Linear layers with BitLinear layers -> done!
