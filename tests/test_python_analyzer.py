"""Tests for Python language analyzer"""
import pytest
from src.language_analyzers.python_analyzer import PythonAnalyzer


class TestPythonAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        return PythonAnalyzer()
    
    def test_file_extensions(self, analyzer):
        assert analyzer.get_file_extensions() == ['.py']
    
    def test_language_name(self, analyzer):
        assert analyzer.get_language_name() == 'Python'
    
    def test_analyze_simple_function(self, analyzer):
        code = '''
def hello_world():
    """Say hello to the world"""
    print("Hello, World!")
'''
        metrics = analyzer.analyze_file('test.py', code)
        
        assert metrics['modularidad']['funciones'] == 1
        assert metrics['documentacion']['cobertura'] == 1.0  # Has docstring
        assert metrics['nombres']['descriptividad'] > 0.5  # hello_world is descriptive
    
    def test_analyze_complex_function(self, analyzer):
        code = '''
def complex_function(a, b, c):
    if a > 0:
        if b > 0:
            for i in range(c):
                if i % 2 == 0:
                    print(i)
    return a + b + c
'''
        metrics = analyzer.analyze_file('test.py', code)
        
        assert metrics['complejidad']['ciclomatica'] < 0.8  # High complexity
        assert metrics['documentacion']['cobertura'] == 0.0  # No docstring
    
    def test_analyze_class(self, analyzer):
        code = '''
class MyClass:
    """A sample class"""
    
    def __init__(self):
        self.value = 0
    
    def get_value(self):
        """Get the value"""
        return self.value
'''
        metrics = analyzer.analyze_file('test.py', code)
        
        assert metrics['modularidad']['clases'] == 1
        assert metrics['modularidad']['funciones'] == 2  # __init__ and get_value
        assert metrics['documentacion']['cobertura'] == 0.5  # 1 of 2 functions has docstring
    
    def test_error_handling_detection(self, analyzer):
        code = '''
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

def unsafe_divide(a, b):
    return a / b
'''
        metrics = analyzer.analyze_file('test.py', code)
        
        assert metrics['manejo_errores']['cobertura'] == 0.5  # 1 of 2 functions has try-except
    
    def test_test_coverage_detection(self, analyzer):
        code = '''
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
'''
        metrics = analyzer.analyze_file('test.py', code)
        
        assert metrics['pruebas']['cobertura'] > 0  # Has test function
    
    def test_security_score(self, analyzer):
        dangerous_code = '''
def execute_code(code):
    eval(code)
    exec(code)
'''
        safe_code = '''
def process_data(data):
    return data.strip().lower()
'''
        
        dangerous_metrics = analyzer.analyze_file('test.py', dangerous_code)
        safe_metrics = analyzer.analyze_file('test.py', safe_code)
        
        assert dangerous_metrics['seguridad']['validacion'] < safe_metrics['seguridad']['validacion']
    
    def test_style_consistency(self, analyzer):
        good_style = '''
def function_one():
    x = 1
    y = 2
    return x + y

def function_two():
    a = 3
    b = 4
    return a * b
'''
        bad_style = '''
def f():
    x=1
    very_long_line_that_exceeds_eighty_characters_and_should_be_split_into_multiple_lines_for_better_readability = 123
    return x
'''
        
        good_metrics = analyzer.analyze_file('test.py', good_style)
        bad_metrics = analyzer.analyze_file('test.py', bad_style)
        
        assert good_metrics['consistencia_estilo']['consistencia'] > bad_metrics['consistencia_estilo']['consistencia']
    
    def test_syntax_error_handling(self, analyzer):
        invalid_code = '''
def broken_function(
    print("This is invalid syntax"
'''
        # Should not raise exception
        metrics = analyzer.analyze_file('test.py', invalid_code)
        assert metrics is not None