module ap_003_register_bank_unnecessary_writes (
    input logic clk,
    input logic rst_n,
    input logic write_en,
    input logic [1:0] addr,
    input logic [7:0] write_data,
    output logic [7:0] read_data
);
    logic [7:0] regs [0:3];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            regs[0] <= 8'd0;
            regs[1] <= 8'd0;
            regs[2] <= 8'd0;
            regs[3] <= 8'd0;
        end else if (write_en && regs[addr] != write_data) begin
            regs[addr] <= write_data;
        end
    end

    always_comb begin
        read_data = regs[addr];
    end
endmodule
