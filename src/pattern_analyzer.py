"""
Analizador de patrones de diseño y anti-patrones.

Este módulo detecta patrones de diseño comunes y anti-patrones
en el código fuente de múltiples lenguajes.

Classes:
    PatternAnalyzer: Analizador principal de patrones.

Features:
    - Detección de patrones de diseño (Singleton, Factory, Observer, etc.)
    - Identificación de anti-patrones
    - Análisis de estructura y organización

Author: R. Benítez
Version: 2.0.0
License: MIT
"""

import re
from typing import Dict, List, Any, Set
from collections import defaultdict


class PatternAnalyzer:
    """Analizador de patrones de diseño y anti-patrones"""
    
    def __init__(self):
        """Inicializa el analizador con definiciones de patrones"""
        # Patrones de diseño por lenguaje
        self.design_patterns = {
            'singleton': {
                'python': [
                    r'class\s+\w+.*:\s*\n\s*_instance\s*=\s*None',
                    r'def\s+__new__\s*\(\s*cls.*\).*:\s*\n.*if.*not.*cls\._instance',
                    r'@singleton',
                ],
                'javascript': [
                    r'class\s+\w+\s*{\s*static\s+instance',
                    r'let\s+instance\s*=\s*null.*getInstance',
                    r'const\s+\w+\s*=\s*\(\s*\)\s*=>\s*{\s*let\s+instance',
                ],
                'java': [
                    r'private\s+static\s+\w+\s+instance',
                    r'public\s+static\s+\w+\s+getInstance',
                    r'private\s+\w+\s*\(\s*\)\s*{\s*}.*getInstance',
                ]
            },
            'factory': {
                'python': [
                    r'class\s+\w*Factory\w*.*:',
                    r'def\s+create_\w+\s*\(',
                    r'def\s+factory_method\s*\(',
                ],
                'javascript': [
                    r'class\s+\w*Factory\w*',
                    r'create[A-Z]\w+\s*\(',
                    r'function\s+\w*[Ff]actory\w*',
                ],
                'java': [
                    r'class\s+\w*Factory\w*',
                    r'public\s+\w+\s+create\w+',
                    r'interface\s+\w*Factory\w*',
                ]
            },
            'observer': {
                'python': [
                    r'def\s+attach\s*\(\s*self.*observer',
                    r'def\s+notify\s*\(\s*self',
                    r'class\s+\w*Observer\w*.*:',
                    r'def\s+update\s*\(\s*self.*subject',
                ],
                'javascript': [
                    r'subscribe\s*\(',
                    r'addEventListener\s*\(',
                    r'on\s*\(\s*[\'"]?\w+[\'"]?\s*,',
                    r'emit\s*\(',
                ],
                'java': [
                    r'interface\s+\w*Observer\w*',
                    r'void\s+update\s*\(',
                    r'addObserver\s*\(',
                    r'notifyObservers\s*\(',
                ]
            },
            'decorator': {
                'python': [
                    r'@\w+\s*\n\s*def\s+\w+',
                    r'def\s+\w+\s*\(\s*func\s*\)',
                    r'@property',
                    r'@staticmethod',
                    r'@classmethod',
                ],
                'javascript': [
                    r'@\w+\s*\n\s*\w+',
                    r'function\s+\w+Decorator',
                ],
                'java': [
                    r'@\w+\s*\n\s*public',
                    r'@Override',
                    r'@Deprecated',
                ]
            },
            'strategy': {
                'python': [
                    r'class\s+\w*Strategy\w*.*:',
                    r'def\s+execute_strategy\s*\(',
                    r'def\s+set_strategy\s*\(',
                ],
                'javascript': [
                    r'class\s+\w*Strategy\w*',
                    r'setStrategy\s*\(',
                    r'executeStrategy\s*\(',
                ],
                'java': [
                    r'interface\s+\w*Strategy\w*',
                    r'void\s+execute\s*\(',
                    r'setStrategy\s*\(',
                ]
            }
        }
        
        # Anti-patrones
        self.anti_patterns = {
            'god_class': {
                'indicators': [
                    'too_many_methods',  # > 20 métodos
                    'too_many_lines',    # > 500 líneas
                    'too_many_dependencies'  # > 10 imports
                ]
            },
            'spaghetti_code': {
                'patterns': [
                    r'goto\s+\w+',  # GOTOs
                    r'if.*:\s*\n\s*if.*:\s*\n\s*if.*:',  # Nested ifs profundos
                    r'while.*:\s*\n\s*while.*:\s*\n\s*while.*:',  # Nested loops
                ]
            },
            'copy_paste': {
                'indicators': [
                    'high_duplication',  # Detectado por duplication analyzer
                    'similar_method_names'
                ]
            },
            'magic_numbers': {
                'patterns': [
                    r'if\s+.*[><=]\s*\d{2,}',  # Números mágicos en condiciones
                    r'return\s+\d{2,}',  # Números mágicos en returns
                    r'=\s*\d{2,}[^\d\.]',  # Asignaciones con números mágicos
                ]
            },
            'long_method': {
                'indicators': [
                    'method_lines > 50'  # Métodos muy largos
                ]
            }
        }
        
        # Estructura y organización
        self.structure_patterns = {
            'mvc': {
                'folders': ['models', 'views', 'controllers'],
                'files': [r'.*model.*', r'.*view.*', r'.*controller.*']
            },
            'layered': {
                'folders': ['presentation', 'business', 'data', 'domain'],
                'files': [r'.*service.*', r'.*repository.*', r'.*dto.*']
            },
            'clean': {
                'folders': ['entities', 'usecases', 'interfaces', 'infrastructure'],
                'files': [r'.*entity.*', r'.*usecase.*', r'.*interface.*']
            },
            'modular': {
                'indicators': [
                    'separate_concerns',
                    'low_coupling',
                    'high_cohesion'
                ]
            }
        }
    
    def analyze_patterns(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza patrones de diseño en los archivos.
        
        Args:
            files: Diccionario con rutas y contenido de archivos
            
        Returns:
            Diccionario con patrones detectados y métricas
        """
        results = {
            'design_patterns': defaultdict(list),
            'anti_patterns': defaultdict(list),
            'structure_analysis': {},
            'pattern_score': 0,
            'recommendations': []
        }
        
        # Analizar cada archivo
        for file_path, content in files.items():
            language = self._detect_language(file_path)
            if language:
                # Detectar patrones de diseño
                design_patterns = self._detect_design_patterns(content, language, file_path)
                for pattern, locations in design_patterns.items():
                    results['design_patterns'][pattern].extend(locations)
                
                # Detectar anti-patrones
                anti_patterns = self._detect_anti_patterns(content, file_path)
                for pattern, locations in anti_patterns.items():
                    results['anti_patterns'][pattern].extend(locations)
        
        # Analizar estructura del proyecto
        results['structure_analysis'] = self._analyze_structure(list(files.keys()))
        
        # Calcular score y recomendaciones
        results['pattern_score'] = self._calculate_pattern_score(results)
        results['recommendations'] = self._generate_recommendations(results)
        
        # Resumen
        results['summary'] = self._generate_summary(results)
        
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
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        import os
        ext = os.path.splitext(file_path)[1].lower()
        return ext_map.get(ext)
    
    def _detect_design_patterns(self, content: str, language: str, file_path: str) -> Dict[str, List[Dict]]:
        """Detecta patrones de diseño en el contenido"""
        found_patterns = defaultdict(list)
        
        for pattern_name, pattern_def in self.design_patterns.items():
            if language in pattern_def:
                patterns = pattern_def[language]
                
                for pattern_regex in patterns:
                    matches = re.finditer(pattern_regex, content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        found_patterns[pattern_name].append({
                            'file': file_path,
                            'line': line_num,
                            'pattern': pattern_name,
                            'confidence': 0.8,  # Confianza base
                            'snippet': match.group(0)[:100]
                        })
        
        return found_patterns
    
    def _detect_anti_patterns(self, content: str, file_path: str) -> Dict[str, List[Dict]]:
        """Detecta anti-patrones en el contenido"""
        found_anti_patterns = defaultdict(list)
        lines = content.split('\n')
        
        # God Class - archivo muy largo
        if len(lines) > 500:
            found_anti_patterns['god_class'].append({
                'file': file_path,
                'issue': 'Archivo muy largo',
                'lines': len(lines),
                'severity': 'high' if len(lines) > 1000 else 'medium'
            })
        
        # Spaghetti code - anidamiento profundo
        max_nesting = self._calculate_max_nesting(content)
        if max_nesting > 4:
            found_anti_patterns['spaghetti_code'].append({
                'file': file_path,
                'issue': 'Anidamiento muy profundo',
                'max_nesting': max_nesting,
                'severity': 'high' if max_nesting > 6 else 'medium'
            })
        
        # Magic numbers
        magic_patterns = self.anti_patterns['magic_numbers']['patterns']
        for pattern in magic_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                found_anti_patterns['magic_numbers'].append({
                    'file': file_path,
                    'line': line_num,
                    'issue': 'Número mágico detectado',
                    'snippet': match.group(0),
                    'severity': 'low'
                })
        
        # Long methods (simplificado)
        method_pattern = r'def\s+\w+.*:|function\s+\w+.*{|public\s+\w+\s+\w+.*{'
        methods = list(re.finditer(method_pattern, content, re.MULTILINE))
        
        for i, method in enumerate(methods):
            start_line = content[:method.start()].count('\n') + 1
            # Estimar fin del método (siguiente método o fin de archivo)
            end_pos = methods[i+1].start() if i+1 < len(methods) else len(content)
            method_lines = content[method.start():end_pos].count('\n')
            
            if method_lines > 50:
                found_anti_patterns['long_method'].append({
                    'file': file_path,
                    'line': start_line,
                    'issue': 'Método muy largo',
                    'lines': method_lines,
                    'severity': 'high' if method_lines > 100 else 'medium'
                })
        
        return found_anti_patterns
    
    def _calculate_max_nesting(self, content: str) -> int:
        """Calcula el nivel máximo de anidamiento"""
        lines = content.split('\n')
        max_nesting = 0
        current_nesting = 0
        
        for line in lines:
            # Contar indentación (asumiendo 4 espacios o 1 tab)
            indent = len(line) - len(line.lstrip())
            nesting_level = indent // 4 if indent % 4 == 0 else indent
            
            # Detectar bloques
            if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'def ', 'class ', 'function ', 'try']):
                current_nesting = nesting_level + 1
                max_nesting = max(max_nesting, current_nesting)
        
        return max_nesting
    
    def _analyze_structure(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analiza la estructura y organización del proyecto"""
        import os
        
        structure = {
            'architecture_type': 'unknown',
            'organization_score': 0,
            'folder_structure': defaultdict(int),
            'file_organization': {}
        }
        
        # Analizar estructura de carpetas
        folders = set()
        for path in file_paths:
            parts = path.split('/')
            if len(parts) > 1:
                folders.update(parts[:-1])
        
        # Detectar arquitectura
        for arch_type, patterns in self.structure_patterns.items():
            if arch_type in ['mvc', 'layered', 'clean']:
                matching_folders = sum(1 for folder in patterns['folders'] if any(folder in f.lower() for f in folders))
                if matching_folders >= len(patterns['folders']) * 0.6:  # 60% match
                    structure['architecture_type'] = arch_type
                    break
        
        # Calcular score de organización
        total_files = len(file_paths)
        organized_files = 0
        
        for path in file_paths:
            # Archivos en carpetas apropiadas
            if '/' in path:  # No en raíz
                organized_files += 1
            
            # Nombres descriptivos
            filename = os.path.basename(path).lower()
            if any(pattern in filename for pattern in ['test', 'spec', 'model', 'view', 'controller', 'service', 'util']):
                organized_files += 0.5
        
        structure['organization_score'] = (organized_files / total_files * 100) if total_files > 0 else 0
        
        # Distribución de archivos por carpeta
        for path in file_paths:
            folder = os.path.dirname(path) or 'root'
            structure['folder_structure'][folder] += 1
        
        return structure
    
    def _calculate_pattern_score(self, results: Dict[str, Any]) -> float:
        """Calcula un score basado en patrones encontrados"""
        score = 50.0  # Base
        
        # Bonus por patrones de diseño
        design_patterns_count = sum(len(locations) for locations in results['design_patterns'].values())
        score += min(design_patterns_count * 5, 30)  # Máx +30
        
        # Penalización por anti-patrones
        for pattern_type, instances in results['anti_patterns'].items():
            for instance in instances:
                severity = instance.get('severity', 'low')
                if severity == 'high':
                    score -= 10
                elif severity == 'medium':
                    score -= 5
                else:
                    score -= 2
        
        # Bonus por buena organización
        org_score = results['structure_analysis']['organization_score']
        score += org_score * 0.2  # Máx +20
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones por anti-patrones
        if results['anti_patterns']['god_class']:
            recommendations.append({
                'type': 'refactoring',
                'priority': 'high',
                'title': 'Refactorizar clases grandes',
                'description': 'Se detectaron clases/archivos muy grandes. Considere dividirlos en componentes más pequeños y cohesivos.'
            })
        
        if results['anti_patterns']['spaghetti_code']:
            recommendations.append({
                'type': 'refactoring',
                'priority': 'high',
                'title': 'Reducir complejidad de código',
                'description': 'Se detectó código con anidamiento muy profundo. Considere extraer métodos y simplificar la lógica.'
            })
        
        if results['anti_patterns']['magic_numbers']:
            recommendations.append({
                'type': 'code_quality',
                'priority': 'medium',
                'title': 'Eliminar números mágicos',
                'description': 'Reemplace números mágicos con constantes nombradas para mejorar la legibilidad.'
            })
        
        if results['anti_patterns']['long_method']:
            recommendations.append({
                'type': 'refactoring',
                'priority': 'medium',
                'title': 'Dividir métodos largos',
                'description': 'Se detectaron métodos muy largos. Considere dividirlos en métodos más pequeños y específicos.'
            })
        
        # Recomendaciones por falta de patrones
        if not results['design_patterns']:
            recommendations.append({
                'type': 'architecture',
                'priority': 'low',
                'title': 'Considerar patrones de diseño',
                'description': 'No se detectaron patrones de diseño comunes. Evalúe si algún patrón podría mejorar la arquitectura.'
            })
        
        # Recomendaciones de estructura
        if results['structure_analysis']['organization_score'] < 60:
            recommendations.append({
                'type': 'organization',
                'priority': 'medium',
                'title': 'Mejorar organización de archivos',
                'description': 'La estructura del proyecto podría mejorarse. Considere organizar archivos en carpetas temáticas.'
            })
        
        return recommendations
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Genera un resumen del análisis de patrones"""
        design_count = sum(len(locations) for locations in results['design_patterns'].values())
        anti_count = sum(len(instances) for instances in results['anti_patterns'].values())
        
        summary = f"Se detectaron {design_count} instancias de patrones de diseño"
        
        if design_count > 0:
            patterns = list(results['design_patterns'].keys())
            summary += f" ({', '.join(patterns)})"
        
        summary += f" y {anti_count} posibles anti-patrones."
        
        arch_type = results['structure_analysis']['architecture_type']
        if arch_type != 'unknown':
            summary += f" La arquitectura parece seguir un patrón {arch_type.upper()}."
        
        score = results['pattern_score']
        if score >= 80:
            summary += " Excelente uso de patrones de diseño."
        elif score >= 60:
            summary += " Buen uso de patrones con algunas áreas de mejora."
        else:
            summary += " Se recomienda revisar la arquitectura y patrones utilizados."
        
        return summary