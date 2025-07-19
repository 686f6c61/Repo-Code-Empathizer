"""
HTML language analyzer implementation
"""
import re
from typing import Dict, List, Any, Optional
from .base import LanguageAnalyzer


class HTMLAnalyzer(LanguageAnalyzer):
    """Analyzer for HTML code"""
    
    def get_file_extensions(self) -> List[str]:
        return ['.html', '.htm', '.xhtml']
    
    def get_language_name(self) -> str:
        return 'HTML'
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze an HTML file"""
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
        tags = self._extract_tags(content)
        ids = self._extract_ids(content)
        classes = self._extract_classes(content)
        semantic_tags = self._count_semantic_tags(content)
        
        # Calculate metrics
        metrics['nombres']['descriptividad'] = self._calculate_name_descriptiveness(ids, classes)
        metrics['documentacion']['cobertura'] = self._calculate_doc_coverage(content)
        metrics['modularidad']['componentes'] = self._calculate_modularity(content)
        metrics['complejidad']['anidacion'] = self._calculate_nesting_complexity(content)
        metrics['manejo_errores']['accesibilidad'] = self._calculate_accessibility(content)
        metrics['pruebas']['validacion'] = self._calculate_validation_score(content)
        metrics['seguridad']['validacion'] = self._calculate_security_score(content)
        metrics['consistencia_estilo']['consistencia'] = self._calculate_style_consistency(content)
        
        # HTML specific metrics
        metrics['html_semantica'] = {
            'uso_semantico': self._calculate_semantic_usage(semantic_tags, len(tags)),
            'estructura_correcta': self._check_document_structure(content)
        }
        
        return metrics
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract all HTML tags"""
        tag_pattern = r'<(\w+)(?:\s[^>]*)?>.*?</\1>|<(\w+)(?:\s[^>]*)?/?>'
        matches = re.findall(tag_pattern, content, re.DOTALL)
        return [tag[0] or tag[1] for tag in matches]
    
    def _extract_ids(self, content: str) -> List[str]:
        """Extract all id attributes"""
        id_pattern = r'id\s*=\s*["\']([^"\']+)["\']'
        return re.findall(id_pattern, content)
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract all class names"""
        class_pattern = r'class\s*=\s*["\']([^"\']+)["\']'
        classes = []
        for match in re.findall(class_pattern, content):
            classes.extend(match.split())
        return classes
    
    def _count_semantic_tags(self, content: str) -> Dict[str, int]:
        """Count semantic HTML5 tags"""
        semantic_tags = [
            'header', 'nav', 'main', 'article', 'section', 'aside',
            'footer', 'figure', 'figcaption', 'time', 'mark', 'details',
            'summary', 'dialog', 'menu', 'menuitem'
        ]
        
        counts = {}
        for tag in semantic_tags:
            pattern = f'<{tag}(?:\\s[^>]*)?>.*?</{tag}>|<{tag}(?:\\s[^>]*)?/?>'
            counts[tag] = len(re.findall(pattern, content, re.IGNORECASE | re.DOTALL))
        
        return counts
    
    def _calculate_name_descriptiveness(self, ids: List[str], classes: List[str]) -> float:
        """Calculate how descriptive IDs and classes are"""
        all_names = ids + classes
        
        if not all_names:
            return 0.0
        
        descriptive_count = 0
        for name in all_names:
            # Good names are descriptive and follow conventions
            if len(name) > 3:
                # Check for meaningful names (not just 'div1', 'a', 'b', etc.)
                if not re.match(r'^[a-z]\d*$', name):
                    # Check for kebab-case, camelCase, or BEM notation
                    if (re.match(r'^[a-z]+(-[a-z]+)*$', name) or  # kebab-case
                        re.match(r'^[a-z][a-zA-Z0-9]*$', name) or  # camelCase
                        re.match(r'^[a-z]+(__[a-z]+)*(--[a-z]+)*$', name)):  # BEM
                        descriptive_count += 1
        
        return descriptive_count / len(all_names)
    
    def _calculate_doc_coverage(self, content: str) -> float:
        """Calculate documentation coverage (comments)"""
        # Count HTML comments
        comments = re.findall(r'<!--[\s\S]*?-->', content)
        
        # Count major sections (could benefit from comments)
        major_sections = len(re.findall(r'<(?:div|section|article|main|header|footer)(?:\s[^>]*)?>',
                                       content, re.IGNORECASE))
        
        if major_sections == 0:
            return 0.0
        
        # Good if there's at least one comment per 3 major sections
        return min(1.0, len(comments) / (major_sections / 3))
    
    def _calculate_modularity(self, content: str) -> float:
        """Calculate modularity based on component structure"""
        # Count reusable components (sections, articles, custom elements)
        components = len(re.findall(r'<(?:section|article|[a-z]+-[a-z]+)(?:\s[^>]*)?>',
                                   content, re.IGNORECASE))
        
        # Count total structural elements
        total_elements = len(re.findall(r'<(?:div|section|article|aside|main|header|footer)(?:\s[^>]*)?>',
                                       content, re.IGNORECASE))
        
        if total_elements == 0:
            return 0.0
        
        # Higher ratio of semantic components = better modularity
        return min(1.0, components / (total_elements * 0.5))
    
    def _calculate_nesting_complexity(self, content: str) -> float:
        """Calculate nesting complexity"""
        # Simple approach: count maximum nesting depth
        max_depth = 0
        current_depth = 0
        
        # Use a simple tag counter
        for char in content:
            if char == '<':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '>':
                current_depth = max(0, current_depth - 1)
        
        # Convert to score (lower nesting is better)
        if max_depth <= 5:
            return 1.0
        elif max_depth <= 10:
            return 0.7
        elif max_depth <= 15:
            return 0.4
        else:
            return 0.2
    
    def _calculate_accessibility(self, content: str) -> float:
        """Calculate accessibility score"""
        score = 0.0
        total_checks = 0
        
        # Check for alt attributes on images
        images = len(re.findall(r'<img(?:\s[^>]*)?>', content, re.IGNORECASE))
        images_with_alt = len(re.findall(r'<img[^>]+alt\s*=\s*["\'][^"\']+["\'][^>]*>',
                                         content, re.IGNORECASE))
        
        if images > 0:
            score += images_with_alt / images
            total_checks += 1
        
        # Check for labels on form inputs
        inputs = len(re.findall(r'<input(?:\s[^>]*)?>', content, re.IGNORECASE))
        labels = len(re.findall(r'<label(?:\s[^>]*)?>', content, re.IGNORECASE))
        
        if inputs > 0:
            score += min(1.0, labels / inputs)
            total_checks += 1
        
        # Check for ARIA attributes
        aria_attrs = len(re.findall(r'aria-\w+\s*=', content))
        if aria_attrs > 0:
            score += min(1.0, aria_attrs * 0.1)
            total_checks += 1
        
        # Check for lang attribute
        if re.search(r'<html[^>]+lang\s*=', content, re.IGNORECASE):
            score += 1.0
            total_checks += 1
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _calculate_validation_score(self, content: str) -> float:
        """Calculate HTML validation score"""
        score = 1.0
        
        # Check for DOCTYPE
        if not re.match(r'^\s*<!DOCTYPE', content, re.IGNORECASE):
            score -= 0.2
        
        # Check for proper structure
        if not re.search(r'<html[^>]*>[\s\S]*<head[^>]*>[\s\S]*</head>[\s\S]*<body[^>]*>[\s\S]*</body>[\s\S]*</html>',
                        content, re.IGNORECASE):
            score -= 0.3
        
        # Check for unclosed tags (simple check)
        open_tags = re.findall(r'<(\w+)(?:\s[^>]*)?>', content)
        close_tags = re.findall(r'</(\w+)>', content)
        
        # Self-closing tags
        self_closing = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source']
        
        open_count = {}
        for tag in open_tags:
            if tag.lower() not in self_closing:
                open_count[tag] = open_count.get(tag, 0) + 1
        
        close_count = {}
        for tag in close_tags:
            close_count[tag] = close_count.get(tag, 0) + 1
        
        # Check if counts match
        for tag, count in open_count.items():
            if close_count.get(tag, 0) != count:
                score -= 0.05
        
        return max(0.0, score)
    
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score for HTML"""
        score = 1.0
        
        # Check for inline JavaScript (security risk)
        if re.search(r'on\w+\s*=\s*["\'][^"\']+["\']', content):
            score -= 0.3
        
        # Check for javascript: protocol
        if re.search(r'href\s*=\s*["\']javascript:', content, re.IGNORECASE):
            score -= 0.3
        
        # Check for external resources without integrity checks
        external_resources = re.findall(r'<(?:script|link)[^>]+(?:src|href)\s*=\s*["\']https?://[^"\']+["\'][^>]*>',
                                       content, re.IGNORECASE)
        resources_with_integrity = re.findall(r'<(?:script|link)[^>]+integrity\s*=', content, re.IGNORECASE)
        
        if external_resources and len(resources_with_integrity) < len(external_resources) * 0.5:
            score -= 0.2
        
        # Check for Content Security Policy meta tag (bonus)
        if re.search(r'<meta[^>]+http-equiv\s*=\s*["\']Content-Security-Policy["\']', content, re.IGNORECASE):
            score = min(1.0, score + 0.1)
        
        return max(0.0, score)
    
    def _calculate_style_consistency(self, content: str) -> float:
        """Calculate style consistency"""
        scores = []
        
        # Check quote consistency
        double_quotes = len(re.findall(r'=\s*"[^"]*"', content))
        single_quotes = len(re.findall(r"=\s*'[^']*'", content))
        
        if double_quotes + single_quotes > 0:
            quote_consistency = max(double_quotes, single_quotes) / (double_quotes + single_quotes)
            scores.append(quote_consistency)
        
        # Check indentation consistency
        lines = content.split('\n')
        indented_lines = [line for line in lines if line and line[0] in ' \t']
        
        if indented_lines:
            # Check for consistent indentation (2 or 4 spaces)
            two_space = sum(1 for line in indented_lines if line.startswith('  ') and not line.startswith('    '))
            four_space = sum(1 for line in indented_lines if line.startswith('    '))
            tab_indent = sum(1 for line in indented_lines if line.startswith('\t'))
            
            total = len(indented_lines)
            consistency = max(two_space, four_space, tab_indent) / total
            scores.append(consistency)
        
        # Check tag case consistency (lowercase preferred)
        lowercase_tags = len(re.findall(r'<[a-z]+(?:\s|>)', content))
        uppercase_tags = len(re.findall(r'<[A-Z]+(?:\s|>)', content))
        
        if lowercase_tags + uppercase_tags > 0:
            case_consistency = lowercase_tags / (lowercase_tags + uppercase_tags)
            scores.append(case_consistency)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_semantic_usage(self, semantic_counts: Dict[str, int], total_tags: int) -> float:
        """Calculate semantic HTML usage"""
        if total_tags == 0:
            return 0.0
        
        semantic_total = sum(semantic_counts.values())
        return min(1.0, semantic_total / (total_tags * 0.2))  # Expect ~20% semantic tags
    
    def _check_document_structure(self, content: str) -> float:
        """Check for proper HTML document structure"""
        score = 0.0
        
        # Check for proper DOCTYPE
        if re.match(r'^\s*<!DOCTYPE html>', content, re.IGNORECASE):
            score += 0.2
        
        # Check for html tag with lang
        if re.search(r'<html[^>]+lang\s*=', content, re.IGNORECASE):
            score += 0.2
        
        # Check for head section with title
        if re.search(r'<head[^>]*>[\s\S]*<title[^>]*>[^<]+</title>[\s\S]*</head>',
                    content, re.IGNORECASE):
            score += 0.2
        
        # Check for meta charset
        if re.search(r'<meta[^>]+charset\s*=', content, re.IGNORECASE):
            score += 0.2
        
        # Check for viewport meta
        if re.search(r'<meta[^>]+name\s*=\s*["\']viewport["\']', content, re.IGNORECASE):
            score += 0.2
        
        return score