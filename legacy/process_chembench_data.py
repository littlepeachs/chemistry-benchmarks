import pandas as pd
import json
import os
import re

# Read the Parquet file

dataset_names = ["analytical_chemistry","materials_science","technical_chemistry","chemical_preference","organic_chemistry","toxicity_and_safety","general_chemistry","physical_chemistry","inorganic_chemistry"]
for dataset_name in dataset_names:
    parquet_file_path = f"/ssd/liwentao/LLM/reasoning/datasets/ChemBench/{dataset_name}/train-00000-of-00001.parquet"
    df = pd.read_parquet(parquet_file_path)

    # Prepare a list for formatted records
    output_data = []

    # Iterate over each DataFrame row
    for index, row in df.iterrows():
        full_text = row['examples'][0]
        
        # Get the question text
        question_text = full_text['input']

        if full_text['target_scores']:
            try:
                target_scores = json.loads(full_text['target_scores'])
            except:
                import pdb; pdb.set_trace()
            # Create the choices and identify the correct answer
            options = list(target_scores.keys())
            correct_option = None
            
            # Select the first choice with a score of 1.0 as the correct answer
            for option, score in target_scores.items():
                if score == 1.0:
                    correct_option = option
                    break
            
            # Build the complete question with choices
            question_with_options = question_text + "\n"
            option_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  # Support additional choices
            
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

        # Split the question and choices using a regular expression
        # Assume the format is: Question\n(A) Option A\n(B) Option B...
        # `re.split` removes the delimiter and returns a list
            
            # Create a dictionary in the target format
        item = {
            "question": full_text,
            "answer": label,
            "subject": subject,
            "num_words": num_words,
        }
        output_data.append(item)

    # Set the output file path in the current directory
    output_json_path = f"/ssd/liwentao/LLM/reasoning/datasets/ChemBench/{dataset_name}/qa_data.json"

    # Write the results to a JSON file
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print(f"Data converted to JSON and saved to: {output_json_path}")
