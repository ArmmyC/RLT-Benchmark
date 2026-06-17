Implement the SystemVerilog module `ap_009_serial_parity_accumulator`.

Ports:

- `input logic clk`
- `input logic rst_n`
- `input logic clear`
- `input logic bit_valid`
- `input logic bit_in`
- `output logic parity`
- `output logic [3:0] bit_count`

Behavior:

- Active-low reset or synchronous `clear` sets `parity` and `bit_count` to zero.
- When `bit_valid` is high, XOR `bit_in` into `parity` and increment
  `bit_count` modulo 16.
- When `bit_valid` is low, hold both outputs.

Return only synthesizable SystemVerilog for the requested module.
