// Working Simulation Example - Simple ALU
module simple_alu(
    input [3:0] a,
    input [3:0] b,
    input [1:0] op,
    output reg [7:0] result
);
    always @(*) begin
        case (op)
            2'b00: result = a + b;  // ADD
            2'b01: result = a - b;  // SUB
            2'b10: result = a & b;  // AND
            2'b11: result = a | b;  // OR
            default: result = 8'h00;
        endcase
    end
endmodule

// Testbench for simple_alu
module testbench;
    reg [3:0] a, b;
    reg [1:0] op;
    wire [7:0] result;
    
    // Instantiate ALU
    simple_alu dut (
        .a(a),
        .b(b),
        .op(op),
        .result(result)
    );
    
    // Test sequence
    initial begin
        // Test ADD operation
        a = 4'h3; b = 4'h5; op = 2'b00;
        #10;
        
        // Test SUB operation
        a = 4'h8; b = 4'h3; op = 2'b01;
        #10;
        
        // Test AND operation
        a = 4'hF; b = 4'h5; op = 2'b10;
        #10;
        
        // Test OR operation
        a = 4'h3; b = 4'hC; op = 2'b11;
        #10;
        
        $finish;
    end
    
    // Monitor changes
    initial begin
        $monitor("Time=%0t: a=%h b=%h op=%b result=%h", $time, a, b, op, result);
    end
    
endmodule