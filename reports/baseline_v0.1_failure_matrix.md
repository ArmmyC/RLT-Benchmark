# Baseline v0.1 Cross-Model Failure Matrix

## Coverage Summary

| Run | Per-task data | Rows |
|---|---|---:|
| verilogeval_pass1_qwen36_27b | unavailable | 0 |
| verilogeval_pass1_qwen36_35b_a3b | unavailable | 0 |
| verilogeval_pass1_qwen3_coder | unavailable | 0 |
| verilogeval_pass1_qwen25_coder | unavailable | 0 |
| verilogeval_pass1_deepseek_coder | unavailable | 0 |
| verilogeval_pass5_qwen36_27b | unavailable | 0 |
| verilogeval_pass5_qwen36_35b_a3b | unavailable | 0 |
| verilogeval_pass5_qwen3_coder | unavailable | 0 |
| verilogeval_pass5_qwen25_coder | unavailable | 0 |
| verilogeval_pass5_deepseek_coder | unavailable | 0 |
| rtllm2_pass1_qwen36_27b | unavailable | 0 |
| rtllm2_pass1_qwen36_35b_a3b | unavailable | 0 |
| rtllm2_pass1_qwen3_coder | unavailable | 0 |
| rtllm2_pass1_qwen25_coder | unavailable | 0 |
| rtllm2_pass1_deepseek_coder | unavailable | 0 |
| protocollm_lint_qwen36_27b | unavailable | 0 |
| protocollm_lint_qwen36_35b_a3b | unavailable | 0 |
| protocollm_lint_qwen3_coder | unavailable | 0 |
| protocollm_lint_qwen25_coder | unavailable | 0 |
| protocollm_lint_deepseek_coder | unavailable | 0 |
| rtlopt_lint_qwen36_27b | unavailable | 0 |
| rtlopt_lint_qwen36_35b_a3b | unavailable | 0 |
| rtlopt_lint_qwen3_coder | unavailable | 0 |
| rtlopt_lint_qwen25_coder | unavailable | 0 |
| rtlopt_lint_deepseek_coder | unavailable | 0 |
| rtlopt_synthesis_qwen36_27b | unavailable | 0 |
| rtlopt_synthesis_qwen36_35b_a3b | unavailable | 0 |
| rtlopt_synthesis_qwen3_coder | unavailable | 0 |
| rtlopt_synthesis_qwen25_coder | unavailable | 0 |
| rtlopt_synthesis_deepseek_coder | unavailable | 0 |
| rtlopt_equivalence_qwen36_27b | unavailable | 0 |
| rtlopt_equivalence_qwen36_35b_a3b | unavailable | 0 |
| rtlopt_equivalence_qwen3_coder | unavailable | 0 |
| rtlopt_equivalence_qwen25_coder | unavailable | 0 |
| rtlopt_equivalence_deepseek_coder | unavailable | 0 |

## Failure Category Counts by Model

| Model | code_extraction_failure | compile_failure | equiv_failure | passed | simulation_failure | synthesis_failure | timeout |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen36-27b | 64 | 140 | 9 | 708 | 183 | 8 | 3 |
| qwen36-35b-a3b | 97 | 166 | 15 | 647 | 180 | 8 | 2 |
| qwen3-coder-30b-a3b-instruct | 13 | 127 | 16 | 549 | 355 | 3 | 2 |
| qwen25-coder-32b | 1 | 128 | 17 | 525 | 386 | 8 | 0 |
| deepseek-coder-v2-lite-instruct | 6 | 148 | 5 | 586 | 362 | 6 | 2 |

Counts in this table come from registered run summaries; they are available even when per-task files are not local.

## Per-Task Analysis

Per-task failure data is not available for this run. The summary-level baseline is still shown from registered summaries.

## Tasks Failed by All Available Models

Unavailable without per-task results.

## Tasks Solved by All Available Models

Unavailable without per-task results.

## Tasks Uniquely Solved by One Model

Unavailable without per-task results.

## Tasks Recovered by Pass@5

Unavailable without paired pass@1 and pass@5 per-task results.

## Missing Data Warnings

- verilogeval_pass1_qwen36_27b: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass1_qwen36_35b_a3b: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass1_qwen3_coder: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass1_qwen25_coder: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass1_deepseek_coder: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass5_qwen36_27b: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass5_qwen36_35b_a3b: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass5_qwen3_coder: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass5_qwen25_coder: results.jsonl unavailable; skipped per-task analysis
- verilogeval_pass5_deepseek_coder: results.jsonl unavailable; skipped per-task analysis
- rtllm2_pass1_qwen36_27b: results.jsonl unavailable; skipped per-task analysis
- rtllm2_pass1_qwen36_35b_a3b: results.jsonl unavailable; skipped per-task analysis
- rtllm2_pass1_qwen3_coder: results.jsonl unavailable; skipped per-task analysis
- rtllm2_pass1_qwen25_coder: results.jsonl unavailable; skipped per-task analysis
- rtllm2_pass1_deepseek_coder: results.jsonl unavailable; skipped per-task analysis
- protocollm_lint_qwen36_27b: results.jsonl unavailable; skipped per-task analysis
- protocollm_lint_qwen36_35b_a3b: results.jsonl unavailable; skipped per-task analysis
- protocollm_lint_qwen3_coder: results.jsonl unavailable; skipped per-task analysis
- protocollm_lint_qwen25_coder: results.jsonl unavailable; skipped per-task analysis
- protocollm_lint_deepseek_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_lint_qwen36_27b: results.jsonl unavailable; skipped per-task analysis
- rtlopt_lint_qwen36_35b_a3b: results.jsonl unavailable; skipped per-task analysis
- rtlopt_lint_qwen3_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_lint_qwen25_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_lint_deepseek_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_synthesis_qwen36_27b: results.jsonl unavailable; skipped per-task analysis
- rtlopt_synthesis_qwen36_35b_a3b: results.jsonl unavailable; skipped per-task analysis
- rtlopt_synthesis_qwen3_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_synthesis_qwen25_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_synthesis_deepseek_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_equivalence_qwen36_27b: results.jsonl unavailable; skipped per-task analysis
- rtlopt_equivalence_qwen36_35b_a3b: results.jsonl unavailable; skipped per-task analysis
- rtlopt_equivalence_qwen3_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_equivalence_qwen25_coder: results.jsonl unavailable; skipped per-task analysis
- rtlopt_equivalence_deepseek_coder: results.jsonl unavailable; skipped per-task analysis
