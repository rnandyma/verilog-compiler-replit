"""
Symbol Table - Manages variable declarations and scopes
Tracks identifiers, their types, and scope information.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from errors import VerilogSemanticError


@dataclass
class Symbol:
    """Represents a symbol in the symbol table."""
    name: str
    symbol_type: str  # 'wire', 'reg', 'port', 'parameter', etc.
    data_type: Optional[str] = None  # Additional type information
    scope: Optional[str] = None
    line: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None


class Scope:
    """Represents a scope in the symbol table."""
    
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []
        
        if parent:
            parent.children.append(self)
    
    def declare(self, symbol: Symbol) -> bool:
        """
        Declare a symbol in this scope.
        
        Args:
            symbol (Symbol): Symbol to declare
            
        Returns:
            bool: True if declaration successful, False if already exists
        """
        if symbol.name in self.symbols:
            return False
        
        self.symbols[symbol.name] = symbol
        symbol.scope = self.name
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol in this scope.
        
        Args:
            name (str): Symbol name to look up
            
        Returns:
            Optional[Symbol]: Symbol if found, None otherwise
        """
        return self.symbols.get(name)
    
    def lookup_recursive(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol in this scope and parent scopes.
        
        Args:
            name (str): Symbol name to look up
            
        Returns:
            Optional[Symbol]: Symbol if found, None otherwise
        """
        symbol = self.lookup(name)
        if symbol:
            return symbol
        
        if self.parent:
            return self.parent.lookup_recursive(name)
        
        return None
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols in this scope."""
        return list(self.symbols.values())


class SymbolTable:
    """Symbol table for managing Verilog identifiers and scopes."""
    
    def __init__(self):
        # Global scope
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.scope_stack: List[Scope] = [self.global_scope]
    
    def enter_scope(self, name: str) -> Scope:
        """
        Enter a new scope.
        
        Args:
            name (str): Name of the new scope
            
        Returns:
            Scope: The new scope
        """
        new_scope = Scope(name, self.current_scope)
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)
        return new_scope
    
    def exit_scope(self) -> Optional[Scope]:
        """
        Exit the current scope.
        
        Returns:
            Optional[Scope]: The exited scope, None if at global scope
        """
        if len(self.scope_stack) <= 1:
            # Can't exit global scope
            return None
        
        exited_scope = self.scope_stack.pop()
        self.current_scope = self.scope_stack[-1]
        return exited_scope
    
    def declare(self, name: str, symbol_type: str, data_type: Optional[str] = None, 
                line: Optional[int] = None, **attributes) -> bool:
        """
        Declare a symbol in the current scope.
        
        Args:
            name (str): Symbol name
            symbol_type (str): Type of symbol ('wire', 'reg', 'port', etc.)
            data_type (Optional[str]): Additional type information
            line (Optional[int]): Line number where declared
            **attributes: Additional attributes
            
        Returns:
            bool: True if declaration successful
            
        Raises:
            VerilogSemanticError: If symbol already declared in current scope
        """
        symbol = Symbol(
            name=name,
            symbol_type=symbol_type,
            data_type=data_type,
            line=line,
            attributes=attributes or {}
        )
        
        if not self.current_scope.declare(symbol):
            existing = self.current_scope.lookup(name)
            raise VerilogSemanticError(
                f"Symbol '{name}' already declared in scope '{self.current_scope.name}' "
                f"(previous declaration at line {existing.line if existing else 'unknown'})",
                line or 0
            )
        
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol starting from current scope.
        
        Args:
            name (str): Symbol name to look up
            
        Returns:
            Optional[Symbol]: Symbol if found, None otherwise
        """
        return self.current_scope.lookup_recursive(name)
    
    def lookup_in_scope(self, name: str, scope_name: str) -> Optional[Symbol]:
        """
        Look up a symbol in a specific scope.
        
        Args:
            name (str): Symbol name to look up
            scope_name (str): Name of scope to search in
            
        Returns:
            Optional[Symbol]: Symbol if found, None otherwise
        """
        scope = self._find_scope(scope_name)
        if scope:
            return scope.lookup(name)
        return None
    
    def _find_scope(self, name: str) -> Optional[Scope]:
        """Find a scope by name (recursive search)."""
        def search_scope(scope: Scope) -> Optional[Scope]:
            if scope.name == name:
                return scope
            
            for child in scope.children:
                result = search_scope(child)
                if result:
                    return result
            
            return None
        
        return search_scope(self.global_scope)
    
    def get_current_scope_name(self) -> str:
        """Get the name of the current scope."""
        return self.current_scope.name
    
    def get_scope_symbols(self, scope_name: Optional[str] = None) -> List[Symbol]:
        """
        Get all symbols in a scope.
        
        Args:
            scope_name (Optional[str]): Scope name, current scope if None
            
        Returns:
            List[Symbol]: List of symbols in the scope
        """
        if scope_name is None:
            return self.current_scope.get_all_symbols()
        
        scope = self._find_scope(scope_name)
        if scope:
            return scope.get_all_symbols()
        
        return []
    
    def print_symbol_table(self) -> str:
        """Print the entire symbol table for debugging."""
        def print_scope(scope: Scope, indent: int = 0) -> str:
            result = "  " * indent + f"Scope: {scope.name}\n"
            
            for symbol in scope.get_all_symbols():
                attrs = ""
                if symbol.attributes:
                    attr_strs = [f"{k}={v}" for k, v in symbol.attributes.items()]
                    attrs = f" ({', '.join(attr_strs)})"
                
                data_type_str = f":{symbol.data_type}" if symbol.data_type else ""
                line_str = f" @{symbol.line}" if symbol.line else ""
                
                result += ("  " * (indent + 1) + 
                          f"- {symbol.name}: {symbol.symbol_type}{data_type_str}{attrs}{line_str}\n")
            
            for child in scope.children:
                result += print_scope(child, indent + 1)
            
            return result
        
        return print_scope(self.global_scope)
    
    def validate_references(self) -> List[str]:
        """
        Validate that all identifier references have corresponding declarations.
        
        Returns:
            List[str]: List of error messages for undefined references
        """
        # This is a placeholder for more sophisticated reference checking
        # In a full implementation, this would track identifier usage
        # and verify against declarations
        errors = []
        
        # For now, just return empty list
        # In practice, this would be called after parsing to validate
        # that all used identifiers are properly declared
        
        return errors
