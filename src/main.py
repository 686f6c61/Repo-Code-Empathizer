#!/usr/bin/env python3
"""
Repo Code Empathizer v2.0 - Aplicación principal.

Herramienta CLI para medir la empatía entre el código de una empresa y
el de un candidato. Soporta múltiples lenguajes de programación y genera
reportes detallados para facilitar decisiones de contratación.

Features:
    - Análisis multi-lenguaje (Python, JS, Java, Go, etc.)
    - Cálculo de empatía con algoritmo avanzado
    - Exportación en múltiples formatos (TXT, JSON, HTML)
    - Sistema de caché para optimizar rendimiento
    - Procesamiento paralelo de archivos

Usage:
    python main.py --empresa "empresa/repo" --candidato "candidato/repo"
    python main.py --list-languages
    python main.py --help

Author: R. Benítez
Version: 2.0.0
License: MIT
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import List
from dotenv import load_dotenv
import yaml

from github_utils import GitHubRepo
from language_analyzers.factory import AnalyzerFactory
from exporters import Exporter
from parallel_analyzer import ParallelAnalyzer
from cache_manager import CacheManager, CachedAnalyzer
from empathy_algorithm import EmpathyAlgorithm

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Colores ANSI
COLORS = {
    'header': '\033[95m',
    'blue': '\033[94m',
    'cyan': '\033[96m',
    'green': '\033[92m',
    'success': '\033[92m',  # Alias for green
    'warning': '\033[93m',
    'fail': '\033[91m',
    'end': '\033[0m',
    'bold': '\033[1m',
    'underline': '\033[4m',
}


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Carga la configuración desde un archivo YAML.
    
    Args:
        config_path: Ruta al archivo de configuración.
    
    Returns:
        dict: Configuración cargada o dict vacío si hay error.
    """
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {}
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}


def print_banner() -> None:
    """
    Muestra el banner de bienvenida de la aplicación.
    
    Utiliza colores ANSI para una presentación visual atractiva.
    """
    banner = f"""
{COLORS['header']}╔═══════════════════════════════════════════════════════════════╗
║              🔍 REPO CODE EMPATHIZER v2.0 🔍                   ║
║     Mide la Empatía entre Código de Empresa y Candidato        ║
╚═══════════════════════════════════════════════════════════════╝{COLORS['end']}
    """
    print(banner)


def print_language_support() -> None:
    """
    Muestra la lista de lenguajes y extensiones soportadas.
    
    Útil para que los usuarios conozcan qué tipos de archivos
    pueden ser analizados por la herramienta.
    """
    languages = AnalyzerFactory.get_supported_languages()
    extensions = AnalyzerFactory.get_supported_extensions()
    
    print(f"\n{COLORS['cyan']}📋 Lenguajes Soportados:{COLORS['end']}")
    for lang in languages:
        print(f"   • {lang.capitalize()}")
    
    print(f"\n{COLORS['cyan']}📄 Extensiones Soportadas:{COLORS['end']}")
    print(f"   {', '.join(extensions)}")


def get_output_format() -> str:
    """
    Solicita al usuario que seleccione el formato de salida.
    
    Returns:
        str: Formato seleccionado ('txt', 'json', 'html', 'dashboard', 'all').
    """
    print(f"\n{COLORS['blue']}📄 FORMATO DE SALIDA{COLORS['end']}")
    print("─" * 40)
    print("Seleccione el formato de exportación:")
    print("  1. TXT - Reporte en texto plano")
    print("  2. JSON - Datos estructurados para APIs")
    print("  3. HTML - Reporte visual básico")
    print("  4. Dashboard - Reporte interactivo completo")
    print("  5. Todos - Generar todos los formatos")
    
    formatos = {
        '1': 'txt',
        '2': 'json', 
        '3': 'html',
        '4': 'dashboard',
        '5': 'all'
    }
    
    while True:
        try:
            opcion = input(f"\nOpción [1-5]: ").strip()
            
            if opcion in formatos:
                formato_seleccionado = formatos[opcion]
                nombre_formato = {
                    'txt': 'Texto plano',
                    'json': 'JSON',
                    'html': 'HTML',
                    'dashboard': 'Dashboard interactivo',
                    'all': 'Todos los formatos'
                }[formato_seleccionado]
                
                print(f"{COLORS['green']}✅ Seleccionado: {nombre_formato}{COLORS['end']}")
                return formato_seleccionado
            else:
                print(f"{COLORS['warning']}⚠️  Por favor seleccione una opción válida (1-5){COLORS['end']}")
                
        except KeyboardInterrupt:
            print(f"\n{COLORS['warning']}⚠️  Operación cancelada{COLORS['end']}")
            exit(0)
        except Exception:
            print(f"{COLORS['warning']}⚠️  Por favor ingrese un número válido{COLORS['end']}")


