"""
AST Node Classes - Abstract Syntax Tree node definitions
Represents different Verilog language constructs.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any


class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern."""
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


class ModuleNode(ASTNode):
    """AST node representing a Verilog module."""
    
    def __init__(self, name: str, ports: List['PortNode'], items: List[ASTNode]):
        self.name = name
        self.ports = ports
        self.items = items
    
    def accept(self, visitor):
        return visitor.visit_module(self)


class PortNode(ASTNode):
    """AST node representing a module port."""
    
    def __init__(self, name: str, direction: Optional[str] = None, range_spec: Optional['RangeNode'] = None):
        self.name = name
        self.direction = direction  # 'input', 'output', 'inout', or None
        self.range_spec = range_spec
    
    def accept(self, visitor):
        return visitor.visit_port(self)


class PortDeclarationNode(ASTNode):
    """AST node representing a port declaration."""
    
    def __init__(self, direction: str, names: List[str], range_spec: Optional['RangeNode'] = None):
        self.direction = direction
        self.names = names
        self.range_spec = range_spec
    
    def accept(self, visitor):
        return visitor.visit_port_declaration(self)


class NetDeclarationNode(ASTNode):
    """AST node representing a net declaration (wire/reg)."""
    
    def __init__(self, net_type: str, names: List[str], range_spec: Optional['RangeNode'] = None):
        self.net_type = net_type  # 'wire' or 'reg'
        self.names = names
        self.range_spec = range_spec
    
    def accept(self, visitor):
        return visitor.visit_net_declaration(self)


class RangeNode(ASTNode):
    """AST node representing a bit range [msb:lsb]."""
    
    def __init__(self, msb: ASTNode, lsb: ASTNode):
        self.msb = msb
        self.lsb = lsb
    
    def accept(self, visitor):
        return visitor.visit_range(self)


class AssignNode(ASTNode):
    """AST node representing an assign statement."""
    
    def __init__(self, target: ASTNode, source: ASTNode):
        self.target = target
        self.source = source
    
    def accept(self, visitor):
        return visitor.visit_assign(self)


class AlwaysNode(ASTNode):
    """AST node representing an always block."""
    
    def __init__(self, sensitivity_list: List[str], statement: ASTNode):
        self.sensitivity_list = sensitivity_list
        self.statement = statement
    
    def accept(self, visitor):
        return visitor.visit_always(self)


class InitialNode(ASTNode):
    """AST node representing an initial block."""
    
    def __init__(self, statement: ASTNode):
        self.statement = statement
    
    def accept(self, visitor):
        return visitor.visit_initial(self)


class DelayNode(ASTNode):
    """AST node representing a delay statement like #20."""
    
    def __init__(self, delay: str, statement: ASTNode):
        self.delay = delay
        self.statement = statement
    
    def accept(self, visitor):
        return visitor.visit_delay(self)


class ForeverNode(ASTNode):
    """AST node representing a forever statement."""
    
    def __init__(self, statement: ASTNode):
        self.statement = statement
    
    def accept(self, visitor):
        return visitor.visit_forever(self)


class SystemTaskNode(ASTNode):
    """AST node representing a system task like $finish; or $monitor(...)."""
    
    def __init__(self, task_name: str, args: List[ASTNode] = None):
        self.task_name = task_name
        self.args = args or []
    
    def accept(self, visitor):
        return visitor.visit_system_task(self)


class BlockNode(ASTNode):
    """AST node representing a begin...end block."""
    
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_block(self)


class IfNode(ASTNode):
    """AST node representing an if statement."""
    
    def __init__(self, condition: ASTNode, then_stmt: ASTNode, else_stmt: Optional[ASTNode] = None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt
    
    def accept(self, visitor):
        return visitor.visit_if(self)


class AssignmentNode(ASTNode):
    """AST node representing an assignment statement."""
    
    def __init__(self, target: ASTNode, source: ASTNode, operator: str):
        self.target = target
        self.source = source
        self.operator = operator  # '=' or '<='
    
    def accept(self, visitor):
        return visitor.visit_assignment(self)


class BinaryOpNode(ASTNode):
    """AST node representing a binary operation."""
    
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_op(self)


class IndexNode(ASTNode):
    """AST node representing single bit indexing like signal[index]."""
    
    def __init__(self, identifier: ASTNode, index: ASTNode):
        self.identifier = identifier
        self.index = index
    
    def accept(self, visitor):
        return visitor.visit_index(self)


class IndexRangeNode(ASTNode):
    """AST node representing bit range indexing like signal[msb:lsb]."""
    
    def __init__(self, identifier: ASTNode, msb: ASTNode, lsb: ASTNode):
        self.identifier = identifier
        self.msb = msb
        self.lsb = lsb
    
    def accept(self, visitor):
        return visitor.visit_index_range(self)


class ModuleInstantiationNode(ASTNode):
    """AST node representing module instantiation."""
    
    def __init__(self, module_type: str, instance_name: str, connections: List['PortConnectionNode']):
        self.module_type = module_type
        self.instance_name = instance_name
        self.connections = connections
    
    def accept(self, visitor):
        return visitor.visit_module_instantiation(self)


class PortConnectionNode(ASTNode):
    """AST node representing port connection in module instantiation."""
    
    def __init__(self, port_name: str, signal: ASTNode):
        self.port_name = port_name
        self.signal = signal
    
    def accept(self, visitor):
        return visitor.visit_port_connection(self)


class UnaryOpNode(ASTNode):
    """AST node representing a unary operation."""
    
    def __init__(self, operator: str, operand: ASTNode):
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)


