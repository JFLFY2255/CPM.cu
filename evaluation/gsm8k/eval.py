import os
import json
from datasets import load_dataset
from transformers import AutoTokenizer

from tqdm import tqdm

import time, torch, re
import numpy as np
import argparse

from tqdm import tqdm
ANS_RE = re.compile(r"#### (\-?[0-9\.\,]+)")
INVALID_ANS = "[invalid]"

N_SHOT = 8
COT_FLAG = True
DEBUG = False
ANSWER_TRIGGER = "The answer is"

def create_demo_text(n_shot=8, cot_flag=True):
    # This function is borrowed from repo Guangxuan-Xiao/GSM8K-eval
    # https://github.com/Guangxuan-Xiao/GSM8K-eval/
    question, chain, answer = [], [], []
    question.append(
        "There are 15 trees in the grove. "
        "Grove workers will plant trees in the grove today. "
        "After they are done, there will be 21 trees. "
        "How many trees did the grove workers plant today?"
    )
    chain.append(
        "There are 15 trees originally. "
        "Then there were 21 trees after some more were planted. "
        "So there must have been 21 - 15 = 6."
    )
    answer.append("6")

    question.append(
        "If there are 3 cars in the parking lot and 2 more cars arrive, "
        "how many cars are in the parking lot?"
    )
    chain.append("There are originally 3 cars. 2 more cars arrive. 3 + 2 = 5.")
    answer.append("5")

    question.append(
        "Leah had 32 chocolates and her sister had 42. If they ate 35, "
        "how many pieces do they have left in total?"
    )
    chain.append(
        "Originally, Leah had 32 chocolates. "
        "Her sister had 42. So in total they had 32 + 42 = 74. "
        "After eating 35, they had 74 - 35 = 39."
    )
    answer.append("39")

    question.append(
        "Jason had 20 lollipops. He gave Denny some lollipops. Now Jason "
        "has 12 lollipops. How many lollipops did Jason give to Denny?"
    )
    chain.append(
        "Jason started with 20 lollipops. Then he had 12 after giving some "
        "to Denny. So he gave Denny 20 - 12 = 8."
    )
    answer.append("8")

    question.append(
        "Shawn has five toys. For Christmas, he got two toys each from his "
        "mom and dad. How many toys does he have now?"
    )
    chain.append(
        "Shawn started with 5 toys. If he got 2 toys each from his mom and "
        "dad, then that is 4 more toys. 5 + 4 = 9."
    )
    answer.append("9")

    question.append(
        "There were nine computers in the server room. Five more computers "
        "were installed each day, from monday to thursday. "
        "How many computers are now in the server room?"
    )
    chain.append(
        "There were originally 9 computers. For each of 4 days, 5 more "
        "computers were added. So 5 * 4 = 20 computers were added. "
        "9 + 20 is 29."
    )
    answer.append("29")

    question.append(
        "Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On "
        "wednesday, he lost 2 more. "
        "How many golf balls did he have at the end of wednesday?"
    )
    chain.append(
        "Michael started with 58 golf balls. After losing 23 on tuesday, "
        "he had 58 - 23 = 35. After losing 2 more, "
        "he had 35 - 2 = 33 golf balls."
    )
    answer.append("33")

    question.append(
        "Olivia has $23. She bought five bagels for $3 each. "
        "How much money does she have left?"
    )
    chain.append(
        "Olivia had 23 dollars. "
        "5 bagels for 3 dollars each will be 5 x 3 = 15 dollars. "
        "So she has 23 - 15 dollars left. 23 - 15 is 8."
    )
    answer.append("8")

    index_list = list(range(len(question)))

    # Concatenate demonstration examples ...
    demo_text = ""
    for i in index_list[:n_shot]:
        if cot_flag:
            demo_text += (
                "Q: "
                + question[i]
                + "\nA: "
                + chain[i]
                + " "
                + ANSWER_TRIGGER
                + " "
                + answer[i]
                + ".\n\n"
            )
        else:
            demo_text += (
                "Question: "
                + question[i]
                + "\nAnswer: "
                + ANSWER_TRIGGER
                + " "
                + answer[i]
                + ".\n\n"
            )
    return demo_text

def clean_answer(model_pred):
    # This function is borrowed from repo Guangxuan-Xiao/GSM8K-eval
    # https://github.com/Guangxuan-Xiao/GSM8K-eval/
    model_pred = model_pred.lower()
    preds = model_pred.split(ANSWER_TRIGGER.lower())
    answer_flag = True if len(preds) > 1 else False
    if answer_flag:
        # Pick first answer with flag
        pred = preds[1]
    else:
        # Pick last number without flag
        pred = preds[-1]

    pred = pred.replace(",", "")
    pred = [s for s in re.findall(r"-?\d+\.?\d*", pred)]

    if len(pred) == 0:
        return "[invalid]"

    if answer_flag:
        # choose the first element in list
        pred = pred[0]
    else:
        # choose the last element in list
        pred = pred[-1]

    # (For arithmetic tasks) if a word ends with period, it will be omitted ...
    if pred[-1] == ".":
        pred = pred[:-1]

    return pred


