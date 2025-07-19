"""
Factory para crear analizadores específicos de lenguaje.

Este módulo implementa el patrón Factory para crear dinámicamente
analizadores apropiados según el lenguaje de programación detectado.
Gestiona el registro de analizadores y el mapeo de extensiones.

Classes:
    AnalyzerFactory: Factory principal para creación de analizadores.

Features:
    - Registro dinámico de analizadores
    - Detección automática de lenguaje por extensión
    - Análisis multi-lenguaje de proyectos
    - Agregación de métricas cross-language

Author: R. Benítez
Version: 2.0.0
License: MIT
"""
import os
from typing import Optional, Dict, List, Type, Any
from .base import LanguageAnalyzer
from .python_analyzer import PythonAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer
from .typescript_analyzer import TypeScriptAnalyzer
from .java_analyzer import JavaAnalyzer
from .go_analyzer import GoAnalyzer
from .csharp_analyzer import CSharpAnalyzer
from .cpp_analyzer import CppAnalyzer
from .php_analyzer import PHPAnalyzer
from .ruby_analyzer import RubyAnalyzer
from .swift_analyzer import SwiftAnalyzer
from .html_analyzer import HTMLAnalyzer
from .css_analyzer import CSSAnalyzer


class AnalyzerFactory:
    """Factory class for creating appropriate language analyzers"""
    
    # Registry of available analyzers
    _analyzers: Dict[str, Type[LanguageAnalyzer]] = {
        'python': PythonAnalyzer,
        'javascript': JavaScriptAnalyzer,
        'typescript': TypeScriptAnalyzer,
        'java': JavaAnalyzer,
        'go': GoAnalyzer,
        'c#': CSharpAnalyzer,
        'csharp': CSharpAnalyzer,
        'c++': CppAnalyzer,
        'cpp': CppAnalyzer,
        'php': PHPAnalyzer,
        'ruby': RubyAnalyzer,
        'swift': SwiftAnalyzer,
        'html': HTMLAnalyzer,
        'css': CSSAnalyzer
    }
    
    # Extension to language mapping
    _extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.mjs': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.hpp': 'cpp',
        '.h': 'cpp',
        '.hh': 'cpp',
        '.php': 'php',
        '.php3': 'php',
        '.php4': 'php',
        '.php5': 'php',
        '.phtml': 'php',
        '.rb': 'ruby',
        '.rake': 'ruby',
        '.gemspec': 'ruby',
        '.swift': 'swift',
        '.html': 'html',
        '.htm': 'html',
        '.xhtml': 'html',
        '.css': 'css',
        '.scss': 'css',
        '.sass': 'css',
        '.less': 'css'
    }
    
    @classmethod
    def register_analyzer(cls, language: str, analyzer_class: Type[LanguageAnalyzer]) -> None:
        """Register a new analyzer for a language"""
        cls._analyzers[language.lower()] = analyzer_class
    
    @classmethod
    def get_analyzer(cls, language: str) -> Optional[LanguageAnalyzer]:
        """Get an analyzer instance for a specific language"""
        analyzer_class = cls._analyzers.get(language.lower())
        if analyzer_class:
            return analyzer_class()
        return None
    
    @classmethod
    def get_analyzer_for_file(cls, file_path: str) -> Optional[LanguageAnalyzer]:
        """Get an analyzer instance based on file extension"""
        _, ext = os.path.splitext(file_path)
        language = cls._extension_map.get(ext.lower())
        
        if language:
            return cls.get_analyzer(language)
        return None
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of all supported file extensions"""
        return list(cls._extension_map.keys())
    
    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Get list of all supported languages"""
        return list(cls._analyzers.keys())
    
    @classmethod
    def detect_primary_language(cls, files: Dict[str, str]) -> Optional[str]:
        """Detect the primary language in a set of files"""
        language_counts = {}
        
        for file_path in files:
            _, ext = os.path.splitext(file_path)
            language = cls._extension_map.get(ext.lower())
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1
        
        if language_counts:
            # Return the most common language
            return max(language_counts, key=language_counts.get)
        return None
    
    @classmethod
    def analyze_multi_language_project(cls, files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze a project with multiple languages"""
        results = {
            'languages': {},
            'total_metrics': {},
            'primary_language': None
        }
        
        # Group files by language
        language_files = {}
        for file_path, content in files.items():
            analyzer = cls.get_analyzer_for_file(file_path)
            if analyzer:
                language = analyzer.get_language_name()
                if language not in language_files:
                    language_files[language] = {}
                language_files[language][file_path] = content
        
        # Analyze each language separately
        for language, lang_files in language_files.items():
            analyzer = cls.get_analyzer(language.lower())
            if analyzer:
                metrics = analyzer.analyze_files(lang_files)
                results['languages'][language] = {
                    'metrics': metrics,
                    'summary': analyzer.get_summary(),
                    'file_count': len(lang_files)
                }
        
        # Determine primary language
        if language_files:
            primary = max(language_files, key=lambda x: len(language_files[x]))
            results['primary_language'] = primary
        
        # Calculate aggregate metrics
        results['total_metrics'] = cls._calculate_aggregate_metrics(results['languages'])
        
        return results
    
    @classmethod
    def _calculate_aggregate_metrics(cls, language_results: Dict) -> Dict[str, Any]:
        """Calculate aggregate metrics across all languages"""
        if not language_results:
            return {}
        
        total_files = sum(lang['file_count'] for lang in language_results.values())
        total_lines = sum(lang['summary']['total_lines'] for lang in language_results.values())
        
        # Weight metrics by file count
        weighted_scores = {}
        for lang_name, lang_data in language_results.items():
            weight = lang_data['file_count'] / total_files
            empathy_score = lang_data['summary']['empathy_score']
            
            if 'weighted_empathy' not in weighted_scores:
                weighted_scores['weighted_empathy'] = 0
            weighted_scores['weighted_empathy'] += empathy_score * weight
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'languages_analyzed': list(language_results.keys()),
            'overall_empathy_score': weighted_scores.get('weighted_empathy', 0)
        }