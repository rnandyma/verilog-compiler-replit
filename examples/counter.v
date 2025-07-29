// Simple counter module
module counter(clk, reset, count);
    input clk, reset;
    output count;
    
    wire clk, reset, count;
    
    // Simplified counter representation
    assign count = clk & ~reset;
endmodule