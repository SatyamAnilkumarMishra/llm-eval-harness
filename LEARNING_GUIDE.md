# Learning Guide: Build This Yourself, In This Order

This copy of the harness is annotated as a **reference**, not something
to copy-paste. Every file's docstring explains *why* it exists and what
concept it's teaching, not just what the code does. Read a file's
annotations, close it, then write your own version in a fresh file
before moving to the next one.

## Suggested build order

| # | What to build | File to read (reference only) | Core concept |
|---|---|---|---|
| 1 | `EvalResult` + `BaseEvaluator` | `evaluators/base.py` | The `(prediction, reference) -> score/passed/reasoning` abstraction everything else plugs into |
| 2 | `ExactMatchEvaluator` | `evaluators/exact_match.py` | Normalization (case/whitespace) before comparison |
| 3 | `KeywordMatchEvaluator` | `evaluators/keyword_match.py` | AND vs OR semantics (`match_all`), partial-credit scoring |
| 4 | `BaseTarget` + `TargetResponse` | `target/base.py` | Provider-agnostic interface; async by default |
| 5 | `GeminiTarget` | `target/providers.py` | Wrapping a real API call: latency capture, usage capture, **retry w/ backoff** |
| 6 | `RubricEvaluator` | `evaluators/rubric.py` | Weighted multi-criterion scoring; where config (like `threshold`) should live |
| 7 | `EvalSample` + `DatasetLoader` | `dataset/loader.py` | Schema validation; per-sample evaluator routing |
| 8 | `LLMJudgeEvaluator` | `evaluators/llm_judge.py` | Structured JSON output from an LLM; fail-closed error handling; judge bias pitfalls |
| 9 | `EvaluationRunner` | `core/runner.py` | `asyncio.Semaphore` for polite concurrency; wiring target + evaluator + sample together |
| 10 | `MetricsTracker` | `core/metrics.py` | Aggregation as computed properties over raw results |
| 11 | `ResultRecorder` | `core/recorder.py` | Crash-safe incremental writes vs. buffer-then-flush |
| 12 | `Reporter` | `reports/reporter.py` | Separating a scannable summary view from the full-detail export |
| 13 | `ModelComparison` | `experiments/compare.py` | Same runner, looped over configs — this is where you'll compare models/prompts for your own RAG project |
| 14 | `main.py` | `main.py` | Thin CLI wiring — no new logic, just assembly |

## Two bugs that were in the original version (fixed here — go find them)

1. **`RubricEvaluator` threshold was dead code.** It read `threshold`
   from `kwargs` inside `evaluate()`, but nothing upstream ever passed
   that kwarg — so it silently always used the hardcoded default. Fixed
   by moving `threshold` to `__init__`. Lesson: config meant to be set
   once per instance belongs in the constructor, not in per-call kwargs
   nobody's guaranteed to populate.

2. **`ResultRecorder` buffered everything in memory, writing only at the
   very end.** A crash mid-run lost every completed result. Fixed by
   opening the output file once and writing each result immediately.
   Lesson: prefer "write as you go" over "buffer then write" for
   anything long-running where partial results still have value.

Also added: **retry with exponential backoff** on both provider targets
(`target/providers.py`) — the original fired one API call per sample
with zero retry, so a single transient error killed that sample's whole
task.

## Exercises once you've rebuilt the core pieces

- Extend `--compare` to load model configs from a JSON file instead of
  editing Python source (see the note in `experiments/compare.py`).
- Add a `semantic_similarity` evaluator (embedding cosine similarity)
  as a middle ground between `keyword_match` and `llm_judge` — cheaper
  and more deterministic than an LLM judge, more semantic than keywords.
- In `LLMJudgeEvaluator`, log cases where the judge's own `passed`
  boolean disagrees with `score >= threshold` — that disagreement rate
  is itself a useful signal about judge reliability.
- Point `dataset/loader.py` at real (context, question, expected_answer)
  triples pulled from your own RAG pipeline's retrieval + generation
  steps, instead of the toy `sample_eval.json`.
