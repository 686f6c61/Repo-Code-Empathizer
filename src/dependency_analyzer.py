"""
Analizador de dependencias para proyectos multi-lenguaje.

Este módulo implementa análisis básico de dependencias sin APIs externas,
detectando imports, requires y otras formas de dependencias en el código.

Classes:
    DependencyAnalyzer: Analizador principal de dependencias.

Features:
    - Detección de imports/requires por lenguaje
    - Análisis de dependencias internas vs externas
    - Identificación de ciclos de dependencias
    - Métricas de acoplamiento

Author: R. Benítez
Version: 2.0.0
License: MIT
"""

import re
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict
import os


class DependencyAnalyzer:
    """Analizador de dependencias multi-lenguaje"""
    
    def __init__(self):
        """Inicializa el analizador con patrones para cada lenguaje"""
        self.patterns = {
            'python': {
                'import': [
                    r'^\s*import\s+(\S+)',
                    r'^\s*from\s+(\S+)\s+import',
                ],
                'internal_prefix': '.',
                'file_extensions': ['.py']
            },
            'javascript': {
                'import': [
                    r'^\s*import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*import\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*const\s+\w+\s*=\s*require\s*\([\'"]([^\'"]+)[\'"]\)',
                    r'^\s*let\s+\w+\s*=\s*require\s*\([\'"]([^\'"]+)[\'"]\)',
                    r'^\s*var\s+\w+\s*=\s*require\s*\([\'"]([^\'"]+)[\'"]\)',
                    r'^\s*require\s*\([\'"]([^\'"]+)[\'"]\)',
                ],
                'internal_prefix': '.',
                'file_extensions': ['.js', '.jsx', '.mjs']
            },
            'typescript': {
                'import': [
                    r'^\s*import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*import\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*const\s+\w+\s*=\s*require\s*\([\'"]([^\'"]+)[\'"]\)',
                ],
                'internal_prefix': '.',
                'file_extensions': ['.ts', '.tsx']
            },
            'java': {
                'import': [
                    r'^\s*import\s+static\s+(\S+);',
                    r'^\s*import\s+(\S+);',
                ],
                'internal_prefix': None,  # Java usa packages
                'file_extensions': ['.java']
            },
            'go': {
                'import': [
                    r'^\s*import\s+"([^"]+)"',
                    r'^\s*import\s+\(\s*"([^"]+)"',
                ],
                'internal_prefix': '.',
                'file_extensions': ['.go']
            },
            'csharp': {
                'import': [
                    r'^\s*using\s+(\S+);',
                    r'^\s*using\s+static\s+(\S+);',
                ],
                'internal_prefix': None,
                'file_extensions': ['.cs']
            },
            'php': {
                'import': [
                    r'^\s*use\s+(\S+);',
                    r'^\s*require\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*require_once\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*include\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*include_once\s+[\'"]([^\'"]+)[\'"]',
                ],
                'internal_prefix': '.',
                'file_extensions': ['.php']
            },
            'ruby': {
                'import': [
                    r'^\s*require\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*require_relative\s+[\'"]([^\'"]+)[\'"]',
                    r'^\s*load\s+[\'"]([^\'"]+)[\'"]',
                ],
                'internal_prefix': '.',
                'file_extensions': ['.rb']
            }
        }
    
    def analyze_dependencies(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Analiza las dependencias en un conjunto de archivos.
        
        Args:
            files: Diccionario con rutas de archivo como claves y contenido como valores
            
        Returns:
            Diccionario con métricas de dependencias
        """
        dependencies = defaultdict(set)
        file_dependencies = defaultdict(set)
        external_deps = set()
        internal_deps = set()
        
        # Analizar cada archivo
        for file_path, content in files.items():
            language = self._detect_language(file_path)
            if not language:
                continue
                
            deps = self._extract_dependencies(content, language)
            
            for dep in deps:
                dependencies[dep].add(file_path)
                file_dependencies[file_path].add(dep)
                
                # Clasificar como interna o externa
                if self._is_internal_dependency(dep, language):
                    internal_deps.add(dep)
                else:
                    external_deps.add(dep)
        
        # Detectar ciclos de dependencias
        cycles = self._detect_cycles(file_dependencies, files.keys())
        
        # Calcular métricas
        total_files = len(files)
        files_with_deps = len([f for f in file_dependencies if file_dependencies[f]])
        
        metrics = {
            'total_dependencies': len(dependencies),
            'external_dependencies': len(external_deps),
            'internal_dependencies': len(internal_deps),
            'dependency_ratio': files_with_deps / total_files if total_files > 0 else 0,
            'avg_dependencies_per_file': sum(len(deps) for deps in file_dependencies.values()) / total_files if total_files > 0 else 0,
            'most_used_dependencies': self._get_top_dependencies(dependencies, 10),
            'files_with_most_dependencies': self._get_files_with_most_deps(file_dependencies, 5),
            'circular_dependencies': len(cycles),
            'circular_dependency_details': cycles[:5],  # Primeros 5 ciclos
            'external_deps_list': sorted(list(external_deps))[:20],  # Top 20 externas
            'coupling_score': self._calculate_coupling_score(file_dependencies, total_files),
            'summary': self._generate_summary(len(dependencies), len(external_deps), len(internal_deps), len(cycles))
        }
        
        return metrics
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detecta el lenguaje basado en la extensión del archivo"""
        ext = os.path.splitext(file_path)[1].lower()
        
        for language, config in self.patterns.items():
            if ext in config['file_extensions']:
                return language
        return None
    
    def _extract_dependencies(self, content: str, language: str) -> Set[str]:
        """Extrae las dependencias del contenido según el lenguaje"""
        dependencies = set()
        
        if language not in self.patterns:
            return dependencies
        
        patterns = self.patterns[language]['import']
        
        for line in content.split('\n'):
            for pattern in patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    # Limpiar la dependencia
                    dep = match.strip()
                    if dep:
                        dependencies.add(dep)
        
        return dependencies
    
    def _is_internal_dependency(self, dependency: str, language: str) -> bool:
        """Determina si una dependencia es interna o externa"""
        if language not in self.patterns:
            return False
        
        prefix = self.patterns[language]['internal_prefix']
        if prefix is None:
            # Para lenguajes como Java/C#, considerar internas las que no son de sistema
            system_packages = {
                'java': ['java.', 'javax.', 'android.', 'org.junit', 'org.apache'],
                'csharp': ['System.', 'Microsoft.', 'Windows.']
            }
            
            if language in system_packages:
                return not any(dependency.startswith(pkg) for pkg in system_packages[language])
            return False
        
        return dependency.startswith(prefix) or dependency.startswith('/')
    
    def _detect_cycles(self, file_dependencies: Dict[str, Set[str]], all_files: Set[str]) -> List[List[str]]:
        """Detecta ciclos de dependencias entre archivos"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def _find_cycles_util(file: str, path: List[str]) -> None:
            visited.add(file)
            rec_stack.add(file)
            path.append(file)
            
            # Buscar dependencias que sean archivos del proyecto
            for dep in file_dependencies.get(file, set()):
                # Convertir dependencia a posible archivo
                possible_files = [
                    f for f in all_files 
                    if f.endswith(dep) or dep in f
                ]
                
                for dep_file in possible_files:
                    if dep_file not in visited:
                        _find_cycles_util(dep_file, path[:])
                    elif dep_file in rec_stack:
                        # Encontramos un ciclo
                        cycle_start = path.index(dep_file)
                        cycle = path[cycle_start:] + [dep_file]
                        if len(cycle) > 2:  # Solo ciclos significativos
                            cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(file)
        
        # Buscar ciclos desde cada archivo
        for file in all_files:
            if file not in visited:
                _find_cycles_util(file, [])
        
        # Eliminar duplicados
        unique_cycles = []
        for cycle in cycles:
            normalized = tuple(sorted(cycle))
            if normalized not in [tuple(sorted(c)) for c in unique_cycles]:
                unique_cycles.append(cycle)
        
        return unique_cycles[:10]  # Limitar a 10 ciclos
    
    def _get_top_dependencies(self, dependencies: Dict[str, Set[str]], limit: int) -> List[Dict[str, Any]]:
        """Obtiene las dependencias más utilizadas"""
        sorted_deps = sorted(
            dependencies.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:limit]
        
        return [
            {
                'dependency': dep,
                'used_by_count': len(files),
                'used_by': list(files)[:3]  # Primeros 3 archivos
            }
            for dep, files in sorted_deps
        ]
    
    def _get_files_with_most_deps(self, file_dependencies: Dict[str, Set[str]], limit: int) -> List[Dict[str, Any]]:
        """Obtiene los archivos con más dependencias"""
        sorted_files = sorted(
            file_dependencies.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:limit]
        
        return [
            {
                'file': file,
                'dependency_count': len(deps),
                'dependencies': list(deps)[:5]  # Primeras 5 dependencias
            }
            for file, deps in sorted_files
        ]
    
    def _calculate_coupling_score(self, file_dependencies: Dict[str, Set[str]], total_files: int) -> float:
        """
        Calcula un score de acoplamiento (0-1, donde 0 es bajo acoplamiento).
        """
        if total_files <= 1:
            return 0.0
        
        # Contar conexiones entre archivos
        connections = 0
        for deps in file_dependencies.values():
            connections += len(deps)
        
        # Máximo posible de conexiones (grafo completo)
        max_connections = total_files * (total_files - 1)
        
        # Score normalizado
        coupling = connections / max_connections if max_connections > 0 else 0
        
        return min(coupling, 1.0)  # Asegurar que esté entre 0 y 1
    
    def _generate_summary(self, total_deps: int, external_deps: int, internal_deps: int, cycles: int) -> str:
        """Genera un resumen del análisis de dependencias"""
        if total_deps == 0:
            return "No se encontraron dependencias en el código analizado."
        
        external_ratio = (external_deps / total_deps) * 100 if total_deps > 0 else 0
        internal_ratio = (internal_deps / total_deps) * 100 if total_deps > 0 else 0
        
        summary = f"Se encontraron {total_deps} dependencias únicas: "
        summary += f"{external_deps} externas ({external_ratio:.1f}%) y "
        summary += f"{internal_deps} internas ({internal_ratio:.1f}%). "
        
        if cycles > 0:
            summary += f"Advertencia: Se detectaron {cycles} dependencias circulares."
        else:
            summary += "No se detectaron dependencias circulares."
        
        return summary