def build_prompt(input_text, n_shot=8, cot_flag=True):
    # This function is borrowed from repo Guangxuan-Xiao/GSM8K-eval
    # https://github.com/Guangxuan-Xiao/GSM8K-eval/
    demo = create_demo_text(n_shot, cot_flag)
    input_text_prompt = demo + "Q: " + input_text + "\n" + "A:"
    return input_text_prompt


def extract_answer_from_output(completion):
    # This function is borrowed from repo Guangxuan-Xiao/GSM8K-eval
    # https://github.com/Guangxuan-Xiao/GSM8K-eval/
    match = ANS_RE.search(completion)
    if match:
        match_str = match.group(1).strip()
        match_str = match_str.replace(",", "")
        return match_str
    else:
        return INVALID_ANS
    
def is_correct(model_answer, answer):
    # This function is borrowed from repo Guangxuan-Xiao/GSM8K-eval
    # https://github.com/Guangxuan-Xiao/GSM8K-eval/
    gt_answer = extract_answer_from_output(answer)
    assert gt_answer != INVALID_ANS
    return model_answer == gt_answer

@torch.inference_mode()
def run_eval(
    model,
    tokenizer,
    data_path,
    forward_func,
    model_id,
    answer_file,
    max_new_tokens,
    max_length,
):
    dataset = load_dataset(data_path, split="test")
    
    entry = dataset[0]
    warmup_times = 3
    for wm_i in range(warmup_times):
        input_str = build_prompt(entry['question'])
        if "deepseek" in model_id:
            messages=[
                { 'role': 'user', 'content': input_str}
            ]
            input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to("cuda")
        else:
            input_ids = tokenizer.encode(input_str, return_tensors="pt").to("cuda").view(1, -1)

        prompt_len = input_ids.shape[-1]
        torch.cuda.synchronize()
        start_time = time.time()
        output_ids, new_token, step, accept_length_tree = forward_func(
            input_ids,
            model,
            tokenizer,
            max_new_tokens,
            max_length,
        )
        torch.cuda.synchronize()
        cur_time = time.time() - start_time
        print(f"warmup {wm_i} done")
    
    # cnt = 0
    result = []
    accept_lengths_tree = []
    total_new_tokens = 0
    total_time = 0
    for idx, entry in tqdm(enumerate(dataset), total=len(dataset)):
        cur_accept_lengths_tree = []

        input_str = build_prompt(entry['question'])
        # TODO: make ouroboros  runnable  and get the lantency as well
        if "deepseek" in model_id:
            messages=[
                { 'role': 'user', 'content': input_str}
            ]
            input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to("cuda")
        else:
            input_ids = tokenizer.encode(input_str, return_tensors="pt").to("cuda").view(1, -1)

        torch.cuda.synchronize()
        start_time = time.time()
        output_ids, new_token, step, accept_length_tree = forward_func(
            input_ids,
            model,
            tokenizer,
            max_new_tokens,
            max_length,
        )
        torch.cuda.synchronize()
        cur_time = time.time() - start_time
        accept_lengths_tree.extend(accept_length_tree)

        output_str = tokenizer.decode(output_ids, skip_special_tokens=True)
        pred_ans = clean_answer(output_str)
        is_cor = is_correct(pred_ans, entry['answer'])

        cur_accept_lengths_tree.extend(accept_length_tree)
        os.makedirs(os.path.dirname(answer_file), exist_ok=True)
        with open(os.path.expanduser(answer_file), "a") as fout:
            ans_json = {
                "data_id": idx,
                "model_id": model_id,
                "model_output": output_str,
                "steps": step,
                "new_tokens": int(new_token),
                "wall_time": cur_time,
                "accept_lengths": cur_accept_lengths_tree,
                "generate_speed": int(new_token) / cur_time,
                "correct": is_cor,
                "tstamp": time.time(),
            }
            fout.write(json.dumps(ans_json) + "\n")

        result.append(is_cor)
        total_new_tokens += new_token
        total_time += cur_time
        # if cnt == 2:
        #     break
        # cnt += 1
    print("#Mean accepted tokens: ", np.mean(accept_lengths_tree))
    print("#Accuracy: ", sum(result) / len(result))
    print("#Generate latency: ", total_time / total_new_tokens)
    

