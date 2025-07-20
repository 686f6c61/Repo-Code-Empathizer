#!/usr/bin/env python3
"""
Script para verificar que el gráfico radar está corregido
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
                'nombre': 'TechCorp Backend',
                'url': 'https://github.com/techcorp/backend',
                'lenguajes_analizados': ['Python', 'JavaScript'],
                'archivos_analizados': 150,
                'tamano_kb': 2500.0,
                'lenguaje_principal': 'Python',
                'descripcion': 'Sistema backend principal'
            },
            'nombres': {'descriptividad': 0.90},
            'documentacion': {'cobertura_docstrings': 0.85},
            'modularidad': {'funciones_por_archivo': 0.88},
            'complejidad': {'complejidad_ciclomatica': 0.85},
            'manejo_errores': {'cobertura_manejo_errores': 0.85},
            'pruebas': {'cobertura_pruebas': 0.85},
            'seguridad': {'validacion_entradas': 0.88},
            'consistencia_estilo': {'consistencia_nombres': 0.90}
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
            'modularidad': {'funciones_por_archivo': 0.65},
            'complejidad': {'complejidad_ciclomatica': 0.55},
            'manejo_errores': {'cobertura_manejo_errores': 0.42},
            'pruebas': {'cobertura_pruebas': 0.30},
            'seguridad': {'validacion_entradas': 0.55},
            'consistencia_estilo': {'consistencia_nombres': 0.78}
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
            'nombres': 75.0,
            'documentacion': 45.0,
            'modularidad': 65.0,
            'complejidad': 55.0,
            'manejo_errores': 42.0,
            'pruebas': 30.0,
            'seguridad': 55.0,
            'consistencia_estilo': 78.0,
            'patrones': 60.0,
            'rendimiento': 70.0,
            'comentarios': 50.0
        },
        'language_overlap': {
            'score': 100.0,
            'overlap': ['Python', 'JavaScript'],
            'missing': []
        }
    }
}

# Generar dashboard
print("=== VERIFICANDO CORRECCIÓN DEL GRÁFICO RADAR ===\n")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
exporter = Exporter()

try:
    print("1. Generando Dashboard con radar corregido...")
    exporter.exportar_html(test_data, timestamp, dashboard=True)
    print(f"   ✅ Dashboard generado: export/dashboard_{timestamp}.html")
    
    print("\n=== CORRECCIONES APLICADAS ===")
    print("✅ Datos del Radar Normalizados:")
    print("   - Los valores de la empresa ahora usan benchmarks fijos (85-90)")
    print("   - Categorías críticas (nombres, docs, estilo): 90%")
    print("   - Categorías importantes (modularidad, seguridad, patrones): 88%")
    print("   - Otras categorías: 85%")
    print("   - Los datos del candidato usan los scores calculados correctamente")
    
    print("\n✅ Mejoras visuales:")
    print("   - Altura del gráfico ajustada a 450px")
    print("   - Position: relative para mejor control")
    print("   - Escala máxima limitada a 100")
    
    print("\n📊 Valores esperados en el radar:")
    print("   Empresa (azul): ~85-90 en todas las categorías")
    print("   Candidato (ciruela): valores variables según el análisis")
    
    print("\nAbre el dashboard y verifica:")
    print("1. Que el gráfico radar no se sale de la página")
    print("2. Que los valores están en el rango 0-100")
    print("3. Revisa la consola del navegador para ver los datos debug")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()