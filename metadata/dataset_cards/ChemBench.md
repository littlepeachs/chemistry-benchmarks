---
license: mit
configs:
- config_name: analytical_chemistry
  data_files:
  - split: train
    path: analytical_chemistry/train-*
- config_name: chemical_preference
  data_files:
  - split: train
    path: chemical_preference/train-*
- config_name: general_chemistry
  data_files:
  - split: train
    path: general_chemistry/train-*
- config_name: inorganic_chemistry
  data_files:
  - split: train
    path: inorganic_chemistry/train-*
- config_name: materials_science
  data_files:
  - split: train
    path: materials_science/train-*
- config_name: organic_chemistry
  data_files:
  - split: train
    path: organic_chemistry/train-*
- config_name: physical_chemistry
  data_files:
  - split: train
    path: physical_chemistry/train-*
- config_name: technical_chemistry
  data_files:
  - split: train
    path: technical_chemistry/train-*
- config_name: toxicity_and_safety
  data_files:
  - split: train
    path: toxicity_and_safety/train-*
dataset_info:
- config_name: analytical_chemistry
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: string
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 100230
    num_examples: 152
  download_size: 42118
  dataset_size: 100230
- config_name: chemical_preference
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: 'null'
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 782655
    num_examples: 1000
  download_size: 118756
  dataset_size: 782655
- config_name: general_chemistry
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: string
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 85271
    num_examples: 149
  download_size: 32835
  dataset_size: 85271
- config_name: inorganic_chemistry
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: string
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 58482
    num_examples: 92
  download_size: 29370
  dataset_size: 58482
- config_name: materials_science
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: string
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 68349
    num_examples: 84
  download_size: 35332
  dataset_size: 68349
- config_name: organic_chemistry
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: string
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 305214
    num_examples: 429
  download_size: 92257
  dataset_size: 305214
- config_name: physical_chemistry
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: string
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 126055
    num_examples: 165
  download_size: 54106
  dataset_size: 126055
- config_name: technical_chemistry
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: string
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 30301
    num_examples: 40
  download_size: 22665
  dataset_size: 30301
- config_name: toxicity_and_safety
  features:
  - name: canary
    dtype: string
  - name: description
    dtype: string
  - name: examples
    list:
    - name: input
      dtype: string
    - name: target
      dtype: 'null'
    - name: target_scores
      dtype: string
  - name: in_humansubset_w_tool
    dtype: bool
  - name: in_humansubset_wo_tool
    dtype: bool
  - name: keywords
    sequence: string
  - name: metrics
    sequence: string
  - name: name
    dtype: string
  - name: preferred_score
    dtype: string
  - name: uuid
    dtype: string
  splits:
  - name: train
    num_bytes: 458362
    num_examples: 675
  download_size: 107350
  dataset_size: 458362
---


THIS DATASET IS NOT FOR TRAINING