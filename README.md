# Custom LLM Eval Harness (RAG Edition)

A from-scratch, async evaluation harness for testing LLMs (and RAG systems) via API.

## Architecture

- **Target**: API adapters (Gemini, OpenAI-compatible). Swappable.
- **Dataset**: Pydantic-validated JSON with `context`, `question`, `expected_answer`.
- **Evaluators**: Pluggable scorers (exact match, keyword, rubric, LLM-as-a-Judge).
- **Runner**: Async batch engine with concurrency control.
- **Reports**: Terminal tables + CSV + JSONL raw dumps.

## Quick Start

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Add keys
cp .env.example .env
# edit .env

# 3. Run evaluation
# Generalised Command
python main.py --provider <PROVIDER> --model <MODEL_NAME> --dataset dataset/sample_eval.json

#Example
python main.py --provider gemini --model gemini-flash-latest --dataset dataset/sample_eval.json
python main.py --provider openai-compatible --model openai/gpt-oss-20b --dataset dataset/sample_eval.json

# 4. Run comparison
#Generalised Command
python main.py --compare --dataset <DATASET_PATH>

#Example
python main.py --compare --dataset dataset/sample_eval.json  

```

## RAG Workflow

1. Run your RAG retriever to get `context` chunks for each question.
2. Save them into `dataset/sample_eval.json` (or your own benchmark).
3. The runner automatically injects `context` + `question` into the prompt.
4. Evaluators score the generated answer against `expected_answer`.

## Extending

- **New Evaluator**: Inherit `BaseEvaluator`, implement `evaluate()`.
- **New Provider**: Inherit `BaseTarget`, implement `generate()`.
- **New Metric**: Add method to `MetricsTracker`.
