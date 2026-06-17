module testbench;
    logic clk;
    logic rst_n;
    logic write_en;
    logic [1:0] addr;
    logic [7:0] write_data;
    logic [7:0] read_data;

    ap_003_register_bank_unnecessary_writes dut (
        .clk(clk),
        .rst_n(rst_n),
        .write_en(write_en),
        .addr(addr),
        .write_data(write_data),
        .read_data(read_data)
    );

    initial clk = 1'b0;
    always #5 clk = ~clk;

    task automatic write_reg(input [1:0] a, input [7:0] d);
        begin
            @(negedge clk);
            addr = a;
            write_data = d;
            write_en = 1'b1;
            @(negedge clk);
            write_en = 1'b0;
            #1;
            if (read_data !== d) $fatal(1, "write/read mismatch");
        end
    endtask

    initial begin
        $dumpfile("activity.vcd");
        $dumpvars(0, testbench);
        rst_n = 1'b0;
        write_en = 1'b0;
        addr = 2'd0;
        write_data = 8'd0;
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        write_reg(2'd0, 8'h12);
        write_reg(2'd1, 8'h34);
        write_reg(2'd1, 8'h34);
        @(negedge clk);
        addr = 2'd0;
        #1;
        if (read_data !== 8'h12) $fatal(1, "readback failed");
        repeat (3) @(posedge clk);
        $finish;
    end
endmodule
