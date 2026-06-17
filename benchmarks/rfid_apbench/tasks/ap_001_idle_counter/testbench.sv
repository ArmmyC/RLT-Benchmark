module testbench;
    logic clk;
    logic rst_n;
    logic active;
    logic clear;
    logic [7:0] count;
    logic expired;

    ap_001_idle_counter dut (
        .clk(clk),
        .rst_n(rst_n),
        .active(active),
        .clear(clear),
        .count(count),
        .expired(expired)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        rst_n = 1'b0;
        active = 1'b0;
        clear = 1'b0;
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        repeat (3) @(posedge clk);
        if (count !== 8'd0 || expired !== 1'b0) $fatal(1, "idle changed state");
        active = 1'b1;
        repeat (15) @(posedge clk);
        if (count !== 8'h0f || expired !== 1'b1) $fatal(1, "terminal count failed");
        active = 1'b0;
        repeat (4) @(posedge clk);
        if (count !== 8'h0f || expired !== 1'b1) $fatal(1, "idle hold failed");
        clear = 1'b1;
        @(posedge clk);
        clear = 1'b0;
        if (count !== 8'd0 || expired !== 1'b0) $fatal(1, "clear failed");
        $finish;
    end
endmodule
