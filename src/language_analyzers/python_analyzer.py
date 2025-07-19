"""
Analizador de código Python basado en AST.

Este módulo implementa el análisis específico para código Python,
utilizando el módulo ast para extraer métricas detalladas sobre
calidad del código, documentación, complejidad y mejores prácticas.

Classes:
    PythonAnalyzer: Analizador específico para archivos Python.
    PythonASTVisitor: Visitador AST para recolectar métricas.

Author: R. Benítez
Version: 2.0.0
License: MIT
"""
import ast
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class PythonAnalyzer(LanguageAnalyzer):
    """
    Analizador especializado para código Python.
    
    Implementa análisis basado en AST (Abstract Syntax Tree) para evaluar:
    - Descriptividad de nombres de variables y funciones
    - Cobertura de documentación (docstrings)
    - Modularidad y estructura del código
    - Complejidad ciclomática
    - Prácticas de manejo de errores
    - Cobertura de pruebas unitarias
    - Validaciones de seguridad
    - Consistencia de estilo (PEP 8)
    """
    
    def get_file_extensions(self) -> List[str]:
        return ['.py']
    
    def get_language_name(self) -> str:
        return 'Python'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a Python file using AST"""
        metrics = {
            'nombres': {},
            'documentacion': {},
            'modularidad': {},
            'complejidad': {},
            'manejo_errores': {},
            'pruebas': {},
            'seguridad': {},
            'consistencia_estilo': {}
        }
        
        try:
            tree = ast.parse(content)
            visitor = PythonASTVisitor()
            visitor.visit(tree)
            
            # Calcular métricas
            metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(visitor)
            metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(visitor)
            metrics['modularidad']['funciones'] = len(visitor.functions)
            metrics['modularidad']['clases'] = len(visitor.classes)
            metrics['complejidad']['ciclomatica'] = self._calculate_cyclomatic_complexity(visitor)
            metrics['manejo_errores']['cobertura'] = self._calculate_error_handling(visitor)
            metrics['pruebas']['cobertura'] = self._calculate_test_coverage(visitor)
            metrics['seguridad']['validacion'] = self._calculate_security_score(visitor)
            metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
            
        except SyntaxError:
            # Return empty metrics for files with syntax errors
            pass
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return metrics
    
    def _calculate_name_descriptiveness(self, visitor) -> float:
        """Calculate how descriptive variable and function names are"""
        all_names = visitor.variables + visitor.function_names + visitor.class_names
        if not all_names:
            return 0.0
            
        descriptive_count = 0
        for name in all_names:
            # Consider names descriptive if they're more than 3 chars and not single letters
            if len(name) > 3 and not (len(name) == 1 and name.isalpha()):
                descriptive_count += 1
                
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, visitor) -> float:
        """Calculate documentation coverage"""
        if not visitor.functions:
            return 0.0
            
        documented = sum(1 for f in visitor.functions if f.get('has_docstring'))
        return documented / len(visitor.functions)
    
    def _calculate_cyclomatic_complexity(self, visitor) -> float:
        """Calculate average cyclomatic complexity"""
        if not visitor.functions:
            return 1.0
            
        total_complexity = sum(f.get('complexity', 1) for f in visitor.functions)
        avg_complexity = total_complexity / len(visitor.functions)
        
        # Normalize to 0-1 scale (lower is better)
        # Complexity of 1-5 is good, 6-10 is moderate, >10 is high
        if avg_complexity <= 5:
            return 1.0
        elif avg_complexity <= 10:
            return 0.7
        else:
            return max(0.3, 1.0 - (avg_complexity - 10) * 0.05)
    
    def _calculate_error_handling(self, visitor) -> float:
        """Calculate error handling coverage"""
        if not visitor.functions:
            return 0.0
            
        with_error_handling = sum(1 for f in visitor.functions if f.get('has_error_handling'))
        return with_error_handling / len(visitor.functions)
    
    def _calculate_test_coverage(self, visitor) -> float:
        """Calculate test coverage based on test functions"""
        test_functions = [f for f in visitor.function_names if f.startswith('test_')]
        if not visitor.functions:
            return 0.0
            
        return min(1.0, len(test_functions) / max(1, len(visitor.functions) - len(test_functions)))
    
    def _calculate_security_score(self, visitor) -> float:
        """Calculate security score based on dangerous functions and validation"""
        dangerous_functions = ['eval', 'exec', 'compile', '__import__']
        
        # Check for dangerous function usage
        dangerous_count = sum(1 for call in visitor.function_calls if call in dangerous_functions)
        
        # Penalize for dangerous functions
        if dangerous_count > 0:
            return max(0.0, 1.0 - (dangerous_count * 0.2))
        
        return 1.0
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate style consistency"""
        lines = content.split('\n')
        if not lines:
            return 0.0
            
        # Check line length consistency
        long_lines = sum(1 for line in lines if len(line) > 80)
        line_length_score = 1.0 - (long_lines / len(lines))
        
        # Check indentation consistency (assuming 4 spaces)
        indented_lines = [line for line in lines if line and line[0] in ' \t']
        space_indent = sum(1 for line in indented_lines if line.startswith('    '))
        
        indent_score = space_indent / len(indented_lines) if indented_lines else 1.0
        
        return (line_length_score + indent_score) / 2


class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor to extract metrics from Python code"""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.variables = []
        self.function_names = []
        self.class_names = []
        self.function_calls = []
        self.current_function = None
        
    def visit_FunctionDef(self, node):
        func_info = {
            'name': node.name,
            'has_docstring': ast.get_docstring(node) is not None,
            'complexity': self._calculate_function_complexity(node),
            'has_error_handling': self._has_error_handling(node),
            'line_count': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
        }
        self.functions.append(func_info)
        self.function_names.append(node.name)
        
        old_function = self.current_function
        self.current_function = func_info
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
        
    def visit_ClassDef(self, node):
        self.classes.append({
            'name': node.name,
            'has_docstring': ast.get_docstring(node) is not None
        })
        self.class_names.append(node.name)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.variables.append(node.id)
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.function_calls.append(node.func.id)
        self.generic_visit(node)
        
    def _calculate_function_complexity(self, node):
        """Calculate cyclomatic complexity of a function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
        
    def _has_error_handling(self, node):
        """Check if function has error handling"""
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False