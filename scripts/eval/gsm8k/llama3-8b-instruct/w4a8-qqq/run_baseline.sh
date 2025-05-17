
Model_Path=/home/ydzhang/checkpoints/QQQ/Meta-Llama-3-8B-Instruct-rotation-gptq-mse-pile/Meta-Llama-3-8B-Instruct-merge
Model_id="llama-3-8b-instruct"
Bench_name="gsm8k"

python3 evaluation/inference_baseline_w4a8_qqq.py \
    --model-path $Model_Path \
    --cuda-graph \
    --model-id ${Model_id}/w4a8-qqq/baseline \
    --memory-limit 0.80 \
    --bench-name $Bench_name \
    --dtype "float16" \
    --max-new-tokens 256
