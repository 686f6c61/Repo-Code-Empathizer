"""
Swift language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class SwiftAnalyzer(LanguageAnalyzer):
    """Analyzer for Swift code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.swift']
    
    def get_language_name(self) -> str:
        return 'Swift'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a Swift file"""
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
        
        # Extract components
        functions = self._extract_functions(content)
        classes = self._extract_classes(content)
        structs = self._extract_structs(content)
        protocols = self._extract_protocols(content)
        variables = self._extract_variables(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(functions, classes, variables)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content, functions)
        metrics['modularidad']['funciones'] = len(functions)
        metrics['modularidad']['tipos'] = len(classes) + len(structs) + len(protocols)
        metrics['complejidad']['ciclomatica'] = self._calculate_cyclomatic_complexity(content)
        metrics['manejo_errores']['cobertura'] = self._calculate_error_handling(content)
        metrics['pruebas']['cobertura'] = self._calculate_test_coverage(functions, classes, file_path)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        return metrics
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        # Functions and methods
        func_pattern = r'(?:(?:public|private|internal|fileprivate|open)\s+)?(?:static\s+)?(?:override\s+)?func\s+(\w+)'
        for match in re.finditer(func_pattern, content):
            functions.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        # Computed properties (getter/setter)
        computed_pattern = r'var\s+(\w+):\s*\w+\s*\{'
        for match in re.finditer(computed_pattern, content):
            # Check if it has get/set
            after_match = content[match.end():match.end() + 100]
            if 'get' in after_match or 'set' in after_match:
                functions.append({
                    'name': match.group(1),
                    'type': 'computed_property',
                    'start': match.start()
                })
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        class_pattern = r'(?:(?:public|private|internal|fileprivate|open)\s+)?(?:final\s+)?class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return classes
    
    def _extract_structs(self, content: str) -> List[Dict[str, Any]]:
        """Extract struct definitions"""
        structs = []
        
        struct_pattern = r'(?:(?:public|private|internal|fileprivate)\s+)?struct\s+(\w+)'
        for match in re.finditer(struct_pattern, content):
            structs.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return structs
    
    def _extract_protocols(self, content: str) -> List[Dict[str, Any]]:
        """Extract protocol definitions"""
        protocols = []
        
        protocol_pattern = r'(?:(?:public|private|internal|fileprivate)\s+)?protocol\s+(\w+)'
        for match in re.finditer(protocol_pattern, content):
            protocols.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return protocols
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extract variable names"""
        variables = []
        
        # var and let declarations
        var_pattern = r'(?:var|let)\s+(\w+)'
        variables.extend(re.findall(var_pattern, content))
        
        return list(set(variables))
    
    def _calculate_name_descriptiveness(self, functions: List[Dict], classes: List[Dict], variables: List[str]) -> float:
        """Calculate how descriptive names are"""
        all_names = [f['name'] for f in functions] + [c['name'] for c in classes] + variables
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # Swift conventions: camelCase for functions/variables, PascalCase for types
            if len(name) > 2:
                if (re.match(r'^[a-z][a-zA-Z0-9]*$', name) or  # camelCase
                    re.match(r'^[A-Z][a-zA-Z0-9]*$', name)):    # PascalCase
                    # Avoid single letter or very generic names
                    if name not in ['i', 'j', 'k', 'x', 'y', 'z', 'tmp', 'temp', 'data']:
                        descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str, functions: List[Dict]) -> float:
        """Calculate documentation coverage"""
        if not functions:
            return 0.0
        
        documented = 0
        for func in functions:
            # Look for documentation comments before function
            before_func = content[:func['start']]
            # Swift uses /// for single line docs or /** */ for multi-line
            if (re.search(r'///.*\n', before_func[-200:]) or 
                re.search(r'/\*\*[\s\S]*?\*/', before_func[-500:])):
                documented += 1
        
        return documented / len(functions)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        complexity_patterns = [
            r'\bif\b',
            r'\belse\s+if\b',
            r'\bguard\b',  # Swift guard statement
            r'\bwhile\b',
            r'\bfor\b',
            r'\brepeat\b',
            r'\bswitch\b',
            r'\bcase\b',
            r'\bcatch\b',
            r'\?\s*[^:]+:',  # Ternary operator
            r'&&',
            r'\|\|',
            r'\?\?',  # Nil coalescing operator
        ]
        
        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, content))
        
        functions = self._extract_functions(content)
        if functions:
            avg_complexity = complexity / len(functions)
            if avg_complexity <= 5:
                return 1.0
            elif avg_complexity <= 10:
                return 0.7
            else:
                return max(0.3, 1.0 - (avg_complexity - 10) * 0.05)
        
        return 0.5
    
    def _calculate_error_handling(self, content: str) -> float:
        """Calculate error handling coverage"""
        # Swift error handling patterns
        do_blocks = len(re.findall(r'\bdo\s*\{', content))
        catch_blocks = len(re.findall(r'\bcatch\b', content))
        throws_funcs = len(re.findall(r'throws\s*->', content))
        try_statements = len(re.findall(r'\btry\b', content))
        
        # Guard statements (defensive programming)
        guard_statements = len(re.findall(r'\bguard\b', content))
        
        # Optional handling
        nil_coalescing = len(re.findall(r'\?\?', content))
        optional_binding = len(re.findall(r'if\s+let\s+\w+\s*=', content))
        
        error_indicators = (do_blocks + catch_blocks + throws_funcs + 
                           guard_statements * 0.5 + optional_binding * 0.3)
        
        # Good if there's reasonable error handling
        if error_indicators > 0:
            score = min(1.0, error_indicators * 0.05)
        else:
            score = 0.3  # Base score
        
        # Bonus for specific error handling
        if catch_blocks > 0:
            score = min(1.0, score + 0.1)
        
        # Penalty for force unwrapping
        force_unwrap = content.count('!')
        if force_unwrap > 5:  # Some ! is ok (e.g., in implicitly unwrapped optionals)
            score = max(0.0, score - (force_unwrap - 5) * 0.02)
        
        return score
    
    def _calculate_test_coverage(self, functions: List[Dict], classes: List[Dict], file_path: str) -> float:
        """Calculate test coverage"""
        # Check if this is a test file
        if any(pattern in file_path for pattern in ['Test', 'test', 'Spec', 'spec']):
            return 1.0
        
        # Look for XCTest patterns
        test_patterns = [
            r'import\s+XCTest',  # XCTest framework
            r'class\s+\w+\s*:\s*XCTestCase',  # Test class
            r'func\s+test\w+',  # Test methods
            r'XCTAssert',  # Assertions
            r'XCTFail',
            r'\.expect\(',  # Quick/Nimble
            r'describe\(',  # Quick/Nimble
            r'it\(',  # Quick/Nimble
        ]
        
        test_count = 0
        for pattern in test_patterns:
            test_count += len(re.findall(pattern, content))
        
        if test_count > 0:
            return min(1.0, test_count * 0.05)
        
        return 0.0
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score"""
        dangerous_patterns = [
            r'UnsafePointer',  # Unsafe memory access
            r'UnsafeMutablePointer',
            r'unsafeBitCast',  # Type casting bypass
            r'withUnsafe',  # Unsafe operations
            r'NSString\s*\(',  # Using NSString instead of String
            r'!\s*as\s+',  # Force casting
        ]
        
        dangerous_count = 0
        for pattern in dangerous_patterns:
            dangerous_count += len(re.findall(pattern, content))
        
        # Check for security best practices
        security_patterns = [
            r'private\s+(?:var|let|func)',  # Access control
            r'fileprivate\s+',  # Access control
            r'final\s+class',  # Prevent subclassing
            r'@escaping',  # Proper closure handling
            r'weak\s+var',  # Avoid retain cycles
            r'unowned\s+',  # Memory management
            r'guard\s+let',  # Safe unwrapping
            r'if\s+let',  # Safe unwrapping
        ]
        
        security_count = 0
        for pattern in security_patterns:
            security_count += len(re.findall(pattern, content))
        
        # Calculate score
        score = 1.0 - (dangerous_count * 0.1)
        score = max(0.0, score)
        
        # Bonus for security practices
        if security_count > 0:
            score = min(1.0, score + (security_count * 0.02))
        
        return score
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate Swift style consistency"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        scores = []
        
        # Check indentation (Swift typically uses 4 spaces or 2 spaces)
        indented_lines = [line for line in lines if line and line[0] == ' ']
        if indented_lines:
            four_space = sum(1 for line in indented_lines if line.startswith('    '))
            two_space = sum(1 for line in indented_lines if line.startswith('  ') and not line.startswith('    '))
            
            if four_space + two_space > 0:
                # Either is fine, consistency matters
                indent_consistency = max(four_space, two_space) / len(indented_lines)
                scores.append(indent_consistency)
        
        # Check brace style (Swift prefers same line)
        same_line_braces = len(re.findall(r'\)\s*\{', content))
        next_line_braces = len(re.findall(r'\)\s*\n\s*\{', content))
        total_braces = same_line_braces + next_line_braces
        
        if total_braces > 0:
            # Swift style guide prefers same line
            brace_consistency = same_line_braces / total_braces
            scores.append(brace_consistency)
        
        # Check optional syntax
        # Prefer ? over ! for optionals
        safe_optionals = content.count('?')
        force_unwrap = content.count('!')
        
        if safe_optionals + force_unwrap > 0:
            optional_safety = safe_optionals / (safe_optionals + force_unwrap)
            scores.append(optional_safety)
        
        # Check trailing closure syntax
        # Swift prefers trailing closures when the closure is the last parameter
        trailing_closures = len(re.findall(r'\)\s*\{', content))
        regular_closures = len(re.findall(r',\s*\{', content))
        
        if trailing_closures + regular_closures > 0:
            closure_consistency = trailing_closures / (trailing_closures + regular_closures)
            scores.append(closure_consistency)
        
        return sum(scores) / len(scores) if scores else 0.5