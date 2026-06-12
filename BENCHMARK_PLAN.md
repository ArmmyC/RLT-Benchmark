# BENCHMARK_PLAN.md

## Phase 1: Normal RTL generation

Benchmarks:
- VerilogEval v2
- RTLLM 2.0

Metrics:
- syntax pass
- functional pass
- pass@1
- pass@5
- failure categories

Models:
- qwen36-27b
- qwen36-35b-a3b

## Phase 2: SystemVerilog/protocol

Benchmark:
- ProtocolLLM public

Metrics:
- lint pass
- compile pass if available
- functional pass only if public tests are available

## Phase 3: RTL optimization

Benchmark:
- RTL-OPT

Metrics:
- lint pass
- synthesis pass
- equivalence pass
- cell count ratio
- area improvement count

## Reporting rule

Do not mix benchmark types into one fake average score.
Report each benchmark separately.