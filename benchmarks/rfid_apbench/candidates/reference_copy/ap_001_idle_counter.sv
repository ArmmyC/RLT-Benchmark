module ap_001_idle_counter (
    input logic clk,
    input logic rst_n,
    input logic active,
    input logic clear,
    output logic [7:0] count,
    output logic expired
);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 8'd0;
            expired <= 1'b0;
        end else if (clear) begin
            count <= 8'd0;
            expired <= 1'b0;
        end else if (active && !expired) begin
            if (count == 8'h0e) begin
                count <= 8'h0f;
                expired <= 1'b1;
            end else begin
                count <= count + 8'd1;
            end
        end
    end
endmodule
