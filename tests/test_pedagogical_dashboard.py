#!/usr/bin/env python3
"""
Script para verificar las mejoras pedagógicas del dashboard
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from exporters import Exporter

# Datos de prueba con todas las métricas
test_data = {
    'repos': {
        'empresa': {
            'metadata': {
                'nombre': 'TechCorp Backend',
                'url': 'https://github.com/techcorp/backend',
                'lenguajes_analizados': ['Python', 'JavaScript'],
                'archivos_analizados': 150,
                'tamano_kb': 2500.5,
                'lenguaje_principal': 'Python',
                'descripcion': 'Sistema backend principal de la empresa'
            },
            'nombres': {'descriptividad': 0.85},
            'documentacion': {'cobertura_docstrings': 0.72},
            'modularidad': {'funciones_por_archivo': 4.5},
            'complejidad': {'complejidad_ciclomatica': 3.2},
            'manejo_errores': {'cobertura_manejo_errores': 0.68},
            'pruebas': {'cobertura_pruebas': 0.75},
            'seguridad': {'validacion_entradas': 0.82},
            'consistencia_estilo': {'consistencia_nombres': 0.91},
            'patrones': {
                'design_patterns': {
                    'singleton': [{'file': 'db.py', 'line': 10}],
                    'factory': [{'file': 'models.py', 'line': 25}]
                },
                'anti_patterns': {},
                'pattern_score': 85.0
            },
            'rendimiento': {
                'performance_issues': {
                    'nested_loops': [{'file': 'process.py', 'line': 45}]
                },
                'performance_score': 78.5
            },
            'comentarios': {
                'comment_metrics': {
                    'comment_ratio': 18.5,
                    'documentation_coverage': 82.0
                },
                'markers': {
                    'todo': [{'file': 'api.py', 'line': 30}],
                    'fixme': []
                }
            }
        },
        'candidato': {
            'metadata': {
                'nombre': 'John Doe Portfolio',
                'url': 'https://github.com/johndoe/portfolio',
                'lenguajes_analizados': ['Python', 'JavaScript'],
                'archivos_analizados': 75,
                'tamano_kb': 850.3,
                'lenguaje_principal': 'Python',
                'descripcion': 'Portfolio de proyectos del candidato'
            },
            'nombres': {'descriptividad': 0.72},
            'documentacion': {'cobertura_docstrings': 0.45},
            'modularidad': {'funciones_por_archivo': 6.2},
            'complejidad': {'complejidad_ciclomatica': 4.8},
            'manejo_errores': {'cobertura_manejo_errores': 0.42},
            'pruebas': {'cobertura_pruebas': 0.35},
            'seguridad': {'validacion_entradas': 0.55},
            'consistencia_estilo': {'consistencia_nombres': 0.78},
            'patrones': {
                'design_patterns': {
                    'observer': [{'file': 'events.py', 'line': 15}]
                },
                'anti_patterns': {
                    'god_class': [{'file': 'main.py', 'severity': 'medium'}]
                },
                'pattern_score': 65.0
            },
            'rendimiento': {
                'performance_issues': {
                    'nested_loops': [
                        {'file': 'analyze.py', 'line': 120},
                        {'file': 'process.py', 'line': 88}
                    ]
                },
                'performance_score': 62.0
            },
            'comentarios': {
                'comment_metrics': {
                    'comment_ratio': 12.3,
                    'documentation_coverage': 58.0
                },
                'markers': {
                    'todo': [
                        {'file': 'utils.py', 'line': 45},
                        {'file': 'helpers.py', 'line': 78}
                    ],
                    'fixme': [
                        {'file': 'api.py', 'line': 92}
                    ],
                    'hack': [
                        {'file': 'workaround.py', 'line': 15}
                    ]
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
            'nombres': 72.0,
            'documentacion': 45.0,
            'modularidad': 65.0,
            'complejidad': 55.0,
            'manejo_errores': 42.0,
            'pruebas': 35.0,
            'seguridad': 55.0,
            'consistencia_estilo': 78.0,
            'patrones': 65.0,
            'rendimiento': 62.0,
            'comentarios': 58.0
        },
        'language_overlap': {
            'score': 100.0,
            'overlap': ['Python', 'JavaScript'],
            'missing': []
        },
        'detailed_analysis': {
            'strengths': [
                {'category': 'consistencia_estilo', 'score': 78.0},
                {'category': 'nombres', 'score': 72.0}
            ],
            'weaknesses': [
                {'category': 'pruebas', 'score': 35.0},
                {'category': 'manejo_errores', 'score': 42.0},
                {'category': 'documentacion', 'score': 45.0}
            ]
        },
        'recommendations': [
            {
                'type': 'critical',
                'priority': 'high',
                'title': 'Implementar más pruebas',
                'description': 'Aumentar la cobertura de pruebas unitarias y de integración'
            },
            {
                'type': 'improvement',
                'priority': 'medium',
                'title': 'Mejorar documentación',
                'description': 'Añadir docstrings a funciones y clases principales'
            },
            {
                'type': 'improvement',
                'priority': 'medium',
                'title': 'Reforzar manejo de errores',
                'description': 'Implementar validaciones y manejo de excepciones más robusto'
            }
        ]
    }
}

# Generar dashboard
print("Generando dashboard pedagógico de prueba...")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
exporter = Exporter()

try:
    exporter.exportar_html(test_data, timestamp, dashboard=True)
    print(f"✅ Dashboard generado exitosamente: export/dashboard_{timestamp}.html")
    print("\nCaracterísticas pedagógicas incluidas:")
    print("- ✓ Tooltips con iconos 'i' en todas las métricas")
    print("- ✓ Explicación de rangos de puntuación")
    print("- ✓ Acordeón con algoritmo completo y fórmula")
    print("- ✓ Tabla de pesos de categorías")
    print("- ✓ Explicación de factores de ajuste")
    print("- ✓ Interpretación de niveles en cada métrica")
    print("\nAbre el archivo HTML en un navegador para verificar todas las mejoras pedagógicas.")
except Exception as e:
    print(f"❌ Error generando dashboard: {e}")
    import traceback
    traceback.print_exc()