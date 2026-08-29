# Capstone — MP1 Prompt Strategy Comparison

This repository contains Mini Project 1 (MP1), which compares four prompting strategies for structured information extraction with OpenAI models.

## Project goal

Given a job-description snippet, the program extracts:

- Company
- Role
- Years of experience required

It compares four prompting strategies:

- Zero-shot
- Few-shot
- Structured prompting
- Chain-of-thought (CoT)

The comparison evaluates accuracy, JSON parse rate, LLM-judge score, cost, and latency.

## Project structure

```text
.
├── README.md
└── mp1/
    ├── mp1_prompt_lab.py
    ├── mp1_comparison.md
    └── mp1_writeup.md
```

## Files

| File | Description |
|---|---|
| `mp1_prompt_lab.py` | Runs the prompting experiment and evaluates the results. |
| `mp1_comparison.md` | Contains the final comparison table. |
| `mp1_writeup.md` | Contains the reflection and findings. |

## Results summary

Few-shot and structured prompting achieved the highest mean extraction accuracy: 2.9 out of 3 fields. All strategies achieved a 100% JSON parse rate. CoT had the lowest median latency in this experiment.

For detailed results, see:

- `mp1/mp1_comparison.md`
- `mp1/mp1_writeup.md`

## Requirements

- Python 3.10 or newer
- OpenAI API key
- Python packages: `openai` and `pandas`
- Input files:
  - `data/job_snippets.jsonl`
  - `data/golden_set.jsonl`

Install the required packages:

```bash
python -m pip install openai pandas
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Run the project

From the `mp1` folder:

```bash
python mp1_prompt_lab.py
```

The program runs 40 extraction calls: 10 job snippets using 4 prompting strategies. It then scores and prints the comparison results.

## Models used

- `gpt-4o-mini` for extraction
- `gpt-4o` for LLM-based evaluation