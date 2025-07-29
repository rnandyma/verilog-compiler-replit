// Control Unit
// Decodes instructions and generates control signals
module control_unit(
    input [3:0] opcode,
    output reg [2:0] alu_op,
    output reg reg_write_en
);

    // Instruction opcodes
    localparam INST_ADD = 4'h0;
    localparam INST_SUB = 4'h1;
    localparam INST_AND = 4'h2;
    localparam INST_OR  = 4'h3;
    localparam INST_XOR = 4'h4;
    localparam INST_SHL = 4'h5;
    localparam INST_SHR = 4'h6;
    localparam INST_NOT = 4'h7;
    localparam INST_NOP = 4'hF;
    
    always @(*) begin
        // Default values
        reg_write_en = 1'b0;
        alu_op = 3'b000;
        
        case (opcode)
            INST_ADD: begin
                alu_op = 3'b000;
                reg_write_en = 1'b1;
            end
            INST_SUB: begin
                alu_op = 3'b001;
                reg_write_en = 1'b1;
            end
            INST_AND: begin
                alu_op = 3'b010;
                reg_write_en = 1'b1;
            end
            INST_OR: begin
                alu_op = 3'b011;
                reg_write_en = 1'b1;
            end
            INST_XOR: begin
                alu_op = 3'b100;
                reg_write_en = 1'b1;
            end
            INST_SHL: begin
                alu_op = 3'b101;
                reg_write_en = 1'b1;
            end
            INST_SHR: begin
                alu_op = 3'b110;
                reg_write_en = 1'b1;
            end
            INST_NOT: begin
                alu_op = 3'b111;
                reg_write_en = 1'b1;
            end
            INST_NOP: begin
                alu_op = 3'b000;
                reg_write_en = 1'b0;
            end
            default: begin
                alu_op = 3'b000;
                reg_write_en = 1'b0;
            end
        endcase
    end

endmodule