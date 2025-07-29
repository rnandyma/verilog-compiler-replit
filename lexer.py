"""
Verilog Lexer - Tokenizes Verilog source code
Handles lexical analysis using regular expressions.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Keywords
    MODULE = 'MODULE'
    ENDMODULE = 'ENDMODULE'
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    INOUT = 'INOUT'
    WIRE = 'WIRE'
    REG = 'REG'
    ASSIGN = 'ASSIGN'
    ALWAYS = 'ALWAYS'
    INITIAL = 'INITIAL'
    BEGIN = 'BEGIN'
    END = 'END'
    IF = 'IF'
    ELSE = 'ELSE'
    FOREVER = 'FOREVER'
    
    # Timing and sensitivity keywords
    POSEDGE = 'POSEDGE'
    NEGEDGE = 'NEGEDGE'
    SENS_OR = 'SENS_OR'  # 'or' in sensitivity lists
    
    # Operators
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    XOR = 'XOR'
    NAND = 'NAND'
    NOR = 'NOR'
    XNOR = 'XNOR'
    
    # Arithmetic operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    MODULO = 'MODULO'
    
    # Assignment operators
    ASSIGN_OP = 'ASSIGN_OP'  # =
    NON_BLOCKING = 'NON_BLOCKING'  # <=
    
    # Delimiters
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    SEMICOLON = 'SEMICOLON'
    COMMA = 'COMMA'
    DOT = 'DOT'
    COLON = 'COLON'
    AT = 'AT'
    HASH = 'HASH'
    DOLLAR = 'DOLLAR'
    
    # Literals and identifiers
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    BINARY = 'BINARY'
    HEX = 'HEX'
    OCTAL = 'OCTAL'
    STRING = 'STRING'
    
    # Special
    NEWLINE = 'NEWLINE'
    WHITESPACE = 'WHITESPACE'
    COMMENT = 'COMMENT'
    EOF = 'EOF'
    UNKNOWN = 'UNKNOWN'


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class VerilogLexer:
    """Lexical analyzer for Verilog source code."""
    
    def __init__(self):
        # Keywords mapping
        self.keywords = {
            'module': TokenType.MODULE,
            'endmodule': TokenType.ENDMODULE,
            'input': TokenType.INPUT,
            'output': TokenType.OUTPUT,
            'inout': TokenType.INOUT,
            'wire': TokenType.WIRE,
            'reg': TokenType.REG,
            'assign': TokenType.ASSIGN,
            'always': TokenType.ALWAYS,
            'initial': TokenType.INITIAL,
            'begin': TokenType.BEGIN,
            'end': TokenType.END,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'posedge': TokenType.POSEDGE,
            'negedge': TokenType.NEGEDGE,
            'or': TokenType.SENS_OR,
            'forever': TokenType.FOREVER,
        }
        
        # Token patterns (order matters for precedence)
        self.token_patterns = [
            # Preprocessor directives
            (r'`include\s+"[^"]*"', TokenType.COMMENT),  # Treat include as comment for now
            (r'`define\s+\w+.*$', TokenType.COMMENT),    # Treat define as comment
            (r'`[a-zA-Z_][a-zA-Z0-9_]*', TokenType.COMMENT), # Other preprocessor directives
            
            # Comments
            (r'//.*$', TokenType.COMMENT),
            (r'/\*.*?\*/', TokenType.COMMENT),
            
            # Numbers and strings
            (r"\d+'[bB][01_]+", TokenType.BINARY),
            (r"\d+'[hH][0-9a-fA-F_]+", TokenType.HEX),
            (r"\d+'[oO][0-7_]+", TokenType.OCTAL),
            (r'"[^"]*"', TokenType.STRING),  # String literals
            (r'\d+', TokenType.NUMBER),
            
            # Operators (two-character first)
            (r'<=', TokenType.NON_BLOCKING),
            
            # Single character operators and delimiters
            (r'=', TokenType.ASSIGN_OP),
            (r'&', TokenType.AND),
            (r'\|', TokenType.OR),
            (r'~', TokenType.NOT),
            (r'\^', TokenType.XOR),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'%', TokenType.MODULO),
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r'\[', TokenType.LBRACKET),
            (r'\]', TokenType.RBRACKET),
            (r';', TokenType.SEMICOLON),
            (r',', TokenType.COMMA),
            (r'\.', TokenType.DOT),
            (r':', TokenType.COLON),
            (r'@', TokenType.AT),
            (r'#', TokenType.HASH),
            (r'\$', TokenType.DOLLAR),
            
            # System tasks and functions (must come before identifiers)
            (r'\$[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            
            # Identifiers (must come after keywords)
            (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
            
            # Whitespace and newlines
            (r'\n', TokenType.NEWLINE),
            (r'[ \t]+', TokenType.WHITESPACE),
        ]
        
        # Compile patterns
        self.compiled_patterns = [
            (re.compile(pattern, re.MULTILINE), token_type)
            for pattern, token_type in self.token_patterns
        ]
    
    def tokenize(self, source_code: str) -> List[Token]:
        """
        Tokenize Verilog source code.
        
        Args:
            source_code (str): The Verilog source code to tokenize
            
        Returns:
            List[Token]: List of tokens found in the source code
        """
        tokens = []
        lines = source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            column = 1
            pos = 0
            
            while pos < len(line):
                match_found = False
                
                for pattern, token_type in self.compiled_patterns:
                    match = pattern.match(line, pos)
                    if match:
                        value = match.group(0)
                        
                        # Skip whitespace and comments in output
                        if token_type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                            # Check if identifier is actually a keyword
                            if token_type == TokenType.IDENTIFIER:
                                token_type = self.keywords.get(value.lower(), TokenType.IDENTIFIER)
                            
                            token = Token(token_type, value, line_num, column)
                            tokens.append(token)
                        
                        pos = match.end()
                        column += len(value)
                        match_found = True
                        break
                
                if not match_found:
                    # Unknown character
                    char = line[pos]
                    token = Token(TokenType.UNKNOWN, char, line_num, column)
                    tokens.append(token)
                    pos += 1
                    column += 1
        
        # Add EOF token
        final_line = len(lines)
        tokens.append(Token(TokenType.EOF, '', final_line, 1))
        
        return tokens
    
    def print_tokens(self, tokens: List[Token]):
        """Print tokens for debugging purposes."""
        print("Tokens:")
        print("-" * 60)
        for token in tokens:
            if token.type != TokenType.EOF:
                print(f"{token.line:3d}:{token.column:3d} {token.type.value:15s} '{token.value}'")
