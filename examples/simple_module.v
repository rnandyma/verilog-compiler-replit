// Simple Verilog module example
module simple_gate(a, b, y);
    input a, b;
    output y;
    
    assign y = a & b;
endmodule
