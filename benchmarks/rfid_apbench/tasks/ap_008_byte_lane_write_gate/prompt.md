Implement the SystemVerilog module `ap_008_byte_lane_write_gate`.

Ports:

- `input logic clk`
- `input logic rst_n`
- `input logic write_en`
- `input logic [1:0] byte_en`
- `input logic [15:0] write_data`
- `output logic [15:0] data_reg`

Behavior:

- Active-low reset clears `data_reg`.
- When `write_en` is low, hold the register.
- When `write_en` is high, update byte 0 only if `byte_en[0]` is high and byte
  1 only if `byte_en[1]` is high.
- Disabled byte lanes retain their prior values.

Return only synthesizable SystemVerilog for the requested module.
