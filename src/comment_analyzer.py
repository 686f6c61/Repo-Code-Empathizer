"""
Analizador de comentarios y TODOs.

Este módulo analiza comentarios, TODOs, FIXMEs y otros marcadores
en el código fuente.

Classes:
    CommentAnalyzer: Analizador principal de comentarios.

Features:
    - Detección y clasificación de comentarios TODO, FIXME, HACK
    - Análisis de ratio comentarios vs código
    - Evaluación de calidad de comentarios

Author: R. Benítez
Version: 2.0.0
License: MIT
"""

import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class CommentAnalyzer:
    """Analizador de comentarios y marcadores en el código"""
    
    def __init__(self):
        """Inicializa el analizador con patrones de comentarios"""
        # Patrones de comentarios por lenguaje
        self.comment_patterns = {
            'single_line': {
                'python': r'#\s*(.*?)$',
                'javascript': r'//\s*(.*?)$',
                'java': r'//\s*(.*?)$',
                'cpp': r'//\s*(.*?)$',
                'csharp': r'//\s*(.*?)$',
                'go': r'//\s*(.*?)$',
                'ruby': r'#\s*(.*?)$',
                'php': r'(?://|#)\s*(.*?)$',
            },
            'multi_line': {
                'python': r'"""(.*?)"""',
                'javascript': r'/\*(.*?)\*/',
                'java': r'/\*(.*?)\*/',
                'cpp': r'/\*(.*?)\*/',
                'csharp': r'/\*(.*?)\*/',
                'go': r'/\*(.*?)\*/',
                'ruby': r'=begin(.*?)=end',
                'php': r'/\*(.*?)\*/',
            },
            'docstring': {
                'python': r'"""(.*?)"""',
                'javascript': r'/\*\*(.*?)\*/',
                'java': r'/\*\*(.*?)\*/',
            }
        }
        
        # Marcadores especiales
        self.markers = {
            'todo': {
                'patterns': [r'TODO\s*:?\s*(.*)'],
                'priority': 'medium',
                'category': 'task'
            },
            'fixme': {
                'patterns': [r'FIXME\s*:?\s*(.*)'],
                'priority': 'high',
                'category': 'bug'
            },
            'hack': {
                'patterns': [r'HACK\s*:?\s*(.*)'],
                'priority': 'high',
                'category': 'technical_debt'
            },
            'bug': {
                'patterns': [r'BUG\s*:?\s*(.*)'],
                'priority': 'critical',
                'category': 'bug'
            },
            'xxx': {
                'patterns': [r'XXX\s*:?\s*(.*)'],
                'priority': 'high',
                'category': 'warning'
            },
            'optimize': {
                'patterns': [r'OPTIMIZE\s*:?\s*(.*)'],
                'priority': 'medium',
                'category': 'performance'
            },
            'note': {
                'patterns': [r'NOTE\s*:?\s*(.*)'],
                'priority': 'low',
                'category': 'info'
            },
            'deprecated': {
                'patterns': [r'DEPRECATED\s*:?\s*(.*)'],
                'priority': 'high',
                'category': 'maintenance'
            }
        }
        
        # Patrones de comentarios de calidad
        self.quality_patterns = {
            'obvious': [
                r'#\s*(?:increment|decrement|add|subtract|return|print|loop|iterate)',
                r'//\s*(?:get|set|check|validate|open|close|start|end)\s*$',
                r'#\s*\w+\s*=\s*\w+',  # i = 0
            ],
            'meaningful': [
                r'(?:why|because|reason|explanation|note|important|warning)',
                r'(?:algorithm|approach|strategy|optimization|workaround)',
                r'(?:see|refer|reference|based on|according to)',
            ],
            'code_smell': [
                r'(?:don\'t|dont|never|always|must|should)\s+(?:change|modify|touch)',
                r'(?:magic|hardcoded|hard-coded|temporary|temp)\s+(?:number|value|fix)',
                r'(?:not sure|don\'t know|dont know|maybe|probably|i think)',
            ]
        }
    
    def analyze_comments(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza comentarios y TODOs en los archivos.
        
        Args:
            files: Diccionario con rutas y contenido de archivos
            
        Returns:
            Diccionario con análisis de comentarios
        """
        results = {
            'markers': defaultdict(list),
            'comment_metrics': {
                'total_comments': 0,
                'total_lines': 0,
                'comment_ratio': 0.0,
                'avg_comment_length': 0,
                'documentation_coverage': 0.0
            },
            'comment_quality': {
                'obvious_comments': [],
                'meaningful_comments': [],
                'code_smells': []
            },
            'by_priority': defaultdict(int),
            'by_category': defaultdict(int),
            'comment_score': 0,
            'recommendations': []
        }
        
        total_comment_chars = 0
        total_functions = 0
        documented_functions = 0
        
        # Analizar cada archivo
        for file_path, content in files.items():
            language = self._detect_language(file_path)
            if not language:
                continue
            
            # Extraer todos los comentarios
            comments = self._extract_comments(content, language)
            results['comment_metrics']['total_comments'] += len(comments)
            
            # Contar líneas totales
            lines = content.split('\n')
            results['comment_metrics']['total_lines'] += len(lines)
            
            # Analizar cada comentario
            for comment_text, line_num, comment_type in comments:
                total_comment_chars += len(comment_text)
                
                # Buscar marcadores
                markers_found = self._find_markers(comment_text, file_path, line_num)
                for marker_type, marker_data in markers_found.items():
                    results['markers'][marker_type].extend(marker_data)
                    priority = self.markers[marker_type]['priority']
                    category = self.markers[marker_type]['category']
                    results['by_priority'][priority] += len(marker_data)
                    results['by_category'][category] += len(marker_data)
                
                # Evaluar calidad del comentario
                quality = self._evaluate_comment_quality(comment_text)
                if quality['is_obvious']:
                    results['comment_quality']['obvious_comments'].append({
                        'file': file_path,
                        'line': line_num,
                        'comment': comment_text[:100]
                    })
                if quality['is_meaningful']:
                    results['comment_quality']['meaningful_comments'].append({
                        'file': file_path,
                        'line': line_num,
                        'comment': comment_text[:100]
                    })
                if quality['has_code_smell']:
                    results['comment_quality']['code_smells'].append({
                        'file': file_path,
                        'line': line_num,
                        'comment': comment_text[:100],
                        'issue': quality['smell_type']
                    })
            
            # Calcular cobertura de documentación
            functions = self._find_functions(content, language)
            total_functions += len(functions)
            documented = self._count_documented_functions(content, functions, language)
            documented_functions += documented
        
        # Calcular métricas finales
        if results['comment_metrics']['total_lines'] > 0:
            results['comment_metrics']['comment_ratio'] = (
                results['comment_metrics']['total_comments'] / 
                results['comment_metrics']['total_lines'] * 100
            )
        
        if results['comment_metrics']['total_comments'] > 0:
            results['comment_metrics']['avg_comment_length'] = (
                total_comment_chars / results['comment_metrics']['total_comments']
            )
        
        if total_functions > 0:
            results['comment_metrics']['documentation_coverage'] = (
                documented_functions / total_functions * 100
            )
        
        # Calcular score y recomendaciones
        results['comment_score'] = self._calculate_comment_score(results)
        results['recommendations'] = self._generate_recommendations(results)
        results['summary'] = self._generate_summary(results)
        
        # Agregar el score a las métricas para compatibilidad
        results['comment_metrics']['comment_quality_score'] = results['comment_score']
        results['comment_metrics']['total_functions'] = total_functions
        
        return results
    
    def _detect_language(self, file_path: str) -> str:
        """Detecta el lenguaje basado en la extensión"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        import os
        ext = os.path.splitext(file_path)[1].lower()
        return ext_map.get(ext)
    
    def _extract_comments(self, content: str, language: str) -> List[Tuple[str, int, str]]:
        """Extrae todos los comentarios del contenido"""
        comments = []
        
        # Comentarios de una línea
        if language in self.comment_patterns['single_line']:
            pattern = self.comment_patterns['single_line'][language]
            for match in re.finditer(pattern, content, re.MULTILINE):
                line_num = content[:match.start()].count('\n') + 1
                comment_text = match.group(1).strip()
                if comment_text:
                    comments.append((comment_text, line_num, 'single'))
        
        # Comentarios multilínea
        if language in self.comment_patterns['multi_line']:
            pattern = self.comment_patterns['multi_line'][language]
            for match in re.finditer(pattern, content, re.DOTALL):
                line_num = content[:match.start()].count('\n') + 1
                comment_text = match.group(1).strip()
                if comment_text:
                    comments.append((comment_text, line_num, 'multi'))
        
        return comments
    
    def _find_markers(self, comment_text: str, file_path: str, line_num: int) -> Dict[str, List[Dict]]:
        """Busca marcadores especiales en el comentario"""
        found_markers = defaultdict(list)
        
        for marker_type, marker_def in self.markers.items():
            for pattern in marker_def['patterns']:
                matches = re.finditer(pattern, comment_text, re.IGNORECASE)
                for match in matches:
                    description = match.group(1).strip() if match.lastindex else ''
                    found_markers[marker_type].append({
                        'file': file_path,
                        'line': line_num,
                        'type': marker_type,
                        'description': description,
                        'priority': marker_def['priority'],
                        'category': marker_def['category']
                    })
        
        return found_markers
    
    def _evaluate_comment_quality(self, comment_text: str) -> Dict[str, Any]:
        """Evalúa la calidad de un comentario"""
        quality = {
            'is_obvious': False,
            'is_meaningful': False,
            'has_code_smell': False,
            'smell_type': None
        }
        
        comment_lower = comment_text.lower()
        
        # Detectar comentarios obvios
        for pattern in self.quality_patterns['obvious']:
            if re.search(pattern, comment_text, re.IGNORECASE):
                quality['is_obvious'] = True
                break
        
        # Detectar comentarios significativos
        for pattern in self.quality_patterns['meaningful']:
            if re.search(pattern, comment_lower):
                quality['is_meaningful'] = True
                break
        
        # Detectar code smells en comentarios
        for pattern in self.quality_patterns['code_smell']:
            if re.search(pattern, comment_lower):
                quality['has_code_smell'] = True
                quality['smell_type'] = 'suspicious_comment'
                break
        
        return quality
    
    def _find_functions(self, content: str, language: str) -> List[Tuple[str, int]]:
        """Encuentra todas las funciones/métodos en el código"""
        functions = []
        
        patterns = {
            'python': r'def\s+(\w+)\s*\(',
            'javascript': r'function\s+(\w+)\s*\(|(\w+)\s*:\s*function\s*\(|(\w+)\s*=\s*\([^)]*\)\s*=>',
            'java': r'(?:public|private|protected)\s+\w+\s+(\w+)\s*\(',
            'csharp': r'(?:public|private|protected)\s+\w+\s+(\w+)\s*\(',
            'go': r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(',
            'ruby': r'def\s+(\w+)',
            'php': r'function\s+(\w+)\s*\('
        }
        
        if language in patterns:
            for match in re.finditer(patterns[language], content, re.MULTILINE):
                func_name = match.group(1) or match.group(2) or match.group(3)
                if func_name:
                    line_num = content[:match.start()].count('\n') + 1
                    functions.append((func_name, line_num))
        
        return functions
    
    def _count_documented_functions(self, content: str, functions: List[Tuple[str, int]], language: str) -> int:
        """Cuenta funciones que tienen documentación"""
        documented = 0
        lines = content.split('\n')
        
        for func_name, line_num in functions:
            # Buscar comentario/docstring antes de la función
            has_doc = False
            
            # Revisar líneas anteriores
            for i in range(max(0, line_num - 5), line_num - 1):
                if i < len(lines):
                    line = lines[i].strip()
                    # Detectar docstrings o comentarios de documentación
                    if language == 'python' and '"""' in line:
                        has_doc = True
                        break
                    elif language in ['javascript', 'java'] and '/**' in line:
                        has_doc = True
                        break
                    elif line.startswith('#') or line.startswith('//'):
                        # Comentario simple también cuenta
                        has_doc = True
                        break
            
            if has_doc:
                documented += 1
        
        return documented
    
    def _calculate_comment_score(self, results: Dict[str, Any]) -> float:
        """Calcula un score basado en la calidad de comentarios"""
        score = 50.0  # Base
        
        # Ratio de comentarios (ideal: 15-25%)
        ratio = results['comment_metrics']['comment_ratio']
        if 15 <= ratio <= 25:
            score += 20
        elif 10 <= ratio <= 30:
            score += 10
        elif ratio < 5:
            score -= 20
        elif ratio > 40:
            score -= 10  # Demasiados comentarios también es malo
        
        # Cobertura de documentación
        doc_coverage = results['comment_metrics']['documentation_coverage']
        score += doc_coverage * 0.3  # Máx +30
        
        # Penalizar por TODOs y FIXMEs
        critical_count = results['by_priority'].get('critical', 0)
        high_count = results['by_priority'].get('high', 0)
        medium_count = results['by_priority'].get('medium', 0)
        
        score -= critical_count * 5
        score -= high_count * 3
        score -= medium_count * 1
        
        # Penalizar por comentarios obvios
        obvious_count = len(results['comment_quality']['obvious_comments'])
        if obvious_count > 10:
            score -= 10
        elif obvious_count > 5:
            score -= 5
        
        # Bonus por comentarios significativos
        meaningful_count = len(results['comment_quality']['meaningful_comments'])
        score += min(meaningful_count * 0.5, 10)  # Máx +10
        
        # Penalizar por code smells
        smell_count = len(results['comment_quality']['code_smells'])
        score -= smell_count * 2
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones por ratio de comentarios
        ratio = results['comment_metrics']['comment_ratio']
        if ratio < 10:
            recommendations.append({
                'type': 'documentation',
                'priority': 'high',
                'title': 'Aumentar documentación',
                'description': 'El código tiene muy pocos comentarios. Agregue comentarios explicativos para lógica compleja.'
            })
        elif ratio > 35:
            recommendations.append({
                'type': 'documentation',
                'priority': 'low',
                'title': 'Revisar exceso de comentarios',
                'description': 'Hay demasiados comentarios. Considere si todos son necesarios o si el código puede ser más autodocumentado.'
            })
        
        # Recomendaciones por cobertura de documentación
        if results['comment_metrics']['documentation_coverage'] < 50:
            recommendations.append({
                'type': 'documentation',
                'priority': 'medium',
                'title': 'Documentar funciones públicas',
                'description': 'Muchas funciones carecen de documentación. Agregue docstrings o comentarios de documentación.'
            })
        
        # Recomendaciones por marcadores
        if results['by_priority'].get('critical', 0) > 0:
            recommendations.append({
                'type': 'maintenance',
                'priority': 'critical',
                'title': 'Resolver BUGs marcados',
                'description': f"Se encontraron {results['by_priority']['critical']} marcadores críticos (BUG) que requieren atención inmediata."
            })
        
        if results['by_priority'].get('high', 0) > 5:
            recommendations.append({
                'type': 'maintenance',
                'priority': 'high',
                'title': 'Revisar FIXMEs y HACKs',
                'description': f"Hay {results['by_priority']['high']} elementos de alta prioridad pendientes. Planifique su resolución."
            })
        
        # Recomendaciones por calidad
        if len(results['comment_quality']['obvious_comments']) > 5:
            recommendations.append({
                'type': 'quality',
                'priority': 'low',
                'title': 'Eliminar comentarios obvios',
                'description': 'Se detectaron comentarios que no agregan valor. El código debe ser autodocumentado cuando sea posible.'
            })
        
        if len(results['comment_quality']['code_smells']) > 0:
            recommendations.append({
                'type': 'quality',
                'priority': 'medium',
                'title': 'Revisar comentarios sospechosos',
                'description': 'Algunos comentarios indican incertidumbre o soluciones temporales. Revise y mejore el código correspondiente.'
            })
        
        return recommendations
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Genera un resumen del análisis de comentarios"""
        total_markers = sum(len(markers) for markers in results['markers'].values())
        ratio = results['comment_metrics']['comment_ratio']
        doc_coverage = results['comment_metrics']['documentation_coverage']
        
        summary = f"El código tiene un {ratio:.1f}% de líneas comentadas"
        
        if ratio < 10:
            summary += " (muy bajo)"
        elif ratio > 30:
            summary += " (muy alto)"
        else:
            summary += " (adecuado)"
        
        summary += f" con {doc_coverage:.1f}% de funciones documentadas."
        
        if total_markers > 0:
            summary += f" Se encontraron {total_markers} marcadores:"
            for marker_type, count in [(k, len(v)) for k, v in results['markers'].items() if v]:
                summary += f" {count} {marker_type.upper()},"
            summary = summary.rstrip(',') + "."
        
        score = results['comment_score']
        if score >= 80:
            summary += " Excelente calidad de documentación."
        elif score >= 60:
            summary += " Buena documentación con áreas de mejora."
        else:
            summary += " La documentación necesita mejoras significativas."
        
        return summary