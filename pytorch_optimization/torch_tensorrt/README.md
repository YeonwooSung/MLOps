# Torch-TensorRT

[Torch-TensorRT](https://github.com/pytorch/TensorRT) is a PyTorch/TorchScript/FX compiler for NVIDIA GPUs using TensorRT

## Installation

You could download and install the pre-built binaries with pip:

```bash
$ pip install tensorrt torch-tensorrt
```

## How to use

```python
import torch_tensorrt


# convert a PyTorch model to a TorchScript model
trt_ts_module = torch_tensorrt.compile(torch_script_module,
    # If the inputs to the module are plain Tensors, specify them via the `inputs` argument:
    inputs = [example_tensor, # Provide example tensor for input shape or...
        torch_tensorrt.Input( # Specify input object with shape and dtype
            min_shape=[1, 3, 224, 224],
            opt_shape=[1, 3, 512, 512],
            max_shape=[1, 3, 1024, 1024],
            # For static size shape=[1, 3, 224, 224]
            dtype=torch.half) # Datatype of input tensor. Allowed options torch.(float|half|int8|int32|bool)
    ],

    # For inputs containing tuples or lists of tensors, use the `input_signature` argument:
    # Below, we have an input consisting of a Tuple of two Tensors (Tuple[Tensor, Tensor])
    # input_signature = ( (torch_tensorrt.Input(shape=[1, 3, 224, 224], dtype=torch.half),
    #                      torch_tensorrt.Input(shape=[1, 3, 224, 224], dtype=torch.half)), ),

    enabled_precisions = {torch.half}, # Run with FP16
)

# run inference
result = trt_ts_module(input_data)

# save the TRT embedded Torchscript
torch.jit.save(trt_ts_module, "trt_torchscript_module.ts")
```

Notes on running in lower precisions:

    - Enabled lower precisions with compile_spec.enabled_precisions
    - The module should be left in FP32 before compilation (FP16 can support half tensor models)
    - Provided input tensors dtype should be the same as module before compilation, regardless of enabled_precisions. This can be overrided by setting Input::dtype

### Use as deployment

To use the compiled module as a deployment, you can use the following code:

```python
# Deployment application
import torch
import torch_tensorrt

trt_ts_module = torch.jit.load("trt_ts_module.ts")
input_data = input_data.to("cuda").half()
result = trt_ts_module(input_data)

#
# Below is an example to compare the outputs of the original PyTorch model and the TensorRT embedded TorchScript
#

# PyTorch model inference
torch_output = model(input_data)

# TensorRT  model inference
trt_output = trt_ts_module(input_data)

# check closeness of outputs
if torch.allclose(torch_output, trt_output, atol=1e-3):
    print("outputs are close")
else:
    print("outputs are different")
```
