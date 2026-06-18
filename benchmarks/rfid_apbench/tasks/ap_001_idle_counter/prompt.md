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
- When `active` is high and `count` is `8'h0e`, the next rising clock edge must update `count` to `8'h0f` and assert `expired` in the same sequential update.
- After expiration, hold `count` at `8'h0f` and keep `expired` high until reset or synchronous clear.
- When `active` is low, hold state without advancing the counter.

Return only synthesizable SystemVerilog for the requested module.
