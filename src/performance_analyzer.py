"""
Analizador de métricas de rendimiento.

Este módulo detecta posibles problemas de rendimiento y operaciones costosas
en el código fuente.

Classes:
    PerformanceAnalyzer: Analizador principal de rendimiento.

Features:
    - Detección de operaciones costosas
    - Identificación de cuellos de botella
    - Análisis de complejidad algorítmica

Author: R. Benítez
Version: 2.0.0
License: MIT
"""

import re
from typing import Dict, List, Any
from collections import defaultdict


class PerformanceAnalyzer:
    """Analizador de métricas de rendimiento y operaciones costosas"""
    
    def __init__(self):
        """Inicializa el analizador con patrones de rendimiento"""
        # Patrones de operaciones costosas
        self.expensive_patterns = {
            'nested_loops': {
                'patterns': [
                    # Python
                    r'for\s+.*:\s*\n\s*.*for\s+.*:',
                    r'while\s+.*:\s*\n\s*.*while\s+.*:',
                    # JavaScript/Java/C++
                    r'for\s*\(.*\)\s*{\s*\n\s*.*for\s*\(.*\)',
                    r'while\s*\(.*\)\s*{\s*\n\s*.*while\s*\(.*\)',
                ],
                'severity': 'high',
                'complexity': 'O(n²)'
            },
            'triple_nested_loops': {
                'patterns': [
                    # Python
                    r'for\s+.*:\s*\n\s*.*for\s+.*:\s*\n\s*.*for\s+.*:',
                    # JavaScript/Java/C++
                    r'for\s*\(.*\)\s*{\s*\n\s*.*for\s*\(.*\)\s*{\s*\n\s*.*for\s*\(.*\)',
                ],
                'severity': 'critical',
                'complexity': 'O(n³)'
            },
            'recursive_calls': {
                'patterns': [
                    # Detectar funciones que se llaman a sí mismas
                    r'def\s+(\w+)\s*\(.*\):\s*\n(?:.*\n)*?\s*\1\s*\(',
                    r'function\s+(\w+)\s*\(.*\)\s*{\s*\n(?:.*\n)*?\s*\1\s*\(',
                ],
                'severity': 'medium',
                'complexity': 'Varies'
            },
            'inefficient_string_concat': {
                'patterns': [
                    # Python - concatenación en loops
                    r'for\s+.*:\s*\n\s*.*\+=\s*["\']',
                    r'while\s+.*:\s*\n\s*.*\+=\s*["\']',
                    # JavaScript
                    r'for\s*\(.*\)\s*{\s*\n\s*.*\+=\s*["\']',
                ],
                'severity': 'medium',
                'complexity': 'O(n²) for strings'
            },
            'database_in_loop': {
                'patterns': [
                    # Queries en loops
                    r'for\s+.*:\s*\n\s*.*(?:query|select|insert|update|delete)',
                    r'while\s+.*:\s*\n\s*.*(?:query|select|insert|update|delete)',
                    r'\.find\(\).*for\s+',  # MongoDB
                    r'\.execute\(\).*for\s+',  # SQL
                ],
                'severity': 'critical',
                'complexity': 'O(n) DB calls'
            },
            'inefficient_list_operations': {
                'patterns': [
                    # Python - operaciones costosas en listas
                    r'\.insert\(0,',  # Insert al inicio O(n)
                    r'in\s+.*for\s+.*in\s+.*for',  # Búsqueda anidada
                    r'\.remove\(.*\)\s*.*for',  # Remove en loop
                ],
                'severity': 'medium',
                'complexity': 'O(n) or worse'
            },
            'synchronous_io': {
                'patterns': [
                    # Operaciones síncronas bloqueantes
                    r'open\s*\(.*\)\.read\(\)',
                    r'requests\.get\s*\(',
                    r'time\.sleep\s*\(',
                    r'input\s*\(',
                ],
                'severity': 'low',
                'complexity': 'Blocking I/O'
            }
        }
        
        # Patrones de optimización
        self.optimization_patterns = {
            'caching': [
                r'@cache',
                r'@memoize',
                r'@lru_cache',
                r'cache\[',
                r'memo\[',
            ],
            'async_operations': [
                r'async\s+def',
                r'await\s+',
                r'Promise\.',
                r'async\s+function',
            ],
            'bulk_operations': [
                r'executemany',
                r'bulk_create',
                r'batch',
                r'chunk',
            ],
            'efficient_data_structures': [
                r'set\s*\(',
                r'dict\s*\(',
                r'defaultdict',
                r'Counter\(',
                r'deque\(',
            ]
        }
    
    def analyze_performance(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza métricas de rendimiento en los archivos.
        
        Args:
            files: Diccionario con rutas y contenido de archivos
            
        Returns:
            Diccionario con problemas de rendimiento detectados
        """
        results = {
            'performance_issues': defaultdict(list),
            'optimizations_found': defaultdict(list),
            'complexity_analysis': {},
            'performance_score': 0,
            'recommendations': [],
            'hotspots': []  # Archivos con más problemas
        }
        
        file_issues = defaultdict(int)
        
        # Analizar cada archivo
        for file_path, content in files.items():
            # Detectar problemas de rendimiento
            issues = self._detect_performance_issues(content, file_path)
            for issue_type, locations in issues.items():
                results['performance_issues'][issue_type].extend(locations)
                file_issues[file_path] += len(locations)
            
            # Detectar optimizaciones existentes
            optimizations = self._detect_optimizations(content, file_path)
            for opt_type, locations in optimizations.items():
                results['optimizations_found'][opt_type].extend(locations)
            
            # Análisis de complejidad
            complexity = self._analyze_complexity(content, file_path)
            if complexity['max_complexity'] > 10:  # Alta complejidad
                results['complexity_analysis'][file_path] = complexity
        
        # Identificar hotspots
        results['hotspots'] = [
            {'file': file, 'issues_count': count}
            for file, count in sorted(file_issues.items(), key=lambda x: x[1], reverse=True)[:5]
            if count > 0
        ]
        
        # Calcular score y recomendaciones
        results['performance_score'] = self._calculate_performance_score(results)
        results['recommendations'] = self._generate_recommendations(results)
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _detect_performance_issues(self, content: str, file_path: str) -> Dict[str, List[Dict]]:
        """Detecta problemas de rendimiento en el contenido"""
        found_issues = defaultdict(list)
        
        for issue_type, issue_def in self.expensive_patterns.items():
            patterns = issue_def['patterns']
            
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        found_issues[issue_type].append({
                            'file': file_path,
                            'line': line_num,
                            'type': issue_type,
                            'severity': issue_def['severity'],
                            'complexity': issue_def['complexity'],
                            'snippet': match.group(0)[:100].replace('\n', ' ')
                        })
                except re.error:
                    continue
        
        return found_issues
    
    def _detect_optimizations(self, content: str, file_path: str) -> Dict[str, List[Dict]]:
        """Detecta optimizaciones ya implementadas"""
        found_optimizations = defaultdict(list)
        
        for opt_type, patterns in self.optimization_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    found_optimizations[opt_type].append({
                        'file': file_path,
                        'line': line_num,
                        'type': opt_type,
                        'snippet': match.group(0)
                    })
        
        return found_optimizations
    
    def _analyze_complexity(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analiza la complejidad ciclomática del código"""
        complexity_data = {
            'max_complexity': 0,
            'avg_complexity': 0,
            'complex_functions': []
        }
        
        # Detectar funciones/métodos
        function_pattern = r'(?:def|function|public\s+\w+|private\s+\w+)\s+(\w+)\s*\([^)]*\)\s*[:{]'
        functions = list(re.finditer(function_pattern, content, re.MULTILINE))
        
        complexities = []
        
        for i, func_match in enumerate(functions):
            func_name = func_match.group(1)
            func_start = func_match.start()
            
            # Estimar fin de la función
            func_end = functions[i+1].start() if i+1 < len(functions) else len(content)
            func_content = content[func_start:func_end]
            
            # Calcular complejidad ciclomática (simplificado)
            complexity = 1  # Base
            
            # Contar estructuras de control
            control_structures = [
                r'\bif\b', r'\belif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
                r'\btry\b', r'\bcatch\b', r'\bcase\b', r'\b\?\s*:', r'&&', r'\|\|'
            ]
            
            for pattern in control_structures:
                complexity += len(re.findall(pattern, func_content))
            
            complexities.append(complexity)
            
            if complexity > 10:  # Alta complejidad
                line_num = content[:func_start].count('\n') + 1
                complexity_data['complex_functions'].append({
                    'name': func_name,
                    'line': line_num,
                    'complexity': complexity
                })
        
        if complexities:
            complexity_data['max_complexity'] = max(complexities)
            complexity_data['avg_complexity'] = sum(complexities) / len(complexities)
        
        return complexity_data
    
    def _calculate_performance_score(self, results: Dict[str, Any]) -> float:
        """Calcula un score de rendimiento"""
        score = 100.0  # Empezar con score perfecto
        
        # Penalizar por problemas de rendimiento
        for issue_type, issues in results['performance_issues'].items():
            issue_def = self.expensive_patterns.get(issue_type, {})
            severity = issue_def.get('severity', 'low')
            
            for issue in issues:
                if severity == 'critical':
                    score -= 15
                elif severity == 'high':
                    score -= 10
                elif severity == 'medium':
                    score -= 5
                else:
                    score -= 2
        
        # Bonus por optimizaciones
        optimization_count = sum(len(opts) for opts in results['optimizations_found'].values())
        score += min(optimization_count * 2, 20)  # Máx +20
        
        # Penalizar por alta complejidad
        for file_data in results['complexity_analysis'].values():
            if file_data['max_complexity'] > 20:
                score -= 10
            elif file_data['max_complexity'] > 15:
                score -= 5
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera recomendaciones de rendimiento"""
        recommendations = []
        
        # Recomendaciones por tipo de problema
        if results['performance_issues']['nested_loops']:
            recommendations.append({
                'type': 'algorithm',
                'priority': 'high',
                'title': 'Optimizar loops anidados',
                'description': 'Se detectaron loops anidados que pueden causar problemas de rendimiento. Considere usar estructuras de datos más eficientes o algoritmos optimizados.',
                'impact': 'Puede reducir complejidad de O(n²) a O(n log n) o mejor'
            })
        
        if results['performance_issues']['database_in_loop']:
            recommendations.append({
                'type': 'database',
                'priority': 'critical',
                'title': 'Evitar queries en loops',
                'description': 'Se detectaron operaciones de base de datos dentro de loops. Use operaciones bulk o carga los datos necesarios antes del loop.',
                'impact': 'Puede reducir llamadas a BD de O(n) a O(1)'
            })
        
        if results['performance_issues']['inefficient_string_concat']:
            recommendations.append({
                'type': 'memory',
                'priority': 'medium',
                'title': 'Optimizar concatenación de strings',
                'description': 'Use StringBuilder, join() o estructuras más eficientes para concatenar strings en loops.',
                'impact': 'Reduce complejidad de O(n²) a O(n)'
            })
        
        if results['performance_issues']['recursive_calls']:
            recommendations.append({
                'type': 'algorithm',
                'priority': 'medium',
                'title': 'Revisar funciones recursivas',
                'description': 'Considere usar iteración o memoización para optimizar funciones recursivas.',
                'impact': 'Previene stack overflow y mejora rendimiento'
            })
        
        # Recomendaciones generales
        if not results['optimizations_found']['caching']:
            recommendations.append({
                'type': 'optimization',
                'priority': 'low',
                'title': 'Implementar caché',
                'description': 'Considere implementar caché para operaciones costosas que se repiten.',
                'impact': 'Puede mejorar rendimiento significativamente'
            })
        
        if not results['optimizations_found']['async_operations'] and results['performance_issues']['synchronous_io']:
            recommendations.append({
                'type': 'concurrency',
                'priority': 'medium',
                'title': 'Usar operaciones asíncronas',
                'description': 'Considere usar async/await para operaciones I/O para evitar bloqueos.',
                'impact': 'Mejora la capacidad de respuesta de la aplicación'
            })
        
        return recommendations
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Genera un resumen del análisis de rendimiento"""
        total_issues = sum(len(issues) for issues in results['performance_issues'].values())
        critical_issues = sum(
            len(issues) for issue_type, issues in results['performance_issues'].items()
            if self.expensive_patterns.get(issue_type, {}).get('severity') == 'critical'
        )
        
        optimizations = sum(len(opts) for opts in results['optimizations_found'].values())
        
        summary = f"Se detectaron {total_issues} posibles problemas de rendimiento"
        
        if critical_issues > 0:
            summary += f" ({critical_issues} críticos)"
        
        summary += f" y {optimizations} optimizaciones implementadas."
        
        if results['hotspots']:
            top_hotspot = results['hotspots'][0]
            summary += f" El archivo con más problemas es {top_hotspot['file']} con {top_hotspot['issues_count']} issues."
        
        score = results['performance_score']
        if score >= 80:
            summary += " El código tiene un buen rendimiento general."
        elif score >= 60:
            summary += " El rendimiento es aceptable pero hay áreas de mejora."
        else:
            summary += " Se recomienda revisar y optimizar el rendimiento del código."
        
        return summary