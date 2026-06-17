module ap_008_byte_lane_write_gate (
    input logic clk,
    input logic rst_n,
    input logic write_en,
    input logic [1:0] byte_en,
    input logic [15:0] write_data,
    output logic [15:0] data_reg
);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data_reg <= 16'd0;
        end else if (write_en) begin
            if (byte_en[0]) data_reg[7:0] <= write_data[7:0];
            if (byte_en[1]) data_reg[15:8] <= write_data[15:8];
        end
    end
endmodule
