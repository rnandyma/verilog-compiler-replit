"""
Error Classes - Custom exception classes for Verilog compiler
Provides structured error reporting with line numbers and context.
"""


class VerilogCompilerError(Exception):
    """Base class for all Verilog compiler errors."""
    
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        """Format error message with location information."""
        if self.line > 0:
            if self.column > 0:
                return f"Line {self.line}, Column {self.column}: {self.message}"
            else:
                return f"Line {self.line}: {self.message}"
        return self.message


class VerilogLexicalError(VerilogCompilerError):
    """Error during lexical analysis (tokenization)."""
    
    def __init__(self, message: str, line: int = 0, column: int = 0, char: str = ""):
        self.char = char
        if char:
            message = f"{message}: '{char}'"
        super().__init__(message, line, column)


class VerilogSyntaxError(VerilogCompilerError):
    """Error during syntax analysis (parsing)."""
    
    def __init__(self, message: str, line: int = 0, column: int = 0, token: str = ""):
        self.token = token
        if token:
            message = f"{message}, got '{token}'"
        super().__init__(message, line, column)


class VerilogSemanticError(VerilogCompilerError):
    """Error during semantic analysis."""
    
    def __init__(self, message: str, line: int = 0, column: int = 0, identifier: str = ""):
        self.identifier = identifier
        if identifier:
            message = f"{message} (identifier: '{identifier}')"
        super().__init__(message, line, column)


class VerilogCodeGenerationError(VerilogCompilerError):
    """Error during code generation."""
    
    def __init__(self, message: str, line: int = 0, column: int = 0, node_type: str = ""):
        self.node_type = node_type
        if node_type:
            message = f"{message} (node type: {node_type})"
        super().__init__(message, line, column)


class VerilogFileError(VerilogCompilerError):
    """Error related to file I/O operations."""
    
    def __init__(self, message: str, filename: str = ""):
        self.filename = filename
        if filename:
            message = f"{message}: {filename}"
        super().__init__(message)


def format_error_context(source_lines: list, line_num: int, column: int = 0, 
                        context_lines: int = 2) -> str:
    """
    Format error with source code context.
    
    Args:
        source_lines (list): List of source code lines
        line_num (int): Line number where error occurred (1-based)
        column (int): Column number where error occurred (1-based)
        context_lines (int): Number of context lines to show before/after
        
    Returns:
        str: Formatted error context
    """
    if not source_lines or line_num < 1:
        return ""
    
    # Convert to 0-based indexing
    error_line_idx = line_num - 1
    
    # Calculate context range
    start_idx = max(0, error_line_idx - context_lines)
    end_idx = min(len(source_lines), error_line_idx + context_lines + 1)
    
    # Format output
    output = []
    max_line_num_width = len(str(end_idx))
    
    for i in range(start_idx, end_idx):
        line_num_display = i + 1
        prefix = f"{line_num_display:>{max_line_num_width}}: "
        
        if i == error_line_idx:
            # Highlight the error line
            output.append(f"> {prefix}{source_lines[i]}")
            
            # Add column pointer if specified
            if column > 0:
                pointer_line = " " * (len(prefix) + 1) + " " * (column - 1) + "^"
                output.append(pointer_line)
        else:
            output.append(f"  {prefix}{source_lines[i]}")
    
    return "\n".join(output)


def create_detailed_error_report(error: VerilogCompilerError, 
                                source_code: str = "") -> str:
    """
    Create a detailed error report with source context.
    
    Args:
        error (VerilogCompilerError): The error to report
        source_code (str): Source code for context (optional)
        
    Returns:
        str: Detailed error report
    """
    report = []
    
    # Error header
    error_type = error.__class__.__name__
    report.append(f"ERROR: {error_type}")
    report.append(f"Message: {error.message}")
    
    if error.line > 0:
        report.append(f"Location: Line {error.line}", end="")
        if error.column > 0:
            report[-1] += f", Column {error.column}"
    
    # Add source context if available
    if source_code and error.line > 0:
        source_lines = source_code.split('\n')
        context = format_error_context(source_lines, error.line, error.column)
        if context:
            report.append("")
            report.append("Source Context:")
            report.append(context)
    
    # Add additional error-specific information
    if hasattr(error, 'token') and error.token:
        report.append(f"Token: '{error.token}'")
    
    if hasattr(error, 'char') and error.char:
        report.append(f"Character: '{error.char}'")
    
    if hasattr(error, 'identifier') and error.identifier:
        report.append(f"Identifier: '{error.identifier}'")
    
    if hasattr(error, 'filename') and error.filename:
        report.append(f"File: {error.filename}")
    
    return "\n".join(report)


class ErrorReporter:
    """Collects and reports compilation errors."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.source_code = ""
    
    def set_source_code(self, source_code: str):
        """Set source code for error context."""
        self.source_code = source_code
    
    def add_error(self, error: VerilogCompilerError):
        """Add an error to the collection."""
        self.errors.append(error)
    
    def add_warning(self, message: str, line: int = 0, column: int = 0):
        """Add a warning message."""
        warning = VerilogCompilerError(f"WARNING: {message}", line, column)
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if any errors have been reported."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if any warnings have been reported."""
        return len(self.warnings) > 0
    
    def get_error_count(self) -> int:
        """Get the number of errors."""
        return len(self.errors)
    
    def get_warning_count(self) -> int:
        """Get the number of warnings."""
        return len(self.warnings)
    
    def generate_report(self, detailed: bool = True) -> str:
        """
        Generate a comprehensive error report.
        
        Args:
            detailed (bool): Include source context in report
            
        Returns:
            str: Formatted error report
        """
        report = []
        
        # Summary
        error_count = self.get_error_count()
        warning_count = self.get_warning_count()
        
        if error_count == 0 and warning_count == 0:
            return "Compilation completed successfully with no errors or warnings."
        
        report.append("COMPILATION REPORT")
        report.append("=" * 50)
        report.append(f"Errors: {error_count}")
        report.append(f"Warnings: {warning_count}")
        report.append("")
        
        # Detailed error reports
        if detailed and self.errors:
            report.append("ERRORS:")
            report.append("-" * 30)
            for i, error in enumerate(self.errors, 1):
                report.append(f"Error {i}:")
                report.append(create_detailed_error_report(error, self.source_code))
                report.append("")
        
        # Warning reports
        if self.warnings:
            if detailed:
                report.append("WARNINGS:")
                report.append("-" * 30)
            for i, warning in enumerate(self.warnings, 1):
                if detailed:
                    report.append(f"Warning {i}: {warning.format_error()}")
                else:
                    report.append(warning.format_error())
        
        return "\n".join(report)
