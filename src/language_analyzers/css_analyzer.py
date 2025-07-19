"""
CSS language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class CSSAnalyzer(LanguageAnalyzer):
    """Analyzer for CSS code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.css', '.scss', '.sass', '.less']
    
    def get_language_name(self) -> str:
        return 'CSS'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a CSS file"""
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
        selectors = self._extract_selectors(content)
        classes = self._extract_classes(selectors)
        ids = self._extract_ids(selectors)
        variables = self._extract_variables(content)
        media_queries = self._extract_media_queries(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(classes, ids, variables)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content)
        metrics['modularidad']['organizacion'] = self._calculate_modularity(content, selectors)
        metrics['complejidad']['especificidad'] = self._calculate_specificity_complexity(selectors)
        metrics['manejo_errores']['fallbacks'] = self._calculate_fallback_coverage(content)
        metrics['pruebas']['validacion'] = self._calculate_validation_score(content)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        # CSS specific metrics
        metrics['css_calidad'] = {
            'uso_variables': self._calculate_variable_usage(variables, content),
            'responsive_design': self._calculate_responsive_score(media_queries),
            'metodologia_bem': self._check_bem_methodology(classes)
        }
        
        return metrics
    
    def _extract_selectors(self, content: str) -> List[str]:
        """Extract all CSS selectors"""
        # Remove comments
        content_no_comments = re.sub(r'/\*[\s\S]*?\*/', '', content)
        
        # Extract selectors (everything before {)
        selector_pattern = r'([^{}]+)\s*\{'
        selectors = re.findall(selector_pattern, content_no_comments)
        
        # Clean and split multiple selectors
        all_selectors = []
        for selector_group in selectors:
            # Split by comma for multiple selectors
            individual_selectors = selector_group.split(',')
            all_selectors.extend([s.strip() for s in individual_selectors])
        
        return all_selectors
    
    def _extract_classes(self, selectors: List[str]) -> List[str]:
        """Extract class names from selectors"""
        classes = []
        class_pattern = r'\.([a-zA-Z0-9_-]+)'
        
        for selector in selectors:
            matches = re.findall(class_pattern, selector)
            classes.extend(matches)
        
        return list(set(classes))  # Remove duplicates
    
    def _extract_ids(self, selectors: List[str]) -> List[str]:
        """Extract ID names from selectors"""
        ids = []
        id_pattern = r'#([a-zA-Z0-9_-]+)'
        
        for selector in selectors:
            matches = re.findall(id_pattern, selector)
            ids.extend(matches)
        
        return list(set(ids))
    
    def _extract_variables(self, content: str) -> Dict[str, List[str]]:
        """Extract CSS variables and preprocessor variables"""
        variables = {
            'css_custom': [],
            'sass': [],
            'less': []
        }
        
        # CSS custom properties
        css_var_pattern = r'--([a-zA-Z0-9_-]+)\s*:'
        variables['css_custom'] = re.findall(css_var_pattern, content)
        
        # SASS/SCSS variables
        sass_var_pattern = r'\$([a-zA-Z0-9_-]+)\s*:'
        variables['sass'] = re.findall(sass_var_pattern, content)
        
        # LESS variables
        less_var_pattern = r'@([a-zA-Z0-9_-]+)\s*:'
        variables['less'] = re.findall(less_var_pattern, content)
        
        return variables
    
    def _extract_media_queries(self, content: str) -> List[str]:
        """Extract media queries"""
        media_pattern = r'@media\s*([^{]+)\{'
        return re.findall(media_pattern, content)
    
    def _calculate_name_descriptiveness(self, classes: List[str], ids: List[str],
                                      variables: Dict[str, List[str]]) -> float:
        """Calculate how descriptive names are"""
        all_vars = variables['css_custom'] + variables['sass'] + variables['less']
        all_names = classes + ids + all_vars
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # Good names are descriptive and follow conventions
            if len(name) > 3:
                # Check for meaningful names
                if not re.match(r'^[a-z]\d*$', name):  # Not just 'a1', 'b2', etc.
                    # Check for kebab-case or camelCase
                    if (re.match(r'^[a-z]+(-[a-z]+)*$', name) or  # kebab-case
                        re.match(r'^[a-z][a-zA-Z0-9]*$', name)):   # camelCase
                        descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str) -> float:
        """Calculate documentation coverage (comments)"""
        # Count comments
        comments = re.findall(r'/\*[\s\S]*?\*/', content)
        
        # Count rule blocks
        rule_blocks = len(re.findall(r'\{[^}]+\}', content))
        
        if rule_blocks == 0:
            return 0.0
        
        # Good if there's at least one comment per 5 rule blocks
        return min(1.0, len(comments) / (rule_blocks / 5))
    
    def _calculate_modularity(self, content: str, selectors: List[str]) -> float:
        """Calculate modularity based on CSS organization"""
        score = 0.0
        
        # Check for sectioned comments (indicates organization)
        section_comments = len(re.findall(r'/\*\s*={3,}.*={3,}\s*\*/', content))
        if section_comments > 2:
            score += 0.3
        
        # Check for utility classes (indicates modular approach)
        utility_classes = [s for s in selectors if re.match(r'^\.[a-z]+-[a-z]+$', s)]
        if len(utility_classes) > len(selectors) * 0.1:
            score += 0.3
        
        # Check for component-based naming
        component_classes = [s for s in selectors if '--' in s or '__' in s]
        if len(component_classes) > len(selectors) * 0.2:
            score += 0.4
        
        return min(1.0, score)
    
    def _calculate_specificity_complexity(self, selectors: List[str]) -> float:
        """Calculate selector specificity complexity"""
        if not selectors:
            return 1.0
        
        total_specificity = 0
        for selector in selectors:
            specificity = self._calculate_selector_specificity(selector)
            total_specificity += specificity
        
        avg_specificity = total_specificity / len(selectors)
        
        # Lower specificity is better
        if avg_specificity <= 10:
            return 1.0
        elif avg_specificity <= 20:
            return 0.7
        elif avg_specificity <= 30:
            return 0.4
        else:
            return 0.2
    
    def _calculate_selector_specificity(self, selector: str) -> int:
        """Calculate specificity score for a single selector"""
        # Simplified specificity calculation
        score = 0
        
        # IDs (weight: 100)
        score += len(re.findall(r'#[a-zA-Z0-9_-]+', selector)) * 100
        
        # Classes, attributes, pseudo-classes (weight: 10)
        score += len(re.findall(r'\.[a-zA-Z0-9_-]+', selector)) * 10
        score += len(re.findall(r'\[[^\]]+\]', selector)) * 10
        score += len(re.findall(r':[a-zA-Z-]+', selector)) * 10
        
        # Elements (weight: 1)
        score += len(re.findall(r'\b[a-z]+\b', selector))
        
        # Penalize deep nesting
        nesting_level = selector.count(' ') + selector.count('>')
        if nesting_level > 3:
            score += (nesting_level - 3) * 5
        
        return score
    
    def _calculate_fallback_coverage(self, content: str) -> float:
        """Calculate browser fallback coverage"""
        score = 0.0
        checks = 0
        
        # Check for vendor prefixes
        properties_needing_prefixes = ['transform', 'transition', 'animation', 'flex', 'grid']
        for prop in properties_needing_prefixes:
            if prop in content:
                checks += 1
                # Check for at least webkit prefix
                if f'-webkit-{prop}' in content:
                    score += 0.5
                # Check for other prefixes
                if f'-moz-{prop}' in content or f'-ms-{prop}' in content:
                    score += 0.5
        
        # Check for fallback values
        if 'var(' in content:
            # CSS custom properties should have fallbacks
            var_uses = len(re.findall(r'var\([^)]+\)', content))
            var_with_fallback = len(re.findall(r'var\([^,]+,[^)]+\)', content))
            if var_uses > 0:
                checks += 1
                score += var_with_fallback / var_uses
        
        return score / checks if checks > 0 else 0.5
    
    def _calculate_validation_score(self, content: str) -> float:
        """Calculate CSS validation score"""
        score = 1.0
        
        # Check for common errors
        # Missing semicolons (rough check)
        if re.search(r'[a-z0-9%]\s*\n\s*[a-z-]+:', content):
            score -= 0.2
        
        # Check for empty rules
        empty_rules = len(re.findall(r'\{\s*\}', content))
        if empty_rules > 0:
            score -= empty_rules * 0.05
        
        # Check for !important usage (should be minimal)
        important_count = content.count('!important')
        if important_count > 5:
            score -= min(0.3, (important_count - 5) * 0.02)
        
        # Check for invalid selectors
        if re.search(r'[^{]*[>+~]\s*$', content, re.MULTILINE):
            score -= 0.1
        
        return max(0.0, score)
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score for CSS"""
        score = 1.0
        
        # Check for expression() (IE specific, security risk)
        if 'expression(' in content:
            score -= 0.5
        
        # Check for javascript: protocol in url()
        if re.search(r'url\s*\(\s*["\']?javascript:', content, re.IGNORECASE):
            score -= 0.5
        
        # Check for data: URIs (can be security risk if not handled properly)
        data_uris = len(re.findall(r'url\s*\(\s*["\']?data:', content, re.IGNORECASE))
        if data_uris > 10:  # Excessive use might indicate issues
            score -= 0.2
        
        return max(0.0, score)
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate style consistency"""
        scores = []
        
        # Check property formatting consistency
        colon_space = len(re.findall(r':\s+', content))
        colon_no_space = len(re.findall(r':[^\s]', content))
        
        if colon_space + colon_no_space > 0:
            consistency = max(colon_space, colon_no_space) / (colon_space + colon_no_space)
            scores.append(consistency)
        
        # Check brace style
        same_line_brace = len(re.findall(r'\S\s*\{', content))
        new_line_brace = len(re.findall(r'\n\s*\{', content))
        
        if same_line_brace + new_line_brace > 0:
            brace_consistency = max(same_line_brace, new_line_brace) / (same_line_brace + new_line_brace)
            scores.append(brace_consistency)
        
        # Check quote consistency
        double_quotes = content.count('"')
        single_quotes = content.count("'")
        
        if double_quotes + single_quotes > 0:
            quote_consistency = max(double_quotes, single_quotes) / (double_quotes + single_quotes)
            scores.append(quote_consistency)
        
        # Check color format consistency
        hex_colors = len(re.findall(r'#[0-9a-fA-F]{3,6}\b', content))
        rgb_colors = len(re.findall(r'rgb\(', content))
        hsl_colors = len(re.findall(r'hsl\(', content))
        
        total_colors = hex_colors + rgb_colors + hsl_colors
        if total_colors > 0:
            color_consistency = max(hex_colors, rgb_colors, hsl_colors) / total_colors
            scores.append(color_consistency)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_variable_usage(self, variables: Dict[str, List[str]], content: str) -> float:
        """Calculate CSS variable usage score"""
        all_vars = variables['css_custom'] + variables['sass'] + variables['less']
        
        if not all_vars:
            return 0.0
        
        # Check how many variables are actually used
        used_vars = 0
        for var_type, var_list in variables.items():
            for var in var_list:
                if var_type == 'css_custom':
                    pattern = f'var\\(--{re.escape(var)}\\)'
                elif var_type == 'sass':
                    pattern = f'\\${re.escape(var)}'
                elif var_type == 'less':
                    pattern = f'@{re.escape(var)}'
                
                # Count uses (excluding definition)
                uses = len(re.findall(pattern, content)) - 1
                if uses > 0:
                    used_vars += 1
        
        return used_vars / len(all_vars)
    
    def _calculate_responsive_score(self, media_queries: List[str]) -> float:
        """Calculate responsive design score"""
        if not media_queries:
            return 0.0
        
        score = min(1.0, len(media_queries) * 0.1)  # Base score for having media queries
        
        # Check for mobile-first approach (min-width queries)
        min_width_queries = sum(1 for q in media_queries if 'min-width' in q)
        if min_width_queries > len(media_queries) * 0.5:
            score = min(1.0, score + 0.2)
        
        # Check for common breakpoints
        common_breakpoints = ['768px', '1024px', '1200px', '480px', '640px']
        for breakpoint in common_breakpoints:
            if any(breakpoint in q for q in media_queries):
                score = min(1.0, score + 0.1)
        
        return score
    
    def _check_bem_methodology(self, classes: List[str]) -> float:
        """Check if BEM methodology is used"""
        if not classes:
            return 0.0
        
        bem_classes = 0
        for class_name in classes:
            # BEM pattern: block__element--modifier
            if re.match(r'^[a-z]+(-[a-z]+)*(__[a-z]+(-[a-z]+)*)?(--[a-z]+(-[a-z]+)*)?$', class_name):
                bem_classes += 1
        
        return bem_classes / len(classes)