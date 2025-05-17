
Model_Path=meta-llama/Meta-Llama-3-8B-Instruct
Model_id="llama-3-8b-instruct"
Bench_name="human_eval"

python3 evaluation/inference_baseline.py \
    --model-path $Model_Path \
    --cuda-graph \
    --model-id ${Model_id}/fp16/baseline \
    --memory-limit 0.80 \
    --bench-name $Bench_name \
    --dtype "float16" \
    --max-new-tokens 512
