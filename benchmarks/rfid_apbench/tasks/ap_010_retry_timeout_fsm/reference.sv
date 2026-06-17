module ap_010_retry_timeout_fsm (
    input logic clk,
    input logic rst_n,
    input logic start,
    input logic ack,
    input logic timeout_tick,
    output logic active,
    output logic retry_pulse,
    output logic failed,
    output logic [1:0] retry_count
);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            active <= 1'b0;
            retry_pulse <= 1'b0;
            failed <= 1'b0;
            retry_count <= 2'd0;
        end else begin
            retry_pulse <= 1'b0;
            if (!active) begin
                if (start) begin
                    active <= 1'b1;
                    failed <= 1'b0;
                    retry_count <= 2'd0;
                end
            end else if (ack) begin
                active <= 1'b0;
                retry_count <= 2'd0;
            end else if (timeout_tick) begin
                if (retry_count == 2'd2) begin
                    active <= 1'b0;
                    failed <= 1'b1;
                    retry_count <= 2'd3;
                end else begin
                    retry_count <= retry_count + 2'd1;
                    retry_pulse <= 1'b1;
                end
            end
        end
    end
endmodule
