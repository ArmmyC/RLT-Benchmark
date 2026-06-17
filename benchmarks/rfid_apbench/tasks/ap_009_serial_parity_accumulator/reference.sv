module ap_009_serial_parity_accumulator (
    input logic clk,
    input logic rst_n,
    input logic clear,
    input logic bit_valid,
    input logic bit_in,
    output logic parity,
    output logic [3:0] bit_count
);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            parity <= 1'b0;
            bit_count <= 4'd0;
        end else if (clear) begin
            parity <= 1'b0;
            bit_count <= 4'd0;
        end else if (bit_valid) begin
            parity <= parity ^ bit_in;
            bit_count <= bit_count + 4'd1;
        end
    end
endmodule
