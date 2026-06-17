module testbench;
    logic valid;
    logic [3:0] length;
    logic [3:0] opcode;
    logic checksum_ok;
    logic accept;
    logic reject;

    ap_007_command_frame_checker dut (
        .valid(valid),
        .length(length),
        .opcode(opcode),
        .checksum_ok(checksum_ok),
        .accept(accept),
        .reject(reject)
    );

    task automatic check(
        input logic v,
        input logic [3:0] len,
        input logic [3:0] op,
        input logic sum_ok,
        input logic expected_accept,
        input logic expected_reject
    );
        begin
            valid = v;
            length = len;
            opcode = op;
            checksum_ok = sum_ok;
            #2;
            if (accept !== expected_accept || reject !== expected_reject)
                $fatal(1, "frame check mismatch");
        end
    endtask

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        check(1'b0, 4'd6, 4'h2, 1'b1, 1'b0, 1'b0);
        check(1'b1, 4'd4, 4'h1, 1'b1, 1'b1, 1'b0);
        check(1'b1, 4'd8, 4'he, 1'b1, 1'b1, 1'b0);
        check(1'b1, 4'd3, 4'h2, 1'b1, 1'b0, 1'b1);
        check(1'b1, 4'd9, 4'h2, 1'b1, 1'b0, 1'b1);
        check(1'b1, 4'd6, 4'h0, 1'b1, 1'b0, 1'b1);
        check(1'b1, 4'd6, 4'hf, 1'b1, 1'b0, 1'b1);
        check(1'b1, 4'd6, 4'h2, 1'b0, 1'b0, 1'b1);
        $finish;
    end
endmodule
