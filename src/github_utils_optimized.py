"""
Versión optimizada de github_utils para repositorios grandes
"""

from github import Github, GithubException
import os
from typing import Dict, Any, List
import logging
from language_analyzers.factory import AnalyzerFactory

logger = logging.getLogger(__name__)

class GitHubRepoOptimized:
    """Cliente optimizado para repositorios grandes"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("Token de GitHub no encontrado")
        self.github = Github(self.token)
    
    def analizar_repo_rapido(self, repo_name: str) -> Dict[str, Any]:
        """Análisis rápido limitando búsqueda a archivos en raíz y primeros subdirectorios"""
        try:
            repo = self.github.get_repo(repo_name)
            
            # Metadata
            metadata = {
                "nombre": repo.name,
                "url": repo.html_url,
                "descripcion": repo.description or "Sin descripción",
                "lenguaje_principal": repo.language or "No especificado",
                "tamano_kb": float(repo.size)
            }
            
            # Límites estrictos
            MAX_FILES = 30 if repo.size > 50000 else 50
            MAX_DEPTH = 2  # Solo explorar 2 niveles de profundidad
            
            print(f"\n🚀 Análisis rápido: máximo {MAX_FILES} archivos, profundidad {MAX_DEPTH}")
            
            archivos_codigo = {}
            archivos_analizados = 0
            extensiones = AnalyzerFactory.get_supported_extensions()
            
            # Solo obtener contenido de la raíz primero
            try:
                contents = repo.get_contents("")
                dirs_to_explore = []
                
                # Primera pasada: archivos en raíz
                for item in contents:
                    if archivos_analizados >= MAX_FILES:
                        break
                        
                    if item.type == "file":
                        for ext in extensiones:
                            if item.path.endswith(ext) and item.size < 500000:  # Max 500KB
                                try:
                                    contenido = item.decoded_content.decode('utf-8')
                                    archivos_codigo[item.path] = contenido
                                    archivos_analizados += 1
                                    if archivos_analizados % 5 == 0:
                                        print(f"   📄 {archivos_analizados} archivos...")
                                    break
                                except:
                                    pass
                    elif item.type == "dir" and len(dirs_to_explore) < 5:
                        # Solo explorar los primeros 5 directorios
                        dirs_to_explore.append(item.path)
                
                # Segunda pasada: primer nivel de subdirectorios
                for dir_path in dirs_to_explore[:3]:  # Solo los primeros 3 directorios
                    if archivos_analizados >= MAX_FILES:
                        break
                    
                    try:
                        dir_contents = repo.get_contents(dir_path)
                        for item in dir_contents[:10]:  # Máximo 10 archivos por directorio
                            if archivos_analizados >= MAX_FILES:
                                break
                                
                            if item.type == "file":
                                for ext in extensiones:
                                    if item.path.endswith(ext) and item.size < 500000:
                                        try:
                                            contenido = item.decoded_content.decode('utf-8')
                                            archivos_codigo[item.path] = contenido
                                            archivos_analizados += 1
                                            if archivos_analizados % 5 == 0:
                                                print(f"   📄 {archivos_analizados} archivos...")
                                            break
                                        except:
                                            pass
                    except:
                        continue
                        
            except Exception as e:
                logger.error(f"Error en análisis rápido: {str(e)}")
            
            metadata['archivos_analizados'] = archivos_analizados
            metadata['modo_analisis'] = 'rápido'
            
            # Análisis simplificado
            print(f"\n📊 Analizando {archivos_analizados} archivos...")
            
            if archivos_codigo:
                from github_utils import GitHubRepo
                github_std = GitHubRepo()
                # Usar el método estándar para procesar los archivos ya obtenidos
                return github_std._procesar_archivos_codigo(archivos_codigo, metadata)
            else:
                # Retornar estructura vacía
                return github_std._crear_metricas_vacias(metadata)
                
        except Exception as e:
            logger.error(f"Error en análisis rápido: {str(e)}")
            raise