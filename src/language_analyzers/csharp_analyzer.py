"""
C# language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class CSharpAnalyzer(LanguageAnalyzer):
    """Analyzer for C# code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.cs']
    
    def get_language_name(self) -> str:
        return 'C#'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a C# file"""
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
        properties = self._extract_properties(content)
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
        """Extract class information from C# code"""
        classes = []
        # Match various class declarations
        class_pattern = r'(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+|sealed\s+|abstract\s+|partial\s+)*class\s+(\w+)(?:\s*:\s*[\w\s,<>]+)?'
        
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'type': 'class',
                'start': match.start()
            })
        
        # Also match interfaces
        interface_pattern = r'(?:public\s+|private\s+|protected\s+|internal\s+)?interface\s+(\w+)'
        for match in re.finditer(interface_pattern, content):
            classes.append({
                'name': match.group(1),
                'type': 'interface',
                'start': match.start()
            })
        
        # Match structs
        struct_pattern = r'(?:public\s+|private\s+|protected\s+|internal\s+)?struct\s+(\w+)'
        for match in re.finditer(struct_pattern, content):
            classes.append({
                'name': match.group(1),
                'type': 'struct',
                'start': match.start()
            })
        
        return classes
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method information"""
        methods = []
        # Match method declarations
        method_pattern = r'(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+|virtual\s+|override\s+|async\s+|sealed\s+)*(?:[\w<>\[\],\s]+)\s+(\w+)\s*\([^)]*\)'
        
        for match in re.finditer(method_pattern, content):
            method_name = match.group(1)
            # Filter out keywords and common type names
            if method_name not in ['if', 'for', 'while', 'switch', 'new', 'return', 'using', 'namespace', 'class', 'struct', 'interface']:
                methods.append({
                    'name': method_name,
                    'start': match.start()
                })
        
        return methods
    
    def _extract_properties(self, content: str) -> List[Dict[str, Any]]:
        """Extract property definitions"""
        properties = []
        # Auto-properties and full properties
        prop_pattern = r'(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+|virtual\s+|override\s+)?[\w<>\[\]]+\s+(\w+)\s*\{\s*(?:get|set)'
        
        for match in re.finditer(prop_pattern, content):
            properties.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return properties
    
    def _extract_fields(self, content: str) -> List[str]:
        """Extract field names"""
        fields = []
        # Field declarations
        field_pattern = r'(?:public\s+|private\s+|protected\s+|internal\s+)?(?:static\s+|readonly\s+|const\s+)?[\w<>\[\]]+\s+(\w+)\s*[=;]'
        
        for match in re.finditer(field_pattern, content):
            field_name = match.group(1)
            # Filter out common type names
            if field_name not in ['string', 'int', 'bool', 'double', 'float', 'decimal', 'long', 'short', 'byte', 'char', 'object', 'var']:
                fields.append(field_name)
        
        return fields
    
    def _calculate_name_descriptiveness(self, classes: List[Dict], methods: List[Dict], fields: List[str]) -> float:
        """Calculate how descriptive names are"""
        all_names = [c['name'] for c in classes] + [m['name'] for m in methods] + fields
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # C# conventions: PascalCase for public, camelCase for private
            if len(name) > 3:
                if re.match(r'^[A-Z][a-zA-Z0-9]*$', name) or re.match(r'^[a-z][a-zA-Z0-9]*$', name):
                    # Check for meaningful names (not just 'Data', 'Info', etc.)
                    if name.lower() not in ['data', 'info', 'temp', 'obj', 'val', 'res']:
                        descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str, methods: List[Dict]) -> float:
        """Calculate XML documentation coverage"""
        if not methods:
            return 0.0
        
        documented = 0
        for method in methods:
            # Look for XML doc comment before method
            before_method = content[:method['start']]
            # XML documentation uses ///
            if re.search(r'///\s*<summary>', before_method[-500:]):
                documented += 1
        
        return documented / len(methods)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        complexity_patterns = [
            r'\bif\s*\(',
            r'\belse\s+if\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bforeach\s*\(',
            r'\bdo\s*\{',
            r'\bcase\s+',
            r'\bcatch\s*\(',
            r'\?\s*[^:]+:',  # Ternary operator
            r'&&',
            r'\|\|',
            r'\?\?'  # Null coalescing operator
        ]
        
        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, content))
        
        methods = self._extract_methods(content)
        if methods:
            avg_complexity = complexity / len(methods)
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
        finally_blocks = len(re.findall(r'\bfinally\s*\{', content))
        using_statements = len(re.findall(r'\busing\s*\(', content))  # Proper resource disposal
        
        error_indicators = try_blocks + using_statements
        
        if not methods:
            return 0.0
        
        # Good coverage if ~30% of methods have error handling
        expected_handlers = max(1, len(methods) * 0.3)
        score = min(1.0, error_indicators / expected_handlers)
        
        # Bonus for specific exception handling
        specific_catches = len(re.findall(r'catch\s*\(\s*\w+Exception\s+\w+\s*\)', content))
        if specific_catches > 0:
            score = min(1.0, score + 0.1)
        
        return score
    
    def _calculate_test_coverage(self, methods: List[Dict], classes: List[Dict]) -> float:
        """Calculate test coverage based on test methods and classes"""
        test_methods = []
        for method in methods:
            # Check for test attributes and naming conventions
            if method['name'].startswith('Test') or method['name'].endswith('Test'):
                test_methods.append(method)
        
        # Check for [Test], [TestMethod], [Fact] attributes
        test_attributes = len(re.findall(r'\[\s*(?:Test|TestMethod|Fact)\s*\]', content))
        
        test_classes = [c for c in classes if 
                       c['name'].endswith('Test') or 
                       c['name'].endswith('Tests') or
                       c['name'].startswith('Test')]
        
        if not methods:
            return 0.0
        
        # Consider both test methods and test attributes
        test_score = (len(test_methods) + test_attributes + len(test_classes) * 3) / len(methods)
        return min(1.0, test_score)
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score"""
        dangerous_patterns = [
            r'SqlCommand\s*\(',  # Potential SQL injection
            r'Process\.Start',  # Process execution
            r'Assembly\.Load',  # Dynamic assembly loading
            r'Activator\.CreateInstance',  # Dynamic instantiation
            r'StreamWriter.*FileMode\.Create',  # File manipulation
            r'Request\[',  # Direct request access
        ]
        
        dangerous_count = 0
        for pattern in dangerous_patterns:
            dangerous_count += len(re.findall(pattern, content))
        
        # Check for security best practices
        security_patterns = [
            r'SqlParameter',  # Parameterized queries
            r'using\s*\(',  # Proper resource disposal
            r'\[Authorize\]',  # Authorization attributes
            r'ValidateAntiForgeryToken',  # CSRF protection
            r'IConfiguration',  # Configuration management
            r'SecureString',  # Secure string handling
            r'Regex\.IsMatch',  # Input validation
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
        """Calculate C# style consistency"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        scores = []
        
        # Check brace style
        same_line_braces = len(re.findall(r'\)\s*\{', content))
        next_line_braces = len(re.findall(r'\)\s*\n\s*\{', content))
        total_braces = same_line_braces + next_line_braces
        
        if total_braces > 0:
            # C# typically uses next line braces
            brace_consistency = next_line_braces / total_braces
            scores.append(brace_consistency)
        
        # Check naming conventions
        # Classes and methods should be PascalCase
        classes = self._extract_classes(content)
        methods = self._extract_methods(content)
        
        pascal_items = 0
        total_items = len(classes) + len(methods)
        
        if total_items > 0:
            for item in classes + methods:
                if re.match(r'^[A-Z][a-zA-Z0-9]*$', item['name']):
                    pascal_items += 1
            scores.append(pascal_items / total_items)
        
        # Check for var usage consistency
        var_usage = content.count('var ')
        explicit_types = len(re.findall(r'(?:int|string|bool|double|float|List|Dictionary)\s+\w+\s*=', content))
        
        if var_usage + explicit_types > 0:
            # Either consistent var usage or consistent explicit types is good
            var_ratio = var_usage / (var_usage + explicit_types)
            consistency = var_ratio if var_ratio > 0.7 else (1 - var_ratio)
            scores.append(consistency)
        
        return sum(scores) / len(scores) if scores else 0.5