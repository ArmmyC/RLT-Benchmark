module ap_004_crc_serial_parallel_tradeoff (
    input logic clk,
    input logic rst_n,
    input logic clear,
    input logic bit_valid,
    input logic bit_in,
    output logic [3:0] crc
);
    logic feedback;

    assign feedback = crc[3] ^ bit_in;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            crc <= 4'hf;
        end else if (clear) begin
            crc <= 4'hf;
        end else if (bit_valid) begin
            crc <= {crc[2], crc[1], crc[0] ^ feedback, feedback};
        end
    end
endmodule
