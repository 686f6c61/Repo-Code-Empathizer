"""
Go language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class GoAnalyzer(LanguageAnalyzer):
    """Analyzer for Go code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.go']
    
    def get_language_name(self) -> str:
        return 'Go'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a Go file"""
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
        structs = self._extract_structs(content)
        interfaces = self._extract_interfaces(content)
        variables = self._extract_variables(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(functions, structs, variables)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content, functions)
        metrics['modularidad']['funciones'] = len(functions)
        metrics['modularidad']['estructuras'] = len(structs) + len(interfaces)
        metrics['complejidad']['ciclomatica'] = self._calculate_cyclomatic_complexity(content)
        metrics['manejo_errores']['cobertura'] = self._calculate_error_handling(content, functions)
        metrics['pruebas']['cobertura'] = self._calculate_test_coverage(functions, file_path)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        return metrics
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function information from Go code"""
        functions = []
        
        # Regular functions
        func_pattern = r'func\s+(\w+)\s*\([^)]*\)(?:\s*\([^)]*\))?\s*(?:\{|$)'
        for match in re.finditer(func_pattern, content):
            functions.append({
                'name': match.group(1),
                'type': 'function',
                'start': match.start()
            })
        
        # Methods (functions with receivers)
        method_pattern = r'func\s*\([^)]+\)\s*(\w+)\s*\([^)]*\)(?:\s*\([^)]*\))?\s*\{'
        for match in re.finditer(method_pattern, content):
            functions.append({
                'name': match.group(1),
                'type': 'method',
                'start': match.start()
            })
        
        return functions
    
    def _extract_structs(self, content: str) -> List[Dict[str, Any]]:
        """Extract struct definitions"""
        structs = []
        struct_pattern = r'type\s+(\w+)\s+struct\s*\{'
        
        for match in re.finditer(struct_pattern, content):
            structs.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return structs
    
    def _extract_interfaces(self, content: str) -> List[Dict[str, Any]]:
        """Extract interface definitions"""
        interfaces = []
        interface_pattern = r'type\s+(\w+)\s+interface\s*\{'
        
        for match in re.finditer(interface_pattern, content):
            interfaces.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return interfaces
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extract variable names"""
        variables = []
        
        # var declarations
        var_pattern = r'var\s+(\w+)\s+'
        variables.extend(re.findall(var_pattern, content))
        
        # const declarations
        const_pattern = r'const\s+(\w+)\s+'
        variables.extend(re.findall(const_pattern, content))
        
        # Short variable declarations
        short_var_pattern = r'(\w+)\s*:='
        variables.extend(re.findall(short_var_pattern, content))
        
        return variables
    
    def _calculate_name_descriptiveness(self, functions: List[Dict], structs: List[Dict], variables: List[str]) -> float:
        """Calculate how descriptive names are"""
        all_names = [f['name'] for f in functions] + [s['name'] for s in structs] + variables
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # Go convention: avoid single letter names except for very short scopes
            # Good names are camelCase or PascalCase
            if len(name) > 2 and not name.isupper():
                if re.match(r'^[a-z][a-zA-Z0-9]*$', name) or re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                    descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str, functions: List[Dict]) -> float:
        """Calculate documentation coverage"""
        if not functions:
            return 0.0
        
        documented = 0
        for func in functions:
            # Look for godoc comment before function
            before_func = content[:func['start']]
            # Godoc comments should be directly before the function
            lines = before_func.split('\n')
            if lines and len(lines) >= 2:
                prev_line = lines[-2].strip()
                if prev_line.startswith('//') and func['name'] in prev_line:
                    documented += 1
        
        return documented / len(functions)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        complexity_patterns = [
            r'\bif\s+',
            r'\belse\s+if\s+',
            r'\bfor\s+',
            r'\bswitch\s+',
            r'\bcase\s+',
            r'\bselect\s+',
            r'&&',
            r'\|\|'
        ]
        
        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, content))
        
        # Count functions for averaging
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
    
    def _calculate_error_handling(self, content: str, functions: List[Dict]) -> float:
        """Calculate error handling coverage"""
        # In Go, good error handling means checking returned errors
        error_checks = len(re.findall(r'if\s+err\s*!=\s*nil', content))
        error_returns = len(re.findall(r'return\s+.*err', content))
        
        # Count functions that return error
        error_func_pattern = r'func[^{]+\)\s*(?:\([^)]*\))?\s*error'
        error_functions = len(re.findall(error_func_pattern, content))
        
        if not functions:
            return 0.0
        
        # Good coverage if most functions handle errors appropriately
        error_score = min(1.0, (error_checks + error_returns) / (len(functions) * 0.5))
        
        # Bonus for functions that return errors (idiomatic Go)
        if error_functions > 0:
            error_score = min(1.0, error_score + 0.2)
        
        return error_score
    
    def _calculate_test_coverage(self, functions: List[Dict], file_path: str) -> float:
        """Calculate test coverage"""
        # Check if this is a test file
        if file_path.endswith('_test.go'):
            return 1.0
        
        # Count test functions
        test_functions = [f for f in functions if f['name'].startswith('Test')]
        benchmark_functions = [f for f in functions if f['name'].startswith('Benchmark')]
        
        if not functions:
            return 0.0
        
        # Calculate coverage based on test density
        test_score = (len(test_functions) + len(benchmark_functions) * 0.5) / max(1, len(functions) * 0.3)
        return min(1.0, test_score)
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score"""
        dangerous_patterns = [
            r'unsafe\.',  # Unsafe package usage
            r'os\.system',  # Command execution
            r'exec\.Command',  # Command execution
            r'fmt\.Sprintf.*%v',  # Potential format string issues
        ]
        
        dangerous_count = 0
        for pattern in dangerous_patterns:
            dangerous_count += len(re.findall(pattern, content))
        
        # Check for good practices
        good_patterns = [
            r'strings\.TrimSpace',  # Input sanitization
            r'regexp\.MatchString',  # Input validation
            r'strconv\.',  # Type conversion (safer than casting)
            r'context\.',  # Context usage (timeout, cancellation)
            r'sync\.',  # Proper synchronization
        ]
        
        good_count = 0
        for pattern in good_patterns:
            good_count += len(re.findall(pattern, content))
        
        # Calculate score
        score = 1.0 - (dangerous_count * 0.2)
        score = max(0.0, score)
        
        # Bonus for good practices
        if good_count > 0:
            score = min(1.0, score + (good_count * 0.05))
        
        return score
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate Go style consistency"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        scores = []
        
        # Check gofmt style (basic approximation)
        # Tabs for indentation (Go standard)
        indented_lines = [line for line in lines if line and line[0] in ' \t']
        if indented_lines:
            tab_indented = sum(1 for line in indented_lines if line.startswith('\t'))
            scores.append(tab_indented / len(indented_lines))
        
        # Check naming conventions
        # Exported names should start with capital letter
        exported_pattern = r'^(func|type|var|const)\s+([A-Z]\w*)'
        unexported_pattern = r'^(func|type|var|const)\s+([a-z]\w*)'
        
        exported_matches = len(re.findall(exported_pattern, content, re.MULTILINE))
        unexported_matches = len(re.findall(unexported_pattern, content, re.MULTILINE))
        
        if exported_matches + unexported_matches > 0:
            # Both patterns are valid in Go, so we just check consistency
            scores.append(1.0)
        
        # Check comment style (should start with name)
        comment_pattern = r'//\s*(\w+)'
        comments = re.findall(comment_pattern, content)
        if comments:
            proper_comments = sum(1 for c in comments if c[0].isupper())
            scores.append(proper_comments / len(comments))
        
        return sum(scores) / len(scores) if scores else 0.5