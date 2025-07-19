"""Tests for base language analyzer"""
import pytest
from src.language_analyzers.base import LanguageAnalyzer


class MockAnalyzer(LanguageAnalyzer):
    """Mock analyzer for testing base functionality"""
    
    def get_file_extensions(self):
        return ['.mock']
    
    def get_language_name(self):
        return 'Mock'
    
    def analyze_file(self, file_path, content):
        return {
            'nombres': {'descriptividad': 0.8},
            'documentacion': {'cobertura': 0.6},
            'modularidad': {'funciones': 5},
            'complejidad': {'ciclomatica': 0.7},
            'manejo_errores': {'cobertura': 0.5},
            'pruebas': {'cobertura': 0.4},
            'seguridad': {'validacion': 0.9},
            'consistencia_estilo': {'consistencia': 0.75}
        }


class TestLanguageAnalyzer:
    
    def test_init(self):
        analyzer = MockAnalyzer()
        assert analyzer.total_files == 0
        assert analyzer.total_lines == 0
        assert isinstance(analyzer.metrics, dict)
        assert all(key in analyzer.metrics for key in [
            'nombres', 'documentacion', 'modularidad', 'complejidad',
            'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo'
        ])
    
    def test_should_analyze_file(self):
        analyzer = MockAnalyzer()
        assert analyzer.should_analyze_file('test.mock')
        assert not analyzer.should_analyze_file('test.py')
        assert not analyzer.should_analyze_file('test.js')
    
    def test_analyze_files(self):
        analyzer = MockAnalyzer()
        files = {
            'test1.mock': 'content1\nline2\nline3',
            'test2.mock': 'content2\nline2',
            'test.py': 'should be ignored'
        }
        
        results = analyzer.analyze_files(files)
        
        assert analyzer.total_files == 2  # Only .mock files
        assert analyzer.total_lines == 5  # 3 + 2 lines
        assert 'nombres' in results
        assert results['nombres']['descriptividad'] == 0.8
    
    def test_aggregate_metrics(self):
        analyzer = MockAnalyzer()
        file_metrics = [
            {
                'nombres': {'descriptividad': 0.8},
                'documentacion': {'cobertura': 0.6},
                'complejidad': {'ciclomatica': 0.5}
            },
            {
                'nombres': {'descriptividad': 0.6},
                'documentacion': {'cobertura': 0.8},
                'complejidad': {'ciclomatica': 0.7}
            }
        ]
        
        analyzer.aggregate_metrics(file_metrics)
        
        assert analyzer.metrics['nombres']['descriptividad'] == 0.7  # (0.8 + 0.6) / 2
        assert analyzer.metrics['documentacion']['cobertura_docstrings'] == 0.7  # (0.6 + 0.8) / 2
        assert analyzer.metrics['complejidad']['complejidad_ciclomatica'] == 0.6  # (0.5 + 0.7) / 2
    
    def test_calculate_empathy_score(self):
        analyzer = MockAnalyzer()
        analyzer.metrics = {
            'nombres': {'descriptividad': 0.8},
            'documentacion': {'cobertura_docstrings': 0.6},
            'modularidad': {'funciones_por_archivo': 0.7},
            'complejidad': {'complejidad_ciclomatica': 0.5},
            'manejo_errores': {'cobertura_manejo_errores': 0.4},
            'pruebas': {'cobertura_pruebas': 0.3},
            'seguridad': {'validacion_entradas': 0.9},
            'consistencia_estilo': {'consistencia_nombres': 0.75}
        }
        
        score = analyzer.calculate_empathy_score()
        
        # Verify score is calculated correctly
        expected = (
            0.8 * 0.15 +   # nombres
            0.6 * 0.15 +   # documentacion
            0.7 * 0.15 +   # modularidad
            0.5 * 0.15 +   # complejidad
            0.4 * 0.10 +   # manejo_errores
            0.3 * 0.10 +   # pruebas
            0.9 * 0.10 +   # seguridad
            0.75 * 0.10    # consistencia_estilo
        )
        assert abs(score - expected) < 0.001
    
    def test_get_summary(self):
        analyzer = MockAnalyzer()
        analyzer.total_files = 5
        analyzer.total_lines = 100
        
        summary = analyzer.get_summary()
        
        assert summary['language'] == 'Mock'
        assert summary['total_files'] == 5
        assert summary['total_lines'] == 100
        assert 'metrics' in summary
        assert 'empathy_score' in summary