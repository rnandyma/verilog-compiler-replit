#!/usr/bin/env python3
"""
Verilog Compiler Web Interface
A Flask web application for the Verilog compiler.
"""

from flask import Flask, render_template, request, jsonify
import os
import tempfile
import time
from datetime import datetime
from lexer import VerilogLexer
from parser import VerilogParser
from code_generator import VerilogCodeGenerator
from errors import VerilogCompilerError
from models import db, init_db, save_compilation_result, get_recent_compilations, get_project_stats, Project, CompilationHistory
from syntax_fixer import VerilogSyntaxFixer
from simulator import VerilogSimulator

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
else:
    print("Warning: DATABASE_URL not found, running without database support")
    
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'verilog-compiler-secret-key')

# Initialize database if available
if database_url:
    init_db(app)

@app.route('/')
def index():
    """Main page with compiler interface."""
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_verilog():
    """Compile Verilog code via API."""
    try:
        data = request.json
        verilog_code = data.get('code', '')
        auto_fix = data.get('auto_fix', False)  # Optional auto-fix flag
        project_id = data.get('project_id')  # Optional project ID
        
        print(f"Received compilation request: auto_fix={auto_fix}, code_length={len(verilog_code)}")
        
        if not verilog_code.strip():
            return jsonify({
                'success': False,
                'error': 'Please provide Verilog code to compile'
            })
        
        # Track compilation time
        start_time = time.time()
        
        # Try auto-fixing if requested or if initial compilation fails
        result = compile_verilog_code(verilog_code)
        
        # If compilation failed and auto-fix is enabled, try to fix the code
        if not result['success'] and auto_fix:
            print(f"Auto-fix requested for failed compilation: {result.get('error', 'Unknown error')}")
            try:
                fixer = VerilogSyntaxFixer()
                print(f"Original code being fixed:\n{repr(verilog_code)}")
                fixed_code, fixes_applied = fixer.fix_code(verilog_code)
                print(f"Auto-fix applied {len(fixes_applied)} fixes")
                if fixes_applied:
                    print("Fixes details:", [f"Line {f.line_number}: {f.description}" for f in fixes_applied])
                print(f"Fixed code:\n{repr(fixed_code)}")
                
                if fixes_applied:
                    # Try compiling the fixed code
                    fixed_result = compile_verilog_code(fixed_code)
                    
                    if fixed_result['success']:
                        # Auto-fix worked! Return the successful result with fix info
                        result = fixed_result
                        result['auto_fixed'] = True
                        result['fixed_code'] = fixed_code
                        result['fixes_applied'] = [
                            {
                                'line': fix.line_number,
                                'description': fix.description,
                                'original': fix.original_line,
                                'fixed': fix.fixed_line,
                                'type': fix.fix_type
                            }
                            for fix in fixes_applied
                        ]
                        result['fixes_summary'] = fixer.get_fixes_summary()
                    else:
                        # Auto-fix didn't resolve the issue
                        result['auto_fix_attempted'] = True
                        result['fixes_applied'] = [
                            {
                                'line': fix.line_number,
                                'description': fix.description,
                                'original': fix.original_line,
                                'fixed': fix.fixed_line,
                                'type': fix.fix_type
                            }
                            for fix in fixes_applied
                        ]
                        result['auto_fix_message'] = "Auto-fix attempted but compilation still failed"
            except Exception as fix_error:
                print(f"Auto-fix error: {fix_error}")
                result['auto_fix_error'] = str(fix_error)
        
        execution_time = time.time() - start_time
        
        # Save compilation result to database if database is available
        if database_url:
            try:
                compilation_record = save_compilation_result(
                    verilog_code, result, execution_time, project_id
                )
                result['compilation_id'] = compilation_record.id
            except Exception as db_error:
                print(f"Database error: {db_error}")
                # Continue without database functionality
        
        result['execution_time'] = execution_time
        # Don't override the success flag from compile_verilog_code
        
        return jsonify(result)
    
    except Exception as e:
        import traceback
        error_details = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_details)  # Log to console for debugging
        return jsonify({
            'success': False,
            'error': str(e),
            'debug_info': error_details
        })

def compile_verilog_code(source_code):
    """
    Compile Verilog source code and return results.
    
    Args:
        source_code (str): Verilog source code
        
    Returns:
        dict: Compilation results with tokens, AST, and generated code
    """
    try:
        # Lexical analysis
        lexer = VerilogLexer()
        tokens = lexer.tokenize(source_code)
        
        # Parsing
        parser = VerilogParser()
        ast = parser.parse(tokens)
        
        # Code generation
        code_generator = VerilogCodeGenerator()
        generated_code = code_generator.generate(ast)
        
        # Get IR data
        ir_data = code_generator.get_ir_data()
        
        # Format tokens for display
        token_list = []
        for token in tokens:
            if token.type.value != 'EOF':
                token_list.append({
                    'type': token.type.value,
                    'value': token.value,
                    'line': token.line,
                    'column': token.column
                })
        
        return {
            'tokens': token_list,
            'token_count': len(token_list),
            'generated_code': generated_code,
            'statistics': ir_data['statistics'],
            'ir_components': ir_data['components'],
            'success': True
        }
        
    except VerilogCompilerError as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': e.__class__.__name__,
            'line': getattr(e, 'line', 0),
            'column': getattr(e, 'column', 0),
            'tokens': [],
            'token_count': 0,
            'generated_code': '',
            'statistics': {},
            'ir_components': {}
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'error_type': 'UnexpectedError',
            'tokens': [],
            'token_count': 0,
            'generated_code': '',
            'statistics': {},
            'ir_components': {}
        }

