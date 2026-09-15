import pandas as pd
import json
import os

# Set the dataset path
dataset_path = "/ssd/liwentao/LLM/reasoning/datasets/ChemBench4K/test"

# Prepare a list for formatted records
output_data = []

# Iterate over all JSON files in the test directory
for filename in os.listdir(dataset_path):
    if filename.endswith('.json'):
        file_path = os.path.join(dataset_path, filename)
        
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process each sample
        for item in data:
            question = item['question']
            answer = item['answer']
            
            # Include the ABCD choices in the question
            options = []
            for option in ['A', 'B', 'C', 'D']:
                if option in item:
                    options.append(f"({option}) {item[option]}")
            # Append the choices to the question
            full_question = question + "\n" + "\n".join(options)
            
            # Create the formatted record
            formatted_item = {
                "question": full_question,
                "answer": answer,
                "subject": filename.replace('.json', '')
            }
            
            output_data.append(formatted_item)

# Save the processed data
output_json_path = "chembench4k_test_formatted.json"
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print(f"Data converted to JSON and saved to: {output_json_path}")
print(f"Processed {len(output_data)} samples in total")
