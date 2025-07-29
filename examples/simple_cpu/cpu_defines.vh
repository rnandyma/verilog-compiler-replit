// CPU Design Constants and Definitions
// Header file with common definitions for the CPU design

`ifndef CPU_DEFINES_VH
`define CPU_DEFINES_VH

// Data width parameters
`define DATA_WIDTH 8
`define ADDR_WIDTH 2
`define OPCODE_WIDTH 4
`define ALU_OP_WIDTH 3

// Register file size
`define NUM_REGISTERS 4
`define REG_ADDR_WIDTH 2

// ALU operation codes
`define ALU_ADD 3'b000
`define ALU_SUB 3'b001
`define ALU_AND 3'b010
`define ALU_OR  3'b011
`define ALU_XOR 3'b100
`define ALU_SHL 3'b101
`define ALU_SHR 3'b110
`define ALU_NOT 3'b111

// Instruction opcodes
`define INST_ADD 4'h0
`define INST_SUB 4'h1
`define INST_AND 4'h2
`define INST_OR  4'h3
`define INST_XOR 4'h4
`define INST_SHL 4'h5
`define INST_SHR 4'h6
`define INST_NOT 4'h7
`define INST_NOP 4'hF

// Clock and reset parameters
`define RESET_ACTIVE_HIGH 1'b1
`define CLOCK_EDGE posedge

`endif // CPU_DEFINES_VH