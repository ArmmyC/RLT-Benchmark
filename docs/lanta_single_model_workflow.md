# LANTA Single-Model Benchmark Workflow

`RLT-Benchmark` assumes one active OpenAI-compatible model endpoint at a time. It sends benchmark requests to that endpoint, saves run artifacts, and evaluates generated RTL. It does not start, stop, or swap the served model.

## Responsibility Split

`Lanta-LLM-Hosting` owns:

- vLLM model serving
- Slurm job submission and GPU allocation
- model download and cache configuration
- switching the active model
- endpoint exposure
- OpenWebUI and LiteLLM, if those services are used

`RLT-Benchmark` owns:

- benchmark task loading and prompts
- OpenAI-compatible generation requests
- RTL extraction
- lint, compile, simulation, synthesis, and equivalence evaluation
- timestamped run artifacts
- the Baseline v0.1 registry, generated reports, and dashboard

## Running One Model

1. In `Lanta-LLM-Hosting`, follow `HOW_TO_SWAP.md` to serve the desired model.
2. Confirm the vLLM endpoint is ready.
3. Query `/v1/models` and verify the active served model name before starting a benchmark.
4. Select the matching model preset from `configs/models.yaml`.
5. Run a small benchmark smoke test before any full condition.
6. Run the required benchmark condition with the same settings used by the comparison baseline.
7. Preserve the timestamped output folder and write a committed report or manifest.
8. Register a selected run in `runs/index.yaml` only after its artifacts and settings have been verified.

Example benchmark invocation after the endpoint is already active:

```bash
rtlbench --config configs/verilogeval.yaml \
  --model-preset <model-preset> \
  --base-url http://<vllm-node>:8000/v1 \
  --limit 3 --samples-per-task 1
```

The endpoint and node shown above are placeholders. Do not commit credentials, private tunnels, or API keys.

## What This Repository Must Not Add

Do not add automatic SSH, Slurm submission, or model-swap logic to the Baseline reporting package. Do not add OpenWebUI or LiteLLM here. Serving orchestration remains in `Lanta-LLM-Hosting`; keeping the boundary explicit makes benchmark results easier to reproduce and audit.
