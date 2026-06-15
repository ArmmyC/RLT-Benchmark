# Baseline v0.2 Consistency Audit

## Audit Scope

- Registry baseline: `baseline_v0_1` (Baseline v0.1 Public RTL Benchmarks)
- Sanitized artifact: `artifacts/baseline_v0.2/per_task_results.jsonl`
- Generated UTC: 2026-06-15T03:11:46+00:00
- Comparison: registered summary sample/category counts versus sanitized per-task rows grouped by `source_run_id`.

## Overall Status

**PASS**

- Matching runs: 35
- Mismatching runs: 0
- Missing artifact runs: 0

Default mode reports mismatches as warnings. Strict mode reports the same findings as FAIL and exits nonzero.

## Run Summary

| Run ID | Benchmark | Mode | Model | Summary samples | Artifact rows | Status | Mismatch fields |
|---|---|---|---|---:|---:|---|---|
| verilogeval_pass1_qwen36_27b | verilogeval | pass1 | qwen36-27b | 156 | 156 | match | - |
| verilogeval_pass1_qwen36_35b_a3b | verilogeval | pass1 | qwen36-35b-a3b | 156 | 156 | match | - |
| verilogeval_pass1_qwen3_coder | verilogeval | pass1 | qwen3-coder-30b-a3b-instruct | 156 | 156 | match | - |
| verilogeval_pass1_qwen25_coder | verilogeval | pass1 | qwen25-coder-32b | 156 | 156 | match | - |
| verilogeval_pass1_deepseek_coder | verilogeval | pass1 | deepseek-coder-v2-lite-instruct | 156 | 156 | match | - |
| verilogeval_pass5_qwen36_27b | verilogeval | pass5 | qwen36-27b | 780 | 780 | match | - |
| verilogeval_pass5_qwen36_35b_a3b | verilogeval | pass5 | qwen36-35b-a3b | 780 | 780 | match | - |
| verilogeval_pass5_qwen3_coder | verilogeval | pass5 | qwen3-coder-30b-a3b-instruct | 780 | 780 | match | - |
| verilogeval_pass5_qwen25_coder | verilogeval | pass5 | qwen25-coder-32b | 780 | 780 | match | - |
| verilogeval_pass5_deepseek_coder | verilogeval | pass5 | deepseek-coder-v2-lite-instruct | 780 | 780 | match | - |
| rtllm2_pass1_qwen36_27b | rtllm2 | pass1 | qwen36-27b | 50 | 50 | match | - |
| rtllm2_pass1_qwen36_35b_a3b | rtllm2 | pass1 | qwen36-35b-a3b | 50 | 50 | match | - |
| rtllm2_pass1_qwen3_coder | rtllm2 | pass1 | qwen3-coder-30b-a3b-instruct | 50 | 50 | match | - |
| rtllm2_pass1_qwen25_coder | rtllm2 | pass1 | qwen25-coder-32b | 50 | 50 | match | - |
| rtllm2_pass1_deepseek_coder | rtllm2 | pass1 | deepseek-coder-v2-lite-instruct | 50 | 50 | match | - |
| protocollm_lint_qwen36_27b | protocollm | lint | qwen36-27b | 9 | 9 | match | - |
| protocollm_lint_qwen36_35b_a3b | protocollm | lint | qwen36-35b-a3b | 9 | 9 | match | - |
| protocollm_lint_qwen3_coder | protocollm | lint | qwen3-coder-30b-a3b-instruct | 9 | 9 | match | - |
| protocollm_lint_qwen25_coder | protocollm | lint | qwen25-coder-32b | 9 | 9 | match | - |
| protocollm_lint_deepseek_coder | protocollm | lint | deepseek-coder-v2-lite-instruct | 9 | 9 | match | - |
| rtlopt_lint_qwen36_27b | rtlopt | lint | qwen36-27b | 40 | 40 | match | - |
| rtlopt_lint_qwen36_35b_a3b | rtlopt | lint | qwen36-35b-a3b | 40 | 40 | match | - |
| rtlopt_lint_qwen3_coder | rtlopt | lint | qwen3-coder-30b-a3b-instruct | 40 | 40 | match | - |
| rtlopt_lint_qwen25_coder | rtlopt | lint | qwen25-coder-32b | 40 | 40 | match | - |
| rtlopt_lint_deepseek_coder | rtlopt | lint | deepseek-coder-v2-lite-instruct | 40 | 40 | match | - |
| rtlopt_synthesis_qwen36_27b | rtlopt | synthesis | qwen36-27b | 40 | 40 | match | - |
| rtlopt_synthesis_qwen36_35b_a3b | rtlopt | synthesis | qwen36-35b-a3b | 40 | 40 | match | - |
| rtlopt_synthesis_qwen3_coder | rtlopt | synthesis | qwen3-coder-30b-a3b-instruct | 40 | 40 | match | - |
| rtlopt_synthesis_qwen25_coder | rtlopt | synthesis | qwen25-coder-32b | 40 | 40 | match | - |
| rtlopt_synthesis_deepseek_coder | rtlopt | synthesis | deepseek-coder-v2-lite-instruct | 40 | 40 | match | - |
| rtlopt_equivalence_qwen36_27b | rtlopt | equivalence | qwen36-27b | 40 | 40 | match | - |
| rtlopt_equivalence_qwen36_35b_a3b | rtlopt | equivalence | qwen36-35b-a3b | 40 | 40 | match | - |
| rtlopt_equivalence_qwen3_coder | rtlopt | equivalence | qwen3-coder-30b-a3b-instruct | 40 | 40 | match | - |
| rtlopt_equivalence_qwen25_coder | rtlopt | equivalence | qwen25-coder-32b | 40 | 40 | match | - |
| rtlopt_equivalence_deepseek_coder | rtlopt | equivalence | deepseek-coder-v2-lite-instruct | 40 | 40 | match | - |

