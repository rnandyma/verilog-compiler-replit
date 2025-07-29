"""
Verilog Parser - Recursive descent parser for Verilog syntax
Builds an Abstract Syntax Tree (AST) from tokens.
"""

from typing import List, Optional, Union
from lexer import Token, TokenType
from ast_nodes import *
from symbol_table import SymbolTable
from errors import VerilogSyntaxError, VerilogSemanticError


class VerilogParser:
    """Recursive descent parser for Verilog language constructs."""
    
    def __init__(self):
        self.tokens = []
        self.current = 0
        self.symbol_table = SymbolTable()
    
    def parse(self, tokens: List[Token]) -> ModuleNode:
        """
        Parse tokens into an AST.
        
        Args:
            tokens (List[Token]): List of tokens from lexer
            
        Returns:
            ModuleNode: Root node of the AST
        """
        self.tokens = [t for t in tokens if t.type not in [TokenType.NEWLINE]]
        self.current = 0
        
        try:
            return self.parse_module()
        except IndexError:
            raise VerilogSyntaxError("Unexpected end of file", self.get_current_line())
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Peek at token without consuming it."""
        pos = self.current + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self) -> Optional[Token]:
        """Consume and return current token."""
        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            self.current += 1
            return token
        return None
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type or raise error."""
        token = self.peek()
        if not token or token.type != token_type:
            expected = token_type.value
            found = token.type.value if token else "EOF"
            raise VerilogSyntaxError(
                f"Expected {expected}, found {found}",
                self.get_current_line()
            )
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        token = self.peek()
        return token and token.type in token_types
    
    def get_current_line(self) -> int:
        """Get current line number for error reporting."""
        token = self.peek()
        return token.line if token else 1
    
    def parse_module(self) -> ModuleNode:
        """Parse module declaration."""
        self.expect(TokenType.MODULE)
        
        # Module name
        name_token = self.expect(TokenType.IDENTIFIER)
        module_name = name_token.value
        
        # Create new scope for module
        self.symbol_table.enter_scope(module_name)
        
        # Port list
        ports = []
        if self.match(TokenType.LPAREN):
            self.advance()  # consume '('
            ports = self.parse_port_list()
            self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.SEMICOLON)
        
        # Module body
        items = []
        while not self.match(TokenType.ENDMODULE):
            if self.match(TokenType.EOF):
                raise VerilogSyntaxError("Expected 'endmodule'", self.get_current_line())
            
            item = self.parse_module_item()
            if item:
                items.append(item)
        
        self.expect(TokenType.ENDMODULE)
        
        # Exit module scope
        self.symbol_table.exit_scope()
        
        return ModuleNode(module_name, ports, items)
    
    def parse_port_list(self) -> List[PortNode]:
        """Parse module port list."""
        ports = []
        
        if not self.match(TokenType.RPAREN):
            ports.append(self.parse_port())
            
            while self.match(TokenType.COMMA):
                self.advance()  # consume ','
                ports.append(self.parse_port())
        
        return ports
    
    def parse_port(self) -> PortNode:
        """Parse a single port declaration."""
        # Port direction
        direction = None
        if self.match(TokenType.INPUT, TokenType.OUTPUT, TokenType.INOUT):
            direction_token = self.advance()
            direction = direction_token.value.lower()
        
        # Optional data type (reg/wire)
        data_type = None
        if self.match(TokenType.REG, TokenType.WIRE):
            data_type_token = self.advance()
            data_type = data_type_token.value.lower()
        
        # Optional bit range specification
        range_spec = None
        if self.match(TokenType.LBRACKET):
            range_spec = self.parse_range()
        
        # Port name
        name_token = self.expect(TokenType.IDENTIFIER)
        port_name = name_token.value
        
        # Only register port in symbol table if not already declared
        # This allows for module port_list followed by input/output declarations
        existing = self.symbol_table.lookup(port_name)
        if not existing:
            self.symbol_table.declare(port_name, 'port', direction)
        
        return PortNode(port_name, direction, range_spec)
    
    def parse_module_item(self) -> Optional[ASTNode]:
        """Parse a module item (declaration or statement)."""
        if self.match(TokenType.INPUT, TokenType.OUTPUT, TokenType.INOUT):
            return self.parse_port_declaration()
        elif self.match(TokenType.WIRE, TokenType.REG):
            return self.parse_net_declaration()
        elif self.match(TokenType.ASSIGN):
            return self.parse_assign_statement()
        elif self.match(TokenType.ALWAYS):
            return self.parse_always_block()
        elif self.match(TokenType.INITIAL):
            return self.parse_initial_statement()
        elif self.match(TokenType.IDENTIFIER):
            # Could be module instantiation
            return self.parse_module_instantiation()
        else:
            # Skip unknown tokens for now
            token = self.advance()
            if token and token.type != TokenType.EOF:
                print(f"Warning: Skipping unknown token '{token.value}' at line {token.line}")
            return None
    
    def parse_port_declaration(self) -> PortDeclarationNode:
        """Parse port declaration."""
        direction_token = self.advance()
        direction = direction_token.value.lower()
        
        # Optional range
        range_spec = None
        if self.match(TokenType.LBRACKET):
            range_spec = self.parse_range()
        
        # Port names
        names = []
        names.append(self.expect(TokenType.IDENTIFIER).value)
        
        while self.match(TokenType.COMMA):
            self.advance()  # consume ','
            names.append(self.expect(TokenType.IDENTIFIER).value)
        
        self.expect(TokenType.SEMICOLON)
        
        # Register in symbol table or update existing port declarations
        for name in names:
            existing = self.symbol_table.lookup(name)
            if not existing:
                self.symbol_table.declare(name, 'port', direction)
            else:
                # Update direction if port was declared without direction in port list
                if existing.data_type is None:
                    existing.data_type = direction
        
        return PortDeclarationNode(direction, names, range_spec)
    
    def parse_net_declaration(self) -> NetDeclarationNode:
        """Parse wire or reg declaration."""
        net_type_token = self.advance()
        net_type = net_type_token.value.lower()
        
        # Optional range
        range_spec = None
        if self.match(TokenType.LBRACKET):
            range_spec = self.parse_range()
        
        # Net names
        names = []
        names.append(self.expect(TokenType.IDENTIFIER).value)
        
        while self.match(TokenType.COMMA):
            self.advance()  # consume ','
            names.append(self.expect(TokenType.IDENTIFIER).value)
        
        self.expect(TokenType.SEMICOLON)
        
        # Register in symbol table
        for name in names:
            self.symbol_table.declare(name, net_type)
        
        return NetDeclarationNode(net_type, names, range_spec)
    
    def parse_range(self) -> RangeNode:
        """Parse bit range [msb:lsb]."""
        self.expect(TokenType.LBRACKET)
        
        msb = self.parse_expression()
        self.expect(TokenType.COLON)
        lsb = self.parse_expression()
        
        self.expect(TokenType.RBRACKET)
        
        return RangeNode(msb, lsb)
    
    def parse_assign_statement(self) -> AssignNode:
        """Parse assign statement."""
        self.expect(TokenType.ASSIGN)
        
        target = self.parse_expression()
        self.expect(TokenType.ASSIGN_OP)
        source = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        
        return AssignNode(target, source)
    
    def parse_always_block(self) -> AlwaysNode:
        """Parse always block."""
        self.expect(TokenType.ALWAYS)
        
        # Sensitivity list
        sensitivity_list = []
        if self.match(TokenType.AT):
            self.advance()  # consume '@'
            if self.match(TokenType.LPAREN):
                self.advance()  # consume '('
                sensitivity_list = self.parse_sensitivity_list()
                self.expect(TokenType.RPAREN)
        
        # Statement
        statement = self.parse_statement()
        
        return AlwaysNode(sensitivity_list, statement)
    
    def parse_initial_statement(self) -> 'InitialNode':
        """Parse initial statement."""
        self.expect(TokenType.INITIAL)
        statement = self.parse_statement()
        return InitialNode(statement)
    
    def parse_sensitivity_list(self) -> List[str]:
        """Parse sensitivity list."""
        signals = []
        
        if not self.match(TokenType.RPAREN):
            # Parse sensitivity items (posedge clk, negedge reset, etc.)
            signals.append(self.parse_sensitivity_item())
            
            while self.match(TokenType.SENS_OR):
                self.advance()  # consume 'or'
                signals.append(self.parse_sensitivity_item())
        
        return signals
    
    def parse_sensitivity_item(self) -> str:
        """Parse a single sensitivity item (posedge clk, negedge reset, or signal)."""
        item_parts = []
        
        # Check for edge specifiers
        if self.match(TokenType.POSEDGE, TokenType.NEGEDGE):
            edge = self.advance().value
            signal = self.expect(TokenType.IDENTIFIER).value
            return f"{edge} {signal}"
        else:
            # Simple signal name
            return self.expect(TokenType.IDENTIFIER).value
    
    def parse_statement(self) -> ASTNode:
        """Parse a statement."""
        if self.match(TokenType.BEGIN):
            return self.parse_block_statement()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.HASH):
            return self.parse_delay_statement()
        elif self.match(TokenType.FOREVER):
            return self.parse_forever_statement()
        elif self.match(TokenType.DOLLAR):
            return self.parse_system_task()
        else:
            # Assignment statement
            return self.parse_assignment_statement()
    
    def parse_block_statement(self) -> BlockNode:
        """Parse begin...end block."""
        self.expect(TokenType.BEGIN)
        
        statements = []
        while not self.match(TokenType.END):
            if self.match(TokenType.EOF):
                raise VerilogSyntaxError("Expected 'end'", self.get_current_line())
            statements.append(self.parse_statement())
        
        self.expect(TokenType.END)
        
        return BlockNode(statements)
    
    def parse_if_statement(self) -> IfNode:
        """Parse if statement."""
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        then_stmt = self.parse_statement()
        
        else_stmt = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_stmt = self.parse_statement()
        
        return IfNode(condition, then_stmt, else_stmt)
    
    def parse_assignment_statement(self) -> AssignmentNode:
        """Parse assignment statement."""
        target = self.parse_expression()
        
        # Determine assignment type
        if self.match(TokenType.ASSIGN_OP):
            op = self.advance().value
        elif self.match(TokenType.NON_BLOCKING):
            op = self.advance().value
        else:
            raise VerilogSyntaxError(
                "Expected assignment operator",
                self.get_current_line()
            )
        
        source = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        
        return AssignmentNode(target, source, op)
    
    def parse_delay_statement(self) -> 'DelayNode':
        """Parse delay statement like #20."""
        self.expect(TokenType.HASH)
        delay_value = self.expect(TokenType.NUMBER).value
        
        # Parse the statement that follows the delay
        statement = self.parse_statement()
        
        return DelayNode(delay_value, statement)
    
    def parse_forever_statement(self) -> 'ForeverNode':
        """Parse forever statement like 'forever #5 clk = ~clk;'."""
        self.expect(TokenType.FOREVER)
        
        # Parse the statement that follows forever
        statement = self.parse_statement()
        
        return ForeverNode(statement)
    
    def parse_system_task(self) -> 'SystemTaskNode':
        """Parse system task like $finish;, $monitor(...);"""
        # We already consumed the $ token in match()
        self.advance()  # consume the $ token
        task_name = '$' + self.expect(TokenType.IDENTIFIER).value
        
        # Check for arguments
        args = []
        if self.match(TokenType.LPAREN):
            self.advance()  # consume '('
            
            # Parse argument list if present
            if not self.match(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()  # consume ','
                    args.append(self.parse_expression())
            
            self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.SEMICOLON)
        return SystemTaskNode(task_name, args)
    
    def parse_expression(self) -> ASTNode:
        """Parse expression with operator precedence."""
        return self.parse_or_expression()
    
    def parse_or_expression(self) -> ASTNode:
        """Parse OR expression."""
        expr = self.parse_and_expression()
        
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.parse_and_expression()
            expr = BinaryOpNode(expr, op, right)
        
        return expr
    
    def parse_and_expression(self) -> ASTNode:
        """Parse AND expression."""
        expr = self.parse_xor_expression()
        
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.parse_xor_expression()
            expr = BinaryOpNode(expr, op, right)
        
        return expr
    
    def parse_xor_expression(self) -> ASTNode:
        """Parse XOR expression."""
        expr = self.parse_additive_expression()
        
        while self.match(TokenType.XOR):
            op = self.advance().value
            right = self.parse_additive_expression()
            expr = BinaryOpNode(expr, op, right)
        
        return expr
    
    def parse_additive_expression(self) -> ASTNode:
        """Parse addition and subtraction expressions."""
        expr = self.parse_multiplicative_expression()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative_expression()
            expr = BinaryOpNode(expr, op, right)
        
        return expr
    
    def parse_multiplicative_expression(self) -> ASTNode:
        """Parse multiplication, division, and modulo expressions."""
        expr = self.parse_unary_expression()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_unary_expression()
            expr = BinaryOpNode(expr, op, right)
        
        return expr
    
    def parse_unary_expression(self) -> ASTNode:
        """Parse unary expression."""
        if self.match(TokenType.NOT):
            op = self.advance().value
            expr = self.parse_primary_expression()
            return UnaryOpNode(op, expr)
        
        return self.parse_primary_expression()
    
    def parse_module_instantiation(self) -> ModuleInstantiationNode:
        """Parse module instantiation."""
        module_type = self.advance().value  # Module type name
        instance_name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.LPAREN)
        
        # Parse port connections
        connections = []
        if not self.match(TokenType.RPAREN):
            connections.append(self.parse_port_connection())
            
            while self.match(TokenType.COMMA):
                self.advance()  # consume ','
                connections.append(self.parse_port_connection())
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        
        return ModuleInstantiationNode(module_type, instance_name, connections)
    
    def parse_port_connection(self) -> PortConnectionNode:
        """Parse port connection like .port_name(signal_name)."""
        self.expect(TokenType.DOT)
        port_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        signal = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        return PortConnectionNode(port_name, signal)
    
    def parse_primary_expression(self) -> ASTNode:
        """Parse primary expression."""
        if self.match(TokenType.IDENTIFIER):
            identifier = IdentifierNode(self.advance().value)
            
            # Check for bit indexing [msb:lsb] or [index]
            if self.match(TokenType.LBRACKET):
                self.advance()  # consume '['
                
                # Parse first index/expression
                first_index = self.parse_expression()
                
                # Check if it's a range [msb:lsb] or single bit [index]
                if self.match(TokenType.COLON):
                    self.advance()  # consume ':'
                    second_index = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    return IndexRangeNode(identifier, first_index, second_index)
                else:
                    self.expect(TokenType.RBRACKET)
                    return IndexNode(identifier, first_index)
            
            return identifier
        elif self.match(TokenType.NUMBER):
            return NumberNode(self.advance().value)
        elif self.match(TokenType.STRING):
            return StringNode(self.advance().value)
        elif self.match(TokenType.BINARY, TokenType.HEX, TokenType.OCTAL):
            return NumberNode(self.advance().value)
        elif self.match(TokenType.DOLLAR):
            # System function in expression (like $time)
            self.advance()  # consume $
            func_name = '$' + self.expect(TokenType.IDENTIFIER).value
            return IdentifierNode(func_name)
        elif self.match(TokenType.LPAREN):
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        else:
            token = self.peek()
            raise VerilogSyntaxError(
                f"Unexpected token '{token.value if token else 'EOF'}'",
                self.get_current_line()
            )
