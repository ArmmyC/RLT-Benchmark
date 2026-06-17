module testbench;
    logic clk;
    logic rst_n;
    logic write_en;
    logic [1:0] byte_en;
    logic [15:0] write_data;
    logic [15:0] data_reg;

    ap_008_byte_lane_write_gate dut (
        .clk(clk),
        .rst_n(rst_n),
        .write_en(write_en),
        .byte_en(byte_en),
        .write_data(write_data),
        .data_reg(data_reg)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    task automatic write_and_check(
        input logic enable,
        input logic [1:0] lanes,
        input logic [15:0] value,
        input logic [15:0] expected
    );
        begin
            @(negedge clk);
            write_en = enable;
            byte_en = lanes;
            write_data = value;
            @(posedge clk);
            #1;
            if (data_reg !== expected) $fatal(1, "byte lane write mismatch");
        end
    endtask

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        rst_n = 1'b0;
        write_en = 1'b0;
        byte_en = 2'b00;
        write_data = 16'd0;
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        write_and_check(1'b1, 2'b01, 16'hab12, 16'h0012);
        write_and_check(1'b1, 2'b10, 16'hcd34, 16'hcd12);
        write_and_check(1'b0, 2'b11, 16'hffff, 16'hcd12);
        write_and_check(1'b1, 2'b00, 16'h5678, 16'hcd12);
        write_and_check(1'b1, 2'b11, 16'h5678, 16'h5678);
        $finish;
    end
endmodule
