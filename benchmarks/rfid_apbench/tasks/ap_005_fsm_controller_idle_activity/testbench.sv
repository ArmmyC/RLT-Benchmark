module testbench;
    logic clk;
    logic rst_n;
    logic field_on;
    logic frame_valid;
    logic crc_ok;
    logic listen;
    logic decode;
    logic respond;
    logic error;

    ap_005_fsm_controller_idle_activity dut (
        .clk(clk),
        .rst_n(rst_n),
        .field_on(field_on),
        .frame_valid(frame_valid),
        .crc_ok(crc_ok),
        .listen(listen),
        .decode(decode),
        .respond(respond),
        .error(error)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        rst_n = 1'b0;
        field_on = 1'b0;
        frame_valid = 1'b0;
        crc_ok = 1'b0;
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        repeat (3) @(posedge clk);
        if (!listen || decode || respond || error) $fatal(1, "idle output mismatch");
        field_on = 1'b1;
        frame_valid = 1'b1;
        crc_ok = 1'b1;
        @(posedge clk);
        frame_valid = 1'b0;
        #1;
        if (!decode) $fatal(1, "decode not entered");
        @(posedge clk);
        #1;
        if (!respond) $fatal(1, "respond not entered");
        @(posedge clk);
        #1;
        if (!listen) $fatal(1, "idle not restored");
        frame_valid = 1'b1;
        crc_ok = 1'b0;
        @(posedge clk);
        frame_valid = 1'b0;
        @(posedge clk);
        #1;
        if (!error) $fatal(1, "error not entered");
        $finish;
    end
endmodule
