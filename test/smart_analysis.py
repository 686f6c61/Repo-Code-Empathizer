#!/usr/bin/env python3
"""
Análisis inteligente que balancea completitud con velocidad.
Analiza una muestra representativa de archivos de cada repositorio.
"""

import sys
import os
import tempfile
import shutil
import subprocess
from typing import Dict, Any, List
import logging
from pathlib import Path
from datetime import datetime
import time
import random

# Configurar paths
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(root_dir, 'src'))

from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, '.env'))

from language_analyzers.factory import AnalyzerFactory
from pattern_analyzer import PatternAnalyzer
from performance_analyzer import PerformanceAnalyzer
from comment_analyzer import CommentAnalyzer
from empathy_algorithm import EmpathyAlgorithm
from exporters import Exporter
from github import Github

logger = logging.getLogger(__name__)

class SmartAnalyzer:
    """Analizador inteligente con muestreo estratégico"""
    
    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.comment_analyzer = CommentAnalyzer()
        self.github = Github(os.getenv('GITHUB_TOKEN'))
        
    def clonar_repo_shallow(self, repo_url: str, target_dir: str) -> bool:
        """Clona solo la estructura superficial del repositorio"""
        try:
            print(f"   🔄 Clonando {repo_url}...")
            cmd = ['git', 'clone', '--depth', '1', '--single-branch', repo_url, target_dir]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Clonado completado")
                return True
            else:
                print(f"   ❌ Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    def obtener_archivos_estrategicos(self, directory: str, max_files: int = 100) -> Dict[str, str]:
        """Obtiene una muestra estratégica de archivos del proyecto"""
        extensions = AnalyzerFactory.get_supported_extensions()
        archivos_por_tipo = {}
        archivos_seleccionados = {}
        
        # Primero, clasificar todos los archivos por tipo
        for root, _, files in os.walk(directory):
            # Saltar directorios no relevantes
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'venv', 'dist', 'build']):
                continue
                
            for file in files:
                for ext in extensions:
                    if file.endswith(ext):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, directory)
                        
                        # Saltar archivos muy grandes
                        try:
                            if os.path.getsize(file_path) > 500 * 1024:  # 500KB
                                continue
                        except:
                            continue
                            
                        if ext not in archivos_por_tipo:
                            archivos_por_tipo[ext] = []
                        archivos_por_tipo[ext].append((rel_path, file_path))
                        break
        
        # Estrategia de selección:
        # 1. Archivos importantes (README, setup, config, main, index)
        archivos_importantes = ['README', 'setup', 'config', 'main', 'index', 'app', 'server']
        
        for ext, archivos in archivos_por_tipo.items():
            for rel_path, file_path in archivos:
                for importante in archivos_importantes:
                    if importante in os.path.basename(file_path).lower():
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                archivos_seleccionados[rel_path] = f.read()
                            if len(archivos_seleccionados) >= max_files:
                                return archivos_seleccionados
                        except:
                            pass
        
        # 2. Muestreo proporcional por tipo de archivo
        archivos_restantes = max_files - len(archivos_seleccionados)
        if archivos_restantes > 0:
            for ext, archivos in archivos_por_tipo.items():
                # Tomar hasta 20% de cada tipo
                num_muestras = min(len(archivos) // 5, archivos_restantes // len(archivos_por_tipo))
                if num_muestras > 0:
                    muestras = random.sample(archivos, min(num_muestras, len(archivos)))
                    for rel_path, file_path in muestras:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                archivos_seleccionados[rel_path] = f.read()
                            if len(archivos_seleccionados) >= max_files:
                                return archivos_seleccionados
                        except:
                            pass
        
        return archivos_seleccionados
    
    def analizar_repositorio_smart(self, repo_name: str, repo_url: str) -> Dict[str, Any]:
        """Analiza un repositorio de forma inteligente"""
        temp_dir = None
        
        try:
            # Obtener metadata de GitHub
            print(f"\n📊 Obteniendo información de {repo_name}...")
            repo = self.github.get_repo(repo_name)
            
            metadata = {
                'nombre': repo.name,
                'url': repo.html_url,
                'descripcion': repo.description or 'Sin descripción',
                'lenguaje_principal': repo.language or 'JavaScript',
                'tamano_kb': float(repo.size),
                'lenguajes_analizados': []
            }
            
            print(f"   Tamaño: {metadata['tamano_kb']/1024:.1f} MB")
            print(f"   Lenguaje principal: {metadata['lenguaje_principal']}")
            
            # Determinar número de archivos a analizar basado en tamaño
            if metadata['tamano_kb'] > 100000:  # >100MB
                max_files = 50
            elif metadata['tamano_kb'] > 50000:  # >50MB
                max_files = 75
            elif metadata['tamano_kb'] > 10000:  # >10MB
                max_files = 100
            else:
                max_files = 150
                
            print(f"   Límite de archivos: {max_files}")
            
            # Clonar repositorio
            temp_dir = tempfile.mkdtemp(prefix=f"smart_analysis_")
            target_dir = os.path.join(temp_dir, repo.name)
            
            if not self.clonar_repo_shallow(repo_url, target_dir):
                return None
            
            # Obtener muestra estratégica de archivos
            print(f"   🎯 Seleccionando muestra estratégica...")
            archivos_codigo = self.obtener_archivos_estrategicos(target_dir, max_files)
            
            print(f"   📄 {len(archivos_codigo)} archivos seleccionados")
            
            if not archivos_codigo:
                print("   ⚠️  No se encontraron archivos de código")
                return None
            
            # Analizar con el factory
            print("   🔍 Calculando métricas...")
            analisis = AnalyzerFactory.analyze_multi_language_project(archivos_codigo)
            
            # Preparar métricas
            metricas = {'metadata': metadata}
            
            if analisis and 'primary_language' in analisis:
                # Actualizar metadata
                metadata['archivos_analizados'] = len(archivos_codigo)
                metadata['lenguajes_analizados'] = analisis.get('total_metrics', {}).get('languages_analyzed', [])
                
                # Obtener métricas del lenguaje principal
                if analisis['primary_language'] in analisis['languages']:
                    lang_data = analisis['languages'][analisis['primary_language']]
                    
                    # Copiar métricas básicas
                    if 'metrics' in lang_data:
                        for categoria in ['nombres', 'documentacion', 'modularidad', 'complejidad',
                                        'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']:
                            if categoria in lang_data['metrics']:
                                metricas[categoria] = lang_data['metrics'][categoria]
                    
                    # Análisis avanzados (solo si hay suficientes archivos)
                    if len(archivos_codigo) >= 10:
                        print("   🎯 Ejecutando análisis avanzados...")
                        
                        # Patrones
                        metricas['patrones'] = self.pattern_analyzer.analyze_patterns(
                            archivos_codigo, 
                            analisis['primary_language']
                        )
                        
                        # Rendimiento
                        metricas['rendimiento'] = self.performance_analyzer.analyze_performance(
                            archivos_codigo,
                            analisis['primary_language']
                        )
                        
                        # Comentarios
                        metricas['comentarios'] = self.comment_analyzer.analyze_comments(
                            archivos_codigo,
                            analisis['primary_language']
                        )
                    else:
                        # Valores por defecto para análisis avanzados
                        metricas['patrones'] = {
                            'design_patterns': {},
                            'anti_patterns': {},
                            'pattern_score': 70.0
                        }
                        metricas['rendimiento'] = {
                            'performance_issues': {},
                            'performance_score': 75.0
                        }
                        metricas['comentarios'] = {
                            'comment_metrics': {
                                'comment_ratio': 15.0,
                                'documentation_coverage': 65.0
                            },
                            'markers': {}
                        }
            
            return metricas
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None
            
        finally:
            # Limpiar
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

def main():
    """Función principal"""
    print("="*60)
    print("ANÁLISIS INTELIGENTE DE REPOSITORIOS")
    print("="*60)
    
    # Repositorios
    empresa_repo = "srbhr/Resume-Matcher"
    candidato_repo = "686f6c61/LLM-Psyche-Modelo-Multidimensional-Personalidad-LLM"
    
    analyzer = SmartAnalyzer()
    
    # Analizar empresa
    print(f"\n1️⃣ ANALIZANDO EMPRESA: {empresa_repo}")
    start = time.time()
    analisis_empresa = analyzer.analizar_repositorio_smart(
        empresa_repo,
        f"https://github.com/{empresa_repo}"
    )
    tiempo_empresa = time.time() - start
    
    if analisis_empresa:
        print(f"   ✅ Completado en {tiempo_empresa:.1f}s")
    else:
        print("   ❌ Error en el análisis")
        return
    
    # Analizar candidato
    print(f"\n2️⃣ ANALIZANDO CANDIDATO: {candidato_repo}")
    start = time.time()
    analisis_candidato = analyzer.analizar_repositorio_smart(
        candidato_repo,
        f"https://github.com/{candidato_repo}"
    )
    tiempo_candidato = time.time() - start
    
    if analisis_candidato:
        print(f"   ✅ Completado en {tiempo_candidato:.1f}s")
    else:
        print("   ❌ Error en el análisis")
        return
    
    # Calcular empatía
    print(f"\n{'='*60}")
    print("📊 CALCULANDO EMPATÍA")
    print(f"{'='*60}")
    
    resultados = {
        'repos': {
            'empresa': analisis_empresa,
            'candidato': analisis_candidato
        }
    }
    
    algorithm = EmpathyAlgorithm()
    empathy_result = algorithm.calculate_empathy_score(
        analisis_empresa,
        analisis_candidato
    )
    
    resultados['empathy_analysis'] = empathy_result
    
    print(f"\n✨ RESULTADO:")
    print(f"   Puntuación: {empathy_result['empathy_score']:.1f}%")
    print(f"   Nivel: {empathy_result['interpretation']['level']}")
    print(f"   Evaluación: {empathy_result['interpretation']['description']}")
    
    # Generar reportes
    print(f"\n📄 GENERANDO REPORTES...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exporter = Exporter()
    
    # Dashboard HTML
    file_html = exporter.exportar_html(resultados, timestamp, dashboard=True)
    print(f"   ✅ Dashboard: {file_html}")
    
    # Reporte TXT
    file_txt = exporter.exportar_txt(resultados, timestamp)
    print(f"   ✅ Texto: {file_txt}")
    
    print(f"\n{'='*60}")
    print("✅ ANÁLISIS COMPLETADO")
    print(f"{'='*60}")
    print(f"   Tiempo total: {tiempo_empresa + tiempo_candidato:.1f}s")
    print(f"   Archivos analizados:")
    print(f"     - Empresa: {analisis_empresa['metadata']['archivos_analizados']}")
    print(f"     - Candidato: {analisis_candidato['metadata']['archivos_analizados']}")

if __name__ == "__main__":
    main()