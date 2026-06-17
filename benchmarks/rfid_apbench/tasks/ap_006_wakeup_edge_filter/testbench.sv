module testbench;
    logic clk;
    logic rst_n;
    logic enable;
    logic signal_in;
    logic wake_pulse;

    ap_006_wakeup_edge_filter dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .signal_in(signal_in),
        .wake_pulse(wake_pulse)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    task automatic drive_and_check(input logic value, input logic expected_pulse);
        begin
            @(negedge clk);
            signal_in = value;
            @(posedge clk);
            #1;
            if (wake_pulse !== expected_pulse) $fatal(1, "wakeup pulse mismatch");
        end
    endtask

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        rst_n = 1'b0;
        enable = 1'b0;
        signal_in = 1'b0;
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        repeat (2) @(posedge clk);
        if (wake_pulse !== 1'b0) $fatal(1, "reset pulse mismatch");
        enable = 1'b1;
        drive_and_check(1'b1, 1'b1);
        drive_and_check(1'b1, 1'b0);
        drive_and_check(1'b0, 1'b0);
        drive_and_check(1'b1, 1'b1);
        @(negedge clk);
        enable = 1'b0;
        signal_in = 1'b1;
        @(posedge clk);
        #1;
        if (wake_pulse !== 1'b0) $fatal(1, "disabled pulse mismatch");
        $finish;
    end
endmodule
