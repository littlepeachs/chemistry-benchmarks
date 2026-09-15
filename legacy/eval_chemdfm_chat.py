import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import logging
import json
import csv
import argparse
import os
logging.getLogger("transformers").setLevel(logging.ERROR)

# 加载分词器与模型 
parser = argparse.ArgumentParser()
parser.add_argument("--model_name", type=str, default="Qwen3-8B")
parser.add_argument("--critic_model_name", type=str, default="Qwen3-8B")
parser.add_argument("--dataset_name", type=str, default="mascqa")
parser.add_argument("--subject", type=str, default=None)
args = parser.parse_args()

model_name = args.model_name
critic_model_name = args.critic_model_name
dataset_name = args.dataset_name
subject = args.subject
model_path = f"/ssd/liwentao/LLM/reasoning/models/{model_name}"

critic_model_path = f"/ssd/liwentao/LLM/reasoning/models/{critic_model_name}"

critic_model = AutoModelForCausalLM.from_pretrained(
    critic_model_path,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)
critic_tokenizer = AutoTokenizer.from_pretrained(critic_model_path)


model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(model_path)

if dataset_name == "mascqa":
    dataset_path = "/ssd/liwentao/LLM/reasoning/datasets/mascqa/mascqa_test.json"
elif dataset_name == "ChemBench4K":
    dataset_path = "/ssd/liwentao/LLM/reasoning/datasets/ChemBench4K/ChemBench4K_test.json"
elif dataset_name == "ChemBench":
    dataset_path = f"/ssd/liwentao/LLM/reasoning/datasets/ChemBench/{subject}/qa_data.json"
else:
    raise ValueError(f"Unsupported dataset: {dataset_name}")

with open(dataset_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

acc = 0
results = {"Truth": [], "Model": [], "Critic": [], "Subject": []}
for idx,item in enumerate(data):
    prompt = item['question'] + "\n Reply with the single letter corresponding to the correct answer (e.g., A, B, C, D or a numerical value). The answer is:"
    answer = item['answer']
    task_name = item['subject']
    text = "User: " + prompt + "\n" + "Assistant:"
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generation_config = GenerationConfig(
        do_sample=True,
        top_k=20,
        top_p=0.9,
        temperature=0.9,
        max_new_tokens=1024,
        repetition_penalty=1.05,
        eos_token_id=tokenizer.eos_token_id
    )
    generated_ids = model.generate(**model_inputs, generation_config=generation_config)
    generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # 移除响应中的思考过程部分
    think_end_tag = "</think>"
    if think_end_tag in response:
        # 假设</think>标签之后是主要的回答内容
        cleaned_response = response.split(think_end_tag, 1)[-1].strip()
    else:
        cleaned_response = response.strip()

    # 进行模糊匹配以判断答案是否正确
    # 为避免部分匹配（例如答案'A'匹配到'Apple'），我们将回复按非字母数字字符分割
    # 首先将标点符号替换为空格

    # 检查标准答案（转为小写字符串）是否存在于回复的各部分中
    critic_prompt = f"You are a critic assistant. For the question: {item['question']}.\n The standard answer is: {answer}.\n The response is: {cleaned_response}.\n Is the response correct? Reply with 'yes' or 'no'.\n"
    critic_messages = [{"role": "user", "content": critic_prompt}]
    critic_text = critic_tokenizer.apply_chat_template(
        critic_messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False  # 关键参数，禁用 Thinking 模式
    )
    critic_model_inputs = critic_tokenizer([critic_text], return_tensors="pt").to(critic_model.device)
    critic_generated_ids = critic_model.generate(**critic_model_inputs, max_new_tokens=1024)
    critic_generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(critic_model_inputs.input_ids, critic_generated_ids)
    ]
    critic_response = critic_tokenizer.batch_decode(critic_generated_ids, skip_special_tokens=True)[0]
    if "yes" in str(critic_response).lower().strip():
        print(f"第{idx}个样本，回答正确")
        acc += 1
    else:
        print(f"第{idx}个样本，回答错误")
    if idx % 5 == 0:
        print(f"第{idx}个样本，标准答案：{answer}",flush=True)
        print(f"第{idx}个样本，模型答案：{cleaned_response}",flush=True)
    results["Truth"].append(answer)
    results["Model"].append(cleaned_response)
    results["Critic"].append(critic_response)
    results["Subject"].append(task_name)
print("#### Final Result ####")
print(f"准确率：{acc / len(data)}")

if not os.path.exists(f"./eval_results/{dataset_name}"):
    os.makedirs(f"./eval_results/{dataset_name}")

if subject: 
    with open(f"./eval_results/{dataset_name}/{model_name}_{critic_model_name}_{subject}.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Truth", "Model", "Critic", "Subject"])
        for truth, model, critic, subject in zip(results["Truth"], results["Model"], results["Critic"], results["Subject"]):
            writer.writerow([truth, model, critic, subject])
else:
    with open(f"./eval_results/{dataset_name}/{model_name}_{critic_model_name}.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Truth", "Model", "Critic", "Subject"])
        for truth, model, critic, subject in zip(results["Truth"], results["Model"], results["Critic"], results["Subject"]):
            writer.writerow([truth, model, critic, subject])
