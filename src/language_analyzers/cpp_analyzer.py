"""
C++ language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class CppAnalyzer(LanguageAnalyzer):
    """Analyzer for C++ code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.cpp', '.cc', '.cxx', '.hpp', '.h', '.hh']
    
    def get_language_name(self) -> str:
        return 'C++'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a C++ file"""
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
        namespaces = self._extract_namespaces(content)
        templates = self._extract_templates(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(functions, classes)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content, functions)
        metrics['modularidad']['funciones'] = len(functions)
        metrics['modularidad']['clases'] = len(classes)
        metrics['complejidad']['ciclomatica'] = self._calculate_cyclomatic_complexity(content)
        metrics['manejo_errores']['cobertura'] = self._calculate_error_handling(content)
        metrics['pruebas']['cobertura'] = self._calculate_test_coverage(functions, file_path)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        return metrics
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        # Regular function pattern (simplified)
        func_pattern = r'(?:(?:inline|static|virtual|explicit|constexpr)\s+)*(?:[\w:]+\s+)*(\w+)\s*\([^)]*\)\s*(?:const)?\s*(?:override)?\s*\{'
        
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            # Filter out keywords
            if func_name not in ['if', 'for', 'while', 'switch', 'catch', 'namespace', 'class', 'struct']:
                functions.append({
                    'name': func_name,
                    'start': match.start()
                })
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """Extract class and struct definitions"""
        classes = []
        
        # Class pattern
        class_pattern = r'(?:template\s*<[^>]*>\s*)?(?:class|struct)\s+(?:\w+::)*(\w+)(?:\s*:\s*(?:public|private|protected)\s+[\w:]+)?'
        
        for match in re.finditer(class_pattern, content):
            classes.append({
                'name': match.group(1),
                'start': match.start()
            })
        
        return classes
    
    def _extract_namespaces(self, content: str) -> List[str]:
        """Extract namespace names"""
        namespace_pattern = r'namespace\s+(\w+)'
        return re.findall(namespace_pattern, content)
    
    def _extract_templates(self, content: str) -> int:
        """Count template definitions"""
        template_pattern = r'template\s*<[^>]+>'
        return len(re.findall(template_pattern, content))
    
    def _calculate_name_descriptiveness(self, functions: List[Dict], classes: List[Dict]) -> float:
        """Calculate how descriptive names are"""
        all_names = [f['name'] for f in functions] + [c['name'] for c in classes]
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # C++ conventions: various styles are acceptable
            if len(name) > 3:
                # Check for camelCase, PascalCase, or snake_case
                if (re.match(r'^[a-z][a-zA-Z0-9]*$', name) or 
                    re.match(r'^[A-Z][a-zA-Z0-9]*$', name) or
                    re.match(r'^[a-z]+(_[a-z]+)*$', name)):
                    descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str, functions: List[Dict]) -> float:
        """Calculate documentation coverage"""
        if not functions:
            return 0.0
        
        documented = 0
        for func in functions:
            # Look for Doxygen or regular comments before function
            before_func = content[:func['start']]
            # Check for various documentation styles
            if (re.search(r'/\*\*[\s\S]*?\*/', before_func[-300:]) or  # Doxygen style
                re.search(r'///.*\n', before_func[-100:])):  # Triple slash style
                documented += 1
        
        return documented / len(functions)
    
    def _calculate_cyclomatic_complexity(self, content: str) -> float:
        """Calculate cyclomatic complexity"""
        complexity_patterns = [
            r'\bif\s*\(',
            r'\belse\s+if\s*\(',
            r'\bwhile\s*\(',
            r'\bfor\s*\(',
            r'\bdo\s*\{',
            r'\bswitch\s*\(',
            r'\bcase\s+',
            r'\bcatch\s*\(',
            r'\?\s*[^:]+:',  # Ternary operator
            r'&&',
            r'\|\|'
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
        # C++ error handling patterns
        try_blocks = len(re.findall(r'\btry\s*\{', content))
        catch_blocks = len(re.findall(r'\bcatch\s*\([^)]*\)\s*\{', content))
        noexcept_specs = len(re.findall(r'noexcept(?:\([^)]*\))?', content))
        
        # RAII patterns (good C++ practice)
        smart_pointers = len(re.findall(r'(?:unique_ptr|shared_ptr|weak_ptr)\s*<', content))
        lock_guards = len(re.findall(r'(?:lock_guard|unique_lock|scoped_lock)\s*<', content))
        
        error_indicators = try_blocks + noexcept_specs + smart_pointers + lock_guards
        
        # Good if there's reasonable error handling
        if error_indicators > 0:
            score = min(1.0, error_indicators * 0.1)
        else:
            score = 0.3  # Base score
        
        # Penalty for catch(...)
        catch_all = len(re.findall(r'catch\s*\(\s*\.\.\.\s*\)', content))
        if catch_all > 0:
            score = max(0.0, score - catch_all * 0.1)
        
        return score
    
    def _calculate_test_coverage(self, functions: List[Dict], file_path: str) -> float:
        """Calculate test coverage"""
        # Check if this is a test file
        if any(pattern in file_path for pattern in ['test', 'Test', 'spec', 'Spec']):
            return 1.0
        
        # Look for test frameworks
        test_frameworks = [
            r'#include\s*[<"]gtest',  # Google Test
            r'#include\s*[<"]catch',  # Catch2
            r'#include\s*[<"]boost/test',  # Boost.Test
            r'TEST\s*\(',  # Google Test macros
            r'TEST_F\s*\(',
            r'TEST_CASE\s*\(',  # Catch2
            r'BOOST_AUTO_TEST_CASE\s*\('  # Boost.Test
        ]
        
        test_count = 0
        for pattern in test_frameworks:
            test_count += len(re.findall(pattern, content))
        
        if test_count > 0:
            return min(1.0, test_count * 0.1)
        
        return 0.0
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score"""
        dangerous_patterns = [
            r'gets\s*\(',  # Buffer overflow risk
            r'strcpy\s*\(',  # Buffer overflow risk
            r'strcat\s*\(',  # Buffer overflow risk
            r'sprintf\s*\(',  # Format string vulnerability
            r'system\s*\(',  # Command injection
            r'scanf\s*\(',  # Buffer overflow risk
            r'reinterpret_cast',  # Type safety bypass
            r'const_cast',  # Const correctness bypass
        ]
        
        dangerous_count = 0
        for pattern in dangerous_patterns:
            dangerous_count += len(re.findall(pattern, content))
        
        # Check for safe alternatives
        safe_patterns = [
            r'fgets\s*\(',  # Safe alternative to gets
            r'strncpy\s*\(',  # Safe alternative to strcpy
            r'strncat\s*\(',  # Safe alternative to strcat
            r'snprintf\s*\(',  # Safe alternative to sprintf
            r'static_cast',  # Type-safe casting
            r'dynamic_cast',  # Type-safe casting
            r'std::string',  # Safe string handling
            r'std::vector',  # Safe dynamic arrays
            r'std::array',  # Safe fixed arrays
        ]
        
        safe_count = 0
        for pattern in safe_patterns:
            safe_count += len(re.findall(pattern, content))
        
        # Calculate score
        score = 1.0 - (dangerous_count * 0.2)
        score = max(0.0, score)
        
        # Bonus for safe practices
        if safe_count > 0:
            score = min(1.0, score + (safe_count * 0.02))
        
        return score
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate C++ style consistency"""
        lines = content.split('\n')
        if not lines:
            return 0.0
        
        scores = []
        
        # Check brace style
        same_line_braces = len(re.findall(r'\)\s*\{', content))
        next_line_braces = len(re.findall(r'\)\s*\n\s*\{', content))
        total_braces = same_line_braces + next_line_braces
        
        if total_braces > 0:
            # Either style is fine, consistency matters
            brace_consistency = max(same_line_braces, next_line_braces) / total_braces
            scores.append(brace_consistency)
        
        # Check naming style consistency
        # Count different naming patterns
        camel_case = len(re.findall(r'\b[a-z][a-zA-Z0-9]*\b', content))
        snake_case = len(re.findall(r'\b[a-z]+(_[a-z]+)+\b', content))
        pascal_case = len(re.findall(r'\b[A-Z][a-zA-Z0-9]*\b', content))
        
        total_names = camel_case + snake_case + pascal_case
        if total_names > 0:
            # Check which style is dominant
            dominant_style = max(camel_case, snake_case, pascal_case)
            naming_consistency = dominant_style / total_names
            scores.append(naming_consistency)
        
        # Check pointer/reference style (* and & placement)
        ptr_with_type = len(re.findall(r'\w+\s*\*\s*\w+', content))  # Type* var
        ptr_with_var = len(re.findall(r'\w+\s+\*\w+', content))  # Type *var
        
        if ptr_with_type + ptr_with_var > 0:
            ptr_consistency = max(ptr_with_type, ptr_with_var) / (ptr_with_type + ptr_with_var)
            scores.append(ptr_consistency)
        
        return sum(scores) / len(scores) if scores else 0.5