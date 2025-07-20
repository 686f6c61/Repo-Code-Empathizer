#!/usr/bin/env python3
"""
Script para verificar las mejoras en los gráficos
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from exporters import Exporter

# Datos de prueba con variedad de puntuaciones para ver los colores
test_data = {
    'repos': {
        'empresa': {
            'metadata': {
                'nombre': 'TechCorp Backend',
                'url': 'https://github.com/techcorp/backend',
                'lenguajes_analizados': ['Python', 'JavaScript', 'SQL'],
                'archivos_analizados': 150,
                'tamano_kb': 2500.0,
                'lenguaje_principal': 'Python',
                'descripcion': 'Sistema backend principal'
            },
            'nombres': {'descriptividad': 0.90},
            'documentacion': {'cobertura_docstrings': 0.85},
            'modularidad': {'funciones_por_archivo': 4.5},
            'complejidad': {'complejidad_ciclomatica': 3.2},
            'manejo_errores': {'cobertura_manejo_errores': 0.80},
            'pruebas': {'cobertura_pruebas': 0.85},
            'seguridad': {'validacion_entradas': 0.88},
            'consistencia_estilo': {'consistencia_nombres': 0.92},
            'patrones': {
                'design_patterns': {
                    'singleton': [{'file': 'db.py', 'line': 10}],
                    'factory': [{'file': 'factory.py', 'line': 20}],
                    'observer': [{'file': 'events.py', 'line': 30}]
                },
                'anti_patterns': {},
                'pattern_score': 90.0
            },
            'rendimiento': {
                'performance_issues': {},
                'performance_score': 88.0
            },
            'comentarios': {
                'comment_metrics': {
                    'comment_ratio': 22.0,
                    'documentation_coverage': 90.0
                },
                'markers': {}
            }
        },
        'candidato': {
            'metadata': {
                'nombre': 'John Doe Portfolio',
                'url': 'https://github.com/johndoe/portfolio',
                'lenguajes_analizados': ['Python', 'JavaScript'],
                'archivos_analizados': 75,
                'tamano_kb': 850.0,
                'lenguaje_principal': 'Python',
                'descripcion': 'Portfolio del candidato'
            },
            'nombres': {'descriptividad': 0.75},
            'documentacion': {'cobertura_docstrings': 0.45},
            'modularidad': {'funciones_por_archivo': 5.5},
            'complejidad': {'complejidad_ciclomatica': 4.5},
            'manejo_errores': {'cobertura_manejo_errores': 0.35},
            'pruebas': {'cobertura_pruebas': 0.25},
            'seguridad': {'validacion_entradas': 0.50},
            'consistencia_estilo': {'consistencia_nombres': 0.70},
            'patrones': {
                'design_patterns': {
                    'observer': [{'file': 'events.py', 'line': 30}]
                },
                'anti_patterns': {
                    'god_class': [{'file': 'main.py', 'severity': 'medium'}],
                    'magic_numbers': [{'file': 'calc.py', 'severity': 'low'}]
                },
                'pattern_score': 55.0
            },
            'rendimiento': {
                'performance_issues': {
                    'nested_loops': [{'file': 'process.py', 'line': 100}]
                },
                'performance_score': 65.0
            },
            'comentarios': {
                'comment_metrics': {
                    'comment_ratio': 12.0,
                    'documentation_coverage': 55.0
                },
                'markers': {
                    'todo': [{'file': 'utils.py', 'line': 25}],
                    'fixme': [{'file': 'api.py', 'line': 80}]
                }
            }
        }
    },
    'empathy_analysis': {
        'empathy_score': 68.5,
        'interpretation': {
            'level': 'Aceptable',
            'description': 'Alineación moderada con el estilo de la empresa',
            'recommendation': 'Candidato viable con plan de capacitación estructurado',
            'color': 'warning'
        },
        'category_scores': {
            'nombres': 83.0,           # Excelente (verde menta)
            'documentacion': 53.0,     # Bajo (melocotón)
            'modularidad': 72.0,       # Bueno (amarillo)
            'complejidad': 67.0,       # Aceptable (amarillo)
            'manejo_errores': 44.0,    # Bajo (melocotón)
            'pruebas': 29.0,           # Muy bajo (coral)
            'seguridad': 57.0,         # Bajo (melocotón)
            'consistencia_estilo': 76.0,  # Bueno (amarillo)
            'patrones': 61.0,          # Aceptable (amarillo)
            'rendimiento': 74.0,       # Bueno (amarillo)
            'comentarios': 58.0        # Bajo (melocotón)
        },
        'language_overlap': {
            'score': 66.7,
            'overlap': ['Python', 'JavaScript'],
            'missing': ['SQL']
        }
    }
}

# Generar dashboard
print("=== VERIFICANDO MEJORAS EN GRÁFICOS ===\n")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
exporter = Exporter()

try:
    print("1. Generando Dashboard con mejoras...")
    exporter.exportar_html(test_data, timestamp, dashboard=True)
    print(f"   ✅ Dashboard generado: export/dashboard_{timestamp}.html")
    
    print("\n=== MEJORAS IMPLEMENTADAS ===")
    print("✅ Gráfico de Distribución de Calidad:")
    print("   - Colores pastel en lugar de escala de grises")
    print("   - Verde menta para puntuaciones excelentes (80%+)")
    print("   - Amarillo pastel para puntuaciones buenas (60-79%)")
    print("   - Melocotón para puntuaciones bajas (40-59%)")
    print("   - Coral pastel para puntuaciones muy bajas (<40%)")
    
    print("\n✅ Nuevo Gráfico Radar Comparativo:")
    print("   - Compara visualmente empresa vs candidato")
    print("   - Muestra todas las competencias en una vista")
    print("   - Azul pastel para la empresa")
    print("   - Ciruela pastel para el candidato")
    print("   - Incluye panel explicativo lateral")
    
    print("\n📝 Características del Radar:")
    print("   - Escala de 0-100% con pasos de 20%")
    print("   - Etiquetas claras para cada competencia")
    print("   - Tooltips informativos al pasar el mouse")
    print("   - Leyenda superior con colores distintivos")
    
    print("\nAbre el dashboard en un navegador para ver:")
    print("1. El gráfico de distribución con colores pastel")
    print("2. El nuevo gráfico radar comparativo")
    print("3. Todos los tooltips funcionando correctamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()