class IdentifierNode(ASTNode):
    """AST node representing an identifier."""
    
    def __init__(self, name: str):
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)


class NumberNode(ASTNode):
    """AST node representing a numeric literal."""
    
    def __init__(self, value: str):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_number(self)


class StringNode(ASTNode):
    """AST node representing a string literal."""
    
    def __init__(self, value: str):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_string(self)


class ASTVisitor(ABC):
    """Base visitor class for traversing AST nodes."""
    
    @abstractmethod
    def visit_module(self, node: ModuleNode):
        pass
    
    @abstractmethod
    def visit_port(self, node: PortNode):
        pass
    
    @abstractmethod
    def visit_port_declaration(self, node: PortDeclarationNode):
        pass
    
    @abstractmethod
    def visit_net_declaration(self, node: NetDeclarationNode):
        pass
    
    @abstractmethod
    def visit_range(self, node: RangeNode):
        pass
    
    @abstractmethod
    def visit_assign(self, node: AssignNode):
        pass
    
    @abstractmethod
    def visit_always(self, node: AlwaysNode):
        pass
    
    @abstractmethod
    def visit_block(self, node: BlockNode):
        pass
    
    @abstractmethod
    def visit_if(self, node: IfNode):
        pass
    
    @abstractmethod
    def visit_assignment(self, node: AssignmentNode):
        pass
    
    @abstractmethod
    def visit_binary_op(self, node: BinaryOpNode):
        pass
    
    @abstractmethod
    def visit_unary_op(self, node: UnaryOpNode):
        pass
    
    @abstractmethod
    def visit_identifier(self, node: IdentifierNode):
        pass
    
    @abstractmethod
    def visit_number(self, node: NumberNode):
        pass


class ASTPrinter(ASTVisitor):
    """Visitor that prints the AST structure."""
    
    def __init__(self):
        self.indent_level = 0
    
    def _indent(self):
        return "  " * self.indent_level
    
    def visit_module(self, node: ModuleNode):
        result = f"{self._indent()}Module: {node.name}\n"
        self.indent_level += 1
        
        if node.ports:
            result += f"{self._indent()}Ports:\n"
            self.indent_level += 1
            for port in node.ports:
                result += port.accept(self)
            self.indent_level -= 1
        
        if node.items:
            result += f"{self._indent()}Body:\n"
            self.indent_level += 1
            for item in node.items:
                result += item.accept(self)
            self.indent_level -= 1
        
        self.indent_level -= 1
        return result
    
    def visit_port(self, node: PortNode):
        direction = f" ({node.direction})" if node.direction else ""
        return f"{self._indent()}- {node.name}{direction}\n"
    
    def visit_port_declaration(self, node: PortDeclarationNode):
        range_str = f" {node.range_spec.accept(self).strip()}" if node.range_spec else ""
        names = ", ".join(node.names)
        return f"{self._indent()}{node.direction.upper()}{range_str}: {names}\n"
    
    def visit_net_declaration(self, node: NetDeclarationNode):
        range_str = f" {node.range_spec.accept(self).strip()}" if node.range_spec else ""
        names = ", ".join(node.names)
        return f"{self._indent()}{node.net_type.upper()}{range_str}: {names}\n"
    
    def visit_range(self, node: RangeNode):
        msb = node.msb.accept(self).strip()
        lsb = node.lsb.accept(self).strip()
        return f"[{msb}:{lsb}]"
    
    def visit_assign(self, node: AssignNode):
        target = node.target.accept(self).strip()
        source = node.source.accept(self).strip()
        return f"{self._indent()}ASSIGN: {target} = {source}\n"
    
    def visit_always(self, node: AlwaysNode):
        sens_list = ", ".join(node.sensitivity_list) if node.sensitivity_list else "*"
        result = f"{self._indent()}ALWAYS @({sens_list}):\n"
        self.indent_level += 1
        result += node.statement.accept(self)
        self.indent_level -= 1
        return result
    
    def visit_block(self, node: BlockNode):
        result = f"{self._indent()}BEGIN\n"
        self.indent_level += 1
        for stmt in node.statements:
            result += stmt.accept(self)
        self.indent_level -= 1
        result += f"{self._indent()}END\n"
        return result
    
    def visit_if(self, node: IfNode):
        condition = node.condition.accept(self).strip()
        result = f"{self._indent()}IF ({condition}):\n"
        self.indent_level += 1
        result += node.then_stmt.accept(self)
        self.indent_level -= 1
        
        if node.else_stmt:
            result += f"{self._indent()}ELSE:\n"
            self.indent_level += 1
            result += node.else_stmt.accept(self)
            self.indent_level -= 1
        
        return result
    
    def visit_assignment(self, node: AssignmentNode):
        target = node.target.accept(self).strip()
        source = node.source.accept(self).strip()
        return f"{self._indent()}{target} {node.operator} {source}\n"
    
    def visit_binary_op(self, node: BinaryOpNode):
        left = node.left.accept(self).strip()
        right = node.right.accept(self).strip()
        return f"({left} {node.operator} {right})"
    
    def visit_unary_op(self, node: UnaryOpNode):
        operand = node.operand.accept(self).strip()
        return f"{node.operator}{operand}"
    
    def visit_identifier(self, node: IdentifierNode):
        return node.name
    
    def visit_number(self, node: NumberNode):
        return node.value
