module testbench;
    logic clk;
    logic rst_n;
    logic clear;
    logic bit_valid;
    logic bit_in;
    logic [3:0] crc;

    ap_004_crc_serial_parallel_tradeoff dut (
        .clk(clk),
        .rst_n(rst_n),
        .clear(clear),
        .bit_valid(bit_valid),
        .bit_in(bit_in),
        .crc(crc)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    task automatic send_bit(input logic b);
        begin
            bit_in = b;
            bit_valid = 1'b1;
            @(posedge clk);
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
        if (crc !== 4'hb) $fatal(1, "crc vector mismatch");
        clear = 1'b1;
        @(posedge clk);
        clear = 1'b0;
        if (crc !== 4'hf) $fatal(1, "clear mismatch");
        $finish;
    end
endmodule
