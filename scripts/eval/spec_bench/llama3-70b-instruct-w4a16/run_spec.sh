Model_Path=/home/ydzhang/checkpoints/AutoGPTQ/Meta-Llama-3-70B-Instruct-qqq-rotation-4bit-128g-pileval-mse_merge
Draft_Path=/home/ydzhang/checkpoints/AutoGPTQ/Meta-Llama-3-8B-Instruct-rotation-4bit-128g-pileval-mse-desc-static_group_default_merge
Model_id="llama-3-70b-instruct"
Bench_name="spec_bench"

python3 evaluation/inference_spec_w4a16_gm_for_w4a16_gm.py \
    --model-path $Model_Path \
    --draft-path $Draft_Path \
    --cuda-graph \
    --model-id ${Model_id}/w4a16/spec \
    --memory-limit 0.9 \
    --bench-name $Bench_name \
    --dtype "float16" \
    --spec-num-iter 6 \
    --draft-prefill-sep \
    --draft-cuda-graph