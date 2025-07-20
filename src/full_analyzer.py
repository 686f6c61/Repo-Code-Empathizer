#!/usr/bin/env python3
"""
Analizador completo sin limitaciones para repositorios grandes.
Utiliza análisis incremental y procesamiento por lotes.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from typing import Dict, Any, List
import logging
from pathlib import Path
from datetime import datetime
import time

# Añadir el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from language_analyzers.factory import AnalyzerFactory
from pattern_analyzer import PatternAnalyzer
from performance_analyzer import PerformanceAnalyzer
from comment_analyzer import CommentAnalyzer

logger = logging.getLogger(__name__)

class FullAnalyzer:
    """Analizador completo sin limitaciones de tamaño"""
    
    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.comment_analyzer = CommentAnalyzer()
        
    def clonar_repositorio(self, repo_url: str, target_dir: str) -> bool:
        """Clona un repositorio con progreso detallado"""
        try:
            print(f"\n🔄 Clonando {repo_url}...")
            
            # Clonar con depth 1 para rapidez pero con todos los archivos
            cmd = ['git', 'clone', '--depth', '1', '--single-branch', '--progress', repo_url, target_dir]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Mostrar progreso
            for line in process.stdout:
                line = line.strip()
                if line and any(word in line for word in ['Receiving', 'Resolving', 'Counting', 'Compressing']):
                    print(f"   {line}")
            
            process.wait()
            
            if process.returncode == 0:
                print("   ✅ Clonado completado")
                return True
            else:
                print("   ❌ Error al clonar")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    
    def contar_archivos(self, directory: str, extensions: List[str]) -> int:
        """Cuenta archivos de código en el directorio"""
        count = 0
        for root, _, files in os.walk(directory):
            # Saltar directorios ocultos y node_modules
            if any(part.startswith('.') or part == 'node_modules' for part in Path(root).parts):
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    count += 1
        return count
    
    def analizar_directorio_completo(self, directory: str) -> Dict[str, Any]:
        """Analiza un directorio completo sin limitaciones"""
        print(f"\n📊 Analizando directorio completo...")
        
        extensions = AnalyzerFactory.get_supported_extensions()
        total_files = self.contar_archivos(directory, extensions)
        print(f"   📁 Total de archivos a analizar: {total_files}")
        
        archivos_codigo = {}
        archivos_procesados = 0
        
        # Procesar por lotes de 50 archivos
        batch_size = 50
        current_batch = {}
        
        for root, _, files in os.walk(directory):
            # Saltar directorios ocultos y node_modules
            if any(part.startswith('.') or part == 'node_modules' for part in Path(root).parts):
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory)
                    
                    try:
                        # Saltar archivos muy grandes (>5MB)
                        if os.path.getsize(file_path) > 5 * 1024 * 1024:
                            continue
                            
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            current_batch[rel_path] = f.read()
                            archivos_procesados += 1
                            
                        # Procesar lote cuando alcance el tamaño
                        if len(current_batch) >= batch_size:
                            archivos_codigo.update(current_batch)
                            current_batch = {}
                            print(f"   📄 Procesados: {archivos_procesados}/{total_files} ({archivos_procesados/total_files*100:.1f}%)")
                            
                    except Exception as e:
                        logger.warning(f"Error leyendo {file_path}: {str(e)}")
        
        # Procesar último lote
        if current_batch:
            archivos_codigo.update(current_batch)
            print(f"   📄 Procesados: {archivos_procesados}/{total_files} (100%)")
        
        print(f"   ✅ Análisis de archivos completado: {archivos_procesados} archivos")
        
        # Analizar con el factory
        print("\n🔍 Calculando métricas...")
        if archivos_codigo:
            analisis = AnalyzerFactory.analyze_multi_language_project(archivos_codigo)
            
            # Extraer métricas del lenguaje principal
            metricas = {
                'metadata': {
                    'archivos_analizados': archivos_procesados,
                    'lenguajes_analizados': analisis.get('total_metrics', {}).get('languages_analyzed', []),
                    'lenguaje_principal': analisis.get('primary_language', 'JavaScript')
                }
            }
            
            # Obtener métricas del lenguaje principal
            if analisis['primary_language'] and analisis['primary_language'] in analisis['languages']:
                lang_metrics = analisis['languages'][analisis['primary_language']]['metrics']
                
                # Copiar métricas básicas
                for categoria in ['nombres', 'documentacion', 'modularidad', 'complejidad', 
                                'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']:
                    if categoria in lang_metrics:
                        metricas[categoria] = lang_metrics[categoria]
                
                # Análisis avanzados
                print("   🎯 Ejecutando análisis de patrones...")
                metricas['patrones'] = self.pattern_analyzer.analyze_patterns(archivos_codigo, analisis['primary_language'])
                
                print("   ⚡ Ejecutando análisis de rendimiento...")
                metricas['rendimiento'] = self.performance_analyzer.analyze_performance(archivos_codigo, analisis['primary_language'])
                
                print("   💬 Ejecutando análisis de comentarios...")
                metricas['comentarios'] = self.comment_analyzer.analyze_comments(archivos_codigo, analisis['primary_language'])
            
            return metricas
        else:
            return None
    
    def analizar_repositorio_completo(self, repo_url: str, repo_name: str) -> Dict[str, Any]:
        """Analiza un repositorio completo sin limitaciones"""
        temp_dir = None
        
        try:
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp(prefix=f"repo_analysis_{repo_name}_")
            target_dir = os.path.join(temp_dir, repo_name)
            
            # Clonar repositorio
            if not self.clonar_repositorio(repo_url, target_dir):
                return None
            
            # Obtener metadata del repositorio
            metadata = {
                'nombre': repo_name,
                'url': repo_url,
                'descripcion': 'Análisis completo sin limitaciones',
                'tamano_kb': 0,
                'fecha_analisis': datetime.now().isoformat()
            }
            
            # Calcular tamaño
            total_size = 0
            for root, _, files in os.walk(target_dir):
                for file in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, file))
                    except:
                        pass
            
            metadata['tamano_kb'] = total_size / 1024
            print(f"   📦 Tamaño del repositorio: {metadata['tamano_kb']/1024:.1f} MB")
            
            # Analizar directorio
            metricas = self.analizar_directorio_completo(target_dir)
            
            if metricas:
                # Actualizar metadata
                metricas['metadata'].update(metadata)
                return metricas
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error analizando repositorio: {str(e)}")
            return None
            
        finally:
            # Limpiar directorio temporal
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    print("   🧹 Directorio temporal eliminado")
                except:
                    pass

def main():
    """Función principal para pruebas"""
    if len(sys.argv) < 3:
        print("Uso: python full_analyzer.py <repo_empresa> <repo_candidato>")
        sys.exit(1)
    
    analyzer = FullAnalyzer()
    
    # Analizar empresa
    print("="*50)
    print("ANÁLISIS COMPLETO SIN LIMITACIONES")
    print("="*50)
    
    empresa_url = f"https://github.com/{sys.argv[1]}"
    empresa_name = sys.argv[1].split('/')[-1]
    
    print(f"\n1️⃣ Analizando empresa: {sys.argv[1]}")
    start = time.time()
    analisis_empresa = analyzer.analizar_repositorio_completo(empresa_url, empresa_name)
    print(f"⏱️  Tiempo total: {time.time() - start:.1f}s")
    
    # Analizar candidato
    candidato_url = f"https://github.com/{sys.argv[2]}"
    candidato_name = sys.argv[2].split('/')[-1]
    
    print(f"\n2️⃣ Analizando candidato: {sys.argv[2]}")
    start = time.time()
    analisis_candidato = analyzer.analizar_repositorio_completo(candidato_url, candidato_name)
    print(f"⏱️  Tiempo total: {time.time() - start:.1f}s")
    
    if analisis_empresa and analisis_candidato:
        print("\n✅ Análisis completo finalizado")
        print(f"   Empresa: {analisis_empresa['metadata']['archivos_analizados']} archivos")
        print(f"   Candidato: {analisis_candidato['metadata']['archivos_analizados']} archivos")
    else:
        print("\n❌ Error en el análisis")

if __name__ == "__main__":
    main()