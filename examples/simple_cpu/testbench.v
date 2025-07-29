// Simple CPU Testbench
// Tests the basic functionality of the CPU design
`include "cpu_defines.vh"

module cpu_testbench;

    // Testbench signals
    reg clk;
    reg reset;
    reg [7:0] instruction;
    wire [7:0] result;
    wire done;
    
    // Instantiate the CPU
    cpu_top dut (
        .clk(clk),
        .reset(reset),
        .instruction(instruction),
        .result(result),
        .done(done)
    );
    
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
        // Assuming registers initialized to some values
        #10 instruction = 8'h01; // ADD R0, R1
        
        // Test SUB instruction
        #10 instruction = 8'h11; // SUB R0, R1
        
        // Test AND instruction
        #10 instruction = 8'h21; // AND R0, R1
        
        // Test OR instruction
        #10 instruction = 8'h31; // OR R0, R1
        
        // Test NOP instruction
        #10 instruction = 8'hF0; // NOP
        
        // Finish simulation
        #50 $finish;
    end
    
    // Monitor outputs
    initial begin
        $monitor("Time=%0t, Reset=%b, Instruction=%h, Result=%h, Done=%b",
                 $time, reset, instruction, result, done);
    end

endmodule