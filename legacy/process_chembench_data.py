import pandas as pd
import json
import os
import re

# 读取parquet文件

dataset_names = ["analytical_chemistry","materials_science","technical_chemistry","chemical_preference","organic_chemistry","toxicity_and_safety","general_chemistry","physical_chemistry","inorganic_chemistry"]
for dataset_name in dataset_names:
    parquet_file_path = f"/ssd/liwentao/LLM/reasoning/datasets/ChemBench/{dataset_name}/train-00000-of-00001.parquet"
    df = pd.read_parquet(parquet_file_path)

    # 准备一个列表来存储格式化后的数据
    output_data = []

    # 遍历DataFrame的每一行
    for index, row in df.iterrows():
        full_text = row['examples'][0]
        
        # 获取问题文本
        question_text = full_text['input']

        if full_text['target_scores']:
            try:
                target_scores = json.loads(full_text['target_scores'])
            except:
                import pdb; pdb.set_trace()
            # 创建选项列表并找到正确答案
            options = list(target_scores.keys())
            correct_option = None
            
            # 找到分数为1.0的选项作为正确答案
            for option, score in target_scores.items():
                if score == 1.0:
                    correct_option = option
                    break
            
            # 构建带有选项的完整问题
            question_with_options = question_text + "\n"
            option_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  # 支持更多选项
            
            for i, option in enumerate(options):
                if i < len(option_labels):
                    question_with_options += f"({option_labels[i]}) {option}\n"
                    if option == correct_option:
                        answer = option_labels[i]
        else:
            question_with_options = full_text['input']
            answer = full_text['target']
        
        full_text = question_with_options.strip()
        label = answer
        subject = dataset_name
        num_words = len(question_with_options.split())

        # 使用正则表达式分割问题和选项
        # 假设格式为：Question\n(A) Option A\n(B) Option B...
        # `re.split` 会将分隔符本身移除，返回一个列表
            
            # 创建符合目标格式的字典
        item = {
            "question": full_text,
            "answer": label,
            "subject": subject,
            "num_words": num_words,
        }
        output_data.append(item)

    # 确定输出文件的路径，保存在当前目录下
    output_json_path = f"/ssd/liwentao/LLM/reasoning/datasets/ChemBench/{dataset_name}/qa_data.json"

    # 将结果写入JSON文件
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print(f"数据已成功转换为JSON格式并保存到: {output_json_path}")
