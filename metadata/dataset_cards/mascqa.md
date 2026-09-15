---
dataset_info:
  features:
  - name: qids
    dtype: string
  - name: qstr
    dtype: string
  - name: num_words
    dtype: int64
  - name: questions
    dtype: string
  - name: subject
    dtype: string
  - name: label
    dtype: string
  - name: __index_level_0__
    dtype: int64
  splits:
  - name: test
    num_bytes: 234736
    num_examples: 650
  download_size: 115912
  dataset_size: 234736
configs:
- config_name: default
  data_files:
  - split: test
    path: data/test-*
---
