
Model_Path=/home/ydzhang/checkpoints/QQQ/Meta-Llama-3-70B-Instruct-rotation-gptq-pile/Meta-Llama-3-70B-Instruct-merge
Model_id="llama-3-70b-instruct"
Bench_name="mt_bench"

python3 evaluation/inference_baseline_w4a8_qqq.py \
    --model-path $Model_Path \
    --cuda-graph \
    --model-id ${Model_id}/w4a8-qqq/baseline \
    --memory-limit 0.80 \
    --bench-name $Bench_name \
    --dtype "float16"
