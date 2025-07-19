"""Tests for JavaScript language analyzer"""
import pytest
from src.language_analyzers.javascript_analyzer import JavaScriptAnalyzer


class TestJavaScriptAnalyzer:
    
    @pytest.fixture
    def analyzer(self):
        return JavaScriptAnalyzer()
    
    def test_file_extensions(self, analyzer):
        assert set(analyzer.get_file_extensions()) == {'.js', '.jsx', '.mjs'}
    
    def test_language_name(self, analyzer):
        assert analyzer.get_language_name() == 'JavaScript'
    
    def test_extract_functions(self, analyzer):
        code = '''
function regularFunction() {
    console.log("Regular function");
}

const arrowFunction = () => {
    console.log("Arrow function");
};

const asyncArrow = async (param) => {
    await doSomething();
};

class MyClass {
    methodOne() {
        return "method";
    }
    
    async methodTwo() {
        return await fetch('/api');
    }
}
'''
        functions = analyzer._extract_functions(code)
        function_names = [f['name'] for f in functions]
        
        assert 'regularFunction' in function_names
        assert 'arrowFunction' in function_names
        assert 'asyncArrow' in function_names
        assert 'methodOne' in function_names
        assert 'methodTwo' in function_names
    
    def test_extract_classes(self, analyzer):
        code = '''
class Animal {
    constructor(name) {
        this.name = name;
    }
}

class Dog extends Animal {
    bark() {
        console.log("Woof!");
    }
}
'''
        classes = analyzer._extract_classes(code)
        class_names = [c['name'] for c in classes]
        
        assert 'Animal' in class_names
        assert 'Dog' in class_names
    
    def test_extract_variables(self, analyzer):
        code = '''
const simpleVar = 42;
let anotherVar = "hello";
var oldStyleVar = true;

const { destructured, props } = obj;
const [first, second] = array;
'''
        variables = analyzer._extract_variables(code)
        
        assert 'simpleVar' in variables
        assert 'anotherVar' in variables
        assert 'oldStyleVar' in variables
        assert 'destructured' in variables
        assert 'props' in variables
        assert 'first' in variables
        assert 'second' in variables
    
    def test_jsdoc_coverage(self, analyzer):
        code = '''
/**
 * Calculate sum of two numbers
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 */
function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}
'''
        metrics = analyzer.analyze_file('test.js', code)
        
        assert metrics['documentacion']['cobertura'] == 0.5  # 1 of 2 functions documented
    
    def test_error_handling(self, analyzer):
        code = '''
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        return response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
}

function riskyOperation() {
    doSomething()
        .then(result => console.log(result))
        .catch(error => console.error(error));
}

function noErrorHandling() {
    return someOperation();
}
'''
        metrics = analyzer.analyze_file('test.js', code)
        
        assert metrics['manejo_errores']['cobertura'] > 0.5  # Good error handling
    
    def test_security_patterns(self, analyzer):
        dangerous_code = '''
function executeUserCode(userInput) {
    eval(userInput);
    document.body.innerHTML = userInput;
    new Function(userInput)();
    setTimeout(userInput, 1000);
}
'''
        safe_code = '''
function processUserInput(input) {
    if (typeof input !== 'string') {
        throw new Error('Invalid input');
    }
    const sanitized = input.trim().toLowerCase();
    if (!/^[a-z0-9]+$/.test(sanitized)) {
        return null;
    }
    return sanitized;
}
'''
        
        dangerous_metrics = analyzer.analyze_file('test.js', dangerous_code)
        safe_metrics = analyzer.analyze_file('test.js', safe_code)
        
        assert dangerous_metrics['seguridad']['validacion'] < 0.5
        assert safe_metrics['seguridad']['validacion'] > 0.8
    
    def test_test_detection(self, analyzer):
        code = '''
describe('Calculator', () => {
    it('should add numbers correctly', () => {
        expect(add(2, 3)).toBe(5);
    });
    
    test('subtraction works', () => {
        expect(subtract(5, 3)).toBe(2);
    });
});

function testManualCheck() {
    console.assert(multiply(2, 3) === 6);
}
'''
        metrics = analyzer.analyze_file('test.js', code)
        
        assert metrics['pruebas']['cobertura'] > 0  # Has test functions
    
    def test_style_consistency(self, analyzer):
        consistent_semicolons = '''
const a = 1;
const b = 2;
function foo() {
    return a + b;
}
'''
        inconsistent_semicolons = '''
const a = 1;
const b = 2
function foo() {
    return a + b;
}
const c = 3
'''
        
        consistent_metrics = analyzer.analyze_file('test.js', consistent_semicolons)
        inconsistent_metrics = analyzer.analyze_file('test.js', inconsistent_semicolons)
        
        assert consistent_metrics['consistencia_estilo']['consistencia'] > inconsistent_metrics['consistencia_estilo']['consistencia']
    
    def test_complexity_calculation(self, analyzer):
        simple_code = '''
function simple() {
    return 42;
}
'''
        complex_code = '''
function complex(a, b, c) {
    if (a > 0) {
        if (b > 0) {
            for (let i = 0; i < c; i++) {
                if (i % 2 === 0) {
                    console.log(i);
                } else if (i % 3 === 0) {
                    console.log(i * 2);
                }
            }
        }
    }
    return a && b || c ? a + b : c;
}
'''
        
        simple_metrics = analyzer.analyze_file('test.js', simple_code)
        complex_metrics = analyzer.analyze_file('test.js', complex_code)
        
        assert simple_metrics['complejidad']['ciclomatica'] > complex_metrics['complejidad']['ciclomatica']