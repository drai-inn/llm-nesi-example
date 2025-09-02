# Triton inference server on RDC A40 GPU

- Triton inference server
- vLLM backend
- Qwen3-Coder-30B-A3B quantised version
- embedding models (not working yet)
- the gpu flavours currently have large storage mounted at */mnt*, we put the triton-server home there which is where huggingface weights are downloaded to
- [dcgm exporter](https://github.com/NVIDIA/dcgm-exporter) also running

## Prerequisites

Follow the steps [here](../vllm-a40-rdc/README.md) to install Nvidia drivers and docker runtime.
