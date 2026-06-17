Implement the SystemVerilog module `ap_007_command_frame_checker`.

Ports:

- `input logic valid`
- `input logic [3:0] length`
- `input logic [3:0] opcode`
- `input logic checksum_ok`
- `output logic accept`
- `output logic reject`

Behavior:

- When `valid` is low, deassert both outputs.
- A valid frame is accepted only when `length` is from 4 through 8 inclusive,
  `opcode` is neither `4'h0` nor `4'hf`, and `checksum_ok` is high.
- Every other valid frame asserts `reject` and deasserts `accept`.

Return only synthesizable SystemVerilog for the requested module.
