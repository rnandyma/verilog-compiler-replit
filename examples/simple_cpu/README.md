# Simple CPU Design

This directory contains a complete Verilog design for a simple 8-bit CPU with the following components:

## Architecture Overview

The CPU consists of four main modules:

### 1. CPU Top Module (`cpu_top.v`)
- Main processor module that connects all components
- Handles instruction decoding and result output
- Coordinates data flow between all units

### 2. Arithmetic Logic Unit (`alu.v`)
- Performs 8 different operations: ADD, SUB, AND, OR, XOR, SHL, SHR, NOT
- 8-bit operands with 3-bit operation selection
- Combinational logic design

### 3. Register File (`register_file.v`)
- Contains 4 general-purpose 8-bit registers
- Dual-port read, single-port write
- Synchronous write with asynchronous read

### 4. Control Unit (`control_unit.v`)
- Decodes 4-bit instruction opcodes
- Generates ALU operation codes and control signals
- Determines when to write results back to registers

## Additional Files

- `cpu_defines.vh`: Header file with system-wide constants and definitions
- `testbench.v`: Comprehensive testbench for CPU verification

## Instruction Format

```
Bits [7:4] - Opcode (4 bits)
Bits [3:2] - Source/Destination Register A (2 bits)
Bits [1:0] - Source Register B (2 bits)
```

## Supported Instructions

| Opcode | Instruction | Operation |
|--------|-------------|-----------|
| 0x0    | ADD         | A = A + B |
| 0x1    | SUB         | A = A - B |
| 0x2    | AND         | A = A & B |
| 0x3    | OR          | A = A \| B |
| 0x4    | XOR         | A = A ^ B |
| 0x5    | SHL         | A = A << B |
| 0x6    | SHR         | A = A >> B |
| 0x7    | NOT         | A = ~A    |
| 0xF    | NOP         | No operation |

## Design Features

- Fully synchronous design with single clock domain
- Modular architecture for easy extension
- Comprehensive parameter definitions in header file
- Complete testbench with multiple instruction tests
- Clean separation of datapath and control logic

This design demonstrates hierarchical Verilog design practices and is suitable for FPGA implementation or simulation.