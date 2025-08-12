#!/bin/bash -e
#SBATCH --job-name=vllm-oss
#SBATCH --time=48:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --gpus-per-node=H100

MODEL=openai/gpt-oss-120b
EXTRA_ARGS="--async-scheduling --gpu-memory-utilization 0.92"
REMOTE_PORT=7002
SIF=/path/to/vllm-openai-gptoss-250812.sif
FAKEHOME=/nesi/nobackup/${SLURM_JOB_ACCOUNT}/${USER}/fakehome
export VLLM_API_KEY="secretkey"

mkdir -p ${FAKEHOME}

# find unused port
port=$(python -c "import socket; s = socket.socket(); s.bind(('', 0)); print(s.getsockname()[1]); s.close()")
echo "Using port: $port"

# open reverse ssh tunnel in background
ssh -Nf -R 0.0.0.0:${REMOTE_PORT}:localhost:$port ubuntu@address-of-vm
echo "SSH connection opened"

# run vllm
echo "Starting vllm"
unset APPTAINER_BIND
apptainer exec --nv --no-home --writable-tmpfs --bind ${FAKEHOME}:${HOME} ${SIF} \
    python3 -m vllm.entrypoints.openai.api_server \
        --host 0.0.0.0 \
        --port ${port} \
        --model ${MODEL} ${EXTRA_ARGS}

echo "Finished"
