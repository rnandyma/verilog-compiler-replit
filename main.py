#!/usr/bin/env python3
"""
Verilog Compiler - Main Entry Point
A basic Verilog compiler with lexer, parser, and code generation capabilities.
"""

import sys
import argparse
from pathlib import Path

from lexer import VerilogLexer
from parser import VerilogParser
from code_generator import VerilogCodeGenerator
from errors import VerilogCompilerError


def compile_verilog_file(input_file, output_file=None, verbose=False):
    """
    Compile a Verilog file through the complete compilation pipeline.
    
    Args:
        input_file (str): Path to input Verilog file
        output_file (str): Path to output file (optional)
        verbose (bool): Enable verbose output
    
    Returns:
        bool: True if compilation successful, False otherwise
    """
    try:
        # Read input file
        with open(input_file, 'r') as f:
            source_code = f.read()
        
        if verbose:
            print(f"Compiling {input_file}...")
        
        # Lexical analysis
        lexer = VerilogLexer()
        tokens = lexer.tokenize(source_code)
        
        if verbose:
            print(f"Lexical analysis complete. Found {len(tokens)} tokens.")
        
        # Parsing
        parser = VerilogParser()
        ast = parser.parse(tokens)
        
        if verbose:
            print("Parsing complete. AST generated successfully.")
        
        # Code generation
        code_generator = VerilogCodeGenerator()
        generated_code = code_generator.generate(ast)
        
        if verbose:
            print("Code generation complete.")
        
        # Output results
        if output_file:
            with open(output_file, 'w') as f:
                f.write(generated_code)
            print(f"Compiled code written to {output_file}")
        else:
            print("Generated Code:")
            print("=" * 50)
            print(generated_code)
        
        return True
        
    except VerilogCompilerError as e:
        print(f"Compilation Error: {e}")
        return False
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Main function handling command-line interface."""
    parser = argparse.ArgumentParser(
        description="Basic Verilog Compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py input.v                    # Compile and print to stdout
  python main.py input.v -o output.txt      # Compile to file
  python main.py input.v -v                 # Verbose compilation
        """
    )
    
    parser.add_argument('input_file', 
                       help='Input Verilog file to compile')
    parser.add_argument('-o', '--output', 
                       help='Output file for compiled code')
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--version', 
                       action='version', 
                       version='Verilog Compiler v1.0')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Compile the file
    success = compile_verilog_file(
        args.input_file, 
        args.output, 
        args.verbose
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
