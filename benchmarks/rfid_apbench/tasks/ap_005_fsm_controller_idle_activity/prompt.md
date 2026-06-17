Implement the SystemVerilog module `ap_005_fsm_controller_idle_activity`.

Ports:

- `input logic clk`
- `input logic rst_n`
- `input logic field_on`
- `input logic frame_valid`
- `input logic crc_ok`
- `output logic listen`
- `output logic decode`
- `output logic respond`
- `output logic error`

Behavior:

- Reset enters idle/listen state.
- While `field_on` is low, remain idle with only `listen` asserted.
- When `field_on` and `frame_valid` are high, enter decode for one cycle.
- If `crc_ok` is high after decode, enter respond for one cycle, then idle.
- If `crc_ok` is low after decode, enter error for one cycle, then idle.

Return only synthesizable SystemVerilog for the requested module.
