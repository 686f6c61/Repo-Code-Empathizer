"""
Ruby language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class RubyAnalyzer(LanguageAnalyzer):
    """Analyzer for Ruby code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.rb', '.rake', '.gemspec']
    
    def get_language_name(self) -> str:
        return 'Ruby'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a Ruby file"""
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
        methods = self._extract_methods(content)
        classes = self._extract_classes(content)
        modules = self._extract_modules(content)
        variables = self._extract_variables(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(methods, classes, variables)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content, methods)
        metrics['modularidad']['funciones'] = len(methods)
        metrics['modularidad']['clases'] = len(classes) + len(modules)
        metrics['complejidad']['ciclomatica'] = self._calculate_cyclomatic_complexity(content)
        metrics['manejo_errores']['cobertura'] = self._calculate_error_handling(content)
        metrics['pruebas']['cobertura'] = self._calculate_test_coverage(methods, file_path)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        return metrics
    
    def _extract_methods(self, content: str) -> List[Dict[str, Any]]:
        """Extract method definitions"""
        methods = []
        
        # def methods
        def_pattern = r'def\s+(\w+(?:\?|!)?)'
        for match in re.finditer(def_pattern, content):
            methods.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        # attr_accessor, attr_reader, attr_writer (generate methods)
        attr_pattern = r'attr_(?:accessor|reader|writer)\s+((?::\w+(?:\s*,\s*)?)+)'
        for match in re.finditer(attr_pattern, content):
            attrs = match.group(1).replace(':', '').split(',')
            for attr in attrs:
                methods.append({
                    'name': attr.strip(),
                    'type': 'attribute',
                    'start': match.start()
                })
        
        return methods
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        # Class definitions
        class_pattern = r'class\s+(\w+)(?:\s*<\s*\w+)?'
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return classes
    
    def _extract_modules(self, content: str) -> List[Dict[str, Any]]:
        """Extract module definitions"""
        modules = []
        
        # Module definitions
        module_pattern = r'module\s+(\w+)'
        for match in re.finditer(module_pattern, content):
            modules.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return modules
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extract variable names"""
        variables = []
        
        # Instance variables
        instance_vars = re.findall(r'@(\w+)', content)
        variables.extend(instance_vars)
        
        # Class variables
        class_vars = re.findall(r'@@(\w+)', content)
        variables.extend(class_vars)
        
        # Local variables (assignment)
        local_vars = re.findall(r'(\w+)\s*=(?!=)', content)
        # Filter out method calls and constants
        local_vars = [v for v in local_vars if v[0].islower()]
        variables.extend(local_vars)
        
        return list(set(variables))  # Remove duplicates
    
    def _calculate_name_descriptiveness(self, methods: List[Dict], classes: List[Dict], variables: List[str]) -> float:
        """Calculate how descriptive names are"""
        all_names = [m['name'] for m in methods] + [c['name'] for c in classes] + variables
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # Ruby conventions: snake_case for methods/variables, CamelCase for classes
            if len(name) > 2:
                # Check for Ruby naming conventions
                if (re.match(r'^[a-z]+(_[a-z]+)*[?!]?$', name) or  # snake_case with optional ? or !
                    re.match(r'^[A-Z][a-zA-Z0-9]*$', name)):       # CamelCase for classes
                    # Avoid single letter or very generic names
                    if name not in ['i', 'j', 'k', 'x', 'y', 'z', 'tmp', 'temp', 'data']:
                        descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str, methods: List[Dict]) -> float:
        """Calculate documentation coverage"""
        if not methods:
            return 0.0
        
        documented = 0
        for method in methods:
            # Look for YARD documentation or comments before method
            before_method = content[:method['start']]
            lines = before_method.split('\n')
            
            if lines:
                # Check last few lines for documentation
                for i in range(max(0, len(lines) - 5), len(lines)):
                    if i < len(lines):
                        line = lines[i].strip()
                        # YARD documentation starts with # @
                        if line.startswith('# @') or line.startswith('#'):
                            documented += 1
                            break
        
        return documented / len(methods)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        complexity_patterns = [
            r'\bif\b',
            r'\bunless\b',
            r'\belsif\b',
            r'\bwhile\b',
            r'\buntil\b',
            r'\bfor\b',
            r'\.each\b',
            r'\.map\b',
            r'\.select\b',
            r'\bcase\b',
            r'\bwhen\b',
            r'\brescue\b',
            r'\?\s*[^:]+:',  # Ternary operator
            r'&&',
            r'\|\|',
            r'&\.',  # Safe navigation operator
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
    
    def _calculate_error_handling(self, content: str) -> float:
        """Calculate error handling coverage"""
        # Ruby error handling patterns
        begin_blocks = len(re.findall(r'\bbegin\b', content))
        rescue_blocks = len(re.findall(r'\brescue\b', content))
        ensure_blocks = len(re.findall(r'\bensure\b', content))
        
        # Method-level rescue
        method_rescue = len(re.findall(r'def\s+\w+.*\n(?:.*\n)*?\s*rescue', content, re.MULTILINE))
        
        # Validation and checking
        validations = len(re.findall(r'(?:validates?|raise|fail)\b', content))
        
        error_indicators = begin_blocks + rescue_blocks + method_rescue + (validations * 0.5)
        
        # Good if there's reasonable error handling
        if error_indicators > 0:
            score = min(1.0, error_indicators * 0.05)
        else:
            score = 0.2  # Base score
        
        # Bonus for specific exception handling
        specific_rescue = len(re.findall(r'rescue\s+\w+Error', content))
        if specific_rescue > 0:
            score = min(1.0, score + specific_rescue * 0.05)
        
        # Penalty for bare rescue
        bare_rescue = len(re.findall(r'rescue\s*$', content, re.MULTILINE))
        if bare_rescue > 0:
            score = max(0.0, score - bare_rescue * 0.1)
        
        return score
    
    def _calculate_test_coverage(self, methods: List[Dict], file_path: str) -> float:
        """Calculate test coverage"""
        # Check if this is a test/spec file
        if any(pattern in file_path for pattern in ['test', 'spec', '_test.rb', '_spec.rb']):
            return 1.0
        
        # Look for test frameworks
        test_patterns = [
            r'require\s+[\'"](?:test_helper|spec_helper|rails_helper)',  # Test helpers
            r'class\s+\w+\s*<\s*(?:Test::Unit::TestCase|ActiveSupport::TestCase)',  # Test::Unit
            r'RSpec\.describe',  # RSpec
            r'describe\s+[\'"\w]',  # RSpec describe blocks
            r'it\s+[\'"]',  # RSpec examples
            r'test\s+[\'"]',  # Rails tests
            r'assert(?:_equal|_nil|_not_nil)?',  # Assertions
            r'expect\(',  # RSpec expectations
            r'should(?:_not)?',  # Old RSpec syntax
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
            r'`[^`]+`',  # Backticks (command execution)
            r'%x\{',  # Command execution
            r'send\s*\(',  # Dynamic method calls
            r'public_send\s*\(',  # Dynamic method calls
            r'constantize\b',  # Dynamic constant loading
            r'\.html_safe\b',  # Bypass HTML escaping
        ]
        
        dangerous_count = 0
        for pattern in dangerous_patterns:
            dangerous_count += len(re.findall(pattern, content))
        
        # Check for security best practices
        security_patterns = [
            r'params\.require\(',  # Strong parameters
            r'params\.permit\(',  # Strong parameters
            r'sanitize\(',  # Input sanitization
            r'escape_html\(',  # HTML escaping
            r'\.where\s*\([\'"][^\'"\?]*\?',  # Parameterized queries
            r'validates?\s+\w+,\s*presence:',  # Validations
            r'before_action\s+:authenticate',  # Authentication
            r'authorize\s+',  # Authorization
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
        """Calculate Ruby style consistency"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        scores = []
        
        # Check indentation (Ruby uses 2 spaces)
        indented_lines = [line for line in lines if line and line[0] == ' ']
        if indented_lines:
            two_space = sum(1 for line in indented_lines if line.startswith('  ') and not line.startswith('    '))
            scores.append(two_space / len(indented_lines))
        
        # Check string quote consistency
        single_quotes = len(re.findall(r"'[^']*'", content))
        double_quotes = len(re.findall(r'"[^"]*"', content))
        
        if single_quotes + double_quotes > 0:
            # Ruby style guide prefers single quotes when no interpolation
            quote_consistency = single_quotes / (single_quotes + double_quotes)
            scores.append(quote_consistency)
        
        # Check hash syntax
        old_hash = len(re.findall(r':\w+\s*=>', content))  # :symbol => value
        new_hash = len(re.findall(r'\w+:\s*[^:]', content))  # symbol: value
        
        if old_hash + new_hash > 0:
            # Prefer new hash syntax
            hash_consistency = new_hash / (old_hash + new_hash)
            scores.append(hash_consistency)
        
        # Check method parentheses consistency
        # Ruby often omits parentheses for DSL-style code
        method_with_parens = len(re.findall(r'def\s+\w+\s*\(', content))
        method_without_parens = len(re.findall(r'def\s+\w+\s+[a-z]', content))
        
        if method_with_parens + method_without_parens > 0:
            # Either style is fine, consistency matters
            paren_consistency = max(method_with_parens, method_without_parens) / (method_with_parens + method_without_parens)
            scores.append(paren_consistency)
        
        return sum(scores) / len(scores) if scores else 0.5