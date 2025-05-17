Model_Path=models/Meta-Llama-3-70B-Instruct-w4a16
Draft_Path=models/Meta-Llama-3-8B-Instruct-w4a16
Eagle_Path=models/EAGLE-LLaMA3-Instruct-70B-on-w4a16
Model_id="llama-3-70b-instruct"
Bench_name="spec_bench"

python3 evaluation/spec_bench/inference_hier_eagle_w4a16_gm_spec_w4a16_gm.py \
    --model-path $Model_Path \
    --draft-path $Draft_Path \
    --eagle-path $Eagle_Path \
    --cuda-graph \
    --model-id ${Model_id}/w4a16/hierspec \
    --memory-limit 0.8 \
    --bench-name $Bench_name \
    --dtype "float16" \
    --draft-prefill-sep \
    --quant-rotation \
    --spec-min-draft-length 6 \
    --draft-cuda-graph \
    --eagle-num-iter 3 \
    --eagle-topk-per-iter 10 \
    --eagle-tree-size 30
