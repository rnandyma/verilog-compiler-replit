// Simple CPU Testbench Example
`timescale 1ns/1ps

module cpu_testbench;
    // Inputs
    reg clk;
    reg reset;
    reg [7:0] instruction;
    
    // Outputs
    wire [7:0] result;
    wire done;
    
    // Instantiate the Unit Under Test (UUT)
    cpu_top uut (
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
        // Initialize inputs
        reset = 1;
        instruction = 8'h00;
        
        // Wait for reset
        #20;
        reset = 0;
        
        // Test instruction 1: Simple ADD operation
        #10;
        instruction = 8'h34; // Example: opcode=3, operands=4
        
        // Wait for processing
        #50;
        
        // Test instruction 2: Different operation
        instruction = 8'h78; // Example: opcode=7, operands=8
        
        // Wait for processing
        #50;
        
        // Test reset during operation
        #20;
        reset = 1;
        #10;
        reset = 0;
        
        // Final test
        #30;
        instruction = 8'hAB; // Example: opcode=A, operands=B
        
        // Wait and finish
        #100;
        $finish;
    end
    
    // Monitor signals
    initial begin
        $monitor("Time=%0t: clk=%b reset=%b instruction=%h result=%h done=%b", 
                 $time, clk, reset, instruction, result, done);
    end
    
endmodule