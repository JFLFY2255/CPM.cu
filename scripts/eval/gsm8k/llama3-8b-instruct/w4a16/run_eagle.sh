Model_Path=/home/ydzhang/checkpoints/AutoGPTQ/Meta-Llama-3-8B-Instruct-rotation-4bit-128g-pileval-mse-desc-static_group_default_merge
Eagle_Path=/home/ydzhang/checkpoints/yuhuili/EAGLE-LLaMA3-Instruct-8B-w4a8_rotation
Model_id="llama-3-8b-instruct"
Bench_name="gsm8k"

python3 evaluation/inference_eagle_w4a16_gptq_marlin.py \
    --model-path $Model_Path \
    --eagle-path $Eagle_Path \
    --cuda-graph \
    --model-id ${Model_id}/w4a16/eagle \
    --memory-limit 0.80 \
    --bench-name $Bench_name \
    --dtype "float16" \
    --quant-rotation \
    --eagle-num-iter 6 \
    --eagle-topk-per-iter 10 \
    --eagle-tree-size 60 \
    --max-new-tokens 256