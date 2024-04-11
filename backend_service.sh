docker run --gpus all \
           -p 15820:80 \
           -v /home/q36862/model_repos:/models ghcr.io/huggingface/text-embeddings-inference:turing-0.6 \
           --model-id /models/multilingual-e5-large

docker run --gpus all \
           --shm-size 1g \
           -p 15810:80 \
           -v /home/q36862/data:/data \
           -v /home/q36862/model_repos:/models ghcr.io/huggingface/text-generation-inference:1.3 \
           --model-id /models/M7 \
           --max-concurrent-requests 1 \
           --max-total-tokens 4096 \
           --max-input-length 2048 \
           --num-shard 1 \
           --quantize bitsandbytes-nf4