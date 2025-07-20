#!/usr/bin/env python3
"""
Script de prueba local para analizar repositorios de ejemplo.
"""

import os
import sys
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from language_analyzers.factory import AnalyzerFactory
from empathy_algorithm import EmpathyAlgorithm
from exporters import Exporter


def analyze_local_repos():
    """Analiza los repositorios de prueba locales."""
    
    print("🔍 Analizando repositorios de prueba locales...")
    
    # Leer archivos de empresa
    empresa_files = {}
    empresa_path = "test_repos/empresa"
    for filename in os.listdir(empresa_path):
        if filename.endswith('.py'):
            filepath = os.path.join(empresa_path, filename)
            with open(filepath, 'r') as f:
                empresa_files[filepath] = f.read()
    
    # Leer archivos de candidato
    candidato_files = {}
    candidato_path = "test_repos/candidato"
    for filename in os.listdir(candidato_path):
        if filename.endswith('.py'):
            filepath = os.path.join(candidato_path, filename)
            with open(filepath, 'r') as f:
                candidato_files[filepath] = f.read()
    
    print(f"📁 Empresa: {len(empresa_files)} archivos")
    print(f"📁 Candidato: {len(candidato_files)} archivos")
    
    # Analizar con el factory
    print("\n🧮 Analizando código...")
    
    empresa_analysis = AnalyzerFactory.analyze_multi_language_project(empresa_files)
    candidato_analysis = AnalyzerFactory.analyze_multi_language_project(candidato_files)
    
    # Preparar métricas para el algoritmo
    metricas = {
        'repos': {
            'empresa': {
                'metadata': {
                    'nombre': 'Empresa Test',
                    'url': 'local://test_repos/empresa',
                    'descripcion': 'Código de prueba de la empresa',
                    'lenguaje_principal': 'Python',
                    'archivos_analizados': len(empresa_files),
                    'tamano_kb': sum(len(content) for content in empresa_files.values()) / 1024
                }
            },
            'candidato': {
                'metadata': {
                    'nombre': 'Candidato Test',
                    'url': 'local://test_repos/candidato',
                    'descripcion': 'Código de prueba del candidato',
                    'lenguaje_principal': 'Python',
                    'archivos_analizados': len(candidato_files),
                    'tamano_kb': sum(len(content) for content in candidato_files.values()) / 1024
                }
            }
        }
    }
    
    # Agregar métricas del análisis
    if empresa_analysis['languages'].get('Python'):
        empresa_metrics = empresa_analysis['languages']['Python']
        metricas['repos']['empresa'].update(empresa_metrics['metrics'])
        metricas['repos']['empresa']['duplicacion'] = empresa_metrics.get('duplication', {})
        metricas['repos']['empresa']['dependencias'] = empresa_metrics.get('dependencies', {})
        metricas['repos']['empresa']['patrones'] = empresa_metrics.get('patterns', {})
        metricas['repos']['empresa']['rendimiento'] = empresa_metrics.get('performance', {})
        metricas['repos']['empresa']['comentarios'] = empresa_metrics.get('comments', {})
    
    if candidato_analysis['languages'].get('Python'):
        candidato_metrics = candidato_analysis['languages']['Python']
        metricas['repos']['candidato'].update(candidato_metrics['metrics'])
        metricas['repos']['candidato']['duplicacion'] = candidato_metrics.get('duplication', {})
        metricas['repos']['candidato']['dependencias'] = candidato_metrics.get('dependencies', {})
        metricas['repos']['candidato']['patrones'] = candidato_metrics.get('patterns', {})
        metricas['repos']['candidato']['rendimiento'] = candidato_metrics.get('performance', {})
        metricas['repos']['candidato']['comentarios'] = candidato_metrics.get('comments', {})
    
    # Calcular empatía
    print("\n🎯 Calculando puntuación de empatía...")
    algorithm = EmpathyAlgorithm()
    empathy_result = algorithm.calculate_empathy(
        metricas['repos']['empresa'],
        metricas['repos']['candidato']
    )
    
    metricas['empathy_analysis'] = empathy_result
    
    print(f"\n📊 PUNTUACIÓN DE EMPATÍA: {empathy_result['empathy_score']:.1f}%")
    print(f"   Nivel: {empathy_result['interpretation']['level']}")
    print(f"   {empathy_result['interpretation']['description']}")
    
    # Exportar resultados
    print("\n📄 Generando reportes...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exporter = Exporter()
    
    os.makedirs('export', exist_ok=True)
    
    # Generar todos los formatos
    exporter.exportar_txt(metricas, timestamp)
    print("✅ Reporte TXT generado")
    
    exporter.exportar_json(metricas, timestamp)
    print("✅ Reporte JSON generado")
    
    exporter.exportar_html(metricas, timestamp, dashboard=True)
    print("✅ Dashboard HTML generado")
    
    try:
        exporter.exportar_pdf(metricas, timestamp)
        print("✅ Reporte PDF generado")
    except Exception as e:
        print(f"⚠️  No se pudo generar PDF: {e}")
    
    print(f"\n✨ Reportes guardados en export/reporte_{timestamp}.*")
    
    # Mostrar resumen de métricas
    print("\n📊 Resumen de métricas:")
    print("\nEMPRESA:")
    for categoria, valores in empresa_metrics['metrics'].items():
        if isinstance(valores, dict) and valores:
            print(f"  {categoria}: {list(valores.values())[0]:.2f}")
    
    print("\nCANDIDATO:")
    for categoria, valores in candidato_metrics['metrics'].items():
        if isinstance(valores, dict) and valores:
            print(f"  {categoria}: {list(valores.values())[0]:.2f}")
    
    # Mostrar análisis avanzado
    if 'patterns' in metricas['repos']['candidato']:
        print("\n🎯 Análisis Avanzado del Candidato:")
        patterns = metricas['repos']['candidato']['patrones']
        if patterns.get('anti_patterns'):
            print("  Anti-patrones detectados:")
            for pattern, instances in patterns['anti_patterns'].items():
                print(f"    - {pattern}: {len(instances)} instancias")
    
    if 'comentarios' in metricas['repos']['candidato']:
        comments = metricas['repos']['candidato']['comentarios']
        if comments.get('markers'):
            print("  Marcadores en comentarios:")
            for marker, items in comments['markers'].items():
                if items:
                    print(f"    - {marker.upper()}: {len(items)}")


if __name__ == "__main__":
    analyze_local_repos()