@app.route('/examples')
def get_examples():
    """Get example Verilog files and directory structures."""
    examples = {}
    
    # Read example files
    example_dir = 'examples'
    if os.path.exists(example_dir):
        # Get individual files
        for filename in os.listdir(example_dir):
            if filename.endswith('.v'):
                filepath = os.path.join(example_dir, filename)
                with open(filepath, 'r') as f:
                    examples[filename] = f.read()
        
        # Get directory-based examples
        for item in os.listdir(example_dir):
            item_path = os.path.join(example_dir, item)
            if os.path.isdir(item_path):
                # Add directory marker
                examples[f"📁 {item}/"] = get_directory_structure(item_path)
    
    return jsonify(examples)

def get_directory_structure(dir_path):
    """Get the structure and content of a directory."""
    structure = {
        'type': 'directory',
        'files': {},
        'description': ''
    }
    
    # Check for README file
    readme_path = os.path.join(dir_path, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            structure['description'] = f.read()
    
    # Get all files in directory
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(('.v', '.sv', '.vh')):
                file_path = os.path.join(root, file)
                # Create relative path from the directory
                rel_path = os.path.relpath(file_path, dir_path)
                
                with open(file_path, 'r') as f:
                    structure['files'][rel_path] = f.read()
    
    return structure

@app.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects."""
    if not database_url:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        projects = Project.query.order_by(Project.updated_at.desc()).all()
        return jsonify([project.to_dict() for project in projects])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/projects', methods=['POST'])
def create_project():
    """Create a new project."""
    if not database_url:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        data = request.json
        project = Project(
            name=data.get('name', 'Untitled Project'),
            description=data.get('description', ''),
            verilog_code=data.get('verilog_code', ''),
            is_public=data.get('is_public', False)
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify(project.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project."""
    if not database_url:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify(project.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project."""
    if not database_url:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        project = Project.query.get_or_404(project_id)
        data = request.json
        
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        project.verilog_code = data.get('verilog_code', project.verilog_code)
        project.is_public = data.get('is_public', project.is_public)
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(project.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project."""
    if not database_url:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_compilation_history():
    """Get recent compilation history."""
    if not database_url:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        limit = request.args.get('limit', 20, type=int)
        compilations = get_recent_compilations(limit)
        return jsonify([comp.to_dict() for comp in compilations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Get compilation and project statistics."""
    if not database_url:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        stats = get_project_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Dashboard page with statistics and history."""
    return render_template('dashboard.html')

@app.route('/simulate', methods=['POST'])
def simulate_verilog():
    """Simulate Verilog code with automatic testbench detection."""
    try:
        data = request.get_json()
        code = data.get('code', '')
        uploaded_files = data.get('uploaded_files', [])
        
        if not code and not uploaded_files:
            return jsonify({
                'success': False,
                'error': 'No Verilog code provided'
            })
        
        # Debug: log received files
        print(f"Simulation request - code length: {len(code)}, uploaded files: {len(uploaded_files)}")
        for i, file_info in enumerate(uploaded_files):
            print(f"File {i}: {file_info.get('name', 'unnamed')} - has content: {bool(file_info.get('content'))}")
        
        # Combine all code sources
        all_code = code
        if uploaded_files:
            for file_info in uploaded_files:
                if file_info.get('content'):
                    all_code += f"\n\n// File: {file_info['name']}\n" + file_info['content']
                    print(f"Added file {file_info['name']} ({len(file_info['content'])} chars)")
        
        # Try to automatically detect module and testbench
        simulator = VerilogSimulator()
        
        # Debug: check for testbench presence
        has_testbench_keyword = 'module testbench' in all_code.lower() or 'module test' in all_code.lower()
        print(f"Testbench keyword found: {has_testbench_keyword}")
        print(f"Combined code length: {len(all_code)}")
        
        # Extract modules to see what we actually have
        modules = simulator.extract_modules(all_code)
        print(f"Extracted modules: {list(modules.keys())}")
        
        # Check for testbench modules (including cpu_testbench pattern)
        testbench_modules = [name for name in modules.keys() 
                           if 'testbench' in name.lower() or 'test' in name.lower()]
        has_testbench = len(testbench_modules) > 0
        print(f"Testbench modules found: {testbench_modules}")
        
        # Check if code contains testbench
        if has_testbench:
            # Code contains testbench, run simulation directly
            result = simulator.run_simulation_from_combined_code(all_code)
        else:
            # No testbench found, create a simple one
            return jsonify({
                'success': False,
                'error': f'No testbench found in the code. Modules found: {list(modules.keys())}. Looking for modules with "testbench" or "test" in their names.'
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/waveform')
def waveform_viewer():
    """Waveform viewer page."""
    return render_template('waveform.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)