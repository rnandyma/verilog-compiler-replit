// Simple CPU Top Module
// Demonstrates a basic processor with ALU, register file, and control unit
module cpu_top(
    input clk,
    input reset,
    input [7:0] instruction,
    output [7:0] result,
    output reg done
);

    // Internal signals
    wire [3:0] opcode;
    wire [1:0] reg_addr_a, reg_addr_b, reg_addr_dest;
    wire [7:0] reg_data_a, reg_data_b;
    wire [7:0] alu_result;
    wire [2:0] alu_op;
    wire reg_write_en;
    
    // Decode instruction
    assign opcode = instruction[7:4];
    assign reg_addr_a = instruction[3:2];
    assign reg_addr_b = instruction[1:0];
    assign reg_addr_dest = reg_addr_a; // Simple destination addressing
    
    // Instantiate modules
    control_unit cu (
        .opcode(opcode),
        .alu_op(alu_op),
        .reg_write_en(reg_write_en)
    );
    
    register_file rf (
        .clk(clk),
        .reset(reset),
        .read_addr_a(reg_addr_a),
        .read_addr_b(reg_addr_b),
        .write_addr(reg_addr_dest),
        .write_data(alu_result),
        .write_en(reg_write_en),
        .read_data_a(reg_data_a),
        .read_data_b(reg_data_b)
    );
    
    alu arithmetic_unit (
        .a(reg_data_a),
        .b(reg_data_b),
        .op(alu_op),
        .result(alu_result)
    );
    
    assign result = alu_result;
    
    // Simple done signal
    always @(posedge clk or posedge reset) begin
        if (reset)
            done <= 1'b0;
        else
            done <= 1'b1;
    end

endmodule