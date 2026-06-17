module ap_005_fsm_controller_idle_activity (
    input logic clk,
    input logic rst_n,
    input logic field_on,
    input logic frame_valid,
    input logic crc_ok,
    output logic listen,
    output logic decode,
    output logic respond,
    output logic error
);
    typedef enum logic [1:0] {
        ST_IDLE,
        ST_DECODE,
        ST_RESPOND,
        ST_ERROR
    } state_t;

    state_t state;
    state_t next_state;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= ST_IDLE;
        end else begin
            state <= next_state;
        end
    end

    always_comb begin
        next_state = state;
        unique case (state)
            ST_IDLE: begin
                if (field_on && frame_valid) begin
                    next_state = ST_DECODE;
                end else begin
                    next_state = ST_IDLE;
                end
            end
            ST_DECODE: begin
                if (crc_ok) begin
                    next_state = ST_RESPOND;
                end else begin
                    next_state = ST_ERROR;
                end
            end
            ST_RESPOND: next_state = ST_IDLE;
            ST_ERROR: next_state = ST_IDLE;
            default: next_state = ST_IDLE;
        endcase
    end

    assign listen = (state == ST_IDLE);
    assign decode = (state == ST_DECODE);
    assign respond = (state == ST_RESPOND);
    assign error = (state == ST_ERROR);
endmodule
