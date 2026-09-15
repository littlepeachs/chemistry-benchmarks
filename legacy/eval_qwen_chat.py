import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
import json
import csv
import argparse

logging.getLogger("transformers").setLevel(logging.ERROR)

# Load the tokenizer and model 
parser = argparse.ArgumentParser()
parser.add_argument("--model_name", type=str, default="Qwen3-8B")
parser.add_argument("--critic_model_name", type=str, default="Qwen3-8B")
parser.add_argument("--dataset_name", type=str, default="mascqa")
parser.add_argument("--subject", type=str, default=None)
args = parser.parse_args()

model_name = args.model_name
critic_model_name = args.critic_model_name
dataset_name = args.dataset_name
model_path = f"/ssd/liwentao/LLM/reasoning/models/{model_name}"
subject = args.subject

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
    text = prompt  # Pretrained model
    messages = [{"role": "user", "content": text}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False  # Disable thinking mode
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(**model_inputs, max_new_tokens=1024)
    generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]


    # Remove the reasoning section from the response
    think_end_tag = "</think>"
    if think_end_tag in response:
        # Assume the main answer follows the </think> tag
        cleaned_response = response.split(think_end_tag, 1)[-1].strip()
    else:
        cleaned_response = response.strip()

    # Use fuzzy matching to determine whether the answer is correct
    # To avoid partial matches (e.g., answer 'A' matching 'Apple'), split on non-alphanumeric characters
    # First replace punctuation with spaces
    import re

    # Check whether the reference answer, converted to lowercase, appears in the response segments
    critic_prompt = f"You are a critic assistant. For the question: {item['question']}.\n The standard answer is: {answer}.\n The response is: {cleaned_response}.\n Is the response correct? Reply with 'yes' or 'no'.\n"
    critic_messages = [{"role": "user", "content": critic_prompt}]
    critic_text = tokenizer.apply_chat_template(
        critic_messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False  # Disable thinking mode
    )
    critic_model_inputs = critic_tokenizer([critic_text], return_tensors="pt").to(critic_model.device)
    critic_generated_ids = critic_model.generate(**critic_model_inputs, max_new_tokens=1024)
    critic_generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(critic_model_inputs.input_ids, critic_generated_ids)
    ]
    critic_response = critic_tokenizer.batch_decode(critic_generated_ids, skip_special_tokens=True)[0]
    if "yes" in str(critic_response).lower().strip():
        print(f"Sample {idx}: correct answer")
        acc += 1
    else:
        print(f"Sample {idx}: incorrect answer")
    if idx % 5 == 0:
        print(f"Sample {idx}: reference answer: {answer}",flush=True)
        print(f"Sample {idx}: model answer: {cleaned_response}",flush=True)
    results["Truth"].append(answer)
    results["Model"].append(cleaned_response)
    results["Critic"].append(critic_response)
    results["Subject"].append(task_name)
print("#### Final Result ####")
print(f"Accuracy: {acc / len(data)}")


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
