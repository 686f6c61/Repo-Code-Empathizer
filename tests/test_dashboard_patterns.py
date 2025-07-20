#!/usr/bin/env python3
"""
Script para probar por qué los patrones no aparecen en el dashboard
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from pattern_analyzer import PatternAnalyzer
from language_analyzers.factory import AnalyzerFactory
from exporters import Exporter
from datetime import datetime

# Código de ejemplo con patrones
test_files = {
    'singleton.py': '''
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        pass

class UserFactory:
    def create_user(self, user_type):
        if user_type == "admin":
            return AdminUser()
        return RegularUser()
''',
    'observer.py': '''
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)
'''
}

# Simular análisis completo
print("1. Analizando archivos con AnalyzerFactory...")
analysis_result = AnalyzerFactory.analyze_multi_language_project(test_files)

print("\n2. Estructura del resultado:")
print(f"   - Lenguaje principal: {analysis_result.get('primary_language')}")
print(f"   - Lenguajes detectados: {list(analysis_result.get('languages', {}).keys())}")

if analysis_result.get('primary_language'):
    lang_data = analysis_result['languages'][analysis_result['primary_language']]
    print(f"\n3. Datos del lenguaje principal ({analysis_result['primary_language']}):")
    print(f"   - Tiene 'patterns'? {'patterns' in lang_data}")
    if 'patterns' in lang_data:
        patterns = lang_data['patterns']
        print(f"   - Contenido de patterns: {json.dumps(patterns, indent=2)}")

# Simular estructura de datos como en main.py
resultados = {
    'repos': {
        'empresa': {
            'metadata': {
                'nombre': 'Test Empresa',
                'url': 'https://github.com/test/empresa',
                'lenguajes_analizados': ['Python'],
                'archivos_analizados': len(test_files),
                'tamano_kb': 10.5,
                'lenguaje_principal': 'Python',
                'descripcion': 'Test repository'
            },
            'nombres': {'descriptividad': 0.8},
            'documentacion': {'cobertura_docstrings': 0.5},
            'modularidad': {'funciones_por_archivo': 2.0},
            'complejidad': {'complejidad_ciclomatica': 3.0},
            'manejo_errores': {'cobertura_manejo_errores': 0.2},
            'pruebas': {'cobertura_pruebas': 0.0},
            'seguridad': {'validacion_entradas': 0.3},
            'consistencia_estilo': {'consistencia_nombres': 0.9},
        },
        'candidato': {
            'metadata': {
                'nombre': 'Test Candidato',
                'url': 'https://github.com/test/candidato',
                'lenguajes_analizados': ['Python'],
                'archivos_analizados': len(test_files),
                'tamano_kb': 8.3,
                'lenguaje_principal': 'Python',
                'descripcion': 'Test candidate repository'
            },
            'nombres': {'descriptividad': 0.7},
            'documentacion': {'cobertura_docstrings': 0.4},
            'modularidad': {'funciones_por_archivo': 2.5},
            'complejidad': {'complejidad_ciclomatica': 4.0},
            'manejo_errores': {'cobertura_manejo_errores': 0.1},
            'pruebas': {'cobertura_pruebas': 0.0},
            'seguridad': {'validacion_entradas': 0.2},
            'consistencia_estilo': {'consistencia_nombres': 0.8},
        }
    },
    'empathy_analysis': {
        'empathy_score': 75.5,
        'interpretation': {
            'level': 'Bueno',
            'description': 'Buena alineación',
            'recommendation': 'Recomendado'
        },
        'category_scores': {
            'nombres': 85.0,
            'documentacion': 70.0,
            'modularidad': 80.0,
            'complejidad': 75.0,
            'manejo_errores': 60.0,
            'pruebas': 50.0,
            'seguridad': 65.0,
            'consistencia_estilo': 90.0,
            'patrones': 75.0,
            'rendimiento': 80.0,
            'comentarios': 70.0
        }
    }
}

# Agregar patrones si existen
if analysis_result.get('primary_language') and 'patterns' in analysis_result['languages'][analysis_result['primary_language']]:
    patterns_data = analysis_result['languages'][analysis_result['primary_language']]['patterns']
    resultados['repos']['empresa']['patrones'] = patterns_data
    resultados['repos']['candidato']['patrones'] = patterns_data  # Simulamos mismo patrón

print("\n4. Estructura de resultados simulada:")
print(f"   - Tiene empresa.patrones? {'patrones' in resultados['repos']['empresa']}")
print(f"   - Tiene candidato.patrones? {'patrones' in resultados['repos']['candidato']}")

# Generar dashboard de prueba
print("\n5. Generando dashboard de prueba...")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
exporter = Exporter()

try:
    exporter.exportar_html(resultados, timestamp, dashboard=True)
    print(f"   ✅ Dashboard generado: export/dashboard_{timestamp}.html")
    
    # Verificar contenido
    with open(f'export/dashboard_{timestamp}.html', 'r') as f:
        content = f.read()
        if 'Análisis de Patrones de Diseño' in content:
            print("   ✅ Sección de patrones encontrada en HTML")
            if 'No se detectaron patrones' in content:
                print("   ⚠️ Pero muestra mensaje de 'No se detectaron patrones'")
        else:
            print("   ❌ Sección de patrones NO encontrada en HTML")
            
except Exception as e:
    print(f"   ❌ Error generando dashboard: {e}")