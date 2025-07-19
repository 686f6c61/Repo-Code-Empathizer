"""
JavaScript language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class JavaScriptAnalyzer(LanguageAnalyzer):
    """Analyzer for JavaScript code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.js', '.jsx', '.mjs']
    
    def get_language_name(self) -> str:
        return 'JavaScript'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a JavaScript file using regex patterns"""
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
        variables = self._extract_variables(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(functions, classes, variables)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content, functions)
        metrics['modularidad']['funciones'] = len(functions)
        metrics['modularidad']['clases'] = len(classes)
        metrics['complejidad']['ciclomatica'] = self._calculate_cyclomatic_complexity(content)
        metrics['manejo_errores']['cobertura'] = self._calculate_error_handling(content)
        metrics['pruebas']['cobertura'] = self._calculate_test_coverage(functions)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        return metrics
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function information from JavaScript code"""
        functions = []
        
        # Regular function declarations
        func_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{'
        for match in re.finditer(func_pattern, content):
            functions.append({
                'name': match.group(1),
                'type': 'function',
                'start': match.start()
            })
        
        # Arrow functions and method definitions
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=])\s*=>'
        for match in re.finditer(arrow_pattern, content):
            functions.append({
                'name': match.group(1),
                'type': 'arrow',
                'start': match.start()
            })
        
        # Class methods
        method_pattern = r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{'
        for match in re.finditer(method_pattern, content):
            name = match.group(1)
            if name not in ['if', 'for', 'while', 'switch', 'catch', 'function']:
                functions.append({
                    'name': name,
                    'type': 'method',
                    'start': match.start()
                })
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class information from JavaScript code"""
        classes = []
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{'
        
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return classes
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extract variable names from JavaScript code"""
        variables = []
        var_patterns = [
            r'(?:const|let|var)\s+(\w+)',
            r'(?:const|let|var)\s*\{([^}]+)\}',  # Destructuring
            r'(?:const|let|var)\s*\[([^\]]+)\]'   # Array destructuring
        ]
        
        for pattern in var_patterns:
            for match in re.finditer(pattern, content):
                if pattern == var_patterns[0]:
                    variables.append(match.group(1))
                else:
                    # Handle destructuring
                    names = match.group(1).split(',')
                    for name in names:
                        name = name.strip().split(':')[0].strip()
                        if name:
                            variables.append(name)
        
        return variables
    
    def _calculate_name_descriptiveness(self, functions: List[Dict], classes: List[Dict], variables: List[str]) -> float:
        """Calculate how descriptive names are"""
        all_names = [f['name'] for f in functions] + [c['name'] for c in classes] + variables
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # Consider names descriptive if they're more than 3 chars and follow conventions
            if len(name) > 3 and not (len(name) == 1 and name.isalpha()):
                # Check for camelCase or meaningful names
                if re.match(r'^[a-z][a-zA-Z0-9]*$', name) or re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                    descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str, functions: List[Dict]) -> float:
        """Calculate JSDoc coverage"""
        if not functions:
            return 0.0
        
        documented = 0
        for func in functions:
            # Look for JSDoc comment before function
            before_func = content[:func['start']]
            if re.search(r'/\*\*[\s\S]*?\*/', before_func[-200:]):  # Check last 200 chars
                documented += 1
        
        return documented / len(functions)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        # Count decision points
        complexity_patterns = [
            r'\bif\s*\(',
            r'\belse\s+if\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bcase\s+',
            r'\?\s*[^:]+:',  # Ternary operator
            r'&&',
            r'\|\|'
        ]
        
        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, content))
        
        # Normalize based on file size
        lines = content.count('\n') + 1
        complexity_per_line = complexity / lines
        
        # Convert to 0-1 scale
        if complexity_per_line < 0.1:
            return 1.0
        elif complexity_per_line < 0.2:
            return 0.7
        else:
            return max(0.3, 1.0 - complexity_per_line)
    
    def _calculate_error_handling(self, content: str) -> float:
        """Calculate error handling coverage"""
        try_blocks = len(re.findall(r'\btry\s*\{', content))
        catch_blocks = len(re.findall(r'\bcatch\s*\([^)]*\)\s*\{', content))
        promise_catches = len(re.findall(r'\.catch\s*\(', content))
        
        error_handlers = try_blocks + promise_catches
        functions = self._extract_functions(content)
        
        if not functions:
            return 0.0
        
        # Assume good coverage if there's at least 1 error handler per 5 functions
        expected_handlers = max(1, len(functions) // 5)
        return min(1.0, error_handlers / expected_handlers)
    
    def _calculate_test_coverage(self, functions: List[Dict]) -> float:
        """Calculate test coverage based on test functions"""
        if not functions:
            return 0.0
        
        test_functions = [f for f in functions if 
                         'test' in f['name'].lower() or 
                         'spec' in f['name'].lower() or
                         f['name'].startswith('it') or
                         f['name'] == 'describe']
        
        return min(1.0, len(test_functions) / max(1, len(functions) // 2))
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score"""
        dangerous_patterns = [
            r'\beval\s*\(',
            r'innerHTML\s*=',
            r'document\.write\s*\(',
            r'new\s+Function\s*\(',
            r'setTimeout\s*\([\'"][^\'")]+[\'"]\)',  # String setTimeout
            r'setInterval\s*\([\'"][^\'")]+[\'"]\)'  # String setInterval
        ]
        
        dangerous_count = 0
        for pattern in dangerous_patterns:
            dangerous_count += len(re.findall(pattern, content))
        
        # Check for input validation
        validation_patterns = [
            r'\.test\s*\(',  # Regex test
            r'\.match\s*\(',
            r'\.includes\s*\(',
            r'typeof\s+\w+\s*===',
            r'instanceof\s+',
            r'\.validate\s*\('
        ]
        
        validation_count = 0
        for pattern in validation_patterns:
            validation_count += len(re.findall(pattern, content))
        
        # Calculate score
        if dangerous_count > 0:
            score = max(0.0, 1.0 - (dangerous_count * 0.2))
        else:
            score = 1.0
        
        # Bonus for validation
        if validation_count > 0:
            score = min(1.0, score + (validation_count * 0.05))
        
        return score
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate style consistency"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        # Check semicolon consistency
        lines_with_code = [line.strip() for line in lines if line.strip() and not line.strip().startswith('//')]
        semicolon_lines = [line for line in lines_with_code if line.endswith(';')]
        
        semicolon_consistency = len(semicolon_lines) / len(lines_with_code) if lines_with_code else 0
        # Good if consistently using or not using semicolons
        semicolon_score = 1.0 if semicolon_consistency > 0.8 or semicolon_consistency < 0.2 else 0.5
        
        # Check quote consistency
        single_quotes = content.count("'")
        double_quotes = content.count('"')
        total_quotes = single_quotes + double_quotes
        
        quote_score = 1.0
        if total_quotes > 0:
            quote_ratio = single_quotes / total_quotes
            # Good if consistently using one type
            quote_score = 1.0 if quote_ratio > 0.8 or quote_ratio < 0.2 else 0.5
        
        # Check indentation (2 or 4 spaces)
        indented_lines = [line for line in lines if line and line[0] == ' ']
        two_space = sum(1 for line in indented_lines if line.startswith('  ') and not line.startswith('    '))
        four_space = sum(1 for line in indented_lines if line.startswith('    '))
        
        indent_score = 1.0
        if indented_lines:
            # Good if consistently using 2 or 4 spaces
            if two_space > four_space * 2:
                indent_score = two_space / len(indented_lines)
            else:
                indent_score = four_space / len(indented_lines)
        
        return (semicolon_score + quote_score + indent_score) / 3