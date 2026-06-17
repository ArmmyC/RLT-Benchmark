Implement the SystemVerilog module `ap_002_command_decoder`.

Ports:

- `input logic [3:0] cmd`
- `input logic valid`
- `output logic do_inventory`
- `output logic do_select`
- `output logic do_read`
- `output logic do_write`
- `output logic illegal`

Behavior:

- Outputs are active only when `valid` is high.
- `cmd == 4'h1` asserts `do_inventory`.
- `cmd == 4'h2` asserts `do_select`.
- `cmd == 4'h3` asserts `do_read`.
- `cmd == 4'h4` asserts `do_write`.
- Other valid commands assert `illegal`.
- Invalid cycles deassert all outputs.

Return only synthesizable SystemVerilog for the requested module.
