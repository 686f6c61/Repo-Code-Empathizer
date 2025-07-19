"""
Módulo de análisis paralelo para mejorar el rendimiento.

Este módulo implementa análisis paralelo de archivos de código utilizando
multiprocesamiento para acelerar el análisis de repositorios grandes.
Agrupa archivos por lenguaje y los procesa en paralelo.

Classes:
    ParallelAnalyzer: Analizador con capacidad de procesamiento paralelo.

Features:
    - Procesamiento paralelo usando ProcessPoolExecutor
    - Agrupación inteligente de archivos por lenguaje
    - Gestión eficiente de recursos del sistema
    - Agregación de resultados thread-safe

Author: R. Benítez
Version: 2.0.0
License: MIT
"""
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
import logging
from language_analyzers.factory import AnalyzerFactory
import os

logger = logging.getLogger(__name__)


class ParallelAnalyzer:
    """Analyzes code files in parallel for better performance"""
    
    def __init__(self, max_workers: Optional[int] = None):
        """Initialize parallel analyzer
        
        Args:
            max_workers: Maximum number of worker processes. If None, uses CPU count.
        """
        self.max_workers = max_workers or mp.cpu_count()
        
    def analyze_files_parallel(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze multiple files in parallel
        
        Args:
            files: Dictionary mapping file paths to file contents
            
        Returns:
            Analysis results with metrics per language
        """
        # Group files by language
        language_files = self._group_files_by_language(files)
        
        # Process each language in parallel
        results = {
            'languages': {},
            'total_metrics': {},
            'primary_language': None
        }
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit analysis tasks for each language
            future_to_language = {}
            for language, lang_files in language_files.items():
                future = executor.submit(self._analyze_language_files, language, lang_files)
                future_to_language[future] = language
            
            # Collect results as they complete
            for future in as_completed(future_to_language):
                language = future_to_language[future]
                try:
                    language_results = future.result()
                    results['languages'][language] = language_results
                except Exception as e:
                    logger.error(f"Error analyzing {language} files: {e}")
                    results['languages'][language] = {
                        'error': str(e),
                        'file_count': len(language_files[language])
                    }
        
        # Determine primary language
        if results['languages']:
            primary = max(results['languages'], 
                         key=lambda x: results['languages'][x].get('file_count', 0))
            results['primary_language'] = primary
        
        # Calculate aggregate metrics
        results['total_metrics'] = self._calculate_aggregate_metrics(results['languages'])
        
        return results
    
    def analyze_files_batch(self, files: Dict[str, str], batch_size: int = 10) -> Dict[str, Any]:
        """Analyze files in batches for memory efficiency
        
        Args:
            files: Dictionary mapping file paths to file contents
            batch_size: Number of files to process in each batch
            
        Returns:
            Analysis results
        """
        # Create batches
        file_items = list(files.items())
        batches = [dict(file_items[i:i + batch_size]) 
                  for i in range(0, len(file_items), batch_size)]
        
        # Process batches
        all_results = []
        for i, batch in enumerate(batches):
            logger.info(f"Processing batch {i+1}/{len(batches)} ({len(batch)} files)")
            batch_results = self.analyze_files_parallel(batch)
            all_results.append(batch_results)
        
        # Merge results
        return self._merge_batch_results(all_results)
    
    def _group_files_by_language(self, files: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Group files by their programming language"""
        language_files = {}
        
        for file_path, content in files.items():
            analyzer = AnalyzerFactory.get_analyzer_for_file(file_path)
            if analyzer:
                language = analyzer.get_language_name()
                if language not in language_files:
                    language_files[language] = {}
                language_files[language][file_path] = content
        
        return language_files
    
    @staticmethod
    def _analyze_language_files(language: str, files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze files for a specific language (runs in separate process)"""
        analyzer = AnalyzerFactory.get_analyzer(language.lower())
        if not analyzer:
            return {'error': f'No analyzer found for {language}'}
        
        # Analyze files
        metrics = analyzer.analyze_files(files)
        summary = analyzer.get_summary()
        
        return {
            'metrics': metrics,
            'summary': summary,
            'file_count': len(files)
        }
    
    def _calculate_aggregate_metrics(self, language_results: Dict) -> Dict[str, Any]:
        """Calculate aggregate metrics across all languages"""
        if not language_results:
            return {}
        
        total_files = sum(lang.get('file_count', 0) for lang in language_results.values() 
                         if 'error' not in lang)
        total_lines = sum(lang.get('summary', {}).get('total_lines', 0) 
                         for lang in language_results.values() if 'error' not in lang)
        
        # Weight metrics by file count
        weighted_empathy = 0
        for lang_name, lang_data in language_results.items():
            if 'error' not in lang_data and total_files > 0:
                weight = lang_data['file_count'] / total_files
                empathy_score = lang_data.get('summary', {}).get('empathy_score', 0)
                weighted_empathy += empathy_score * weight
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'languages_analyzed': [k for k in language_results.keys() if 'error' not in language_results[k]],
            'overall_empathy_score': weighted_empathy
        }
    
    def _merge_batch_results(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results from multiple batches"""
        merged = {
            'languages': {},
            'total_metrics': {},
            'primary_language': None
        }
        
        # Merge language results
        for result in batch_results:
            for language, data in result.get('languages', {}).items():
                if language not in merged['languages']:
                    merged['languages'][language] = {
                        'metrics': {},
                        'summary': {},
                        'file_count': 0
                    }
                
                # Merge metrics
                if 'metrics' in data:
                    for category, values in data['metrics'].items():
                        if category not in merged['languages'][language]['metrics']:
                            merged['languages'][language]['metrics'][category] = {}
                        merged['languages'][language]['metrics'][category].update(values)
                
                # Update file count
                merged['languages'][language]['file_count'] += data.get('file_count', 0)
        
        # Recalculate summary and primary language
        if merged['languages']:
            primary = max(merged['languages'], 
                         key=lambda x: merged['languages'][x].get('file_count', 0))
            merged['primary_language'] = primary
        
        merged['total_metrics'] = self._calculate_aggregate_metrics(merged['languages'])
        
        return merged


class FileAnalysisTask:
    """Represents a single file analysis task"""
    
    def __init__(self, file_path: str, content: str, language: str):
        self.file_path = file_path
        self.content = content
        self.language = language
    
    def analyze(self) -> Tuple[str, Dict[str, Any]]:
        """Analyze the file and return results"""
        analyzer = AnalyzerFactory.get_analyzer(self.language.lower())
        if not analyzer:
            return self.file_path, {'error': f'No analyzer for {self.language}'}
        
        try:
            metrics = analyzer.analyze_file(self.file_path, self.content)
            return self.file_path, metrics
        except Exception as e:
            logger.error(f"Error analyzing {self.file_path}: {e}")
            return self.file_path, {'error': str(e)}


def analyze_file_worker(task: FileAnalysisTask) -> Tuple[str, Dict[str, Any]]:
    """Worker function for analyzing a single file"""
    return task.analyze()