## Category-Count Comparison

| Run ID | Field | Summary | Artifact | Delta | Status |
|---|---|---:|---:|---:|---|
| verilogeval_pass1_qwen36_27b | samples | 156 | 156 | 0 | match |
| verilogeval_pass1_qwen36_27b | passed | 96 | 96 | 0 | match |
| verilogeval_pass1_qwen36_27b | compile_failure | 17 | 17 | 0 | match |
| verilogeval_pass1_qwen36_27b | simulation_failure | 35 | 35 | 0 | match |
| verilogeval_pass1_qwen36_27b | code_extraction_failure | 8 | 8 | 0 | match |
| verilogeval_pass1_qwen36_27b | timeout | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen36_27b | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen36_27b | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen36_35b_a3b | samples | 156 | 156 | 0 | match |
| verilogeval_pass1_qwen36_35b_a3b | passed | 89 | 89 | 0 | match |
| verilogeval_pass1_qwen36_35b_a3b | compile_failure | 26 | 26 | 0 | match |
| verilogeval_pass1_qwen36_35b_a3b | simulation_failure | 29 | 29 | 0 | match |
| verilogeval_pass1_qwen36_35b_a3b | code_extraction_failure | 12 | 12 | 0 | match |
| verilogeval_pass1_qwen36_35b_a3b | timeout | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen36_35b_a3b | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen36_35b_a3b | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen3_coder | samples | 156 | 156 | 0 | match |
| verilogeval_pass1_qwen3_coder | passed | 75 | 75 | 0 | match |
| verilogeval_pass1_qwen3_coder | compile_failure | 20 | 20 | 0 | match |
| verilogeval_pass1_qwen3_coder | simulation_failure | 60 | 60 | 0 | match |
| verilogeval_pass1_qwen3_coder | code_extraction_failure | 1 | 1 | 0 | match |
| verilogeval_pass1_qwen3_coder | timeout | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen3_coder | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen3_coder | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen25_coder | samples | 156 | 156 | 0 | match |
| verilogeval_pass1_qwen25_coder | passed | 70 | 70 | 0 | match |
| verilogeval_pass1_qwen25_coder | compile_failure | 18 | 18 | 0 | match |
| verilogeval_pass1_qwen25_coder | simulation_failure | 68 | 68 | 0 | match |
| verilogeval_pass1_qwen25_coder | code_extraction_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen25_coder | timeout | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen25_coder | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_qwen25_coder | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_deepseek_coder | samples | 156 | 156 | 0 | match |
| verilogeval_pass1_deepseek_coder | passed | 76 | 76 | 0 | match |
| verilogeval_pass1_deepseek_coder | compile_failure | 21 | 21 | 0 | match |
| verilogeval_pass1_deepseek_coder | simulation_failure | 58 | 58 | 0 | match |
| verilogeval_pass1_deepseek_coder | code_extraction_failure | 1 | 1 | 0 | match |
| verilogeval_pass1_deepseek_coder | timeout | N/A | 0 |  | n/a |
| verilogeval_pass1_deepseek_coder | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass1_deepseek_coder | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen36_27b | samples | 780 | 780 | 0 | match |
| verilogeval_pass5_qwen36_27b | passed | 477 | 477 | 0 | match |
| verilogeval_pass5_qwen36_27b | compile_failure | 104 | 104 | 0 | match |
| verilogeval_pass5_qwen36_27b | simulation_failure | 144 | 144 | 0 | match |
| verilogeval_pass5_qwen36_27b | code_extraction_failure | 55 | 55 | 0 | match |
| verilogeval_pass5_qwen36_27b | timeout | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen36_27b | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen36_27b | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen36_35b_a3b | samples | 780 | 780 | 0 | match |
| verilogeval_pass5_qwen36_35b_a3b | passed | 438 | 438 | 0 | match |
| verilogeval_pass5_qwen36_35b_a3b | compile_failure | 121 | 121 | 0 | match |
| verilogeval_pass5_qwen36_35b_a3b | simulation_failure | 143 | 143 | 0 | match |
| verilogeval_pass5_qwen36_35b_a3b | code_extraction_failure | 78 | 78 | 0 | match |
| verilogeval_pass5_qwen36_35b_a3b | timeout | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen36_35b_a3b | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen36_35b_a3b | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen3_coder | samples | 780 | 780 | 0 | match |
| verilogeval_pass5_qwen3_coder | passed | 378 | 378 | 0 | match |
| verilogeval_pass5_qwen3_coder | compile_failure | 101 | 101 | 0 | match |
| verilogeval_pass5_qwen3_coder | simulation_failure | 295 | 295 | 0 | match |
| verilogeval_pass5_qwen3_coder | code_extraction_failure | 6 | 6 | 0 | match |
| verilogeval_pass5_qwen3_coder | timeout | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen3_coder | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen3_coder | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen25_coder | samples | 780 | 780 | 0 | match |
| verilogeval_pass5_qwen25_coder | passed | 357 | 357 | 0 | match |
| verilogeval_pass5_qwen25_coder | compile_failure | 104 | 104 | 0 | match |
| verilogeval_pass5_qwen25_coder | simulation_failure | 318 | 318 | 0 | match |
| verilogeval_pass5_qwen25_coder | code_extraction_failure | 1 | 1 | 0 | match |
| verilogeval_pass5_qwen25_coder | timeout | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen25_coder | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_qwen25_coder | equiv_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_deepseek_coder | samples | 780 | 780 | 0 | match |
| verilogeval_pass5_deepseek_coder | passed | 376 | 376 | 0 | match |
| verilogeval_pass5_deepseek_coder | compile_failure | 111 | 111 | 0 | match |
| verilogeval_pass5_deepseek_coder | simulation_failure | 291 | 291 | 0 | match |
| verilogeval_pass5_deepseek_coder | code_extraction_failure | 2 | 2 | 0 | match |
| verilogeval_pass5_deepseek_coder | timeout | N/A | 0 |  | n/a |
| verilogeval_pass5_deepseek_coder | synthesis_failure | N/A | 0 |  | n/a |
| verilogeval_pass5_deepseek_coder | equiv_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen36_27b | samples | 50 | 50 | 0 | match |
| rtllm2_pass1_qwen36_27b | passed | 30 | 30 | 0 | match |
| rtllm2_pass1_qwen36_27b | compile_failure | 14 | 14 | 0 | match |
| rtllm2_pass1_qwen36_27b | simulation_failure | 4 | 4 | 0 | match |
| rtllm2_pass1_qwen36_27b | code_extraction_failure | 1 | 1 | 0 | match |
| rtllm2_pass1_qwen36_27b | timeout | 1 | 1 | 0 | match |
| rtllm2_pass1_qwen36_27b | synthesis_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen36_27b | equiv_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen36_35b_a3b | samples | 50 | 50 | 0 | match |
| rtllm2_pass1_qwen36_35b_a3b | passed | 30 | 30 | 0 | match |
| rtllm2_pass1_qwen36_35b_a3b | compile_failure | 10 | 10 | 0 | match |
| rtllm2_pass1_qwen36_35b_a3b | simulation_failure | 8 | 8 | 0 | match |
| rtllm2_pass1_qwen36_35b_a3b | code_extraction_failure | 1 | 1 | 0 | match |
| rtllm2_pass1_qwen36_35b_a3b | timeout | 1 | 1 | 0 | match |
| rtllm2_pass1_qwen36_35b_a3b | synthesis_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen36_35b_a3b | equiv_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen3_coder | samples | 50 | 50 | 0 | match |
| rtllm2_pass1_qwen3_coder | passed | N/A | 25 |  | n/a |
| rtllm2_pass1_qwen3_coder | compile_failure | N/A | 17 |  | n/a |
| rtllm2_pass1_qwen3_coder | simulation_failure | N/A | 8 |  | n/a |
| rtllm2_pass1_qwen3_coder | code_extraction_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen3_coder | timeout | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen3_coder | synthesis_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen3_coder | equiv_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen25_coder | samples | 50 | 50 | 0 | match |
| rtllm2_pass1_qwen25_coder | passed | N/A | 27 |  | n/a |
| rtllm2_pass1_qwen25_coder | compile_failure | N/A | 13 |  | n/a |
| rtllm2_pass1_qwen25_coder | simulation_failure | N/A | 9 |  | n/a |
| rtllm2_pass1_qwen25_coder | code_extraction_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen25_coder | timeout | N/A | 1 |  | n/a |
| rtllm2_pass1_qwen25_coder | synthesis_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_qwen25_coder | equiv_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_deepseek_coder | samples | 50 | 50 | 0 | match |
| rtllm2_pass1_deepseek_coder | passed | 26 | 26 | 0 | match |
| rtllm2_pass1_deepseek_coder | compile_failure | 11 | 11 | 0 | match |
| rtllm2_pass1_deepseek_coder | simulation_failure | 13 | 13 | 0 | match |
| rtllm2_pass1_deepseek_coder | code_extraction_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_deepseek_coder | timeout | N/A | 0 |  | n/a |
| rtllm2_pass1_deepseek_coder | synthesis_failure | N/A | 0 |  | n/a |
| rtllm2_pass1_deepseek_coder | equiv_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_27b | samples | 9 | 9 | 0 | match |
| protocollm_lint_qwen36_27b | passed | 7 | 7 | 0 | match |
| protocollm_lint_qwen36_27b | compile_failure | 2 | 2 | 0 | match |
| protocollm_lint_qwen36_27b | simulation_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_27b | code_extraction_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_27b | timeout | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_27b | synthesis_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_27b | equiv_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_35b_a3b | samples | 9 | 9 | 0 | match |
| protocollm_lint_qwen36_35b_a3b | passed | 2 | 2 | 0 | match |
| protocollm_lint_qwen36_35b_a3b | compile_failure | 4 | 4 | 0 | match |
| protocollm_lint_qwen36_35b_a3b | simulation_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_35b_a3b | code_extraction_failure | 3 | 3 | 0 | match |
| protocollm_lint_qwen36_35b_a3b | timeout | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_35b_a3b | synthesis_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen36_35b_a3b | equiv_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen3_coder | samples | 9 | 9 | 0 | match |
| protocollm_lint_qwen3_coder | passed | 7 | 7 | 0 | match |
| protocollm_lint_qwen3_coder | compile_failure | 2 | 2 | 0 | match |
| protocollm_lint_qwen3_coder | simulation_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen3_coder | code_extraction_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen3_coder | timeout | N/A | 0 |  | n/a |
| protocollm_lint_qwen3_coder | synthesis_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen3_coder | equiv_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen25_coder | samples | 9 | 9 | 0 | match |
| protocollm_lint_qwen25_coder | passed | 6 | 6 | 0 | match |
| protocollm_lint_qwen25_coder | compile_failure | 3 | 3 | 0 | match |
| protocollm_lint_qwen25_coder | simulation_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen25_coder | code_extraction_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen25_coder | timeout | N/A | 0 |  | n/a |
| protocollm_lint_qwen25_coder | synthesis_failure | N/A | 0 |  | n/a |
| protocollm_lint_qwen25_coder | equiv_failure | N/A | 0 |  | n/a |
| protocollm_lint_deepseek_coder | samples | 9 | 9 | 0 | match |
| protocollm_lint_deepseek_coder | passed | 6 | 6 | 0 | match |
| protocollm_lint_deepseek_coder | compile_failure | 3 | 3 | 0 | match |
| protocollm_lint_deepseek_coder | simulation_failure | N/A | 0 |  | n/a |
| protocollm_lint_deepseek_coder | code_extraction_failure | N/A | 0 |  | n/a |
| protocollm_lint_deepseek_coder | timeout | N/A | 0 |  | n/a |
| protocollm_lint_deepseek_coder | synthesis_failure | N/A | 0 |  | n/a |
| protocollm_lint_deepseek_coder | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_27b | samples | 40 | 40 | 0 | match |
| rtlopt_lint_qwen36_27b | passed | 37 | 37 | 0 | match |
| rtlopt_lint_qwen36_27b | compile_failure | 3 | 3 | 0 | match |
| rtlopt_lint_qwen36_27b | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_27b | code_extraction_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_27b | timeout | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_27b | synthesis_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_27b | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_35b_a3b | samples | 40 | 40 | 0 | match |
| rtlopt_lint_qwen36_35b_a3b | passed | 34 | 34 | 0 | match |
| rtlopt_lint_qwen36_35b_a3b | compile_failure | 5 | 5 | 0 | match |
| rtlopt_lint_qwen36_35b_a3b | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_35b_a3b | code_extraction_failure | 1 | 1 | 0 | match |
| rtlopt_lint_qwen36_35b_a3b | timeout | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_35b_a3b | synthesis_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen36_35b_a3b | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen3_coder | samples | 40 | 40 | 0 | match |
| rtlopt_lint_qwen3_coder | passed | 33 | 33 | 0 | match |
| rtlopt_lint_qwen3_coder | compile_failure | 4 | 4 | 0 | match |
| rtlopt_lint_qwen3_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen3_coder | code_extraction_failure | 3 | 3 | 0 | match |
| rtlopt_lint_qwen3_coder | timeout | N/A | 0 |  | n/a |
| rtlopt_lint_qwen3_coder | synthesis_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen3_coder | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen25_coder | samples | 40 | 40 | 0 | match |
| rtlopt_lint_qwen25_coder | passed | 37 | 37 | 0 | match |
| rtlopt_lint_qwen25_coder | compile_failure | 3 | 3 | 0 | match |
| rtlopt_lint_qwen25_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen25_coder | code_extraction_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen25_coder | timeout | N/A | 0 |  | n/a |
| rtlopt_lint_qwen25_coder | synthesis_failure | N/A | 0 |  | n/a |
| rtlopt_lint_qwen25_coder | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_lint_deepseek_coder | samples | 40 | 40 | 0 | match |
| rtlopt_lint_deepseek_coder | passed | 37 | 37 | 0 | match |
| rtlopt_lint_deepseek_coder | compile_failure | 2 | 2 | 0 | match |
| rtlopt_lint_deepseek_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_lint_deepseek_coder | code_extraction_failure | 1 | 1 | 0 | match |
| rtlopt_lint_deepseek_coder | timeout | N/A | 0 |  | n/a |
| rtlopt_lint_deepseek_coder | synthesis_failure | N/A | 0 |  | n/a |
| rtlopt_lint_deepseek_coder | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_27b | samples | 40 | 40 | 0 | match |
| rtlopt_synthesis_qwen36_27b | passed | 36 | 36 | 0 | match |
| rtlopt_synthesis_qwen36_27b | compile_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_27b | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_27b | code_extraction_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_27b | timeout | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_27b | synthesis_failure | 4 | 4 | 0 | match |
| rtlopt_synthesis_qwen36_27b | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_35b_a3b | samples | 40 | 40 | 0 | match |
| rtlopt_synthesis_qwen36_35b_a3b | passed | 35 | 35 | 0 | match |
| rtlopt_synthesis_qwen36_35b_a3b | compile_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_35b_a3b | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_35b_a3b | code_extraction_failure | 2 | 2 | 0 | match |
| rtlopt_synthesis_qwen36_35b_a3b | timeout | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen36_35b_a3b | synthesis_failure | 3 | 3 | 0 | match |
| rtlopt_synthesis_qwen36_35b_a3b | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen3_coder | samples | 40 | 40 | 0 | match |
| rtlopt_synthesis_qwen3_coder | passed | 37 | 37 | 0 | match |
| rtlopt_synthesis_qwen3_coder | compile_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen3_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen3_coder | code_extraction_failure | 1 | 1 | 0 | match |
| rtlopt_synthesis_qwen3_coder | timeout | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen3_coder | synthesis_failure | 2 | 2 | 0 | match |
| rtlopt_synthesis_qwen3_coder | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen25_coder | samples | 40 | 40 | 0 | match |
| rtlopt_synthesis_qwen25_coder | passed | 36 | 36 | 0 | match |
| rtlopt_synthesis_qwen25_coder | compile_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen25_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen25_coder | code_extraction_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen25_coder | timeout | N/A | 0 |  | n/a |
| rtlopt_synthesis_qwen25_coder | synthesis_failure | 4 | 4 | 0 | match |
| rtlopt_synthesis_qwen25_coder | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_deepseek_coder | samples | 40 | 40 | 0 | match |
| rtlopt_synthesis_deepseek_coder | passed | 36 | 36 | 0 | match |
| rtlopt_synthesis_deepseek_coder | compile_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_deepseek_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_synthesis_deepseek_coder | code_extraction_failure | 1 | 1 | 0 | match |
| rtlopt_synthesis_deepseek_coder | timeout | N/A | 0 |  | n/a |
| rtlopt_synthesis_deepseek_coder | synthesis_failure | 3 | 3 | 0 | match |
| rtlopt_synthesis_deepseek_coder | equiv_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen36_27b | samples | 40 | 40 | 0 | match |
| rtlopt_equivalence_qwen36_27b | passed | 25 | 25 | 0 | match |
| rtlopt_equivalence_qwen36_27b | compile_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen36_27b | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen36_27b | code_extraction_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen36_27b | timeout | 2 | 2 | 0 | match |
| rtlopt_equivalence_qwen36_27b | synthesis_failure | 4 | 4 | 0 | match |
| rtlopt_equivalence_qwen36_27b | equiv_failure | 9 | 9 | 0 | match |
| rtlopt_equivalence_qwen36_35b_a3b | samples | 40 | 40 | 0 | match |
| rtlopt_equivalence_qwen36_35b_a3b | passed | 19 | 19 | 0 | match |
| rtlopt_equivalence_qwen36_35b_a3b | compile_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen36_35b_a3b | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen36_35b_a3b | code_extraction_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen36_35b_a3b | timeout | 1 | 1 | 0 | match |
| rtlopt_equivalence_qwen36_35b_a3b | synthesis_failure | 5 | 5 | 0 | match |
| rtlopt_equivalence_qwen36_35b_a3b | equiv_failure | 15 | 15 | 0 | match |
| rtlopt_equivalence_qwen3_coder | samples | 40 | 40 | 0 | match |
| rtlopt_equivalence_qwen3_coder | passed | 19 | 19 | 0 | match |
| rtlopt_equivalence_qwen3_coder | compile_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen3_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen3_coder | code_extraction_failure | 2 | 2 | 0 | match |
| rtlopt_equivalence_qwen3_coder | timeout | 2 | 2 | 0 | match |
| rtlopt_equivalence_qwen3_coder | synthesis_failure | 1 | 1 | 0 | match |
| rtlopt_equivalence_qwen3_coder | equiv_failure | 16 | 16 | 0 | match |
| rtlopt_equivalence_qwen25_coder | samples | 40 | 40 | 0 | match |
| rtlopt_equivalence_qwen25_coder | passed | 19 | 19 | 0 | match |
| rtlopt_equivalence_qwen25_coder | compile_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen25_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen25_coder | code_extraction_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen25_coder | timeout | N/A | 0 |  | n/a |
| rtlopt_equivalence_qwen25_coder | synthesis_failure | 4 | 4 | 0 | match |
| rtlopt_equivalence_qwen25_coder | equiv_failure | 17 | 17 | 0 | match |
| rtlopt_equivalence_deepseek_coder | samples | 40 | 40 | 0 | match |
| rtlopt_equivalence_deepseek_coder | passed | 29 | 29 | 0 | match |
| rtlopt_equivalence_deepseek_coder | compile_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_deepseek_coder | simulation_failure | N/A | 0 |  | n/a |
| rtlopt_equivalence_deepseek_coder | code_extraction_failure | 1 | 1 | 0 | match |
| rtlopt_equivalence_deepseek_coder | timeout | 2 | 2 | 0 | match |
| rtlopt_equivalence_deepseek_coder | synthesis_failure | 3 | 3 | 0 | match |
| rtlopt_equivalence_deepseek_coder | equiv_failure | 5 | 5 | 0 | match |

## Notes

- This audit is diagnostic. It does not rewrite `runs/index.yaml`, `manual_summary`, or benchmark outputs.
- A difference may indicate that an accessible `summary.json` overrides an older manual summary, that the sanitized per-task export reflects corrected source rows, or that the registry has drifted from its registered output.
- `N/A` means the registered summary did not provide that value, so no equality decision was made for that field.
- Review every mismatch before tagging Baseline v0.2; do not edit counts merely to make the audit pass.

## Loader Warnings

None.
