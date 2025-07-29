// Tests the basic functionality of the CPU design
`include "cpu_defines.vh"

module cpu_testbench;
    reg clk;
    reg reset;
    reg [7:0] instruction;
    
    // Clock generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // 100MHz clock
    end
    
    // Test sequence
    initial begin
        // Initialize
        reset = 1;
        instruction = 8'h00;
        
        // Release reset
        #20 reset = 0;
        
        // Test ADD instruction (opcode=0, reg_a=0, reg_b=1)
        #10 instruction = 8'h01; // ADD R0, R1
    end  // <-- This end was missing in your original code
endmodule