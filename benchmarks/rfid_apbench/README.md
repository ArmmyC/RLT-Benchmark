# RFID-APBench Public/Synthetic Benchmark

RFID-APBench is a public/synthetic RFID/NFC-style RTL benchmark for area plus activity evaluation.

This directory contains ten small synthetic tasks intended to exercise `area_activity` scoring. Activity means a VCD toggle-count proxy under a declared workload. It is not measured silicon power, final silicon power, or final PPA.

The benchmark contains no generated RTL from model outputs, raw responses,
logs, VCD output files, private SiliconCraft RTL, or training artifacts.

## Contents

- `manifest.yaml`: benchmark manifest listing the public synthetic tasks.
- `tasks/ap_001_idle_counter`: idle-aware counter.
- `tasks/ap_002_command_decoder`: small command decoder.
- `tasks/ap_003_register_bank_unnecessary_writes`: small register bank with stable disabled writes.
- `tasks/ap_004_crc_serial_parallel_tradeoff`: small CRC update block.
- `tasks/ap_005_fsm_controller_idle_activity`: low-duty-cycle controller FSM.
- `tasks/ap_006_wakeup_edge_filter`: enabled rising-edge wakeup pulse filter.
- `tasks/ap_007_command_frame_checker`: small command-frame validity checker.
- `tasks/ap_008_byte_lane_write_gate`: byte-lane gated register writes.
- `tasks/ap_009_serial_parity_accumulator`: serial parity and bit-count accumulator.
- `tasks/ap_010_retry_timeout_fsm`: low-activity retry and timeout controller.

Each task directory contains:

- `task.yaml`
- `prompt.md`
- `reference.sv`
- `testbench.sv`
- `activity_workload.yaml`
- `expected/reference_metrics.yaml` after tool-enabled validation

The five v0.6 expansion task packages (`ap_006` through `ap_010`) also include
`constraints.sdc`. The original v0.5 task assets remain unchanged.

## Artifact Policy

Do not commit benchmark run outputs, generated RTL, raw prompts, raw model responses, simulator logs, synthesis logs, VCD files, secrets, private data, training datasets, model weights, or LoRA/QLoRA/DoRA adapters.

## Documentation

- `docs/rfid_apbench.md`: benchmark overview and current public baseline summary.
- `docs/release/rfid_apbench_reproducibility.md`: local reproduction guide.
- `docs/release/rfid_apbench_report_hygiene.md`: report schema and artifact hygiene expectations.
