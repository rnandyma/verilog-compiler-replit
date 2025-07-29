// Register File
// Contains 4 general-purpose 8-bit registers
module register_file(
    input clk,
    input reset,
    input [1:0] read_addr_a,
    input [1:0] read_addr_b,
    input [1:0] write_addr,
    input [7:0] write_data,
    input write_en,
    output [7:0] read_data_a,
    output [7:0] read_data_b
);

    // 4 registers, 8 bits each
    reg [7:0] registers [0:3];
    
    // Asynchronous read
    assign read_data_a = registers[read_addr_a];
    assign read_data_b = registers[read_addr_b];
    
    // Synchronous write
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            registers[0] <= 8'b0;
            registers[1] <= 8'b0;
            registers[2] <= 8'b0;
            registers[3] <= 8'b0;
        end else if (write_en) begin
            registers[write_addr] <= write_data;
        end
    end

endmodule