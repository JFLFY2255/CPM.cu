Model_Path=models/Meta-Llama-3-70B-Instruct-w8a8
Model_id="llama-3-70b-instruct"
Bench_name="mt_bench"

python3 evaluation/spec_bench/inference_baseline_w8a8.py \
    --model-path $Model_Path \
    --cuda-graph \
    --model-id ${Model_id}/w8a8/baseline \
    --memory-limit 0.95 \
    --bench-name $Bench_name \
    --dtype "float16"
