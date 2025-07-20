"""
Analizador local que clona repositorios temporalmente para análisis más rápido
"""

import os
import shutil
import tempfile
import subprocess
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import time

from language_analyzers.factory import AnalyzerFactory

logger = logging.getLogger(__name__)

class LocalRepoAnalyzer:
    """
    Analiza repositorios clonándolos localmente para mejor rendimiento
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Inicializa el analizador local
        
        Args:
            temp_dir: Directorio temporal personalizado (opcional)
        """
        self.temp_base = temp_dir or os.path.join(tempfile.gettempdir(), 'repo_empathizer_temp')
        self._ensure_temp_dir()
    
    def _ensure_temp_dir(self):
        """Asegura que el directorio temporal existe"""
        os.makedirs(self.temp_base, exist_ok=True)
        logger.info(f"Directorio temporal: {self.temp_base}")
    
    def _clean_temp_dir(self, repo_path: str):
        """Limpia un directorio temporal específico"""
        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                logger.info(f"Limpiado: {repo_path}")
        except Exception as e:
            logger.error(f"Error limpiando {repo_path}: {str(e)}")
    
    def _clone_repo(self, repo_url: str, target_dir: str) -> bool:
        """
        Clona un repositorio usando git
        
        Returns:
            True si el clonado fue exitoso, False en caso contrario
        """
        try:
            # Construir URL completa si es necesario
            if not repo_url.startswith('http'):
                # Asume formato usuario/repo
                repo_url = f"https://github.com/{repo_url}.git"
            elif not repo_url.endswith('.git'):
                repo_url += '.git'
            
            print(f"\n📥 Clonando {repo_url}...")
            print(f"   Destino: {target_dir}")
            
            # Clonar con profundidad 1 y sin historial para ser más rápido
            cmd = ['git', 'clone', '--depth', '1', '--single-branch', '--progress', repo_url, target_dir]
            
            # Usar Popen para mostrar progreso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Timeout manual
            start_time = time.time()
            timeout = 120  # 2 minutos máximo
            
            while True:
                if time.time() - start_time > timeout:
                    process.terminate()
                    print(f"   ❌ Timeout: Clonado tardó más de {timeout} segundos")
                    return False
                
                line = process.stdout.readline()
                if not line:
                    break
                    
                # Mostrar progreso del git
                line = line.strip()
                if line and ('Receiving' in line or 'Resolving' in line or 'Counting' in line):
                    print(f"   {line}")
            
            process.wait()
            
            if process.returncode == 0:
                print("   ✅ Clonado exitosamente")
                return True
            else:
                print(f"   ❌ Error al clonar: código {process.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"Error clonando repositorio: {str(e)}")
            return False
    
    def _get_repo_metadata(self, repo_path: str, repo_name: str) -> Dict[str, Any]:
        """Obtiene metadata básica del repositorio local"""
        try:
            # Obtener tamaño del directorio
            total_size = 0
            file_count = 0
            for dirpath, dirnames, filenames in os.walk(repo_path):
                # Ignorar .git
                if '.git' in dirpath:
                    continue
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
                        file_count += 1
            
            # Detectar lenguaje principal por extensiones
            lang_counts = {}
            for dirpath, dirnames, filenames in os.walk(repo_path):
                if '.git' in dirpath:
                    continue
                for f in filenames:
                    ext = os.path.splitext(f)[1].lower()
                    if ext:
                        lang_counts[ext] = lang_counts.get(ext, 0) + 1
            
            # Mapear extensiones a lenguajes
            ext_to_lang = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.java': 'Java',
                '.cpp': 'C++',
                '.cs': 'C#',
                '.php': 'PHP',
                '.go': 'Go',
                '.rb': 'Ruby',
                '.swift': 'Swift',
                '.html': 'HTML',
                '.css': 'CSS'
            }
            
            lang_files = {}
            for ext, count in lang_counts.items():
                if ext in ext_to_lang:
                    lang = ext_to_lang[ext]
                    lang_files[lang] = lang_files.get(lang, 0) + count
            
            primary_lang = max(lang_files.items(), key=lambda x: x[1])[0] if lang_files else "Unknown"
            
            return {
                "nombre": repo_name.split('/')[-1],
                "url": f"https://github.com/{repo_name}",
                "descripcion": "Análisis local",
                "lenguaje_principal": primary_lang,
                "tamano_kb": float(total_size / 1024),
                "archivos_totales": file_count,
                "modo_analisis": "local"
            }
        except Exception as e:
            logger.error(f"Error obteniendo metadata: {str(e)}")
            return {
                "nombre": repo_name,
                "url": f"https://github.com/{repo_name}",
                "descripcion": "Error en metadata",
                "lenguaje_principal": "Unknown",
                "tamano_kb": 0.0
            }
    
    def analizar_repo_local(self, repo_name: str, max_files: int = 50) -> Dict[str, Any]:
        """
        Analiza un repositorio clonándolo localmente
        
        Args:
            repo_name: Nombre del repo (formato: usuario/repo)
            max_files: Número máximo de archivos a analizar
            
        Returns:
            Diccionario con métricas del análisis
        """
        # Crear directorio temporal único
        timestamp = str(int(time.time()))
        safe_name = repo_name.replace('/', '_')
        repo_dir = os.path.join(self.temp_base, f"{safe_name}_{timestamp}")
        
        try:
            # Clonar el repositorio
            if not self._clone_repo(repo_name, repo_dir):
                raise Exception("No se pudo clonar el repositorio")
            
            # Obtener metadata
            metadata = self._get_repo_metadata(repo_dir, repo_name)
            print(f"\n📊 Analizando {metadata['archivos_totales']} archivos localmente...")
            
            # Obtener archivos de código
            archivos_codigo = {}
            archivos_analizados = 0
            extensiones_soportadas = AnalyzerFactory.get_supported_extensions()
            
            # Primero, recopilar todos los archivos relevantes
            archivos_relevantes = []
            for root, dirs, files in os.walk(repo_dir):
                # Ignorar directorios especiales (más agresivo)
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    'node_modules', 'vendor', '__pycache__', 'dist', 'build', 
                    'coverage', '.git', 'venv', 'env', 'target', 'out',
                    'bower_components', 'packages', '.next', '.nuxt'
                ]]
                
                # Solo explorar los primeros niveles para ser más rápido
                depth = root[len(repo_dir):].count(os.sep)
                if depth > 3:  # Máximo 3 niveles de profundidad
                    dirs[:] = []  # No explorar más subdirectorios
                    continue
                
                for file in files:
                    # Verificar extensión primero (más eficiente)
                    if any(file.endswith(ext) for ext in extensiones_soportadas):
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            if size <= 500 * 1024:  # Máximo 500KB por archivo
                                archivos_relevantes.append((file_path, size))
                        except:
                            pass
            
            # Ordenar por tamaño (archivos más pequeños primero)
            archivos_relevantes.sort(key=lambda x: x[1])
            
            # Analizar solo los primeros max_files
            print(f"   📁 Encontrados {len(archivos_relevantes)} archivos relevantes")
            print(f"   🎯 Analizando los primeros {min(max_files, len(archivos_relevantes))} archivos...")
            
            for file_path, _ in archivos_relevantes[:max_files]:
                try:
                    rel_path = os.path.relpath(file_path, repo_dir)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        contenido = f.read()
                        archivos_codigo[rel_path] = contenido
                        archivos_analizados += 1
                        
                        if archivos_analizados % 25 == 0:
                            print(f"   📄 {archivos_analizados} archivos procesados...")
                            
                except Exception as e:
                    logger.warning(f"Error leyendo {rel_path}: {str(e)}")
            
            metadata['archivos_analizados'] = archivos_analizados
            print(f"   ✅ {archivos_analizados} archivos procesados")
            
            # Inicializar métricas
            metricas_totales = {
                'metadata': metadata,
                'nombres': {'descriptividad': 0.0},
                'documentacion': {'cobertura_docstrings': 0.0},
                'modularidad': {
                    'funciones_por_archivo': 0.0,
                    'clases_por_archivo': 0.0,
                    'cohesion_promedio': 0.0,
                    'acoplamiento_promedio': 0.0
                },
                'complejidad': {
                    'complejidad_ciclomatica': 0.0,
                    'max_nivel_anidacion': 0.0,
                    'longitud_promedio_funciones': 0.0
                },
                'manejo_errores': {
                    'cobertura_manejo_errores': 0.0,
                    'especificidad_excepciones': 0.0,
                    'densidad_try_except': 0.0
                },
                'pruebas': {
                    'cobertura_pruebas': 0.0,
                    'densidad_asserts': 0.0,
                    'funciones_test': 0.0
                },
                'seguridad': {
                    'validacion_entradas': 0.0,
                    'uso_funciones_peligrosas': 1.0,
                    'total_validaciones': 0.0
                },
                'consistencia_estilo': {
                    'consistencia_nombres': 0.0,
                    'espaciado_consistente': 0.0,
                    'longitud_lineas_consistente': 0.0
                }
            }
            
            # Analizar archivos
            if archivos_codigo:
                print("\n🔍 Calculando métricas...")
                analisis_multi = AnalyzerFactory.analyze_multi_language_project(archivos_codigo)
                
                # Extraer métricas del lenguaje principal
                if analisis_multi['primary_language']:
                    lenguaje_principal = analisis_multi['primary_language']
                    metricas_principales = analisis_multi['languages'][lenguaje_principal]['metrics']
                    
                    # Actualizar métricas totales
                    for categoria in metricas_totales:
                        if categoria != 'metadata' and categoria in metricas_principales:
                            metricas_totales[categoria] = metricas_principales[categoria]
                    
                    # Añadir lenguajes analizados
                    metricas_totales['metadata']['lenguajes_analizados'] = list(analisis_multi['languages'].keys())
                
                # Análisis avanzados
                from pattern_analyzer import PatternAnalyzer
                from performance_analyzer import PerformanceAnalyzer
                from comment_analyzer import CommentAnalyzer
                
                print("   🏗️  Analizando patrones de diseño...")
                pattern_analyzer = PatternAnalyzer()
                metricas_totales['patrones'] = pattern_analyzer.analyze_patterns(archivos_codigo)
                
                print("   ⚡ Analizando rendimiento...")
                perf_analyzer = PerformanceAnalyzer()
                metricas_totales['rendimiento'] = perf_analyzer.analyze_performance(archivos_codigo)
                
                print("   💬 Analizando comentarios...")
                comment_analyzer = CommentAnalyzer()
                metricas_totales['comentarios'] = comment_analyzer.analyze_comments(archivos_codigo)
            
            return metricas_totales
            
        except Exception as e:
            logger.error(f"Error en análisis local: {str(e)}")
            raise
        finally:
            # Siempre limpiar el directorio temporal
            print(f"\n🧹 Limpiando archivos temporales...")
            self._clean_temp_dir(repo_dir)
    
    def limpiar_todo(self):
        """Limpia todo el directorio temporal"""
        try:
            if os.path.exists(self.temp_base):
                shutil.rmtree(self.temp_base)
                print(f"✅ Directorio temporal limpiado: {self.temp_base}")
        except Exception as e:
            logger.error(f"Error limpiando directorio temporal: {str(e)}")