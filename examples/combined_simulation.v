// Simple 4-bit counter module
module counter(
    input clk,
    input reset,
    output reg [3:0] count
);
    always @(posedge clk or posedge reset) begin
        if (reset)
            count <= 4'b0000;
        else
            count <= count + 1;
    end
endmodule

// Testbench for the counter
module testbench;
    reg clk, reset;
    wire [3:0] count;
    
    // Instantiate counter
    counter dut (
        .clk(clk),
        .reset(reset),
        .count(count)
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
        #15;
        reset = 0;
        
        // Let counter run
        #80;
        
        // Test reset during counting
        reset = 1;
        #10;
        reset = 0;
        
        // Run more
        #50;
        
        $finish;
    end
    
    // Monitor output
    initial begin
        $monitor("Time=%0t: clk=%b reset=%b count=%d", $time, clk, reset, count);
    end
    
endmodule