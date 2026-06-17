module ap_006_wakeup_edge_filter (
    input logic clk,
    input logic rst_n,
    input logic enable,
    input logic signal_in,
    output logic wake_pulse
);
    logic previous_signal;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            previous_signal <= 1'b0;
            wake_pulse <= 1'b0;
        end else if (!enable) begin
            previous_signal <= 1'b0;
            wake_pulse <= 1'b0;
        end else begin
            wake_pulse <= signal_in && !previous_signal;
            previous_signal <= signal_in;
        end
    end
endmodule
