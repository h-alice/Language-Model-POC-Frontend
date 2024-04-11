docker run --gpus all \
           -p 15820:80 \
           -v /home/q36862/model_repos:/models ghcr.io/huggingface/text-embeddings-inference:turing-0.6 \
           --model-id /models/multilingual-e5-large