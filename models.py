"""
Database Models for Verilog Compiler Web App
Stores compilation history, user projects, and analysis data.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    """Model for storing user Verilog projects."""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    verilog_code = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    # Relationship to compilation history
    compilations = db.relationship('CompilationHistory', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'verilog_code': self.verilog_code,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_public': self.is_public,
            'compilation_count': len(self.compilations)
        }

class CompilationHistory(db.Model):
    """Model for storing compilation history and results."""
    __tablename__ = 'compilation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    verilog_code = db.Column(db.Text, nullable=False)
    compilation_success = db.Column(db.Boolean, nullable=False)
    generated_code = db.Column(db.Text)
    error_message = db.Column(db.Text)
    statistics = db.Column(db.JSON)  # Store compilation statistics as JSON
    tokens_data = db.Column(db.JSON)  # Store token information as JSON
    ir_components = db.Column(db.JSON)  # Store IR components as JSON
    compiled_at = db.Column(db.DateTime, default=datetime.utcnow)
    execution_time = db.Column(db.Float)  # Compilation time in seconds
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'verilog_code': self.verilog_code,
            'compilation_success': self.compilation_success,
            'generated_code': self.generated_code,
            'error_message': self.error_message,
            'statistics': self.statistics,
            'tokens_data': self.tokens_data,
            'ir_components': self.ir_components,
            'compiled_at': self.compiled_at.isoformat(),
            'execution_time': self.execution_time
        }

class ModuleAnalysis(db.Model):
    """Model for storing detailed analysis of Verilog modules."""
    __tablename__ = 'module_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    compilation_id = db.Column(db.Integer, db.ForeignKey('compilation_history.id'), nullable=False)
    module_name = db.Column(db.String(100), nullable=False)
    port_count = db.Column(db.Integer, default=0)
    wire_count = db.Column(db.Integer, default=0)
    reg_count = db.Column(db.Integer, default=0)
    assign_count = db.Column(db.Integer, default=0)
    always_block_count = db.Column(db.Integer, default=0)
    complexity_score = db.Column(db.Float)  # Simple complexity metric
    ports_data = db.Column(db.JSON)  # Detailed port information
    signals_data = db.Column(db.JSON)  # Signal information
    logic_data = db.Column(db.JSON)  # Logic block information
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    compilation = db.relationship('CompilationHistory', backref=db.backref('module_analyses', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'compilation_id': self.compilation_id,
            'module_name': self.module_name,
            'port_count': self.port_count,
            'wire_count': self.wire_count,
            'reg_count': self.reg_count,
            'assign_count': self.assign_count,
            'always_block_count': self.always_block_count,
            'complexity_score': self.complexity_score,
            'ports_data': self.ports_data,
            'signals_data': self.signals_data,
            'logic_data': self.logic_data,
            'created_at': self.created_at.isoformat()
        }

class CompilationStats(db.Model):
    """Model for tracking overall compilation statistics."""
    __tablename__ = 'compilation_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date())
    total_compilations = db.Column(db.Integer, default=0)
    successful_compilations = db.Column(db.Integer, default=0)
    failed_compilations = db.Column(db.Integer, default=0)
    avg_execution_time = db.Column(db.Float, default=0.0)
    most_common_errors = db.Column(db.JSON)  # Store common error types
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'total_compilations': self.total_compilations,
            'successful_compilations': self.successful_compilations,
            'failed_compilations': self.failed_compilations,
            'avg_execution_time': self.avg_execution_time,
            'most_common_errors': self.most_common_errors
        }

def calculate_complexity_score(statistics):
    """
    Calculate a simple complexity score based on module statistics.
    
    Args:
        statistics (dict): Compilation statistics
    
    Returns:
        float: Complexity score (higher = more complex)
    """
    if not statistics:
        return 0.0
    
    # Simple scoring algorithm
    score = 0.0
    score += statistics.get('ports', 0) * 1.0
    score += statistics.get('wires', 0) * 0.5
    score += statistics.get('regs', 0) * 0.7
    score += statistics.get('assigns', 0) * 1.2
    score += statistics.get('always_blocks', 0) * 2.0
    
    return round(score, 2)

def init_db(app):
    """Initialize database with the Flask app."""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def get_recent_compilations(limit=10):
    """Get recent compilation history."""
    return CompilationHistory.query.order_by(
        CompilationHistory.compiled_at.desc()
    ).limit(limit).all()

def get_project_stats():
    """Get overall project statistics."""
    total_projects = Project.query.count()
    public_projects = Project.query.filter_by(is_public=True).count()
    total_compilations = CompilationHistory.query.count()
    successful_compilations = CompilationHistory.query.filter_by(compilation_success=True).count()
    
    return {
        'total_projects': total_projects,
        'public_projects': public_projects,
        'total_compilations': total_compilations,
        'successful_compilations': successful_compilations,
        'success_rate': round((successful_compilations / total_compilations * 100) if total_compilations > 0 else 0, 1)
    }

def save_compilation_result(verilog_code, result, execution_time, project_id=None):
    """
    Save compilation result to database.
    
    Args:
        verilog_code (str): Original Verilog code
        result (dict): Compilation result
        execution_time (float): Time taken to compile
        project_id (int): Optional project ID
    
    Returns:
        CompilationHistory: Saved compilation record
    """
    compilation = CompilationHistory(
        project_id=project_id,
        verilog_code=verilog_code,
        compilation_success=result.get('success', False),
        generated_code=result.get('generated_code'),
        error_message=result.get('error'),
        statistics=result.get('statistics'),
        tokens_data=result.get('tokens', []),
        ir_components=result.get('ir_components'),
        execution_time=execution_time
    )
    
    db.session.add(compilation)
    db.session.commit()
    
    # Create module analysis if compilation was successful
    if result.get('success') and result.get('statistics'):
        create_module_analysis(compilation.id, result)
    
    return compilation

def create_module_analysis(compilation_id, result):
    """Create detailed module analysis from compilation result."""
    statistics = result.get('statistics', {})
    ir_components = result.get('ir_components', {})
    
    # Extract module name from IR components
    modules = ir_components.get('modules', [])
    if not modules:
        return
    
    module_data = modules[0]  # Assume single module for now
    module_name = module_data.get('name', 'unknown')
    
    analysis = ModuleAnalysis(
        compilation_id=compilation_id,
        module_name=module_name,
        port_count=statistics.get('ports', 0),
        wire_count=statistics.get('wires', 0),
        reg_count=statistics.get('regs', 0),
        assign_count=statistics.get('assigns', 0),
        always_block_count=statistics.get('always_blocks', 0),
        complexity_score=calculate_complexity_score(statistics),
        ports_data=module_data.get('ports', []),
        signals_data=ir_components.get('signals', []),
        logic_data={
            'combinational': ir_components.get('combinational_logic', []),
            'sequential': ir_components.get('sequential_logic', [])
        }
    )
    
    db.session.add(analysis)
    db.session.commit()
    
    return analysis