Implement the SystemVerilog module `ap_003_register_bank_unnecessary_writes`.

Ports:

- `input logic clk`
- `input logic rst_n`
- `input logic write_en`
- `input logic [1:0] addr`
- `input logic [7:0] write_data`
- `output logic [7:0] read_data`

Behavior:

- Reset clears all four 8-bit registers.
- When `write_en` is high, update the register selected by `addr`.
- When `write_en` is low, register contents must hold.
- `read_data` always reflects the register selected by `addr`.

Return only synthesizable SystemVerilog for the requested module.
