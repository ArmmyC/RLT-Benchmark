Implement the SystemVerilog module `ap_001_idle_counter`.

Ports:

- `input logic clk`
- `input logic rst_n`
- `input logic active`
- `input logic clear`
- `output logic [7:0] count`
- `output logic expired`

Behavior:

- Reset drives `count` to zero and `expired` low.
- `clear` synchronously clears `count` and `expired`.
- When `active` is high, increment `count` until it reaches `8'h0f`.
- Once `count` is `8'h0f`, hold the count and assert `expired`.
- When `active` is low, hold state without advancing the counter.

Return only synthesizable SystemVerilog for the requested module.
