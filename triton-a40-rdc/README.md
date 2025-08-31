# Triton inference server on RDC A40 GPU

- Triton inference server
- vLLM backend
- Qwen3-8B
- embedding models (not working yet)
- tried Qwen3-Coder-30B-A3B but had CUDA memory problems, may be possible with more work
- the gpu flavours currently have large storage mounted at */mnt*, we put the triton-server home there which is where huggingface weights are downloaded to

## Prerequisites

Follow the steps [here](../vllm-a40-rdc/README.md) to install Nvidia drivers and docker runtime.
