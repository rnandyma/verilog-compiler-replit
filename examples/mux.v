// Simple 2-to-1 multiplexer
module mux2to1(sel, a, b, y);
    input sel, a, b;
    output y;
    
    assign y = sel ? a : b;
endmodule