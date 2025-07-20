#!/usr/bin/env python3
"""
Genera reportes de ejemplo con datos predefinidos
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from exporters import Exporter

# Datos de ejemplo completos
sample_data = {
    'repos': {
        'empresa': {
            'metadata': {
                'nombre': 'Express Framework',
                'url': 'https://github.com/expressjs/express',
                'lenguajes_analizados': ['JavaScript'],
                'archivos_analizados': 50,
                'tamano_kb': 1200.0,
                'lenguaje_principal': 'JavaScript',
                'descripcion': 'Fast, unopinionated, minimalist web framework',
                'modo_analisis': 'local'
            },
            'nombres': {'descriptividad': 0.92},
            'documentacion': {'cobertura_docstrings': 0.78},
            'modularidad': {'funciones_por_archivo': 0.85},
            'complejidad': {'complejidad_ciclomatica': 0.88},
            'manejo_errores': {'cobertura_manejo_errores': 0.90},
            'pruebas': {'cobertura_pruebas': 0.85},
            'seguridad': {'validacion_entradas': 0.87},
            'consistencia_estilo': {'consistencia_nombres': 0.93},
            'patrones': {
                'design_patterns': {
                    'factory': [{'file': 'router/index.js', 'line': 30}],
                    'strategy': [{'file': 'middleware/init.js', 'line': 15}],
                    'observer': [{'file': 'events.js', 'line': 45}]
                },
                'anti_patterns': {},
                'pattern_score': 92.0
            },
            'rendimiento': {
                'performance_issues': {},
                'performance_score': 89.0
            },
            'comentarios': {
                'comment_metrics': {
                    'comment_ratio': 18.5,
                    'documentation_coverage': 82.0
                },
                'markers': {
                    'todo': [{'file': 'lib/application.js', 'line': 102}],
                    'deprecated': [{'file': 'lib/response.js', 'line': 567}]
                }
            }
        },
        'candidato': {
            'metadata': {
                'nombre': 'Koa Framework',
                'url': 'https://github.com/koajs/koa',
                'lenguajes_analizados': ['JavaScript'],
                'archivos_analizados': 50,
                'tamano_kb': 980.0,
                'lenguaje_principal': 'JavaScript',
                'descripcion': 'Expressive middleware framework using async functions',
                'modo_analisis': 'local'
            },
            'nombres': {'descriptividad': 0.88},
            'documentacion': {'cobertura_docstrings': 0.72},
            'modularidad': {'funciones_por_archivo': 0.90},
            'complejidad': {'complejidad_ciclomatica': 0.82},
            'manejo_errores': {'cobertura_manejo_errores': 0.85},
            'pruebas': {'cobertura_pruebas': 0.90},
            'seguridad': {'validacion_entradas': 0.83},
            'consistencia_estilo': {'consistencia_nombres': 0.89},
            'patrones': {
                'design_patterns': {
                    'factory': [{'file': 'lib/application.js', 'line': 25}],
                    'decorator': [{'file': 'lib/context.js', 'line': 40}]
                },
                'anti_patterns': {
                    'god_class': [{'file': 'lib/application.js', 'severity': 'low'}]
                },
                'pattern_score': 78.0
            },
            'rendimiento': {
                'performance_issues': {
                    'nested_loops': [{'file': 'lib/request.js', 'line': 150}]
                },
                'performance_score': 82.0
            },
            'comentarios': {
                'comment_metrics': {
                    'comment_ratio': 15.2,
                    'documentation_coverage': 75.0
                },
                'markers': {
                    'todo': [
                        {'file': 'lib/context.js', 'line': 89},
                        {'file': 'lib/response.js', 'line': 234}
                    ],
                    'fixme': [{'file': 'lib/request.js', 'line': 156}]
                }
            }
        }
    },
    'empathy_analysis': {
        'empathy_score': 85.7,
        'interpretation': {
            'level': 'Bueno',
            'description': 'Buena alineación con el estilo de la empresa',
            'recommendation': 'Candidato recomendado con capacitación menor',
            'color': 'success'
        },
        'category_scores': {
            'nombres': 88.0,
            'documentacion': 72.0,
            'modularidad': 90.0,
            'complejidad': 82.0,
            'manejo_errores': 85.0,
            'pruebas': 90.0,
            'seguridad': 83.0,
            'consistencia_estilo': 89.0,
            'patrones': 78.0,
            'rendimiento': 82.0,
            'comentarios': 75.0
        },
        'language_overlap': {
            'score': 100.0,
            'overlap': ['JavaScript'],
            'missing': []
        },
        'recommendations': [
            {
                'category': 'documentacion',
                'priority': 'media',
                'title': 'Mejorar documentación del código',
                'description': 'Aumentar la cobertura de documentación, especialmente en funciones públicas',
                'message': 'Aumentar la cobertura de documentación, especialmente en funciones públicas'
            },
            {
                'category': 'patrones',
                'priority': 'baja',
                'title': 'Considerar más patrones de diseño',
                'description': 'Implementar patrones adicionales como Observer o Strategy donde sea apropiado',
                'message': 'Implementar patrones adicionales como Observer o Strategy donde sea apropiado'
            },
            {
                'category': 'comentarios',
                'priority': 'media',
                'title': 'Mejorar ratio de comentarios',
                'description': 'Añadir más comentarios explicativos en secciones complejas del código',
                'message': 'Añadir más comentarios explicativos en secciones complejas del código'
            }
        ]
    }
}

# Generar reportes
print("=== GENERANDO REPORTES DE EJEMPLO ===\n")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
exporter = Exporter()

try:
    # TXT
    print("1. Generando reporte TXT...")
    exporter.exportar_txt(sample_data, timestamp)
    print(f"   ✅ export/reporte_{timestamp}.txt")
    
    # JSON
    print("\n2. Generando reporte JSON...")
    exporter.exportar_json(sample_data, timestamp)
    print(f"   ✅ export/reporte_{timestamp}.json")
    
    # HTML
    print("\n3. Generando reporte HTML...")
    exporter.exportar_html(sample_data, timestamp, dashboard=False)
    print(f"   ✅ export/reporte_{timestamp}.html")
    
    # Dashboard
    print("\n4. Generando Dashboard Bootstrap...")
    exporter.exportar_html(sample_data, timestamp, dashboard=True)
    print(f"   ✅ export/dashboard_{timestamp}.html")
    
    print(f"\n✨ Todos los reportes generados exitosamente!")
    print(f"   Revisa la carpeta 'export/' para ver los resultados")
    print(f"\n📊 Dashboard disponible en: export/dashboard_{timestamp}.html")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()