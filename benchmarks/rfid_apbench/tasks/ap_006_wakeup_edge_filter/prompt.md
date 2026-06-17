Implement the SystemVerilog module `ap_006_wakeup_edge_filter`.

Ports:

- `input logic clk`
- `input logic rst_n`
- `input logic enable`
- `input logic signal_in`
- `output logic wake_pulse`

Behavior:

- Active-low reset clears all state and drives `wake_pulse` low.
- When `enable` is low, drive `wake_pulse` low and forget prior input state.
- When enabled, assert `wake_pulse` for one cycle on each rising edge of `signal_in`.
- Holding `signal_in` high must not retrigger the pulse.

Return only synthesizable SystemVerilog for the requested module.
