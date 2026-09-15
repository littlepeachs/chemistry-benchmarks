import pandas as pd
import json
import os
import re

# 读取parquet文件
parquet_file_path = "/ssd/liwentao/LLM/reasoning/datasets/mascqa/data/test-00000-of-00001.parquet"
df = pd.read_parquet(parquet_file_path)

# 准备一个列表来存储格式化后的数据
output_data = []

# 遍历DataFrame的每一行
for index, row in df.iterrows():
    full_text = row['questions']
    label = row['label']
    subject = row['subject']
    qstr = row['qstr']
    qids = row['qids']
    num_words = row['num_words']


    # 使用正则表达式分割问题和选项
    # 假设格式为：Question\n(A) Option A\n(B) Option B...
    # `re.split` 会将分隔符本身移除，返回一个列表
        
        # 创建符合目标格式的字典
    item = {
        "question": full_text,
        "answer": label,
        "subject": subject,
        "qstr": qstr,
        "qids": qids,
        "num_words": num_words,
    }
    output_data.append(item)

# 确定输出文件的路径，保存在当前目录下
output_json_path = "mascqa_test.json"

# 将结果写入JSON文件
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print(f"数据已成功转换为JSON格式并保存到: {output_json_path}")
