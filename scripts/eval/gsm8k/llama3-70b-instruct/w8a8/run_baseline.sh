Model_Path=/home/ydzhang/checkpoints/deepcompress/Meta-Llama-3-70B-Instruct-w8a8-gchn
Model_id="llama-3-70b-instruct"
Bench_name="gsm8k"

python3 evaluation/inference_baseline_w8a8.py \
    --model-path $Model_Path \
    --cuda-graph \
    --model-id ${Model_id}/w8a8/baseline \
    --memory-limit 0.95 \
    --bench-name $Bench_name \
    --dtype "float16" \
    --max-new-tokens 256
