"""
Automatic syntax fixer for common Verilog compilation issues.
Provides intelligent fixes for basic syntax errors.
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SyntaxFix:
    """Represents a syntax fix that was applied."""
    line_number: int
    original_line: str
    fixed_line: str
    fix_type: str
    description: str

class VerilogSyntaxFixer:
    """Automatic fixer for common Verilog syntax errors."""
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_code(self, code: str) -> Tuple[str, List[SyntaxFix]]:
        """
        Automatically fix common syntax errors in Verilog code.
        
        Returns:
            Tuple of (fixed_code, list_of_fixes_applied)
        """
        self.fixes_applied = []
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_line = self._fix_line(line, i + 1)
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines), self.fixes_applied
    
    def _fix_line(self, line: str, line_number: int) -> str:
        """Fix syntax errors in a single line."""
        original_line = line
        
        # Debug: print each line being processed
        print(f"Processing line {line_number}: {repr(line.strip())}")
        
        # Fix 1: Missing semicolon after assign statements
        line = self._fix_missing_semicolon_assign(line, line_number, original_line)
        
        # Fix 2: Missing semicolon after variable declarations
        line = self._fix_missing_semicolon_declaration(line, line_number, original_line)
        
        # Fix 3: Mismatched or missing parentheses
        line = self._fix_parentheses(line, line_number, original_line)
        
        # Fix 4: Missing commas in port lists
        line = self._fix_missing_commas(line, line_number, original_line)
        
        # Fix 5: Incorrect module declaration syntax
        line = self._fix_module_declaration(line, line_number, original_line)
        
        # Fix 6: Missing endmodule
        line = self._fix_missing_endmodule(line, line_number, original_line)
        
        return line
    
    def _fix_missing_semicolon_assign(self, line: str, line_number: int, original_line: str) -> str:
        """Fix missing semicolons after assign statements."""
        # Pattern: assign statement without semicolon at end
        assign_pattern = r'^\s*assign\s+.+[^;]\s*$'
        
        stripped_line = line.strip()
        print(f"  Checking assign pattern for: {repr(stripped_line)}")
        
        if stripped_line.startswith('assign') and not stripped_line.endswith(';'):
            print(f"  Found assign without semicolon!")
            fixed_line = line.rstrip() + ';'
            self._record_fix(line_number, original_line, fixed_line, 
                           "missing_semicolon", "Added missing semicolon after assign statement")
            return fixed_line
        
        return line
    
    def _fix_missing_semicolon_declaration(self, line: str, line_number: int, original_line: str) -> str:
        """Fix missing semicolons after variable declarations."""
        # Pattern: input/output/wire/reg declarations without semicolon
        decl_pattern = r'^\s*(input|output|wire|reg|integer|parameter)\s+[^;]+(?<![;])\s*$'
        
        if re.match(decl_pattern, line.strip()):
            stripped = line.rstrip()
            if not stripped.endswith(';') and not stripped.endswith(','):
                fixed_line = stripped + ';'
                self._record_fix(line_number, original_line, fixed_line,
                               "missing_semicolon", "Added missing semicolon after declaration")
                return fixed_line
        
        return line
    
    def _fix_parentheses(self, line: str, line_number: int, original_line: str) -> str:
        """Fix mismatched parentheses."""
        # Count opening and closing parentheses
        open_parens = line.count('(')
        close_parens = line.count(')')
        
        # If we have more opening than closing, add closing parens
        if open_parens > close_parens:
            # Check if this looks like a module instantiation or function call
            if 'assign' in line or '=' in line:
                missing_parens = open_parens - close_parens
                fixed_line = line.rstrip() + ')' * missing_parens
                self._record_fix(line_number, original_line, fixed_line,
                               "missing_parentheses", f"Added {missing_parens} missing closing parenthesis")
                return fixed_line
        
        return line
    
    def _fix_missing_commas(self, line: str, line_number: int, original_line: str) -> str:
        """Fix missing commas in port lists."""
        # Pattern: port list items without commas
        # This is more complex and context-dependent, so we'll be conservative
        
        # Look for patterns like: input a b; (should be input a, b;)
        port_pattern = r'^\s*(input|output)\s+(\w+)\s+(\w+)\s*;'
        match = re.match(port_pattern, line.strip())
        
        if match:
            port_type, port1, port2 = match.groups()
            fixed_line = line.replace(f'{port1} {port2}', f'{port1}, {port2}')
            self._record_fix(line_number, original_line, fixed_line,
                           "missing_comma", "Added missing comma in port declaration")
            return fixed_line
        
        return line
    
    def _fix_module_declaration(self, line: str, line_number: int, original_line: str) -> str:
        """Fix incorrect module declaration syntax."""
        # Pattern: module name without parentheses for port list
        module_pattern = r'^\s*module\s+(\w+)\s*([^();]*);'
        match = re.match(module_pattern, line.strip())
        
        if match:
            module_name, port_part = match.groups()
            if port_part.strip() and not port_part.strip().startswith('('):
                # Add parentheses around port list
                fixed_line = f"module {module_name}({port_part.strip()});"
                self._record_fix(line_number, original_line, fixed_line,
                               "module_syntax", "Added parentheses around module port list")
                return line.replace(line.strip(), fixed_line)
        
        return line
    
    def _fix_missing_endmodule(self, line: str, line_number: int, original_line: str) -> str:
        """This would require multi-line analysis, so we'll skip for now."""
        return line
    
    def _record_fix(self, line_number: int, original: str, fixed: str, fix_type: str, description: str):
        """Record a fix that was applied."""
        self.fixes_applied.append(SyntaxFix(
            line_number=line_number,
            original_line=original.strip(),
            fixed_line=fixed.strip(),
            fix_type=fix_type,
            description=description
        ))
    
    def get_fixes_summary(self) -> str:
        """Get a summary of all fixes applied."""
        if not self.fixes_applied:
            return "No automatic fixes were applied."
        
        summary = f"Applied {len(self.fixes_applied)} automatic fixes:\n"
        for fix in self.fixes_applied:
            summary += f"• Line {fix.line_number}: {fix.description}\n"
            summary += f"  Before: {fix.original_line}\n"
            summary += f"  After:  {fix.fixed_line}\n\n"
        
        return summary.strip()