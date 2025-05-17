
Model_Path=models/Meta-Llama-3-8B-Instruct-w4a16
Model_id="llama-3-8b-instruct"
Bench_name="mt_bench"

python3 evaluation/inference_baseline_w4a16_gptq_marlin.py \
    --model-path $Model_Path \
    --cuda-graph \
    --model-id ${Model_id}/w4a16/baseline \
    --memory-limit 0.80 \
    --bench-name $Bench_name \
    --dtype "float16"
