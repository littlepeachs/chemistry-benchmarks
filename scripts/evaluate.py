import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUFFIX = '\n Reply with the single letter corresponding to the correct answer (e.g., A, B, C, D or a numerical value). The answer is:'


def arguments():
    parser = argparse.ArgumentParser(description='Portable historical prompting/generation protocol; outputs new runs only.')
    parser.add_argument('--model', required=True)
    parser.add_argument('--benchmark', choices=['ChemBench', 'MASCQA', 'ChemBench4K'], required=True)
    parser.add_argument('--subject', help='Required for ChemBench')
    parser.add_argument('--model-root', type=Path, default=ROOT/'models')
    parser.add_argument('--model-path', type=Path, help='Override model directory')
    parser.add_argument('--data-root', type=Path, default=ROOT/'data')
    parser.add_argument('--output', type=Path, required=True, help='New run directory; never overwrite archived results')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--attention', choices=['sdpa', 'eager', 'flash_attention_2'], default='sdpa')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--include-historically-skipped', action='store_true')
    parser.add_argument('--allow-remote-code', action='store_true', help='Opt in to running ChemLLM custom model code')
    parser.add_argument('--dry-run', action='store_true', help='Check full dataset hash and show plan without loading models')
    return parser.parse_args()


def main():
    args = arguments()
    models = json.loads((ROOT/'metadata/models.json').read_text())
    if args.model not in models:
        raise ValueError(f'Unknown model: {args.model}')
    if args.limit is not None and args.limit <= 0:
        raise ValueError('--limit must be positive')
    datasets = json.loads((ROOT/'metadata/datasets.json').read_text())
    dataset = next(item for item in datasets if item['benchmark'] == args.benchmark)
    if args.benchmark == 'ChemBench':
        prepared = next((item for item in dataset['outputs'] if item['subject'] == args.subject), None)
        if prepared is None:
            raise ValueError('ChemBench requires a valid --subject; see metadata/datasets.json')
    else:
        if args.subject:
            raise ValueError('--subject only applies to ChemBench')
        prepared = dataset['outputs'][0]
    data_path = args.data_root/prepared['path']
    rows = json.loads(data_path.read_text())
    from prepare_data import normalized_hash
    if len(rows) != prepared['rows'] or normalized_hash(rows) != prepared['normalized_sha256']:
        raise ValueError('Data differs from recorded evaluation input')
    model_path = args.model_path or args.model_root/args.model
    critic_path = args.model_root/'Qwen3-8B'
    selected = list(enumerate(rows))
    if args.limit:
        selected = selected[:args.limit]
    skipped = []
    if args.model == 'ChemLLM-7B-Chat' and not args.include_historically_skipped:
        skipped = [index for index, item in selected if index == 3814]
        selected = [(index, item) for index, item in selected if index != 3814]
    metadata = dict(model=args.model, benchmark=args.benchmark, subject=args.subject,
                    model_path=str(model_path), critic_path=str(critic_path), seed=args.seed,
                    attention=args.attention, dataset_sha256=prepared['normalized_sha256'],
                    full_dataset_rows=len(rows), selected_indices=[index for index, item in selected],
                    skipped_indices=skipped, python=platform.python_version(),
                    protocol='historical prompt/settings with newly fixed seed; not bitwise replay')
    if args.dry_run:
        print(json.dumps({**metadata, 'selected_indices': f'{len(selected)} rows'}, indent=2))
        return
    if args.model == 'ChemLLM-7B-Chat' and not args.allow_remote_code:
        raise ValueError('Review pinned upstream model code, then opt in with --allow-remote-code')
    for path in [model_path, critic_path]:
        if not path.is_dir():
            raise FileNotFoundError(f'Model missing: {path}; use download_models.py or --model-path')
    try:
        args.output.resolve().relative_to((ROOT/'results').resolve())
    except ValueError:
        pass
    else:
        raise ValueError('Never write inference outputs into archived results/')
    if args.output.exists():
        raise FileExistsError('Use a new output directory to avoid overwriting a run')
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, set_seed

    set_seed(args.seed)
    loading = dict(torch_dtype=torch.bfloat16, attn_implementation=args.attention, device_map='auto')
    critic_model = AutoModelForCausalLM.from_pretrained(critic_path, **loading)
    critic_tokenizer = AutoTokenizer.from_pretrained(critic_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=args.allow_remote_code, **loading)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=args.allow_remote_code)
    model.eval()
    critic_model.eval()
    metadata.update(torch=torch.__version__, transformers=transformers.__version__,
                    cuda=torch.version.cuda, gpus=[torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())],
                    model_generation_config=model.generation_config.to_dict(),
                    critic_generation_config=critic_model.generation_config.to_dict(),
                    prompt_suffix=SUFFIX)
    for label, directory in [('model', model_path), ('critic', critic_path)]:
        metadata[label+'_config_hashes'] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in directory.iterdir() if path.name in ['config.json', 'generation_config.json', 'tokenizer_config.json', 'chat_template.jinja']}
    args.output.mkdir(parents=True)
    (args.output/'run.json').write_text(json.dumps(metadata, indent=2)+'\n')
    filename = args.model+'_Qwen3-8B'+('_'+args.subject if args.subject else '')+'.csv'

    def generate(active_model, active_tokenizer, text, **kwargs):
        inputs = active_tokenizer([text], return_tensors='pt').to(active_model.device)
        with torch.inference_mode():
            output = active_model.generate(**inputs, **kwargs)
        return active_tokenizer.decode(output[0, inputs.input_ids.shape[1]:], skip_special_tokens=True)

    with (args.output/filename).open('x', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['Truth', 'Model', 'Critic', 'Subject'])
        writer.writeheader()
        for index, item in selected:
            prompt = item['question']+SUFFIX
            if args.model == 'ChemDFM-v1.0-13B':
                text = 'User: '+prompt+'\nAssistant:'
                config = GenerationConfig(do_sample=True, top_k=20, top_p=0.9, temperature=0.9,
                    max_new_tokens=1024, repetition_penalty=1.05, eos_token_id=tokenizer.eos_token_id)
                response = generate(model, tokenizer, text, generation_config=config)
            elif args.model == 'ChemLLM-7B-Chat':
                config = GenerationConfig(do_sample=True, top_k=1, temperature=0.9,
                    max_new_tokens=500, repetition_penalty=1.5, pad_token_id=tokenizer.eos_token_id)
                response = generate(model, tokenizer, prompt, generation_config=config)
            else:
                text = tokenizer.apply_chat_template([dict(role='user', content=prompt)],
                    tokenize=False, add_generation_prompt=True, enable_thinking=False)
                response = generate(model, tokenizer, text, max_new_tokens=1024)
            response = response.split('</think>', 1)[-1].strip()
            critic_prompt = f"You are a critic assistant. For the question: {item['question']}.\n The standard answer is: {item['answer']}.\n The response is: {response}.\n Is the response correct? Reply with 'yes' or 'no'.\n"
            template_tokenizer = tokenizer if args.model.startswith('Qwen') else critic_tokenizer
            critic_text = template_tokenizer.apply_chat_template([dict(role='user', content=critic_prompt)],
                tokenize=False, add_generation_prompt=True, enable_thinking=False)
            critic_response = generate(critic_model, critic_tokenizer, critic_text, max_new_tokens=1024)
            writer.writerow(dict(Truth=item['answer'], Model=response, Critic=critic_response, Subject=item['subject']))
            handle.flush()
            print(f'{index}: completed', flush=True)
    metadata['completed'] = True
    metadata['output_sha256'] = hashlib.sha256((args.output/filename).read_bytes()).hexdigest()
    (args.output/'run.json').write_text(json.dumps(metadata, indent=2)+'\n')


if __name__ == '__main__':
    main()
