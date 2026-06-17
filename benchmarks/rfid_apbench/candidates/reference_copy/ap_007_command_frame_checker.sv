module ap_007_command_frame_checker (
    input logic valid,
    input logic [3:0] length,
    input logic [3:0] opcode,
    input logic checksum_ok,
    output logic accept,
    output logic reject
);
    logic frame_ok;

    always_comb begin
        frame_ok = (length >= 4'd4) && (length <= 4'd8)
            && (opcode != 4'h0) && (opcode != 4'hf) && checksum_ok;
        accept = valid && frame_ok;
        reject = valid && !frame_ok;
    end
endmodule
