#!/bin/bash -e
#SBATCH --job-name=vllm-oss
#SBATCH --time=100:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --gpus-per-node=H100

MODEL=openai/gpt-oss-120b
EXTRA_ARGS="--async-scheduling --gpu-memory-utilization 0.92 --tool-call-parser openai --enable-auto-tool-choice"
REMOTE_PORT=7002
REMOTE_ADDRESS="ubuntu@1.2.3.4"
SIF=/opt/nesi/containers/vllm/vllm-openai-v0.10.2.sif
export VLLM_API_KEY="secretkey"

# find unused port
port=$(python -c "import socket; s = socket.socket(); s.bind(('', 0)); print(s.getsockname()[1]); s.close()")
echo "Using port: $port"

# open reverse ssh tunnel in background (make sure you can SSH here non-interactively first)
ssh -Nf -R 0.0.0.0:${REMOTE_PORT}:localhost:$port ${REMOTE_ADDRESS}
echo "SSH connection opened: remote port is ${REMOTE_PORT}"

# create a fake home directory to isolate things
# model weights will be downloaded here
fakehome=/nesi/nobackup/${SLURM_JOB_ACCOUNT}/${USER}/fakehome
mkdir -p ${fakehome}
echo "Fake home for apptainer: ${fakehome}"

# run vllm
echo "Starting vllm"
unset APPTAINER_BIND
apptainer exec --nv --no-home --writable-tmpfs --bind ${fakehome}:${HOME} ${SIF} \
    python3 -m vllm.entrypoints.openai.api_server \
        --host 0.0.0.0 \
        --port $port \
        --model ${MODEL} ${EXTRA_ARGS}

echo "Finished"
