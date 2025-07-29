module test_module(a, b, y);
    input a, b;
    output y;
    
    // This line has an error - missing semicolon
    assign y = a & b
    
    wire extra_wire;
endmodule