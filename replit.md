# Verilog Compiler

## Overview

This is a comprehensive Verilog compiler implementation with a modern web interface and database integration. The system provides lexical analysis, parsing, and code generation capabilities for Verilog hardware description language code. It features a Flask web application with PostgreSQL database for storing compilation history, project management, and detailed analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The compiler follows a classic three-phase architecture:

1. **Lexical Analysis** - Tokenizes Verilog source code using regular expressions
2. **Syntax Analysis** - Builds an Abstract Syntax Tree (AST) using recursive descent parsing
3. **Code Generation** - Converts AST to intermediate representation or target code

The architecture implements the visitor pattern for AST traversal, uses a symbol table for semantic analysis, and provides structured error handling with location information.

## Key Components

### Frontend Components

- **Lexer (`lexer.py`)** - Tokenizes Verilog source code into meaningful tokens
  - Uses enum-based token types for all Verilog language constructs
  - Handles keywords, operators, identifiers, and delimiters
  - Provides position tracking for error reporting

- **Parser (`parser.py`)** - Recursive descent parser that builds AST from tokens
  - Implements parsing for modules, ports, declarations, and statements
  - Integrates with symbol table for semantic checking
  - Provides detailed syntax error reporting

### AST and Data Structures

- **AST Nodes (`ast_nodes.py`)** - Abstract syntax tree node definitions
  - Base `ASTNode` class with visitor pattern support
  - Specific nodes for modules, ports, declarations, and other Verilog constructs
  - Clean separation between different language elements

- **Symbol Table (`symbol_table.py`)** - Manages variable declarations and scopes
  - Hierarchical scope management for nested constructs
  - Symbol lookup with proper scoping rules
  - Type checking and redeclaration detection

### Backend Components

- **Code Generator (`code_generator.py`)** - Converts AST to intermediate representation
  - Implements visitor pattern for AST traversal
  - Generates statistics and analysis data
  - Produces structured intermediate representation

- **Verilog Simulator (`simulator.py`)** - Simulation engine for testbench execution
  - Testbench parsing and signal extraction
  - Simple combinational and sequential logic evaluation
  - Waveform data generation with time-value tracking
  - Support for clock generation and reset sequences
  - Integration with web interface for interactive simulation

### Support Systems

- **Error Handling (`errors.py`)** - Custom exception hierarchy
  - Structured error reporting with line/column information
  - Separate error types for lexical, syntax, and semantic errors
  - Context-aware error messages

- **Main Driver (`main.py`)** - Command-line interface and compilation pipeline
  - File I/O handling
  - Command-line argument processing
  - Integration of all compiler phases

### Web Application Components

- **Flask Web Server (`app.py`)** - HTTP API and web interface
  - RESTful API endpoints for compilation and project management
  - Real-time compilation with execution time tracking
  - Database integration with error handling
  - Static file serving for examples and templates

- **Database Models (`models.py`)** - Data persistence layer
  - **Project** - User projects with Verilog code and metadata
  - **CompilationHistory** - Detailed compilation records and results
  - **ModuleAnalysis** - In-depth analysis of compiled modules
  - **CompilationStats** - System-wide statistics and metrics

- **Web Templates** - Modern responsive UI
  - **index.html** - Main compiler interface with tabbed results and simulation modal
  - **dashboard.html** - Analytics dashboard with project overview
  - **waveform.html** - Professional waveform viewer with signal traces and timing analysis

## Data Flow

### Command-Line Mode
1. **Input Processing** - Source Verilog file is read from disk
2. **Tokenization** - Lexer converts source text into token stream
3. **Parsing** - Parser builds AST while populating symbol table
4. **Semantic Analysis** - Symbol table validates declarations and references
5. **Code Generation** - AST visitor generates intermediate representation
6. **Output** - Generated code or analysis results are written to output

### Web Application Mode
1. **HTTP Request** - User submits Verilog code via web interface
2. **Compilation Pipeline** - Same lexer → parser → code generator flow
3. **Database Storage** - Results saved to PostgreSQL with execution metrics
4. **Module Analysis** - Detailed statistics and complexity analysis generated
5. **JSON Response** - Compilation results returned to web interface
6. **Dashboard Updates** - System statistics updated in real-time

The compiler maintains error context throughout the pipeline, allowing for precise error reporting with file locations. All compilation attempts are logged to the database for historical analysis and performance monitoring.

## Recent Changes (July 29, 2025)

- **Database Integration Added** - PostgreSQL support with comprehensive data models
- **Web Dashboard Created** - Analytics interface showing compilation statistics and project history
- **Project Management** - Save and manage Verilog projects with metadata
- **Compilation Tracking** - Detailed logging of all compilation attempts with performance metrics
- **Module Analysis** - Automated complexity scoring and detailed code analysis
- **Responsive UI Updates** - Navigation between compiler and dashboard views
- **Simulation and Waveform Viewer Added** - Complete simulation environment with visual waveform display:
  - VerilogSimulator class for testbench-driven simulation
  - Testbench parsing with signal extraction and test vector generation
  - Waveform data generation with time-value pairs for all signals
  - Professional waveform viewer with zoom, signal traces, and timing analysis
  - Modal simulation interface integrated into main compiler web UI
  - Support for clock generation, reset sequences, and signal monitoring
- **Critical Compiler Fixes** - Fixed lexer and parser bugs causing false syntax errors:
  - Added arithmetic operators (+, -, *, /, %) to lexer with proper tokenization
  - Enhanced parser with arithmetic expression hierarchy and operator precedence
  - Fixed port declaration parsing to handle bit vector specifications ([7:0])
  - Added support for 'output reg' and 'input reg' port declarations
  - Added bit indexing support for expressions like signal[7:4] and signal[index]
  - Implemented module instantiation parsing with port connections (.port(signal))
  - Fixed always block parsing with proper sensitivity list handling (posedge, negedge, or)
  - Resolved core parsing issues that were incorrectly flagged as syntax errors

## External Dependencies

### Backend Dependencies
- **Python Standard Library** - Uses `re`, `enum`, `dataclasses`, `pathlib`, `argparse`, `time`, `datetime`
- **Flask** - Web framework for the HTTP API and user interface
- **Flask-SQLAlchemy** - Database ORM for PostgreSQL integration
- **psycopg2-binary** - PostgreSQL database adapter

### Database
- **PostgreSQL** - Primary database for storing projects, compilation history, and analytics

The core compiler remains self-contained while the web interface adds modern functionality for project management and analysis.

## Deployment Strategy

The system offers multiple deployment modes:

- **Web Application** - Flask server running on port 5000 with full web interface
- **Command-Line Tool** - Direct execution via `main.py` for batch processing
- **Module Import** - Individual components can be imported and used separately
- **Database Integration** - PostgreSQL backend for persistent data storage

### Web Features
- **Interactive Compiler Interface** - Real-time compilation with syntax highlighting
- **Project Management** - Save, load, and manage Verilog projects
- **Compilation History** - Track all compilation attempts with detailed analytics
- **Dashboard** - System statistics and project overview
- **Example Library** - Built-in example Verilog modules for learning

The modular design allows for easy extension and modification of individual compiler phases without affecting others. Each component has clear interfaces and can be tested independently.

## Key Design Decisions

- **Recursive Descent Parsing** - Chosen for simplicity and readability over parser generators
- **Visitor Pattern** - Enables clean separation between AST structure and operations
- **Hierarchical Symbol Tables** - Supports proper Verilog scoping rules
- **Exception-Based Error Handling** - Provides structured error reporting with context
- **Minimal Dependencies** - Keeps the codebase focused and educational