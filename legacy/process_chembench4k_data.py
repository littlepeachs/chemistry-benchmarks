import pandas as pd
import json
import os

# 设置数据集路径
dataset_path = "/ssd/liwentao/LLM/reasoning/datasets/ChemBench4K/test"

# 准备一个列表来存储格式化后的数据
output_data = []

# 遍历test目录下的所有JSON文件
for filename in os.listdir(dataset_path):
    if filename.endswith('.json'):
        file_path = os.path.join(dataset_path, filename)
        
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理每个样本
        for item in data:
            question = item['question']
            answer = item['answer']
            
            # 整合ABCD选项到问题中
            options = []
            for option in ['A', 'B', 'C', 'D']:
                if option in item:
                    options.append(f"({option}) {item[option]}")
            # 将选项添加到问题中
            full_question = question + "\n" + "\n".join(options)
            
            # 创建新的格式化数据
            formatted_item = {
                "question": full_question,
                "answer": answer,
                "subject": filename.replace('.json', '')
            }
            
            output_data.append(formatted_item)

# 保存处理后的数据
output_json_path = "chembench4k_test_formatted.json"
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print(f"数据已成功转换为JSON格式并保存到: {output_json_path}")
print(f"总共处理了 {len(output_data)} 个样本")

