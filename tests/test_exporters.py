"""
Tests for export functionality (HTML, JSON, TXT)
Tests the complete export pipeline for all supported formats
"""

import os
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from exporters import Exporter


class TestExporters:
    """Test suite for all export formats"""
    
    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics data for testing"""
        return {
            'repos': {
                'empresa': {
                    'metadata': {
                        'nombre': 'test-empresa',
                        'url': 'https://github.com/empresa/test',
                        'descripcion': 'Empresa test repository',
                        'lenguaje_principal': 'Python',
                        'lenguajes_analizados': ['Python', 'JavaScript'],
                        'archivos_analizados': 25,
                        'tamano_kb': 150.5
                    },
                    'nombres': {'descriptividad': 0.85},
                    'documentacion': {'cobertura_docstrings': 0.75},
                    'modularidad': {'funciones_por_archivo': 0.8},
                    'complejidad': {'complejidad_ciclomatica': 0.7},
                    'manejo_errores': {'cobertura_manejo_errores': 0.6},
                    'pruebas': {'cobertura_pruebas': 0.5},
                    'seguridad': {'validacion_entradas': 0.9},
                    'consistencia_estilo': {'consistencia_nombres': 0.88}
                },
                'candidato': {
                    'metadata': {
                        'nombre': 'test-candidato',
                        'url': 'https://github.com/candidato/portfolio',
                        'descripcion': 'Candidato portfolio',
                        'lenguaje_principal': 'Python',
                        'lenguajes_analizados': ['Python'],
                        'archivos_analizados': 15,
                        'tamano_kb': 75.2
                    },
                    'nombres': {'descriptividad': 0.78},
                    'documentacion': {'cobertura_docstrings': 0.45},
                    'modularidad': {'funciones_por_archivo': 0.7},
                    'complejidad': {'complejidad_ciclomatica': 0.65},
                    'manejo_errores': {'cobertura_manejo_errores': 0.4},
                    'pruebas': {'cobertura_pruebas': 0.3},
                    'seguridad': {'validacion_entradas': 0.7},
                    'consistencia_estilo': {'consistencia_nombres': 0.75}
                }
            },
            'empathy_analysis': {
                'empathy_score': 72.5,
                'category_scores': {
                    'nombres': 91.8,
                    'documentacion': 60.0,
                    'modularidad': 87.5,
                    'complejidad': 92.9,
                    'manejo_errores': 66.7,
                    'pruebas': 60.0,
                    'seguridad': 77.8,
                    'consistencia_estilo': 85.2
                },
                'language_overlap': {
                    'score': 50.0,
                    'overlap': ['Python'],
                    'missing': ['JavaScript'],
                    'extra': []
                },
                'interpretation': {
                    'level': 'Aceptable',
                    'description': 'Alineación moderada, requiere adaptación',
                    'recommendation': 'Candidato viable con plan de capacitación',
                    'color': '#FFC107'
                },
                'detailed_analysis': {
                    'strengths': [
                        {'category': 'nombres', 'score': 91.8},
                        {'category': 'modularidad', 'score': 87.5}
                    ],
                    'weaknesses': [
                        {'category': 'documentacion', 'score': 60.0},
                        {'category': 'pruebas', 'score': 60.0}
                    ]
                },
                'recommendations': [
                    {
                        'priority': 'high',
                        'category': 'documentacion',
                        'title': 'Aumentar documentación',
                        'description': 'Añada más comentarios y documentación al código',
                        'tips': ['Documente todas las funciones públicas']
                    }
                ]
            },
            'timestamp': datetime.now().isoformat()
        }
    
    @pytest.fixture
    def temp_export_dir(self):
        """Create temporary export directory"""
        temp_dir = tempfile.mkdtemp()
        export_dir = os.path.join(temp_dir, 'export')
        os.makedirs(export_dir)
        
        # Temporarily change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        yield export_dir
        
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
    
    def test_txt_export(self, sample_metrics, temp_export_dir):
        """Test TXT export functionality"""
        exporter = Exporter()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export to TXT
        exporter.exportar_txt(sample_metrics, timestamp)
        
        # Check file was created
        txt_file = os.path.join(temp_export_dir, f'reporte_{timestamp}.txt')
        assert os.path.exists(txt_file)
        
        # Verify content
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check key sections exist
        assert "ANÁLISIS DE EMPATÍA EMPRESA-CANDIDATO" in content
        assert "EMPRESA (Master)" in content
        assert "CANDIDATO" in content
        assert "PUNTUACIÓN DE EMPATÍA: 72.5%" in content
        assert "Nivel: Aceptable" in content
        assert "Puntuaciones por Categoría:" in content
        assert "Coincidencia de Lenguajes: 50.0%" in content
        assert "MÉTRICAS DETALLADAS POR CATEGORÍA" in content
        assert "CONCLUSIÓN Y DECISIÓN DE CONTRATACIÓN" in content
    
    def test_json_export(self, sample_metrics, temp_export_dir):
        """Test JSON export functionality"""
        exporter = Exporter()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export to JSON
        exporter.exportar_json(sample_metrics, timestamp)
        
        # Check file was created
        json_file = os.path.join(temp_export_dir, f'reporte_{timestamp}.json')
        assert os.path.exists(json_file)
        
        # Verify content
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structure
        assert 'timestamp' in data
        assert 'metricas' in data
        assert 'repos' in data['metricas']
        assert 'empresa' in data['metricas']['repos']
        assert 'candidato' in data['metricas']['repos']
        assert 'empathy_analysis' in data['metricas']
        assert data['metricas']['empathy_analysis']['empathy_score'] == 72.5
    
    def test_html_export_dashboard(self, sample_metrics, temp_export_dir):
        """Test HTML dashboard export functionality"""
        # Create templates directory
        templates_dir = os.path.join(os.path.dirname(temp_export_dir), 'templates')
        os.makedirs(templates_dir)
        
        # Create minimal template
        dashboard_template = '''
        <!DOCTYPE html>
        <html>
        <head><title>Test Dashboard</title></head>
        <body>
            <h1>Empathy Score: {{ metricas.empathy_analysis.empathy_score }}%</h1>
            <p>{{ metricas.empathy_analysis.interpretation.level }}</p>
            {% for repo_tipo, repo_data in metricas.repos.items() %}
                <div>{{ repo_tipo }}: {{ repo_data.metadata.nombre }}</div>
            {% endfor %}
        </body>
        </html>
        '''
        
        with open(os.path.join(templates_dir, 'dashboard_empathy.html'), 'w') as f:
            f.write(dashboard_template)
        
        exporter = Exporter()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export dashboard
        exporter.exportar_html(sample_metrics, timestamp, dashboard=True)
        
        # Check file was created
        html_file = os.path.join(temp_export_dir, f'dashboard_{timestamp}.html')
        assert os.path.exists(html_file)
        
        # Verify content
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check key elements
        assert "Empathy Score: 72.5%" in content
        assert "Aceptable" in content
        assert "empresa: test-empresa" in content
        assert "candidato: test-candidato" in content
    
    def test_html_export_report(self, sample_metrics, temp_export_dir):
        """Test HTML report export functionality"""
        # Create templates directory
        templates_dir = os.path.join(os.path.dirname(temp_export_dir), 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create minimal report template
        report_template = '''
        <!DOCTYPE html>
        <html>
        <head><title>Test Report</title></head>
        <body>
            <h1>Analysis Report</h1>
            <p>Score: {{ metricas.empathy_analysis.empathy_score }}%</p>
        </body>
        </html>
        '''
        
        with open(os.path.join(templates_dir, 'informe_template.html'), 'w') as f:
            f.write(report_template)
        
        exporter = Exporter()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export report
        exporter.exportar_html(sample_metrics, timestamp, dashboard=False)
        
        # Check file was created
        html_file = os.path.join(temp_export_dir, f'informe_{timestamp}.html')
        assert os.path.exists(html_file)
    
    def test_export_with_missing_empathy_analysis(self, temp_export_dir):
        """Test export with legacy format (no empathy analysis)"""
        legacy_metrics = {
            'repos': {
                'A': {
                    'metadata': {'nombre': 'repo-a'},
                    'nombres': {'descriptividad': 0.8}
                },
                'B': {
                    'metadata': {'nombre': 'repo-b'},
                    'nombres': {'descriptividad': 0.7}
                }
            }
        }
        
        exporter = Exporter()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Should not raise error
        exporter.exportar_txt(legacy_metrics, timestamp)
        exporter.exportar_json(legacy_metrics, timestamp)
    
    def test_export_with_empty_metrics(self, temp_export_dir):
        """Test export with empty metrics"""
        empty_metrics = {'repos': {}}
        
        exporter = Exporter()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Should handle gracefully
        exporter.exportar_txt(empty_metrics, timestamp)
        exporter.exportar_json(empty_metrics, timestamp)
    
    def test_format_date_filter(self):
        """Test the format_date filter"""
        exporter = Exporter()
        
        # Test with ISO string
        iso_date = "2024-07-19T10:30:00"
        formatted = exporter.format_date(iso_date)
        assert "/" in formatted
        assert ":" in formatted
        
        # Test with datetime object
        dt = datetime.now()
        formatted = exporter.format_date(dt)
        assert "/" in formatted
        assert ":" in formatted
        
        # Test with invalid date
        invalid = "not a date"
        formatted = exporter.format_date(invalid)
        assert formatted == invalid
    
    def test_export_creates_directory(self):
        """Test that export creates directory if it doesn't exist"""
        # Use a temp directory without export subdirectory
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            exporter = Exporter()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export should create the directory
            exporter.exportar_txt({'repos': {}}, timestamp)
            
            assert os.path.exists('export')
            assert os.path.isdir('export')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])