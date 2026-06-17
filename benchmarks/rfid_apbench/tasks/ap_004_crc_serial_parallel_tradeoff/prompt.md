Implement the SystemVerilog module `ap_004_crc_serial_parallel_tradeoff`.

Ports:

- `input logic clk`
- `input logic rst_n`
- `input logic clear`
- `input logic bit_valid`
- `input logic bit_in`
- `output logic [3:0] crc`

Behavior:

- Reset or `clear` loads `crc` with `4'hf`.
- When `bit_valid` is high, update the CRC using polynomial `x^4 + x + 1`.
- When `bit_valid` is low, hold `crc`.
- The serial update feedback is `crc[3] ^ bit_in`; next CRC is `{crc[2], crc[1], crc[0] ^ feedback, feedback}`.

Return only synthesizable SystemVerilog for the requested module.
