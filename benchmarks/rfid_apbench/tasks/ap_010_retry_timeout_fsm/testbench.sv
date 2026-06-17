module testbench;
    logic clk;
    logic rst_n;
    logic start;
    logic ack;
    logic timeout_tick;
    logic active;
    logic retry_pulse;
    logic failed;
    logic [1:0] retry_count;

    ap_010_retry_timeout_fsm dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .ack(ack),
        .timeout_tick(timeout_tick),
        .active(active),
        .retry_pulse(retry_pulse),
        .failed(failed),
        .retry_count(retry_count)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    task automatic pulse_start;
        begin
            @(negedge clk);
            start = 1'b1;
            @(posedge clk);
            #1;
            start = 1'b0;
        end
    endtask

    task automatic pulse_ack;
        begin
            @(negedge clk);
            ack = 1'b1;
            @(posedge clk);
            #1;
            ack = 1'b0;
        end
    endtask

    task automatic pulse_timeout;
        begin
            @(negedge clk);
            timeout_tick = 1'b1;
            @(posedge clk);
            #1;
            timeout_tick = 1'b0;
        end
    endtask

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        rst_n = 1'b0;
        start = 1'b0;
        ack = 1'b0;
        timeout_tick = 1'b0;
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        pulse_start();
        if (!active || failed || retry_count !== 2'd0) $fatal(1, "start mismatch");
        pulse_timeout();
        if (!active || !retry_pulse || retry_count !== 2'd1) $fatal(1, "first retry mismatch");
        @(posedge clk);
        #1;
        if (retry_pulse) $fatal(1, "retry pulse did not clear");
        pulse_ack();
        if (active || retry_count !== 2'd0) $fatal(1, "ack mismatch");
        pulse_start();
        pulse_timeout();
        pulse_timeout();
        pulse_timeout();
        if (active || !failed || retry_pulse || retry_count !== 2'd3)
            $fatal(1, "terminal timeout mismatch");
        $finish;
    end
endmodule
