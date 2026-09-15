---
license: mit
---


## Introduction
chembench is a large-scale chemistry competency evaluation benchmark for language models, which includes nine chemistry core tasks and 4100 high-quality single-choice questions and answers.

chembench是一个包含了九项化学核心任务，4100个高质量单选问答的大语言模型化学能力评测基准.

## Example

```
    {
        "question": "Create a molecule that satisfies the conditions outlined in the description.\nThe molecule is a natural product found in Cinnamomum camphora, Otoba parvifolia, and Zanthoxylum wutaiense with data available.",
        "answer": "C",
        "A": "In my opinion, the answer would be C12C3(O)CCC(C4=CC(=O)OC4)C3(C(O)CC1C1(C)CCC(OC3OC(C)C(C(C3)O)OC3CC(C(C(O3)C)OC3CC(C(C(O3)C)O)O)O)CC1CC2)C",
        "B": "In my opinion, the answer would be c1c(c(=O)c2ccc(O)cc2o1)-c1cc(c(c(O)c1O)OC)C(C)(C=C)C",
        "C": "From my perspective, the answer is O1C(C2C(C1)C(c1cc3c(OCO3)cc1)OC2)c1ccc(c(c1)OC)O",
        "D": "I would conclude that c1(cc(oc(c1C)=O)C=CC(C)=CC(C)=Cc1ccccc1)OC"
    }
```

## How to use

We have integrated ChemBench into OpenCompass, an open source, efficient, and comprehensive large model evaluation kit, hub, ranking system designed by Shanghai AI Lab. You can find it on its official website opencompass.org.cn and github website https://github.com/open-compass/opencompass. 

As for the prompt template, you can refer to the file https://github.com/open-compass/opencompass/blob/main/configs/datasets/ChemBench/ChemBench_gen.py. Here are some detailed instructions:

1.	In ChemBench, all questions are presented in a multiple-choice format. The prompt is structured as follows: “There is a single choice question about chemistry. Answer the question by replying A, B, C, or D.\nQuestion: {{input}}\nA. {{A}}\nB. {{B}}\nC. {{C}}\nD. {{D}}\nAnswer: ” where “{{input}}” is the question and “{{A}}” – “{{D}}” are the choices. The expected response format contains only a capital letter A, B, C, or D. This format ensures a consistent and clear presentation of the questions.

2.	We extract the first capital letters from the responses as the answer choices.

3.	We use few-shot examples to help the LLMs answer in the required format. The number of examples is 5 by default. If the total length is longer than the max length of an LLM, the number is reduced accordingly. 

We now give some simple instructions on how to use OpenCompass to test an LLM on ChenBench. For more details, please refer to the official website of OpenCompass.

1.	Define the LLM. Here is an example: https://github.com/open-compass/opencompass/blob/main/configs/models/hf_internlm/hf_internlm_chat_7b.py. 

2.	Write an eval config file. Copy the file https://github.com/open-compass/opencompass/blob/main/configs/eval_chembench.py, and change the model to the one you defined in the previous step. 

3.	Run the eval process using the command: 
```
python run.py configs/eval_demo.py -w outputs/demo
```

4.	Find your results in the outputs/demo folder.

We hope these instructions answer your questions.

## Citation

```
@misc{zhang2024chemllm,
      title={ChemLLM: A Chemical Large Language Model}, 
      author={Di Zhang and Wei Liu and Qian Tan and Jingdan Chen and Hang Yan and Yuliang Yan and Jiatong Li and Weiran Huang and Xiangyu Yue and Dongzhan Zhou and Shufei Zhang and Mao Su and Hansen Zhong and Yuqiang Li and Wanli Ouyang},
      year={2024},
      eprint={2402.06852},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
```

