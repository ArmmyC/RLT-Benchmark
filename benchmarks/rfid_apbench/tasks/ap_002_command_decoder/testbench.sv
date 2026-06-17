module testbench;
    logic [3:0] cmd;
    logic valid;
    logic do_inventory;
    logic do_select;
    logic do_read;
    logic do_write;
    logic illegal;

    ap_002_command_decoder dut (
        .cmd(cmd),
        .valid(valid),
        .do_inventory(do_inventory),
        .do_select(do_select),
        .do_read(do_read),
        .do_write(do_write),
        .illegal(illegal)
    );

    task automatic check(input [3:0] c, input v, input [4:0] expected);
        begin
            cmd = c;
            valid = v;
            #1;
            if ({do_inventory, do_select, do_read, do_write, illegal} !== expected) begin
                $fatal(1, "decode mismatch");
            end
        end
    endtask

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        check(4'h1, 1'b1, 5'b10000);
        check(4'h2, 1'b1, 5'b01000);
        check(4'h3, 1'b1, 5'b00100);
        check(4'h4, 1'b1, 5'b00010);
        check(4'hf, 1'b1, 5'b00001);
        check(4'h1, 1'b0, 5'b00000);
        $finish;
    end
endmodule
