// Arithmetic Logic Unit
// Performs basic arithmetic and logic operations
module alu(
    input [7:0] a,
    input [7:0] b,
    input [2:0] op,
    output reg [7:0] result
);

    // ALU operations
    localparam ADD = 3'b000;
    localparam SUB = 3'b001;
    localparam AND = 3'b010;
    localparam OR  = 3'b011;
    localparam XOR = 3'b100;
    localparam SHL = 3'b101;
    localparam SHR = 3'b110;
    localparam NOT = 3'b111;
    
    always @(*) begin
        case (op)
            ADD: result = a + b;
            SUB: result = a - b;
            AND: result = a & b;
            OR:  result = a | b;
            XOR: result = a ^ b;
            SHL: result = a << b[2:0];
            SHR: result = a >> b[2:0];
            NOT: result = ~a;
            default: result = 8'b0;
        endcase
    end

endmodule