def get_repo_input(tipo: str, repos_disponibles: list, repo_previo: str = None) -> str:
    """
    Solicita al usuario que seleccione o ingrese un repositorio.
    
    Args:
        tipo: Tipo de repositorio ('empresa' o 'candidato').
        repos_disponibles: Lista de repositorios precargados.
        repo_previo: Repositorio seleccionado previamente para validación.
    
    Returns:
        str: Repositorio seleccionado en formato 'usuario/repo'.
    
    Raises:
        ValueError: Si el formato del repositorio es inválido.
    """
    label = "EMPRESA (Master)" if tipo == "empresa" else "CANDIDATO"
    print(f"\n{COLORS['blue']}📂 REPOSITORIO {label}{COLORS['end']}")
    print("─" * 40)
    
    # Mostrar mensaje si hay repositorios en REPO.txt
    if repos_disponibles:
        print("Opciones:")
        for i, repo in enumerate(repos_disponibles, 1):
            print(f"  {i}. {repo}")
        print(f"  {len(repos_disponibles) + 1}. Ingresar URL o usuario/repo manualmente")
    else:
        print("No hay repositorios predefinidos en REPO.txt")
    
    while True:
        try:
            if repos_disponibles:
                opcion = input(f"\nSeleccione opción (1-{len(repos_disponibles) + 1}): ")
                opcion_num = int(opcion)
                
                if 1 <= opcion_num <= len(repos_disponibles):
                    repo_seleccionado = repos_disponibles[opcion_num - 1]
                elif opcion_num == len(repos_disponibles) + 1:
                    repo_input = input("Ingrese URL de GitHub o formato 'usuario/repo': ")
                    repo_seleccionado = GitHubRepo.extraer_usuario_repo(repo_input)
                else:
                    print(f"{COLORS['warning']}⚠️  Opción inválida{COLORS['end']}")
                    continue
            else:
                repo_input = input("Ingrese URL de GitHub o formato 'usuario/repo': ")
                repo_seleccionado = GitHubRepo.extraer_usuario_repo(repo_input)
            
            # Validar que no sea el mismo repositorio
            if repo_previo and repo_seleccionado == repo_previo:
                print(f"{COLORS['fail']}❌ Error: El repositorio del candidato no puede ser el mismo que el de la empresa{COLORS['end']}")
                print(f"{COLORS['warning']}Por favor, seleccione un repositorio diferente{COLORS['end']}")
                continue
                
            return repo_seleccionado
            
        except ValueError:
            print(f"{COLORS['warning']}⚠️  Por favor ingrese un número válido{COLORS['end']}")
        except Exception as e:
            print(f"{COLORS['fail']}❌ Error: {str(e)}{COLORS['end']}")


