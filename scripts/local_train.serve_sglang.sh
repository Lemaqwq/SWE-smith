#!/bin/bash

# N_HOURS=4 N_GPUS=4 modal run --detach swesmith/train/serve_sglang.py \
#     --model-path /weights/outputs/qwen2p5-coder-32b-lora-lr1e-4-warmup5___difficulty/qwen2p5-coder-32b-lora-lr1e-4-warmup5___difficulty/merged \
#     --served-model-name gpt-4o \
#     --tokenizer-path /weights/Qwen/Qwen2.5-Coder-32B-Instruct

# N_HOURS=3 N_GPUS=8 modal run --detach swesmith/train/serve_sglang.py \
#     --model-path /mnt/nfs/liheng/models/exps/qwen2p5-coder-32b-full-lr1e-4-warmup5___xml_all_250413/epoch_2 \
#     --served-model-name gpt-4o \
#     --tokenizer-path /mnt/nfs/liheng/models/Qwen/Qwen2.5-Coder-32B-Instruct


#!/bin/bash
export CUDA_VISIBLE_DEVICES=3,4

# Configuration
MODEL_PATH="/mnt/nfs/liheng/models/exps/qwen2p5-coder-32b-full-lr1e-4-warmup5___xml_all_250413/epoch_2"
TOKENIZER_PATH="/mnt/nfs/liheng/models/Qwen/Qwen2.5-Coder-32B-Instruct"
SERVED_MODEL_NAME="gpt-4o"
N_GPUS=2
CONTEXT_LENGTH=32768

echo "Serving model locally from $MODEL_PATH using $N_GPUS GPUsd"

# Launch SGLang server directly
python -m sglang.launch_server \
    --model-path "$MODEL_PATH" \
    --tokenizer-path "$TOKENIZER_PATH" \
    --tp-size "$N_GPUS" \
    --port 3000 \
    --host 0.0.0.0 \
    --served-model-name "$SERVED_MODEL_NAME" \
    --context-length "$CONTEXT_LENGTH" \
    --api-key swesmith