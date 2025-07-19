"""
PHP language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class PHPAnalyzer(LanguageAnalyzer):
    """Analyzer for PHP code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.php', '.php3', '.php4', '.php5', '.phtml']
    
    def get_language_name(self) -> str:
        return 'PHP'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a PHP file"""
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
        methods = self._extract_methods(content)
        variables = self._extract_variables(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(functions, classes, variables)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content, functions + methods)
        metrics['modularidad']['funciones'] = len(functions) + len(methods)
        metrics['modularidad']['clases'] = len(classes)
        metrics['complejidad']['ciclomatica'] = self._calculate_cyclomatic_complexity(content)
        metrics['manejo_errores']['cobertura'] = self._calculate_error_handling(content)
        metrics['pruebas']['cobertura'] = self._calculate_test_coverage(methods, classes, file_path)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        return metrics
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        # Regular functions
        func_pattern = r'function\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(func_pattern, content):
            # Make sure it's not inside a class (standalone function)
            before_match = content[:match.start()]
            if not re.search(r'class\s+\w+[^}]*$', before_match):
                functions.append({
                    'name': match.group(1),
                    'start': match.start()
                })
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        # Class definitions
        class_pattern = r'(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?'
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        # Interfaces
        interface_pattern = r'interface\s+(\w+)'
        for match in re.finditer(interface_pattern, content):
            classes.append({
                'name': match.group(1),
                'type': 'interface',
                'start': match.start()
            })
        
        # Traits
        trait_pattern = r'trait\s+(\w+)'
        for match in re.finditer(trait_pattern, content):
            classes.append({
                'name': match.group(1),
                'type': 'trait',
                'start': match.start()
            })
        
        return classes
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract class methods"""
        methods = []
        
        # Methods inside classes
        method_pattern = r'(?:public|private|protected|static|final|abstract)*\s*function\s+(\w+)\s*\([^)]*\)'
        
        # Find all class blocks
        class_blocks = re.finditer(r'class\s+\w+[^{]*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', content, re.DOTALL)
        
        for class_block in class_blocks:
            class_content = class_block.group(1)
            for match in re.finditer(method_pattern, class_content):
                methods.append({
                    'name': match.group(1),
                    'start': class_block.start() + match.start()
                })
        
        return methods
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extract variable names"""
        variables = []
        
        # PHP variables start with $
        var_pattern = r'\$(\w+)'
        variables = re.findall(var_pattern, content)
        
        # Remove common superglobals
        superglobals = ['_GET', '_POST', '_SESSION', '_COOKIE', '_FILES', '_SERVER', '_ENV', 'GLOBALS']
        variables = [v for v in variables if v not in superglobals]
        
        return list(set(variables))  # Remove duplicates
    
    def _calculate_name_descriptiveness(self, functions: List[Dict], classes: List[Dict], variables: List[str]) -> float:
        """Calculate how descriptive names are"""
        all_names = [f['name'] for f in functions] + [c['name'] for c in classes] + variables
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # PHP conventions: various styles acceptable
            if len(name) > 3:
                # Check for meaningful names
                if (re.match(r'^[a-z][a-zA-Z0-9]*$', name) or  # camelCase
                    re.match(r'^[A-Z][a-zA-Z0-9]*$', name) or  # PascalCase
                    re.match(r'^[a-z]+(_[a-z]+)*$', name)):    # snake_case
                    descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str, functions: List[Dict]) -> float:
        """Calculate PHPDoc coverage"""
        if not functions:
            return 0.0
        
        documented = 0
        for func in functions:
            # Look for PHPDoc comment before function
            before_func = content[:func['start']]
            # PHPDoc uses /** */
            if re.search(r'/\*\*[\s\S]*?\*/', before_func[-500:]):
                documented += 1
        
        return documented / len(functions)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        complexity_patterns = [
            r'\bif\s*\(',
            r'\belseif\s*\(',
            r'\belse\s+if\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bforeach\s*\(',
            r'\bdo\s*\{',
            r'\bswitch\s*\(',
            r'\bcase\s+',
            r'\bcatch\s*\(',
            r'\?\s*[^:]+:',  # Ternary operator
            r'&&',
            r'\|\|',
            r'\?\?'  # Null coalescing operator (PHP 7+)
        ]
        
        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, content))
        
        all_functions = self._extract_functions(content) + self._extract_methods(content)
        if all_functions:
            avg_complexity = complexity / len(all_functions)
            if avg_complexity <= 5:
                return 1.0
            elif avg_complexity <= 10:
                return 0.7
            else:
                return max(0.3, 1.0 - (avg_complexity - 10) * 0.05)
        
        return 0.5
    
    def _calculate_error_handling(self, content: str) -> float:
        """Calculate error handling coverage"""
        # PHP error handling patterns
        try_blocks = len(re.findall(r'\btry\s*\{', content))
        catch_blocks = len(re.findall(r'\bcatch\s*\([^)]*\)\s*\{', content))
        finally_blocks = len(re.findall(r'\bfinally\s*\{', content))
        
        # Error reporting functions
        error_functions = len(re.findall(r'(?:error_log|trigger_error|throw\s+new)', content))
        
        # Input validation
        validation_functions = len(re.findall(r'(?:filter_input|filter_var|isset|empty|is_\w+)\s*\(', content))
        
        error_indicators = try_blocks + error_functions + (validation_functions * 0.5)
        
        # Good if there's reasonable error handling
        if error_indicators > 0:
            score = min(1.0, error_indicators * 0.05)
        else:
            score = 0.2  # Base score
        
        # Penalty for @ error suppression
        error_suppression = content.count('@')
        if error_suppression > 0:
            score = max(0.0, score - error_suppression * 0.05)
        
        return score
    
    def _calculate_test_coverage(self, methods: List[Dict], classes: List[Dict], file_path: str) -> float:
        """Calculate test coverage"""
        # Check if this is a test file
        if any(pattern in file_path.lower() for pattern in ['test', 'spec']):
            return 1.0
        
        # Look for PHPUnit patterns
        test_patterns = [
            r'class\s+\w+\s+extends\s+.*TestCase',  # PHPUnit test class
            r'@test\b',  # @test annotation
            r'function\s+test\w+',  # test methods
            r'->assert',  # PHPUnit assertions
            r'->expect',  # PHPUnit expectations
            r'\$this->assertEquals',
            r'\$this->assertTrue',
            r'\$this->assertFalse',
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
            r'eval\s*\(',  # Code injection
            r'exec\s*\(',  # Command injection
            r'system\s*\(',  # Command injection
            r'shell_exec\s*\(',  # Command injection
            r'passthru\s*\(',  # Command injection
            r'\$_REQUEST',  # Mixed input source
            r'mysql_query\s*\(',  # Deprecated, SQL injection prone
            r'\.\s*\$_(?:GET|POST)',  # Direct concatenation of user input
            r'include\s+\$',  # Dynamic includes
            r'require\s+\$',  # Dynamic requires
        ]
        
        dangerous_count = 0
        for pattern in dangerous_patterns:
            dangerous_count += len(re.findall(pattern, content))
        
        # Check for security best practices
        security_patterns = [
            r'htmlspecialchars\s*\(',  # XSS prevention
            r'mysqli_real_escape_string\s*\(',  # SQL injection prevention
            r'password_hash\s*\(',  # Secure password hashing
            r'password_verify\s*\(',  # Secure password verification
            r'filter_input\s*\(',  # Input filtering
            r'filter_var\s*\(',  # Variable filtering
            r'prepared\s+statement',  # Prepared statements
            r'bindParam\s*\(',  # Parameter binding
            r'FILTER_SANITIZE',  # Sanitization filters
        ]
        
        security_count = 0
        for pattern in security_patterns:
            security_count += len(re.findall(pattern, content))
        
        # Calculate score
        score = 1.0 - (dangerous_count * 0.15)
        score = max(0.0, score)
        
        # Bonus for security practices
        if security_count > 0:
            score = min(1.0, score + (security_count * 0.05))
        
        return score
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate PHP style consistency"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        scores = []
        
        # Check PHP tag style
        short_tags = content.count('<?')
        long_tags = content.count('<?php')
        
        if short_tags > 0:
            # Long tags are preferred
            tag_consistency = long_tags / short_tags
            scores.append(min(1.0, tag_consistency))
        
        # Check brace style
        same_line_braces = len(re.findall(r'\)\s*\{', content))
        next_line_braces = len(re.findall(r'\)\s*\n\s*\{', content))
        total_braces = same_line_braces + next_line_braces
        
        if total_braces > 0:
            # PSR standards prefer same line for classes/methods, next line for control structures
            # But consistency is key
            brace_consistency = max(same_line_braces, next_line_braces) / total_braces
            scores.append(brace_consistency)
        
        # Check array syntax
        old_array = content.count('array(')
        new_array = content.count('[')  # Approximate, but good enough
        
        if old_array + new_array > 0:
            # Prefer new array syntax []
            array_consistency = new_array / (old_array + new_array)
            scores.append(array_consistency)
        
        # Check naming conventions
        # Count different patterns in variables
        camel_case_vars = len(re.findall(r'\$[a-z][a-zA-Z0-9]*', content))
        snake_case_vars = len(re.findall(r'\$[a-z]+(_[a-z]+)+', content))
        
        total_vars = camel_case_vars + snake_case_vars
        if total_vars > 0:
            # Either style is fine, consistency matters
            var_consistency = max(camel_case_vars, snake_case_vars) / total_vars
            scores.append(var_consistency)
        
        return sum(scores) / len(scores) if scores else 0.5