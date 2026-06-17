Implement the SystemVerilog module `ap_010_retry_timeout_fsm`.

Ports:

- `input logic clk`
- `input logic rst_n`
- `input logic start`
- `input logic ack`
- `input logic timeout_tick`
- `output logic active`
- `output logic retry_pulse`
- `output logic failed`
- `output logic [1:0] retry_count`

Behavior:

- Active-low reset clears all outputs and the retry count.
- When idle, `start` begins an active attempt, clears `failed`, and resets the
  retry count.
- While active, `ack` returns to idle and clears the retry count.
- Without `ack`, each `timeout_tick` increments the retry count and asserts
  `retry_pulse` for one cycle for the first two retries.
- The third timeout ends the attempt, sets `retry_count` to 3, and asserts
  `failed` without asserting `retry_pulse`.
- Inputs have no effect while idle except for `start`.

Return only synthesizable SystemVerilog for the requested module.
