#!/usr/bin/env python3
"""
Script para probar el análisis completo sin limitaciones
"""

import sys
import os
from datetime import datetime
import time

# Configurar paths
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(root_dir, 'src'))

from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, '.env'))

from full_analyzer import FullAnalyzer
from empathy_algorithm import EmpathyAlgorithm
from exporters import Exporter
from github import Github

print("="*60)
print("ANÁLISIS COMPLETO DE REPOSITORIOS (SIN LIMITACIONES)")
print("="*60)

# Repositorios a analizar
empresa_repo = "srbhr/Resume-Matcher"
candidato_repo = "686f6c61/LLM-Psyche-Modelo-Multidimensional-Personalidad-LLM"

print(f"\n📊 Repositorios a analizar:")
print(f"   Empresa: {empresa_repo}")
print(f"   Candidato: {candidato_repo}")

# Obtener metadata de GitHub
g = Github(os.getenv('GITHUB_TOKEN'))

def get_repo_metadata(repo_name):
    """Obtiene metadata del repositorio desde GitHub"""
    try:
        repo = g.get_repo(repo_name)
        return {
            'nombre': repo.name,
            'url': repo.html_url,
            'descripcion': repo.description or 'Sin descripción',
            'lenguaje_principal': repo.language or 'JavaScript',
            'tamano_kb': float(repo.size)
        }
    except Exception as e:
        print(f"Error obteniendo metadata: {e}")
        return None

# Inicializar analizador
analyzer = FullAnalyzer()

# Analizar empresa
print(f"\n{'='*60}")
print("1️⃣ ANALIZANDO REPOSITORIO DE LA EMPRESA")
print(f"{'='*60}")

empresa_metadata = get_repo_metadata(empresa_repo)
if empresa_metadata:
    print(f"   Nombre: {empresa_metadata['nombre']}")
    print(f"   Tamaño: {empresa_metadata['tamano_kb']/1024:.1f} MB")
    print(f"   Lenguaje: {empresa_metadata['lenguaje_principal']}")

start = time.time()
empresa_url = f"https://github.com/{empresa_repo}"
analisis_empresa = analyzer.analizar_repositorio_completo(
    empresa_url, 
    empresa_repo.split('/')[-1]
)
tiempo_empresa = time.time() - start

if analisis_empresa:
    # Actualizar con metadata de GitHub
    if empresa_metadata:
        analisis_empresa['metadata'].update(empresa_metadata)
    print(f"\n✅ Análisis completado en {tiempo_empresa:.1f}s")
    print(f"   Archivos analizados: {analisis_empresa['metadata']['archivos_analizados']}")
else:
    print("\n❌ Error en el análisis de la empresa")

# Analizar candidato
print(f"\n{'='*60}")
print("2️⃣ ANALIZANDO REPOSITORIO DEL CANDIDATO")
print(f"{'='*60}")

candidato_metadata = get_repo_metadata(candidato_repo)
if candidato_metadata:
    print(f"   Nombre: {candidato_metadata['nombre']}")
    print(f"   Tamaño: {candidato_metadata['tamano_kb']/1024:.1f} MB")
    print(f"   Lenguaje: {candidato_metadata['lenguaje_principal']}")

start = time.time()
candidato_url = f"https://github.com/{candidato_repo}"
analisis_candidato = analyzer.analizar_repositorio_completo(
    candidato_url,
    candidato_repo.split('/')[-1]
)
tiempo_candidato = time.time() - start

if analisis_candidato:
    # Actualizar con metadata de GitHub
    if candidato_metadata:
        analisis_candidato['metadata'].update(candidato_metadata)
    print(f"\n✅ Análisis completado en {tiempo_candidato:.1f}s")
    print(f"   Archivos analizados: {analisis_candidato['metadata']['archivos_analizados']}")
else:
    print("\n❌ Error en el análisis del candidato")

# Si ambos análisis fueron exitosos, calcular empatía
if analisis_empresa and analisis_candidato:
    print(f"\n{'='*60}")
    print("📊 CALCULANDO PUNTUACIÓN DE EMPATÍA")
    print(f"{'='*60}")
    
    # Preparar resultados
    resultados = {
        'repos': {
            'empresa': analisis_empresa,
            'candidato': analisis_candidato
        }
    }
    
    # Calcular empatía
    algorithm = EmpathyAlgorithm()
    empathy_result = algorithm.calculate_empathy_score(
        analisis_empresa,
        analisis_candidato
    )
    
    resultados['empathy_analysis'] = empathy_result
    
    print(f"\n✨ RESULTADO FINAL:")
    print(f"   Puntuación de empatía: {empathy_result['empathy_score']:.1f}%")
    print(f"   Nivel: {empathy_result['interpretation']['level']}")
    print(f"   Evaluación: {empathy_result['interpretation']['description']}")
    print(f"   Recomendación: {empathy_result['interpretation']['recommendation']}")
    
    # Generar reportes
    print(f"\n{'='*60}")
    print("📄 GENERANDO REPORTES")
    print(f"{'='*60}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exporter = Exporter()
    
    # HTML (Dashboard)
    file_html = exporter.exportar_html(resultados, timestamp, dashboard=True)
    print(f"   ✅ Dashboard HTML: {file_html}")
    
    # TXT
    file_txt = exporter.exportar_txt(resultados, timestamp)
    print(f"   ✅ Reporte TXT: {file_txt}")
    
    print(f"\n{'='*60}")
    print("✅ ANÁLISIS COMPLETO FINALIZADO")
    print(f"{'='*60}")
    print(f"   Tiempo total: {tiempo_empresa + tiempo_candidato:.1f}s")
    print(f"   Archivos totales analizados: {analisis_empresa['metadata']['archivos_analizados'] + analisis_candidato['metadata']['archivos_analizados']}")
    
else:
    print(f"\n{'='*60}")
    print("❌ NO SE PUDO COMPLETAR EL ANÁLISIS")
    print(f"{'='*60}")