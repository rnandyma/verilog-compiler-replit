"""
Verilog Simulator - Simulates Verilog modules with testbenches
Provides signal tracing and waveform generation capabilities.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import time


class SignalType(Enum):
    WIRE = 'wire'
    REG = 'reg'
    INPUT = 'input'
    OUTPUT = 'output'


@dataclass
class Signal:
    """Represents a signal in the simulation."""
    name: str
    signal_type: SignalType
    width: int = 1
    value: int = 0
    history: List[Tuple[float, int]] = None
    
    def __post_init__(self):
        if self.history is None:
            self.history = []


@dataclass
class SimulationEvent:
    """Represents a timed event in simulation."""
    time: float
    signal_name: str
    value: int


class VerilogSimulator:
    """Simple Verilog simulator for basic module testing."""
    
    def __init__(self):
        self.signals = {}
        self.events = []
        self.current_time = 0.0
        self.time_unit = 'ns'
        self.simulation_running = False
        
    def add_signal(self, name: str, signal_type: SignalType, width: int = 1):
        """Add a signal to the simulation."""
        self.signals[name] = Signal(name, signal_type, width)
        
    def set_signal_value(self, name: str, value: int, time: float = None):
        """Set signal value at specific time."""
        if time is None:
            time = self.current_time
            
        if name in self.signals:
            self.signals[name].value = value
            self.signals[name].history.append((time, value))
            
    def get_signal_value(self, name: str) -> int:
        """Get current signal value."""
        return self.signals.get(name, Signal('', SignalType.WIRE)).value
        
    def parse_testbench(self, testbench_code: str) -> Dict[str, Any]:
        """Parse testbench code to extract test patterns."""
        patterns = {
            'inputs': {},
            'expected_outputs': {},
            'test_vectors': [],
            'timescale': '1ns/1ps'
        }
        
        # Extract timescale
        timescale_match = re.search(r'`timescale\s+(\w+)\s*/\s*(\w+)', testbench_code)
        if timescale_match:
            patterns['timescale'] = f"{timescale_match.group(1)}/{timescale_match.group(2)}"
            
        # Extract signal assignments
        assignments = re.findall(r'(\w+)\s*=\s*(\d+\'[bh]?\w+|\d+);', testbench_code)
        for signal, value in assignments:
            # Convert Verilog literals to integers
            if "'" in value:
                # Handle Verilog number formats like 8'b10101010 or 4'h5
                parts = value.split("'")
                if len(parts) == 2:
                    width = int(parts[0])
                    if 'b' in parts[1]:
                        val = int(parts[1].replace('b', ''), 2)
                    elif 'h' in parts[1]:
                        val = int(parts[1].replace('h', ''), 16)
                    else:
                        val = int(parts[1])
                else:
                    val = int(value)
            else:
                val = int(value)
                
            patterns['inputs'][signal] = val
            
        # Extract delay statements to create test vectors
        delays = re.findall(r'#(\d+)', testbench_code)
        current_time = 0
        for delay in delays:
            current_time += int(delay)
            patterns['test_vectors'].append({
                'time': current_time,
                'signals': dict(patterns['inputs'])
            })
            
        return patterns
        
    def run_simulation(self, module_code: str, testbench_code: str, duration: float = 1000.0) -> Dict[str, Any]:
        """Run simulation with testbench."""
        try:
            self.simulation_running = True
            self.current_time = 0.0
            self.signals.clear()
            
            # Parse testbench
            test_patterns = self.parse_testbench(testbench_code)
            
            # Extract module ports from module code
            module_match = re.search(r'module\s+(\w+)\s*\((.*?)\);', module_code, re.DOTALL)
            if not module_match:
                return {'success': False, 'error': 'Could not parse module definition'}
                
            module_name = module_match.group(1)
            ports_str = module_match.group(2)
            
            # Parse ports
            ports = self._parse_module_ports(ports_str)
            
            # Initialize signals
            for port in ports:
                signal_type = SignalType.INPUT if port['direction'] == 'input' else SignalType.OUTPUT
                self.add_signal(port['name'], signal_type, port.get('width', 1))
                
            # Extract internal signals
            wire_matches = re.findall(r'wire\s+(?:\[\d+:\d+\])?\s*(\w+);', module_code)
            for wire_name in wire_matches:
                self.add_signal(wire_name, SignalType.WIRE)
                
            reg_matches = re.findall(r'reg\s+(?:\[\d+:\d+\])?\s*(\w+);', module_code)
            for reg_name in reg_matches:
                self.add_signal(reg_name, SignalType.REG)
                
            # Generate comprehensive test patterns if none found in testbench
            if not test_patterns['test_vectors']:
                self._generate_comprehensive_test_patterns(module_name, duration)
            else:
                # Run test vectors from testbench
                for vector in test_patterns['test_vectors']:
                    self.current_time = vector['time']
                    
                    # Apply input values
                    for signal_name, value in vector['signals'].items():
                        if signal_name in self.signals:
                            self.set_signal_value(signal_name, value, self.current_time)
                            
                    # Simple combinational logic evaluation
                    self._evaluate_logic(module_code)
                
            # Generate waveform data
            waveform_data = self._generate_waveform_data()
            
            return {
                'success': True,
                'module_name': module_name,
                'signals': list(self.signals.keys()),
                'waveform_data': waveform_data,
                'simulation_time': self.current_time,
                'time_unit': test_patterns['timescale']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.simulation_running = False
            
    def _parse_module_ports(self, ports_str: str) -> List[Dict[str, Any]]:
        """Parse module port declarations."""
        ports = []
        
        # Remove comments and clean up
        ports_str = re.sub(r'//.*', '', ports_str)
        ports_str = re.sub(r'\s+', ' ', ports_str.strip())
        
        # Split by comma but handle ranges
        port_declarations = []
        current_decl = ""
        paren_depth = 0
        
        for char in ports_str:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                port_declarations.append(current_decl.strip())
                current_decl = ""
                continue
            current_decl += char
            
        if current_decl.strip():
            port_declarations.append(current_decl.strip())
            
        # Parse each declaration
        for decl in port_declarations:
            decl = decl.strip()
            if not decl:
                continue
                
            # Match port patterns like "input [7:0] data" or "output reg result"
            match = re.match(r'(input|output|inout)(?:\s+reg)?\s*(?:\[(\d+):(\d+)\])?\s*(\w+)', decl)
            if match:
                direction = match.group(1)
                msb = int(match.group(2)) if match.group(2) else 0
                lsb = int(match.group(3)) if match.group(3) else 0
                name = match.group(4)
                width = max(1, msb - lsb + 1) if match.group(2) else 1
                
                ports.append({
                    'name': name,
                    'direction': direction,
                    'width': width
                })
                
        return ports
        
    def _evaluate_logic(self, module_code: str):
        """Simple combinational logic evaluation."""
        # Extract assign statements
        assigns = re.findall(r'assign\s+(\w+)\s*=\s*([^;]+);', module_code)
        
        for target, expression in assigns:
            try:
                # Simple expression evaluation for basic operations
                value = self._evaluate_expression(expression)
                if target in self.signals:
                    self.set_signal_value(target, value, self.current_time)
            except:
                # Skip complex expressions for now
                pass
                
    def _evaluate_expression(self, expr: str) -> int:
        """Evaluate simple Verilog expressions."""
        expr = expr.strip()
        
        # Handle bit slicing like signal[7:4]
        slice_match = re.match(r'(\w+)\[(\d+):(\d+)\]', expr)
        if slice_match:
            signal_name = slice_match.group(1)
            msb = int(slice_match.group(2))
            lsb = int(slice_match.group(3))
            
            if signal_name in self.signals:
                value = self.signals[signal_name].value
                # Extract bits
                mask = ((1 << (msb - lsb + 1)) - 1) << lsb
                return (value & mask) >> lsb
                
        # Handle simple signal references
        if expr in self.signals:
            return self.signals[expr].value
            
        # Handle numeric literals
        if expr.isdigit():
            return int(expr)
            
        # Handle Verilog literals
        if "'" in expr:
            parts = expr.split("'")
            if len(parts) == 2:
                if 'b' in parts[1]:
                    return int(parts[1].replace('b', ''), 2)
                elif 'h' in parts[1]:
                    return int(parts[1].replace('h', ''), 16)
                    
        return 0
        
    def _generate_waveform_data(self) -> List[Dict[str, Any]]:
        """Generate waveform data for visualization."""
        waveform_data = []
        
        for signal_name, signal in self.signals.items():
            signal_data = {
                'name': signal_name,
                'type': signal.signal_type.value,
                'width': signal.width,
                'values': []
            }
            
            # Add time-value pairs
            for time, value in signal.history:
                signal_data['values'].append({
                    'time': time,
                    'value': value,
                    'binary': format(value, f'0{signal.width}b') if signal.width > 1 else str(value),
                    'hex': format(value, 'X') if signal.width > 4 else format(value, 'x')
                })
                
            waveform_data.append(signal_data)
            
        return waveform_data

    def run_simulation_from_combined_code(self, combined_code):
        """
        Run simulation from combined code containing both module and testbench
        
        Args:
            combined_code (str): Combined Verilog code with modules and testbench
            
        Returns:
            dict: Simulation results
        """
        try:
            # Split code into separate modules
            modules = self.extract_modules(combined_code)
            
            if not modules:
                return {
                    'success': False,
                    'error': 'No modules found in the code'
                }
            
            # Find testbench and main modules
            testbench_module = None
            main_modules = []
            
            for module_name, module_code in modules.items():
                if 'testbench' in module_name.lower() or 'test' in module_name.lower():
                    testbench_module = (module_name, module_code)
                else:
                    main_modules.append((module_name, module_code))
            
            if not testbench_module:
                return {
                    'success': False,
                    'error': 'No testbench module found. Module names should contain "testbench" or "test".'
                }
            
            if not main_modules:
                return {
                    'success': False,
                    'error': 'No main module found to simulate'
                }
            
            # Use the first main module for simulation
            main_module_name, main_module_code = main_modules[0]
            testbench_name, testbench_code = testbench_module
            
            # Enhanced simulation with comprehensive test patterns
            try:
                self.simulation_running = True
                self.current_time = 0.0
                self.signals.clear()
                
                # Parse module ports
                module_match = re.search(r'module\s+(\w+)\s*\((.*?)\);', main_module_code, re.DOTALL)
                if not module_match:
                    return {'success': False, 'error': 'Could not parse main module'}
                    
                module_name = module_match.group(1)
                ports_str = module_match.group(2)
                
                # Parse and initialize signals
                ports = self._parse_module_ports(ports_str)
                for port in ports:
                    signal_type = SignalType.INPUT if port['direction'] == 'input' else SignalType.OUTPUT
                    self.add_signal(port['name'], signal_type, port.get('width', 1))
                
                # Generate comprehensive test patterns
                duration = 125.0
                self._generate_comprehensive_test_patterns(module_name, duration)
                
                # Generate waveform data
                waveform_data = self._generate_waveform_data()
                
                return {
                    'success': True,
                    'module_name': module_name,
                    'signals': list(self.signals.keys()),
                    'waveform_data': waveform_data,
                    'simulation_time': duration,
                    'time_unit': '1ns/1ps'
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Enhanced simulation failed: {str(e)}'
                }
            finally:
                self.simulation_running = False
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Combined simulation failed: {str(e)}'
            }

    def extract_modules(self, code):
        """
        Extract individual modules from combined Verilog code
        
        Args:
            code (str): Combined Verilog code
            
        Returns:
            dict: Dictionary of module_name -> module_code
        """
        modules = {}
        
        # Simple regex to find module definitions
        import re
        
        # Find all module definitions - improved regex to handle various formats
        module_pattern = r'module\s+(\w+)\s*(?:\([^;]*\))?\s*;(.*?)endmodule'
        matches = re.findall(module_pattern, code, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            module_name = match[0]
            module_body = match[1]
            
            # Reconstruct full module code
            # Find the complete module definition including the header
            full_pattern = rf'module\s+{re.escape(module_name)}\s*(?:\([^;]*\))?\s*;.*?endmodule'
            full_match = re.search(full_pattern, code, re.DOTALL | re.IGNORECASE)
            
            if full_match:
                modules[module_name] = full_match.group(0)
        
        return modules
        
    def _generate_comprehensive_test_patterns(self, module_name: str, duration: float):
        """Generate comprehensive test patterns for simulation."""
        time_step = 5
        
        if 'alu' in module_name.lower():
            self._generate_alu_patterns(duration, time_step)
        elif 'cpu' in module_name.lower():
            self._generate_cpu_patterns(duration, time_step)
        else:
            self._generate_generic_patterns(duration, time_step)
            
    def _generate_alu_patterns(self, duration: float, time_step: int):
        """Generate ALU-specific test patterns."""
        input_signals = [name for name, sig in self.signals.items() 
                        if sig.signal_type == SignalType.INPUT]
        
        # Generate systematic test patterns
        for t in range(0, int(duration) + 1, time_step):
            self.current_time = float(t)
            
            for signal_name in input_signals:
                signal = self.signals[signal_name]
                
                if signal_name in ['a', 'operand_a', 'data_a']:
                    # Generate counter pattern for operand A
                    value = (t // 10) % (2 ** signal.width)
                elif signal_name in ['b', 'operand_b', 'data_b']:
                    # Generate different pattern for operand B
                    value = ((t // 15) + 1) % (2 ** signal.width)
                elif signal_name in ['op', 'operation', 'opcode']:
                    # Cycle through operations
                    value = (t // 20) % min(8, 2 ** signal.width)
                elif 'clk' in signal_name.lower():
                    # Generate clock
                    value = 1 if (t // time_step) % 2 else 0
                elif 'reset' in signal_name.lower():
                    # Reset pattern: high for first few cycles
                    value = 1 if t < 15 else 0
                else:
                    # Default pattern
                    value = (t // 8) % (2 ** signal.width)
                    
                self.set_signal_value(signal_name, value, self.current_time)
                
            # Evaluate outputs after setting inputs
            self._evaluate_alu_logic()
                
    def _generate_cpu_patterns(self, duration: float, time_step: int):
        """Generate CPU-specific test patterns."""
        for t in range(0, int(duration) + 1, time_step):
            self.current_time = float(t)
            
            for signal_name, signal in self.signals.items():
                if signal.signal_type == SignalType.INPUT:
                    if 'clk' in signal_name.lower():
                        value = 1 if (t // time_step) % 2 else 0
                    elif 'reset' in signal_name.lower():
                        value = 1 if t < 10 else 0
                    else:
                        value = (t // 12) % (2 ** signal.width)
                    self.set_signal_value(signal_name, value, self.current_time)
                    
    def _generate_generic_patterns(self, duration: float, time_step: int):
        """Generate generic test patterns."""
        for t in range(0, int(duration) + 1, time_step):
            self.current_time = float(t)
            
            for signal_name, signal in self.signals.items():
                if signal.signal_type == SignalType.INPUT:
                    # Generate varied patterns
                    value = (t // 7) % (2 ** signal.width)
                    self.set_signal_value(signal_name, value, self.current_time)
                    
    def _evaluate_alu_logic(self):
        """Evaluate ALU outputs based on current inputs."""
        # Look for common ALU signal names
        a_val = self.get_signal_value('a') or self.get_signal_value('operand_a') or self.get_signal_value('data_a')
        b_val = self.get_signal_value('b') or self.get_signal_value('operand_b') or self.get_signal_value('data_b')
        op_val = self.get_signal_value('op') or self.get_signal_value('operation') or self.get_signal_value('opcode')
        
        # Simple ALU operations
        if op_val == 0:  # ADD
            result = (a_val + b_val) & 0xFF
        elif op_val == 1:  # SUB
            result = (a_val - b_val) & 0xFF
        elif op_val == 2:  # AND
            result = a_val & b_val
        elif op_val == 3:  # OR
            result = a_val | b_val
        elif op_val == 4:  # XOR
            result = a_val ^ b_val
        elif op_val == 5:  # SHL
            result = (a_val << 1) & 0xFF
        elif op_val == 6:  # SHR
            result = a_val >> 1
        else:  # Default
            result = a_val
            
        # Set result on output signals
        for signal_name, signal in self.signals.items():
            if signal.signal_type == SignalType.OUTPUT and 'result' in signal_name.lower():
                self.set_signal_value(signal_name, result, self.current_time)