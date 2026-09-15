import pandas as pd
import json
import os
import re

# Read the Parquet file
parquet_file_path = "/ssd/liwentao/LLM/reasoning/datasets/mascqa/data/test-00000-of-00001.parquet"
df = pd.read_parquet(parquet_file_path)

# Prepare a list for formatted records
output_data = []

# Iterate over each DataFrame row
for index, row in df.iterrows():
    full_text = row['questions']
    label = row['label']
    subject = row['subject']
    qstr = row['qstr']
    qids = row['qids']
    num_words = row['num_words']


    # Split the question and choices using a regular expression
    # Assume the format is: Question\n(A) Option A\n(B) Option B...
    # `re.split` removes the delimiter and returns a list
        
        # Create a dictionary in the target format
    item = {
        "question": full_text,
        "answer": label,
        "subject": subject,
        "qstr": qstr,
        "qids": qids,
        "num_words": num_words,
    }
    output_data.append(item)

# Set the output file path in the current directory
output_json_path = "mascqa_test.json"

# Write the results to a JSON file
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print(f"Data converted to JSON and saved to: {output_json_path}")
