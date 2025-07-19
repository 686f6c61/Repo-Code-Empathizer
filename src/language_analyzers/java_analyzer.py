"""
Java language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class JavaAnalyzer(LanguageAnalyzer):
    """Analyzer for Java code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.java']
    
    def get_language_name(self) -> str:
        return 'Java'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a Java file"""
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
        classes = self._extract_classes(content)
        methods = self._extract_methods(content)
        fields = self._extract_fields(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(classes, methods, fields)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content, methods)
        metrics['modularidad']['funciones'] = len(methods)
        metrics['modularidad']['clases'] = len(classes)
        metrics['complejidad']['ciclomatica'] = self._calculate_cyclomatic_complexity(content)
        metrics['manejo_errores']['cobertura'] = self._calculate_error_handling(content, methods)
        metrics['pruebas']['cobertura'] = self._calculate_test_coverage(methods, classes)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        return metrics
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class information from Java code"""
        classes = []
        # Match class declarations with various modifiers
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?\s*\{'
        
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        # Also match interfaces and enums
        interface_pattern = r'(?:public\s+|private\s+|protected\s+)?interface\s+(\w+)'
        for match in re.finditer(interface_pattern, content):
            classes.append({
                'name': match.group(1),
                'type': 'interface',
                'start': match.start()
            })
        
        enum_pattern = r'(?:public\s+|private\s+|protected\s+)?enum\s+(\w+)'
        for match in re.finditer(enum_pattern, content):
            classes.append({
                'name': match.group(1),
                'type': 'enum',
                'start': match.start()
            })
        
        return classes
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method information from Java code"""
        methods = []
        # Match method declarations
        method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?(?:abstract\s+)?(?:[\w<>\[\],\s]+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
        
        for match in re.finditer(method_pattern, content):
            method_name = match.group(1)
            # Filter out keywords that might be matched incorrectly
            if method_name not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'new', 'return']:
                methods.append({
                    'name': method_name,
                    'start': match.start()
                })
        
        # Also match constructors
        constructor_pattern = r'(?:public\s+|private\s+|protected\s+)?(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{'
        for match in re.finditer(constructor_pattern, content):
            name = match.group(1)
            # Check if it's likely a constructor (matches a class name)
            if any(c['name'] == name for c in self._extract_classes(content)):
                methods.append({
                    'name': name,
                    'type': 'constructor',
                    'start': match.start()
                })
        
        return methods
    
    def _extract_fields(self, content: str) -> List[str]:
        """Extract field names from Java code"""
        fields = []
        # Match field declarations
        field_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(?:volatile\s+)?(?:transient\s+)?[\w<>\[\],\s]+\s+(\w+)\s*[=;]'
        
        for match in re.finditer(field_pattern, content):
            field_name = match.group(1)
            # Filter out common type names and keywords
            if field_name not in ['String', 'int', 'boolean', 'double', 'float', 'long', 'short', 'byte', 'char', 'void', 'new', 'return', 'class', 'interface', 'enum']:
                fields.append(field_name)
        
        return fields
    
    def _calculate_name_descriptiveness(self, classes: List[Dict], methods: List[Dict], fields: List[str]) -> float:
        """Calculate how descriptive names are"""
        all_names = [c['name'] for c in classes] + [m['name'] for m in methods] + fields
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # Java conventions: camelCase for methods/fields, PascalCase for classes
            if len(name) > 3:
                # Check if follows Java naming conventions
                if re.match(r'^[a-z][a-zA-Z0-9]*$', name) or re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                    descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str, methods: List[Dict]) -> float:
        """Calculate Javadoc coverage"""
        if not methods:
            return 0.0
        
        documented = 0
        for method in methods:
            # Look for Javadoc comment before method
            before_method = content[:method['start']]
            if re.search(r'/\*\*[\s\S]*?\*/', before_method[-500:]):  # Check last 500 chars
                documented += 1
        
        return documented / len(methods)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        # Count decision points
        complexity_patterns = [
            r'\bif\s*\(',
            r'\belse\s+if\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bdo\s*\{',
            r'\bcase\s+',
            r'\bcatch\s*\(',
            r'\?\s*[^:]+:',  # Ternary operator
            r'&&',
            r'\|\|'
        ]
        
        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, content))
        
        # Normalize based on method count
        methods = self._extract_methods(content)
        if methods:
            avg_complexity = complexity / len(methods)
            # Convert to 0-1 scale
            if avg_complexity <= 5:
                return 1.0
            elif avg_complexity <= 10:
                return 0.7
            else:
                return max(0.3, 1.0 - (avg_complexity - 10) * 0.05)
        
        return 0.5
    
    def _calculate_error_handling(self, content: str, methods: List[Dict]) -> float:
        """Calculate error handling coverage"""
        try_blocks = len(re.findall(r'\btry\s*\{', content))
        catch_blocks = len(re.findall(r'\bcatch\s*\([^)]*\)\s*\{', content))
        throws_declarations = len(re.findall(r'\bthrows\s+\w+', content))
        
        error_indicators = try_blocks + throws_declarations
        
        if not methods:
            return 0.0
        
        # Good coverage if ~30% of methods have error handling
        expected_handlers = max(1, len(methods) * 0.3)
        return min(1.0, error_indicators / expected_handlers)
    
    def _calculate_test_coverage(self, methods: List[Dict], classes: List[Dict]) -> float:
        """Calculate test coverage based on test methods and classes"""
        test_methods = [m for m in methods if 
                       m['name'].startswith('test') or 
                       m['name'].endswith('Test') or
                       '@Test' in str(m)]
        
        test_classes = [c for c in classes if 
                       c['name'].endswith('Test') or 
                       c['name'].endswith('Tests') or
                       c['name'].startswith('Test')]
        
        if not methods:
            return 0.0
        
        # Consider both test methods and test classes
        test_score = (len(test_methods) + len(test_classes) * 5) / len(methods)
        return min(1.0, test_score)
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score"""
        # Check for dangerous patterns
        dangerous_patterns = [
            r'Runtime\.getRuntime\(\)\.exec',
            r'new\s+ProcessBuilder',
            r'\.printStackTrace\(\)',  # Should use logger instead
            r'System\.out\.print',      # Should use logger
            r'new\s+File\s*\([\'"][^\'")]+[\'"]\)',  # Hardcoded file paths
        ]
        
        dangerous_count = 0
        for pattern in dangerous_patterns:
            dangerous_count += len(re.findall(pattern, content))
        
        # Check for security best practices
        security_patterns = [
            r'\.equals\s*\(',  # Using equals instead of ==
            r'PreparedStatement',  # SQL injection prevention
            r'@Valid',  # Bean validation
            r'@NotNull',
            r'@Size',
            r'@Pattern',
            r'try\s*\(',  # Try-with-resources
            r'final\s+',  # Immutability
        ]
        
        security_count = 0
        for pattern in security_patterns:
            security_count += len(re.findall(pattern, content))
        
        # Calculate score
        score = 1.0 - (dangerous_count * 0.15)
        score = max(0.0, score)
        
        # Bonus for security practices
        if security_count > 0:
            score = min(1.0, score + (security_count * 0.02))
        
        return score
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate style consistency for Java conventions"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        scores = []
        
        # Check brace style (same line vs next line)
        same_line_braces = len(re.findall(r'\)\s*\{', content))
        next_line_braces = len(re.findall(r'\)\s*\n\s*\{', content))
        total_braces = same_line_braces + next_line_braces
        
        if total_braces > 0:
            brace_consistency = max(same_line_braces, next_line_braces) / total_braces
            scores.append(brace_consistency)
        
        # Check naming conventions
        # Classes should be PascalCase
        classes = self._extract_classes(content)
        if classes:
            pascal_classes = sum(1 for c in classes if c['name'][0].isupper())
            scores.append(pascal_classes / len(classes))
        
        # Methods and fields should be camelCase
        methods = self._extract_methods(content)
        fields = self._extract_fields(content)
        
        camel_items = 0
        total_items = len(methods) + len(fields)
        
        if total_items > 0:
            for m in methods:
                if m['name'][0].islower() or m['type'] == 'constructor':
                    camel_items += 1
            for f in fields:
                if f[0].islower() or f.isupper():  # camelCase or CONSTANTS
                    camel_items += 1
            scores.append(camel_items / total_items)
        
        # Check indentation (4 spaces is Java standard)
        indented_lines = [line for line in lines if line and line[0] == ' ']
        if indented_lines:
            four_space = sum(1 for line in indented_lines if line.startswith('    '))
            scores.append(four_space / len(indented_lines))
        
        return sum(scores) / len(scores) if scores else 0.0