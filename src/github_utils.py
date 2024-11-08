from github import Github, GithubException
import os
from typing import Dict, Any, List
import tempfile
import logging
from pathlib import Path
import ast
import re
import pytz
import time
from datetime import datetime
from analyzers import CodeAnalyzer

logger = logging.getLogger(__name__)

class GitHubRepo:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("Token de GitHub no encontrado")
        self.github = Github(self.token)

    def analizar_repo(self, repo_name: str) -> Dict[str, Any]:
        """Analiza un repositorio y retorna sus métricas"""
        try:
            repo = self.github.get_repo(repo_name)
            
            # Obtener metadata básica
            metadata = {
                "nombre": repo.name,
                "url": repo.html_url,
                "descripcion": repo.description or "Sin descripción",
                "url_clone": repo.clone_url,
                "rama_default": repo.default_branch,
                "fecha_creacion": repo.created_at.isoformat(),
                "fecha_ultimo_push": repo.pushed_at.isoformat(),
                "lenguaje_principal": repo.language or "No especificado",
                "tamano_kb": float(repo.size)
            }
            
            # Obtener archivos Python
            archivos_python = []
            try:
                contents = repo.get_contents("")
                while contents:
                    file_content = contents.pop(0)
                    if file_content.type == "dir":
                        contents.extend(repo.get_contents(file_content.path))
                    elif file_content.path.endswith('.py'):
                        try:
                            contenido = repo.get_contents(file_content.path).decoded_content.decode('utf-8')
                            archivos_python.append({
                                'path': file_content.path,
                                'content': contenido
                            })
                        except Exception as e:
                            logger.warning(f"Error leyendo {file_content.path}: {str(e)}")
            except Exception as e:
                logger.error(f"Error obteniendo contenido del repo: {str(e)}")

            # Inicializar métricas con valores numéricos
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

            # Analizar cada archivo
            analyzer = CodeAnalyzer()
            for archivo in archivos_python:
                try:
                    tree = ast.parse(archivo['content'])
                    metricas_archivo = analyzer.analizar_archivo(archivo['content'])
                    
                    # Acumular métricas asegurando tipos numéricos
                    for categoria, valores in metricas_archivo.items():
                        if isinstance(valores, dict) and categoria in metricas_totales:
                            for metrica, valor in valores.items():
                                if metrica in metricas_totales[categoria]:
                                    # Convertir a float para asegurar operaciones numéricas
                                    metricas_totales[categoria][metrica] += float(valor)
                except Exception as e:
                    logger.warning(f"Error analizando {archivo['path']}: {str(e)}")

            # Promediar métricas
            num_archivos = len(archivos_python) or 1
            for categoria, valores in metricas_totales.items():
                if isinstance(valores, dict) and categoria != 'metadata':
                    for metrica in valores:
                        valores[metrica] = float(valores[metrica]) / num_archivos

            return metricas_totales

        except GithubException as e:
            if e.status == 403:
                logger.warning("Límite de rate alcanzado, esperando reset...")
                self.esperar_reset_rate_limit()
                return self.analizar_repo(repo_name)
            else:
                logger.error(f"Error de GitHub: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error analizando repo {repo_name}: {str(e)}")
            return None

    def esperar_reset_rate_limit(self):
        """Espera hasta que se resetee el límite de rate de GitHub"""
        rate_limit = self.github.get_rate_limit()
        reset_time = rate_limit.core.reset
        current_time = datetime.now(pytz.UTC)
        wait_time = (reset_time - current_time).total_seconds()
        
        if wait_time > 0:
            print(f"\n⏳ Esperando {wait_time/60:.1f} minutos hasta que se resetee el límite...")
            print(f"🕐 Hora estimada de reinicio: {reset_time.strftime('%H:%M:%S')}")
            
            while wait_time > 0:
                mins, secs = divmod(int(wait_time), 60)
                print(f"\r⌛ Tiempo restante: {mins:02d}:{secs:02d}", end='')
                time.sleep(1)
                wait_time -= 1
            
            print("\n✅ ¡Límite reseteado! Continuando con el análisis...")
            time.sleep(1)

    @staticmethod
    def extraer_usuario_repo(repo_input: str) -> str:
        """Extrae el formato usuario/repo de una URL de GitHub"""
        if '/' in repo_input and 'github.com' not in repo_input:
            return repo_input
        
        match = re.search(r'github\.com/([^/]+/[^/]+)/?$', repo_input)
        if match:
            return match.group(1)
        
        raise ValueError("Formato inválido. Use 'usuario/repo' o una URL de GitHub válida")

    def get_repo_info(self, url: str) -> Dict[str, Any]:
        """Obtiene información básica del repositorio"""
        try:
            # Extraer owner/repo de la URL
            parts = url.strip("/").split("/")
            repo_full_name = f"{parts[-2]}/{parts[-1]}"
            
            repo = self.github.get_repo(repo_full_name)
            
            return {
                "nombre": repo.name,
                "url": repo.html_url,
                "descripcion": repo.description,
                "url_clone": repo.clone_url,
                "rama_default": repo.default_branch,
                "fecha_creacion": repo.created_at.isoformat(),
                "fecha_ultimo_push": repo.pushed_at.isoformat(),
                "lenguaje_principal": repo.language,
                "tamano_kb": repo.size
            }
        except Exception as e:
            logger.error(f"Error obteniendo info del repo: {str(e)}")
            raise

    def get_python_files(self, repo_url: str) -> List[Dict[str, Any]]:
        """Obtiene todos los archivos Python del repositorio"""
        try:
            repo = self.github.get_repo(repo_url)
            contents = repo.get_contents("")
            python_files = []

            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                elif file_content.path.endswith(".py"):
                    python_files.append({
                        "path": file_content.path,
                        "content": file_content.decoded_content.decode()
                    })

            return python_files
        except Exception as e:
            logger.error(f"Error obteniendo archivos Python: {str(e)}")
            raise

    @staticmethod
    def get_repo_from_input(tipo: str) -> str:
        """Obtiene URL del repositorio desde input del usuario"""
        repos_disponibles = [
            "https://github.com/usuario1/repo1",
            "https://github.com/usuario2/repo2"
        ]
        
        print(f"\nREPOSITORIO {tipo.upper()}")
        print("-" * 20)
        for i, repo in enumerate(repos_disponibles, 1):
            print(f"{i}. {repo}")
            
        while True:
            try:
                opcion = int(input(f"\nSeleccione repositorio {tipo} (1-{len(repos_disponibles)}): "))
                if 1 <= opcion <= len(repos_disponibles):
                    return repos_disponibles[opcion - 1]
            except ValueError:
                print("Por favor, ingrese un número válido.")