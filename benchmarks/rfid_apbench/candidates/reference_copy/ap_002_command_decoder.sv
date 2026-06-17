module ap_002_command_decoder (
    input logic [3:0] cmd,
    input logic valid,
    output logic do_inventory,
    output logic do_select,
    output logic do_read,
    output logic do_write,
    output logic illegal
);
    always_comb begin
        do_inventory = 1'b0;
        do_select = 1'b0;
        do_read = 1'b0;
        do_write = 1'b0;
        illegal = 1'b0;
        if (valid) begin
            unique case (cmd)
                4'h1: do_inventory = 1'b1;
                4'h2: do_select = 1'b1;
                4'h3: do_read = 1'b1;
                4'h4: do_write = 1'b1;
                default: illegal = 1'b1;
            endcase
        end
    end
endmodule
