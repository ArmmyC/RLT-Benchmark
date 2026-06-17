# RFID-APBench MVP Scaffold

RFID-APBench is a public/synthetic RFID/NFC-style RTL benchmark scaffold for area plus activity evaluation.

This directory contains five small synthetic tasks intended to exercise future `area_activity` scoring. Activity means a VCD toggle-count proxy under a declared workload. It is not measured silicon power, final silicon power, or final PPA.

This is an MVP scaffold, not a completed benchmark result. It contains no model runs, no generated RTL from model outputs, no raw responses, no logs, no VCD output files, no private SiliconCraft RTL, and no training artifacts.

## Contents

- `manifest.yaml`: benchmark manifest listing the public synthetic tasks.
- `tasks/ap_001_idle_counter`: idle-aware counter.
- `tasks/ap_002_command_decoder`: small command decoder.
- `tasks/ap_003_register_bank_unnecessary_writes`: small register bank with stable disabled writes.
- `tasks/ap_004_crc_serial_parallel_tradeoff`: small CRC update block.
- `tasks/ap_005_fsm_controller_idle_activity`: low-duty-cycle controller FSM.

Each task directory contains:

- `task.yaml`
- `prompt.md`
- `reference.sv`
- `testbench.sv`
- `activity_workload.yaml`

## Artifact Policy

Do not commit benchmark run outputs, generated RTL, raw prompts, raw model responses, simulator logs, synthesis logs, VCD files, secrets, private data, training datasets, model weights, or LoRA/QLoRA/DoRA adapters.
