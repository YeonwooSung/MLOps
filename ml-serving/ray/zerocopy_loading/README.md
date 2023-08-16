# Zerocopy Loading for faster ML model loading

- [bert_zerocopy.py](./bert_zerocopy.py) file shows the way to copy the PyTorch model extremely fast by using ray's shared memory.
- [ray_baseline.ipynb](./ray_baseline.ipynb) is a baseline notebook for serving model with ray
- [ray_deploy.ipynb](./ray_deploy.ipynb) is a notebook for deploying model with ray

The module `zerocopy` is a module for copying PyTorch model with Ray's shared memory.
It is a part of IBM's [Project Codeflare](https://github.com/project-codeflare).

## References

- [How to load PyTorch models 340 times faster with ray](https://medium.com/ibm-data-ai/how-to-load-pytorch-models-340-times-faster-with-ray-8be751a6944c)
- [Easier model serving with zerocopy](https://medium.com/ibm-data-ai/easier-model-serving-with-zerocopy-3930d1d2a1af)
