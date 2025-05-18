Quant_Path=quant_models/Meta-Llama-3-8B-Instruct-w4a8-qqq-g128
Output_Path=models/Meta-Llama-3-8B-Instruct-w4a8-qqq-g128

python model_convert/convert_w4a8_qqq_group.py \
    --quant-path $Quant_Path \
    --output-path $Output_Path 