def analyze_team_mode(github_repo: GitHubRepo, repo_empresa: str, candidatos: List[str], 
                     cache_manager: CacheManager, args) -> None:
    """
    Ejecuta análisis en modo equipo para múltiples candidatos.
    
    Args:
        github_repo: Cliente GitHub configurado
        repo_empresa: Repositorio de la empresa
        candidatos: Lista de repositorios de candidatos
        cache_manager: Gestor de caché
        args: Argumentos de línea de comandos
    """
    print(f"\n{COLORS['bold']}🏢 MODO EQUIPO: Analizando {len(candidatos)} candidatos{COLORS['end']}")
    print(f"{COLORS['cyan']}📊 Empresa: {repo_empresa}{COLORS['end']}")
    
    # Analizar empresa una sola vez
    print(f"\n{COLORS['cyan']}🔍 Analizando repositorio de la empresa...{COLORS['end']}")
    analisis_empresa = analyze_repository(github_repo, repo_empresa, cache_manager, args.parallel, use_local=args.local)
    
    if not analisis_empresa:
        print(f"{COLORS['fail']}❌ Error analizando repositorio de empresa{COLORS['end']}")
        return
    
    # Resultados del equipo
    resultados_equipo = {
        'empresa': analisis_empresa,
        'candidatos': {},
        'timestamp': datetime.now().isoformat(),
        'modo': 'equipo'
    }
    
    # Analizar cada candidato
    for i, candidato in enumerate(candidatos, 1):
        print(f"\n{COLORS['cyan']}👤 Analizando candidato {i}/{len(candidatos)}: {candidato}{COLORS['end']}")
        
        try:
            candidato_repo = GitHubRepo.extraer_usuario_repo(candidato)
            
            # Verificar que no sea el mismo que la empresa
            if candidato_repo == repo_empresa:
                print(f"{COLORS['warning']}⚠️  Saltando: El candidato no puede ser el mismo que la empresa{COLORS['end']}")
                continue
            
            # Analizar candidato
            analisis_candidato = analyze_repository(github_repo, candidato_repo, cache_manager, args.parallel, use_local=args.local)
            
            if analisis_candidato:
                # Calcular empatía para este candidato
                resultado_individual = {
                    'repos': {
                        'empresa': analisis_empresa,
                        'candidato': analisis_candidato
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                # Calcular puntuación de empatía
                algorithm = EmpathyAlgorithm()
                empathy_result = algorithm.calculate_empathy_score(
                    resultado_individual['repos']['empresa'],
                    resultado_individual['repos']['candidato']
                )
                
                # Guardar resultado
                resultados_equipo['candidatos'][candidato_repo] = {
                    'analisis': analisis_candidato,
                    'empathy_score': empathy_result['empathy_score'],
                    'empathy_analysis': empathy_result
                }
                
                print(f"{COLORS['success']}✅ {candidato_repo}: Puntuación de empatía = {empathy_result['empathy_score']:.1f}%{COLORS['end']}")
            else:
                print(f"{COLORS['fail']}❌ Error analizando candidato: {candidato}{COLORS['end']}")
                
        except Exception as e:
            print(f"{COLORS['fail']}❌ Error con candidato {candidato}: {str(e)}{COLORS['end']}")
    
    # Generar resumen del equipo
    if resultados_equipo['candidatos']:
        print(f"\n{COLORS['bold']}📊 RESUMEN DEL EQUIPO{COLORS['end']}")
        print("=" * 60)
        
        # Ordenar candidatos por puntuación
        candidatos_ordenados = sorted(
            resultados_equipo['candidatos'].items(),
            key=lambda x: x[1]['empathy_score'],
            reverse=True
        )
        
        print(f"\n{COLORS['cyan']}🏆 Ranking de Candidatos:{COLORS['end']}")
        for i, (nombre, datos) in enumerate(candidatos_ordenados, 1):
            score = datos['empathy_score']
            nivel = datos['empathy_analysis']['interpretation']['level']
            print(f"  {i}. {nombre}: {score:.1f}% - {nivel}")
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exporter = Exporter()
        
        # Generar reporte especial de equipo
        exporter.exportar_equipo(resultados_equipo, timestamp)
        
        print(f"\n{COLORS['success']}✨ Análisis de equipo completado{COLORS['end']}")
        print(f"Reporte generado: export/equipo_{timestamp}.html")
    else:
        print(f"{COLORS['fail']}❌ No se pudo analizar ningún candidato{COLORS['end']}")


def analyze_repository(github_repo: GitHubRepo, repo_name: str, cache_manager: CacheManager = None, 
                      use_parallel: bool = True, force_analysis: bool = False, use_local: bool = False) -> dict:
    """
    Analiza un repositorio de GitHub y extrae sus métricas.
    
    Implementa caché para evitar análisis repetidos y soporta
    procesamiento paralelo para repositorios grandes.
    
    Args:
        github_repo: Cliente de GitHub para acceder al repositorio.
        repo_name: Nombre del repositorio en formato 'usuario/repo'.
        cache_manager: Gestor de caché (opcional).
        use_parallel: Si usar procesamiento paralelo.
        force_analysis: Forzar análisis ignorando caché.
        use_local: Si clonar y analizar localmente.
    
    Returns:
        dict: Métricas del repositorio o None si hay error.
    """
    
    # Verificar caché si está disponible
    if cache_manager and not force_analysis:
        cached_result = cache_manager.get(repo_name)
        if cached_result:
            print(f"{COLORS['green']}✅ Usando resultados en caché para {repo_name}{COLORS['end']}")
            return cached_result
    
    print(f"\n{COLORS['cyan']}🔍 Analizando {repo_name}...{COLORS['end']}")
    
    try:
        # Usar análisis local si está habilitado
        if use_local:
            from local_analyzer import LocalRepoAnalyzer
            print(f"{COLORS['cyan']}📥 Usando análisis local (clonando repositorio)...{COLORS['end']}")
            local_analyzer = LocalRepoAnalyzer()
            result = local_analyzer.analizar_repo_local(repo_name)
        else:
            # Usar el método de análisis remoto via API de GitHub
            result = github_repo.analizar_repo(repo_name)
        
        # Guardar en caché si está disponible
        if cache_manager and result:
            cache_manager.set(repo_name, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analizando {repo_name}: {e}")
        return None


def main() -> None:
    """
    Función principal de la aplicación CLI.
    
    Gestiona los argumentos de línea de comandos, orquesta el análisis
    de repositorios, calcula la empatía y genera los reportes.
    
    Exit codes:
        0: Ejecución exitosa
        1: Error en parámetros o análisis
        2: Error de configuración o token
    """
    parser = argparse.ArgumentParser(description='Repo Code Empathizer - Mide la empatía entre código de empresa y candidato')
    parser.add_argument('--empresa', type=str, help='Repositorio de la empresa (formato: usuario/repo)')
    parser.add_argument('--candidato', type=str, help='Repositorio del candidato (formato: usuario/repo)')
    parser.add_argument('--candidatos', nargs='+', help='Múltiples repositorios de candidatos (modo equipo)')
    parser.add_argument('--config', type=str, default='config.yaml', help='Archivo de configuración')
    parser.add_argument('--output', type=str, default=None, 
                       choices=['txt', 'json', 'html', 'dashboard', 'all'],
                       help='Formato de salida (si no se especifica, se preguntará interactivamente)')
    parser.add_argument('--no-cache', action='store_true', help='Desactivar caché')
    parser.add_argument('--clear-cache', action='store_true', help='Limpiar caché antes de ejecutar')
    parser.add_argument('--parallel', action='store_true', default=True, help='Usar procesamiento paralelo')
    parser.add_argument('--local', action='store_true', help='Clonar y analizar repositorios localmente (recomendado para repos grandes)')
    parser.add_argument('--languages', nargs='+', help='Lenguajes específicos a analizar')
    parser.add_argument('--list-languages', action='store_true', help='Listar lenguajes soportados')
    parser.add_argument('--team-mode', action='store_true', help='Activar modo equipo para análisis comparativo')
    
    args = parser.parse_args()
    
    # Mostrar lenguajes soportados si se solicita
    if args.list_languages:
        print_language_support()
        return
    
    # Cargar configuración
    config = load_config(args.config)
    
    # Mostrar banner
    print_banner()
    
    # Mostrar lenguajes soportados
    print_language_support()
    
    try:
        # Inicializar GitHub
        github_repo = GitHubRepo()
        
        # Inicializar caché si no está desactivado
        cache_manager = None
        if not args.no_cache:
            cache_manager = CacheManager()
            if args.clear_cache:
                cache_manager.clear_all()
                print(f"{COLORS['green']}✅ Caché limpiado{COLORS['end']}")
        
        # Cargar repositorios disponibles desde REPO.txt
        repos_disponibles = []
        if os.path.exists("REPO.txt"):
            with open("REPO.txt", "r") as f:
                repos_disponibles = [line.strip() for line in f if line.strip()]
        
        # Verificar modo equipo
        if args.team_mode or args.candidatos:
            # Modo equipo
            if args.empresa:
                repo_empresa = GitHubRepo.extraer_usuario_repo(args.empresa)
            else:
                repo_empresa = get_repo_input("empresa", repos_disponibles)
            
            # Obtener lista de candidatos
            if args.candidatos:
                candidatos = args.candidatos
            else:
                print(f"\n{COLORS['cyan']}📋 Ingrese los repositorios de los candidatos (uno por línea).{COLORS['end']}")
                print(f"{COLORS['cyan']}   Presione Enter sin escribir nada para finalizar:{COLORS['end']}")
                candidatos = []
                while True:
                    candidato = input(f"Candidato {len(candidatos) + 1}: ").strip()
                    if not candidato:
                        break
                    candidatos.append(candidato)
                
                if not candidatos:
                    print(f"{COLORS['fail']}❌ Debe ingresar al menos un candidato{COLORS['end']}")
                    return
            
            # Ejecutar análisis en modo equipo
            analyze_team_mode(github_repo, repo_empresa, candidatos, cache_manager, args)
            return
        
        # Modo normal (un solo candidato)
        if args.empresa:
            repo_empresa = GitHubRepo.extraer_usuario_repo(args.empresa)
        else:
            repo_empresa = get_repo_input("empresa", repos_disponibles)
        
        if args.candidato:
            repo_candidato = GitHubRepo.extraer_usuario_repo(args.candidato)
            # Validar que no sea el mismo
            if repo_candidato == repo_empresa:
                print(f"{COLORS['fail']}❌ Error: El repositorio del candidato no puede ser el mismo que el de la empresa{COLORS['end']}")
                return
        else:
            repo_candidato = get_repo_input("candidato", repos_disponibles, repo_empresa)
        
        # Seleccionar formato de salida si no se especificó
        if args.output is None:
            output_format = get_output_format()
        else:
            output_format = args.output
        
        # Analizar repositorios
        print(f"\n{COLORS['bold']}🚀 Iniciando análisis de empatía empresa-candidato...{COLORS['end']}")
        
        resultados = {
            'repos': {
                'empresa': analyze_repository(github_repo, repo_empresa, cache_manager, args.parallel, use_local=args.local),
                'candidato': analyze_repository(github_repo, repo_candidato, cache_manager, args.parallel, use_local=args.local)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar que ambos análisis fueron exitosos
        if not resultados['repos']['empresa'] or not resultados['repos']['candidato']:
            print(f"{COLORS['fail']}❌ Error en el análisis de uno o ambos repositorios{COLORS['end']}")
            return
        
        # Calcular empatía usando el algoritmo complejo
        print(f"\n{COLORS['cyan']}🧮 Calculando puntuación de empatía...{COLORS['end']}")
        empathy_algo = EmpathyAlgorithm()
        resultados['empathy_analysis'] = empathy_algo.calculate_empathy_score(
            resultados['repos']['empresa'],
            resultados['repos']['candidato']
        )
        
        # Mostrar resultado principal
        score = resultados['empathy_analysis']['empathy_score']
        interpretation = resultados['empathy_analysis']['interpretation']
        print(f"\n{COLORS['bold']}📊 PUNTUACIÓN DE EMPATÍA: {interpretation['color']}{score}%{COLORS['end']}")
        print(f"   {interpretation['level']}: {interpretation['description']}")
        print(f"   {interpretation['recommendation']}")
        
        # Exportar resultados
        print(f"\n{COLORS['cyan']}📄 Generando reportes...{COLORS['end']}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exporter = Exporter()
        
        if output_format in ['txt', 'all']:
            exporter.exportar_txt(resultados, timestamp)
            print(f"{COLORS['green']}✅ Reporte TXT generado{COLORS['end']}")
        
        if output_format in ['json', 'all']:
            exporter.exportar_json(resultados, timestamp)
            print(f"{COLORS['green']}✅ Reporte JSON generado{COLORS['end']}")
        
        if output_format in ['html', 'all']:
            exporter.exportar_html(resultados, timestamp)
            print(f"{COLORS['green']}✅ Reporte HTML generado{COLORS['end']}")
        
        if output_format in ['dashboard', 'all']:
            exporter.exportar_html(resultados, timestamp, dashboard=True)
            print(f"{COLORS['green']}✅ Dashboard interactivo generado{COLORS['end']}")
        
        # Mostrar resumen
        mostrar_resumen(resultados)
        
        # Mostrar información de caché si está activo
        if cache_manager:
            cache_info = cache_manager.get_cache_info()
            print(f"\n{COLORS['cyan']}💾 Información de caché:{COLORS['end']}")
            print(f"   • Entradas: {cache_info['total_entries']}")
            print(f"   • Tamaño: {cache_info['total_size_mb']} MB")
        
        print(f"\n{COLORS['green']}✨ ¡Análisis completado exitosamente!{COLORS['end']}")
        print(f"Los reportes se encuentran en la carpeta 'export/'")
        
    except KeyboardInterrupt:
        print(f"\n{COLORS['warning']}⚠️  Análisis cancelado por el usuario{COLORS['end']}")
    except Exception as e:
        print(f"\n{COLORS['fail']}❌ Error: {str(e)}{COLORS['end']}")
        logger.exception("Error en la ejecución principal")




def mostrar_resumen(resultados: dict) -> None:
    """
    Muestra un resumen detallado de los resultados en la consola.
    
    Incluye información de los repositorios, puntuación de empatía,
    puntuaciones por categoría y recomendaciones principales.
    
    Args:
        resultados: Diccionario con los resultados del análisis.
    """
    print(f"\n{COLORS['bold']}📊 RESUMEN DEL ANÁLISIS DE EMPATÍA{COLORS['end']}")
    print("═" * 60)
    
    # Mostrar información de repositorios
    for repo_tipo, repo_data in resultados['repos'].items():
        if not repo_data or 'metadata' not in repo_data:
            continue
            
        metadata = repo_data['metadata']
        label = "EMPRESA" if repo_tipo == "empresa" else "CANDIDATO"
        print(f"\n{COLORS['cyan']}{label}:{COLORS['end']} {metadata.get('nombre', 'N/A')}")
        print(f"  • Lenguaje principal: {metadata.get('lenguaje_principal', 'N/A')}")
        
        if 'lenguajes_analizados' in metadata:
            print(f"  • Lenguajes analizados: {', '.join(metadata['lenguajes_analizados'])}")
        print(f"  • Archivos analizados: {metadata.get('archivos_analizados', 0)}")
    
    # Mostrar análisis de empatía si existe
    if 'empathy_analysis' in resultados:
        analysis = resultados['empathy_analysis']
        print(f"\n{COLORS['bold']}🎯 ANÁLISIS DE EMPATÍA{COLORS['end']}")
        print("─" * 40)
        
        # Puntuaciones por categoría
        print(f"\n{COLORS['cyan']}📈 Puntuaciones por Categoría:{COLORS['end']}")
        for categoria, score in analysis['category_scores'].items():
            color = COLORS['green'] if score >= 80 else COLORS['warning'] if score >= 60 else COLORS['fail']
            print(f"  • {categoria.replace('_', ' ').title()}: {color}{score:.1f}%{COLORS['end']}")
        
        # Coincidencia de lenguajes
        lang_overlap = analysis['language_overlap']
        print(f"\n{COLORS['cyan']}🔤 Coincidencia de Lenguajes:{COLORS['end']} {lang_overlap['score']:.1f}%")
        if lang_overlap['missing']:
            print(f"  ⚠️  Lenguajes faltantes: {', '.join(lang_overlap['missing'])}")
        
        # Recomendaciones principales
        if analysis['recommendations']:
            print(f"\n{COLORS['cyan']}💡 Recomendaciones Principales:{COLORS['end']}")
            for i, rec in enumerate(analysis['recommendations'][:3]):
                print(f"  {i+1}. {rec['title']}: {rec['description']}")


if __name__ == "__main__":
    main()