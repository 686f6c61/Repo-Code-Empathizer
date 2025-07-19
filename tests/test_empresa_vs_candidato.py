"""
Integration tests for empresa vs candidato comparisons
Tests different technology stacks and real-world scenarios
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from language_analyzers.factory import AnalyzerFactory
from empathy_algorithm import EmpathyAlgorithm


class TestEmpresaVsCandidato:
    """Test empresa vs candidato comparisons for different technologies"""
    
    @pytest.fixture
    def empathy_algorithm(self):
        """Create empathy algorithm instance"""
        return EmpathyAlgorithm()
    
    def test_python_empresa_vs_candidato(self, empathy_algorithm):
        """Test Python empresa vs Python candidato"""
        # Simulate empresa metrics (Django-style)
        empresa_metrics = {
            'metadata': {
                'nombre': 'empresa-django',
                'lenguajes_analizados': ['Python'],
                'archivos_analizados': 50
            },
            'nombres': {'descriptividad': 0.9, 'snake_case': 0.95},
            'documentacion': {'cobertura_docstrings': 0.85, 'calidad': 0.8},
            'modularidad': {'funciones_por_archivo': 0.7, 'cohesion': 0.8},
            'complejidad': {'ciclomatica': 0.8, 'anidacion': 0.85},
            'manejo_errores': {'cobertura': 0.75, 'especificidad': 0.8},
            'pruebas': {'cobertura': 0.8, 'densidad': 0.75},
            'seguridad': {'validacion': 0.9, 'funciones_seguras': 0.95},
            'consistencia_estilo': {'formato': 0.9, 'nombres': 0.88}
        }
        
        # Simulate candidato metrics (Flask-style)
        candidato_metrics = {
            'metadata': {
                'nombre': 'candidato-flask',
                'lenguajes_analizados': ['Python'],
                'archivos_analizados': 25
            },
            'nombres': {'descriptividad': 0.85, 'snake_case': 0.9},
            'documentacion': {'cobertura_docstrings': 0.6, 'calidad': 0.65},
            'modularidad': {'funciones_por_archivo': 0.75, 'cohesion': 0.7},
            'complejidad': {'ciclomatica': 0.75, 'anidacion': 0.8},
            'manejo_errores': {'cobertura': 0.6, 'especificidad': 0.65},
            'pruebas': {'cobertura': 0.5, 'densidad': 0.55},
            'seguridad': {'validacion': 0.8, 'funciones_seguras': 0.85},
            'consistencia_estilo': {'formato': 0.85, 'nombres': 0.8}
        }
        
        # Calculate empathy score
        result = empathy_algorithm.calculate_empathy_score(empresa_metrics, candidato_metrics)
        
        # Assertions
        assert 'empathy_score' in result
        assert 0 <= result['empathy_score'] <= 100
        assert result['language_overlap']['score'] == 100  # Both use Python
        assert len(result['category_scores']) > 0
        assert 'recommendations' in result
        assert 'interpretation' in result
        
        # Python to Python should have good alignment
        assert result['empathy_score'] > 60
    
    def test_javascript_empresa_vs_candidato(self, empathy_algorithm):
        """Test JavaScript/TypeScript empresa vs candidato"""
        # Simulate empresa metrics (React + TypeScript)
        empresa_metrics = {
            'metadata': {
                'nombre': 'empresa-react',
                'lenguajes_analizados': ['JavaScript', 'TypeScript'],
                'archivos_analizados': 100
            },
            'nombres': {'descriptividad': 0.88, 'camelCase': 0.92},
            'documentacion': {'jsdoc': 0.7, 'comentarios': 0.75},
            'modularidad': {'componentes': 0.85, 'imports': 0.8},
            'complejidad': {'funciones': 0.75, 'jsx': 0.8},
            'manejo_errores': {'try_catch': 0.7, 'boundaries': 0.65},
            'pruebas': {'jest': 0.75, 'react_testing': 0.7},
            'seguridad': {'xss': 0.85, 'validacion': 0.8},
            'consistencia_estilo': {'eslint': 0.9, 'prettier': 0.95}
        }
        
        # Simulate candidato metrics (Vue.js)
        candidato_metrics = {
            'metadata': {
                'nombre': 'candidato-vue',
                'lenguajes_analizados': ['JavaScript'],
                'archivos_analizados': 40
            },
            'nombres': {'descriptividad': 0.82, 'camelCase': 0.88},
            'documentacion': {'jsdoc': 0.5, 'comentarios': 0.6},
            'modularidad': {'componentes': 0.8, 'imports': 0.75},
            'complejidad': {'funciones': 0.7, 'jsx': 0.0},  # Vue doesn't use JSX
            'manejo_errores': {'try_catch': 0.65, 'boundaries': 0.5},
            'pruebas': {'jest': 0.6, 'react_testing': 0.0},
            'seguridad': {'xss': 0.75, 'validacion': 0.7},
            'consistencia_estilo': {'eslint': 0.85, 'prettier': 0.8}
        }
        
        result = empathy_algorithm.calculate_empathy_score(empresa_metrics, candidato_metrics)
        
        # Missing TypeScript should reduce score
        assert result['language_overlap']['score'] == 50  # 1 of 2 languages
        assert 'TypeScript' in result['language_overlap']['missing']
        assert result['empathy_score'] < 70  # Lower due to missing TS
    
    def test_java_empresa_vs_candidato(self, empathy_algorithm):
        """Test Java empresa vs candidato"""
        empresa_metrics = {
            'metadata': {
                'nombre': 'empresa-spring',
                'lenguajes_analizados': ['Java'],
                'archivos_analizados': 200
            },
            'nombres': {'descriptividad': 0.92, 'camelCase': 0.95},
            'documentacion': {'javadoc': 0.88, 'comentarios': 0.8},
            'modularidad': {'clases': 0.85, 'paquetes': 0.9},
            'complejidad': {'metodos': 0.8, 'herencia': 0.75},
            'manejo_errores': {'excepciones': 0.85, 'especificas': 0.8},
            'pruebas': {'junit': 0.82, 'mockito': 0.78},
            'seguridad': {'validacion': 0.88, 'sql': 0.9},
            'consistencia_estilo': {'convenciones': 0.92, 'formato': 0.9}
        }
        
        candidato_metrics = {
            'metadata': {
                'nombre': 'candidato-microservices',
                'lenguajes_analizados': ['Java'],
                'archivos_analizados': 80
            },
            'nombres': {'descriptividad': 0.88, 'camelCase': 0.92},
            'documentacion': {'javadoc': 0.75, 'comentarios': 0.7},
            'modularidad': {'clases': 0.82, 'paquetes': 0.85},
            'complejidad': {'metodos': 0.78, 'herencia': 0.8},
            'manejo_errores': {'excepciones': 0.8, 'especificas': 0.75},
            'pruebas': {'junit': 0.78, 'mockito': 0.72},
            'seguridad': {'validacion': 0.82, 'sql': 0.85},
            'consistencia_estilo': {'convenciones': 0.88, 'formato': 0.85}
        }
        
        result = empathy_algorithm.calculate_empathy_score(empresa_metrics, candidato_metrics)
        
        # Good alignment expected for Java to Java
        assert result['empathy_score'] > 75
        assert result['language_overlap']['score'] == 100
    
    def test_go_empresa_vs_candidato(self, empathy_algorithm):
        """Test Go empresa vs candidato"""
        empresa_metrics = {
            'metadata': {
                'nombre': 'empresa-kubernetes',
                'lenguajes_analizados': ['Go'],
                'archivos_analizados': 300
            },
            'nombres': {'descriptividad': 0.9, 'go_conventions': 0.95},
            'documentacion': {'godoc': 0.85, 'comentarios': 0.8},
            'modularidad': {'paquetes': 0.88, 'interfaces': 0.85},
            'complejidad': {'funciones': 0.82, 'goroutines': 0.78},
            'manejo_errores': {'error_returns': 0.9, 'panic_recover': 0.85},
            'pruebas': {'testing': 0.85, 'benchmarks': 0.7},
            'seguridad': {'validacion': 0.88, 'concurrencia': 0.82},
            'consistencia_estilo': {'gofmt': 0.98, 'convenciones': 0.95}
        }
        
        candidato_metrics = {
            'metadata': {
                'nombre': 'candidato-cli-tools',
                'lenguajes_analizados': ['Go'],
                'archivos_analizados': 50
            },
            'nombres': {'descriptividad': 0.85, 'go_conventions': 0.88},
            'documentacion': {'godoc': 0.7, 'comentarios': 0.65},
            'modularidad': {'paquetes': 0.8, 'interfaces': 0.75},
            'complejidad': {'funciones': 0.78, 'goroutines': 0.6},
            'manejo_errores': {'error_returns': 0.82, 'panic_recover': 0.7},
            'pruebas': {'testing': 0.72, 'benchmarks': 0.5},
            'seguridad': {'validacion': 0.8, 'concurrencia': 0.7},
            'consistencia_estilo': {'gofmt': 0.95, 'convenciones': 0.88}
        }
        
        result = empathy_algorithm.calculate_empathy_score(empresa_metrics, candidato_metrics)
        
        # Go has strong conventions, should show in consistency
        assert result['category_scores']['consistencia_estilo'] > 85
    
    def test_mixed_stack_empresa_vs_candidato(self, empathy_algorithm):
        """Test empresa with multiple languages vs candidato with subset"""
        # Empresa: Full-stack (Python + JS + HTML + CSS)
        empresa_metrics = {
            'metadata': {
                'nombre': 'empresa-fullstack',
                'lenguajes_analizados': ['Python', 'JavaScript', 'HTML', 'CSS'],
                'archivos_analizados': 150
            },
            'nombres': {'descriptividad': 0.88},
            'documentacion': {'cobertura': 0.75},
            'modularidad': {'organizacion': 0.82},
            'complejidad': {'general': 0.78},
            'manejo_errores': {'cobertura': 0.72},
            'pruebas': {'cobertura': 0.68},
            'seguridad': {'validacion': 0.85},
            'consistencia_estilo': {'general': 0.88}
        }
        
        # Candidato: Backend only (Python)
        candidato_metrics = {
            'metadata': {
                'nombre': 'candidato-backend',
                'lenguajes_analizados': ['Python'],
                'archivos_analizados': 40
            },
            'nombres': {'descriptividad': 0.92},
            'documentacion': {'cobertura': 0.8},
            'modularidad': {'organizacion': 0.85},
            'complejidad': {'general': 0.82},
            'manejo_errores': {'cobertura': 0.78},
            'pruebas': {'cobertura': 0.75},
            'seguridad': {'validacion': 0.88},
            'consistencia_estilo': {'general': 0.9}
        }
        
        result = empathy_algorithm.calculate_empathy_score(empresa_metrics, candidato_metrics)
        
        # Should show missing languages
        assert result['language_overlap']['score'] == 25  # 1 of 4 languages
        assert set(result['language_overlap']['missing']) == {'JavaScript', 'HTML', 'CSS'}
        
        # Should recommend learning missing languages
        lang_recommendations = [r for r in result['recommendations'] 
                               if r['category'] == 'languages']
        assert len(lang_recommendations) > 0
    
    def test_perfect_match_scenario(self, empathy_algorithm):
        """Test perfect match between empresa and candidato"""
        # Both have identical metrics
        perfect_metrics = {
            'metadata': {
                'nombre': 'perfect-match',
                'lenguajes_analizados': ['Python', 'JavaScript'],
                'archivos_analizados': 100
            },
            'nombres': {'descriptividad': 0.9},
            'documentacion': {'cobertura': 0.85},
            'modularidad': {'organizacion': 0.88},
            'complejidad': {'general': 0.82},
            'manejo_errores': {'cobertura': 0.8},
            'pruebas': {'cobertura': 0.78},
            'seguridad': {'validacion': 0.9},
            'consistencia_estilo': {'general': 0.92}
        }
        
        result = empathy_algorithm.calculate_empathy_score(
            perfect_metrics, 
            perfect_metrics  # Same metrics
        )
        
        # Should have very high score
        assert result['empathy_score'] > 95
        assert result['language_overlap']['score'] == 100
        assert result['interpretation']['level'] == 'Excelente'
        assert len(result['recommendations']) == 0 or all(
            r['priority'] == 'low' for r in result['recommendations']
        )
    
    def test_poor_match_scenario(self, empathy_algorithm):
        """Test poor match between empresa and candidato"""
        empresa_metrics = {
            'metadata': {
                'nombre': 'empresa-high-standards',
                'lenguajes_analizados': ['Python', 'Go', 'Rust'],
                'archivos_analizados': 500
            },
            'nombres': {'descriptividad': 0.95},
            'documentacion': {'cobertura': 0.9},
            'modularidad': {'organizacion': 0.92},
            'complejidad': {'general': 0.88},
            'manejo_errores': {'cobertura': 0.9},
            'pruebas': {'cobertura': 0.95},
            'seguridad': {'validacion': 0.95},
            'consistencia_estilo': {'general': 0.98}
        }
        
        candidato_metrics = {
            'metadata': {
                'nombre': 'candidato-beginner',
                'lenguajes_analizados': ['JavaScript'],
                'archivos_analizados': 10
            },
            'nombres': {'descriptividad': 0.4},
            'documentacion': {'cobertura': 0.1},
            'modularidad': {'organizacion': 0.3},
            'complejidad': {'general': 0.2},  # Very complex/messy
            'manejo_errores': {'cobertura': 0.15},
            'pruebas': {'cobertura': 0.0},
            'seguridad': {'validacion': 0.3},
            'consistencia_estilo': {'general': 0.35}
        }
        
        result = empathy_algorithm.calculate_empathy_score(empresa_metrics, candidato_metrics)
        
        # Should have very low score
        assert result['empathy_score'] < 30
        assert result['language_overlap']['score'] == 0  # No common languages
        assert result['interpretation']['level'] == 'Muy Bajo'
        assert len(result['recommendations']) > 3  # Many recommendations
        assert all(r['priority'] == 'high' for r in result['recommendations'][:2])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])