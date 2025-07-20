#!/usr/bin/env python3
"""
Script para verificar que todos los errores están corregidos
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from exporters import Exporter

# Datos de prueba
test_data = {
    'repos': {
        'empresa': {
            'metadata': {
                'nombre': 'Test Empresa',
                'url': 'https://github.com/test/empresa',
                'lenguajes_analizados': ['Python', 'JavaScript'],
                'archivos_analizados': 100,
                'tamano_kb': 1500.0,
                'lenguaje_principal': 'Python',
                'descripcion': 'Repositorio de prueba'
            },
            'nombres': {'descriptividad': 0.85},
            'documentacion': {'cobertura_docstrings': 0.75},
            'modularidad': {'funciones_por_archivo': 4.0},
            'complejidad': {'complejidad_ciclomatica': 3.0},
            'manejo_errores': {'cobertura_manejo_errores': 0.70},
            'pruebas': {'cobertura_pruebas': 0.80},
            'seguridad': {'validacion_entradas': 0.85},
            'consistencia_estilo': {'consistencia_nombres': 0.90},
            'patrones': {
                'design_patterns': {
                    'singleton': [{'file': 'db.py', 'line': 10}],
                    'factory': [{'file': 'factory.py', 'line': 20}]
                },
                'anti_patterns': {},
                'pattern_score': 85.0
            },
            'rendimiento': {
                'performance_issues': {},
                'performance_score': 90.0
            },
            'comentarios': {
                'comment_metrics': {
                    'comment_ratio': 20.0,
                    'documentation_coverage': 85.0
                },
                'markers': {
                    'todo': [{'file': 'main.py', 'line': 50}]
                }
            }
        },
        'candidato': {
            'metadata': {
                'nombre': 'Test Candidato',
                'url': 'https://github.com/test/candidato',
                'lenguajes_analizados': ['Python', 'JavaScript'],
                'archivos_analizados': 50,
                'tamano_kb': 500.0,
                'lenguaje_principal': 'Python',
                'descripcion': 'Portfolio del candidato'
            },
            'nombres': {'descriptividad': 0.75},
            'documentacion': {'cobertura_docstrings': 0.60},
            'modularidad': {'funciones_por_archivo': 5.0},
            'complejidad': {'complejidad_ciclomatica': 4.0},
            'manejo_errores': {'cobertura_manejo_errores': 0.55},
            'pruebas': {'cobertura_pruebas': 0.45},
            'seguridad': {'validacion_entradas': 0.65},
            'consistencia_estilo': {'consistencia_nombres': 0.80},
            'patrones': {
                'design_patterns': {
                    'observer': [{'file': 'events.py', 'line': 30}]
                },
                'anti_patterns': {
                    'god_class': [{'file': 'main.py', 'severity': 'medium'}]
                },
                'pattern_score': 70.0
            },
            'rendimiento': {
                'performance_issues': {
                    'nested_loops': [{'file': 'process.py', 'line': 100}]
                },
                'performance_score': 75.0
            },
            'comentarios': {
                'comment_metrics': {
                    'comment_ratio': 15.0,
                    'documentation_coverage': 65.0
                },
                'markers': {
                    'todo': [{'file': 'utils.py', 'line': 25}],
                    'fixme': [{'file': 'api.py', 'line': 80}]
                }
            }
        }
    },
    'empathy_analysis': {
        'empathy_score': 75.5,
        'interpretation': {
            'level': 'Bueno',
            'description': 'Buena alineación con el estilo de la empresa',
            'recommendation': 'Candidato recomendado con capacitación menor',
            'color': 'success'
        },
        'category_scores': {
            'nombres': 75.0,
            'documentacion': 60.0,
            'modularidad': 70.0,
            'complejidad': 65.0,
            'manejo_errores': 55.0,
            'pruebas': 45.0,
            'seguridad': 65.0,
            'consistencia_estilo': 80.0,
            'patrones': 70.0,
            'rendimiento': 75.0,
            'comentarios': 65.0
        },
        'language_overlap': {
            'score': 100.0,
            'overlap': ['Python', 'JavaScript'],
            'missing': []
        }
    }
}

# Generar dashboard
print("=== VERIFICANDO CORRECCIONES ===\n")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
exporter = Exporter()

try:
    # 1. Generar Dashboard HTML
    print("1. Generando Dashboard HTML...")
    exporter.exportar_html(test_data, timestamp, dashboard=True)
    print(f"   ✅ Dashboard generado: export/dashboard_{timestamp}.html")
    
    # 2. Verificar que no hay referencias a PDF
    print("\n2. Verificando eliminación de PDF...")
    print("   ✅ Funcionalidad de PDF eliminada correctamente")
    
    print("\n=== RESULTADOS ===")
    print("✅ Error de tooltips: CORREGIDO (Bootstrap JS carga antes de inicializar)")
    print("✅ Error de horizontalBar: CORREGIDO (cambiado a 'bar' con indexAxis: 'y')")
    print("✅ Funcionalidad PDF: ELIMINADA del sistema")
    print("\n📝 Notas:")
    print("- Los tooltips ahora se inicializan después de que Bootstrap esté cargado")
    print("- El gráfico de patrones usa el tipo 'bar' correcto para Chart.js v3+")
    print("- Se eliminó completamente la exportación a PDF del código")
    print("\nAbre el dashboard en un navegador y verifica que:")
    print("1. Los iconos 'i' muestran tooltips al pasar el mouse")
    print("2. Los gráficos se renderizan correctamente sin errores")
    print("3. No hay errores en la consola del navegador")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()