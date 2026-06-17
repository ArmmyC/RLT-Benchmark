module testbench;
    logic clk;
    logic rst_n;
    logic clear;
    logic bit_valid;
    logic bit_in;
    logic parity;
    logic [3:0] bit_count;

    ap_009_serial_parity_accumulator dut (
        .clk(clk),
        .rst_n(rst_n),
        .clear(clear),
        .bit_valid(bit_valid),
        .bit_in(bit_in),
        .parity(parity),
        .bit_count(bit_count)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    task automatic send_bit(input logic value);
        begin
            @(negedge clk);
            bit_in = value;
            bit_valid = 1'b1;
            @(posedge clk);
            #1;
            bit_valid = 1'b0;
        end
    endtask

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        rst_n = 1'b0;
        clear = 1'b0;
        bit_valid = 1'b0;
        bit_in = 1'b0;
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        send_bit(1'b1);
        send_bit(1'b0);
        send_bit(1'b1);
        send_bit(1'b1);
        if (parity !== 1'b1 || bit_count !== 4'd4) $fatal(1, "parity accumulation mismatch");
        repeat (2) @(posedge clk);
        if (parity !== 1'b1 || bit_count !== 4'd4) $fatal(1, "invalid-cycle hold mismatch");
        @(negedge clk);
        clear = 1'b1;
        @(posedge clk);
        #1;
        clear = 1'b0;
        if (parity !== 1'b0 || bit_count !== 4'd0) $fatal(1, "clear mismatch");
        $finish;
    end
endmodule
