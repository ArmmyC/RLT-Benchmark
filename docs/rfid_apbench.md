# RFID-APBench

RFID-APBench is RTLBench's current public/synthetic benchmark for RFID/NFC-style area/activity evaluation.

It is intentionally small, transparent, and commit-safe: every task includes a public prompt, reference RTL, testbench, declared activity workload, and sanitized reference metrics. It does not contain private RFID RTL or private task text.

## Inventory

The benchmark lives under `benchmarks/rfid_apbench/` and currently contains 10 tasks:

| Task | Summary |
| --- | --- |
| `ap_001_idle_counter` | Idle-aware counter |
| `ap_002_command_decoder` | Small command decoder |
| `ap_003_register_bank_unnecessary_writes` | Register bank with stable disabled writes |
| `ap_004_crc_serial_parallel_tradeoff` | CRC update block |
| `ap_005_fsm_controller_idle_activity` | Low-duty-cycle controller FSM |
| `ap_006_wakeup_edge_filter` | Enabled rising-edge wakeup pulse filter |
| `ap_007_command_frame_checker` | Command-frame validity checker |
| `ap_008_byte_lane_write_gate` | Byte-lane gated register writes |
| `ap_009_serial_parity_accumulator` | Serial parity and bit-count accumulator |
| `ap_010_retry_timeout_fsm` | Retry and timeout controller |

## Evaluation

Each generated candidate is evaluated through:

1. RTL extraction for the required top module.
2. Icarus Verilog compile.
3. Functional simulation against the public testbench.
4. Yosys generic synthesis.
5. VCD toggle-count activity measurement under the declared workload.
6. Correctness-gated area/activity scoring.

Compile-only or synthesis-only success is not functional correctness.

## v0.7 Public Baseline Summary

The v0.7 post-fix baseline evidence recorded:

| Metric | Result |
| --- | ---: |
| Tasks | 10 |
| Samples per task | 3 |
| Attempted rows | 30 |
| Non-empty responses | 30/30 |
| Extraction passed | 30/30 |
| Functional simulation passed | 27/30 |
| Valid scores | 27/30 |
| Mean valid score | 0.951014 |
| All-sample zero-filled score | 0.855912 |

The known v0.7 limitation is localized to `ap_006_wakeup_edge_filter` candidate behavior in that run. The release evidence did not support an endpoint, extractor, tool, evaluator, scoring, prompt-profile, or benchmark-asset defect for that limitation.

## Caveats

- Activity is a VCD toggle-count proxy, not measured power.
- Area is Yosys generic cell count, not foundry area.
- RFID-APBench is public/synthetic, not private evaluation.
- The benchmark is not fine-tuning readiness evidence.

## Related Docs

- [Release checklist](release/rfid_apbench_release_checklist.md)
- [Reproducibility guide](release/rfid_apbench_reproducibility.md)
- [Report hygiene](release/rfid_apbench_report_hygiene.md)
- [Task schema](rfid_apbench_task_schema.md)
