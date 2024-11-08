import os
from datetime import datetime
import sys
from typing import Dict, Any, List
import logging
from dotenv import load_dotenv

from github_utils import GitHubRepo
from analyzers import CodeAnalyzer
from exporters import Exporter

logger = logging.getLogger(__name__)

def mostrar_menu() -> None:
    print("\n=== ANÁLISIS DE EMPATÍA DE CÓDIGO por @686f6c61 ===")
    print("🔍 https://github.com/686f6c61\n")
    
    print("\033[1;36mEste programa analiza y compara dos repositorios de GitHub")
    print("para evaluar su nivel de empatía en el código.\033[0m\n")
    
    print("\033[1;33mCATEGORÍAS A ANALIZAR:\033[0m")
    print("------------------------")
    print("1. 📝 Nombres descriptivos")
    print("2. 🔄 Complejidad ciclomática")
    print("3. 📦 Modularidad")
    print("4. 📚 Documentación")
    print("5. ⚠️ Manejo de errores")
    print("6. 🧪 Pruebas")
    print("7. 🎨 Consistencia de estilo")
    print("8. 🔒 Seguridad\n")
    
    print("\033[1;33mFORMATOS DE EXPORTACIÓN:\033[0m")
    print("------------------------")
    print("1. 📄 TXT (Reporte simple)")
    print("2. 📊 JSON (Datos crudos)")
    print("3. 📈 HTML (Reporte detallado)")
    print("4. ✨ Todos los formatos\n")

def cargar_repos_disponibles() -> List[str]:
    try:
        # Obtener la ruta absoluta del directorio raíz del proyecto
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        repo_file = os.path.join(root_dir, "REPO.txt")
        
        if not os.path.exists(repo_file):
            logger.error(f"Archivo REPO.txt no encontrado en: {repo_file}")
            return []
        
        with open(repo_file, 'r') as f:
            repos = [line.strip() for line in f if line.strip()]
            
        if not repos:
            logger.warning("REPO.txt está vacío")
            return []
            
        logger.info(f"Repositorios cargados: {len(repos)}")
        return repos
        
    except Exception as e:
        logger.error(f"Error cargando repos: {str(e)}")
        return []

def obtener_repo_input(mensaje: str, repos_disponibles: List[str], tipo_repo: str = "Master") -> str:
    try:
        while True:
            print(f"\n{mensaje}")
            print("1. Seleccionar de la lista")
            print("2. Ingresar URL manualmente")
            opcion = input("Seleccione una opción (1-2): ").strip()
            
            if opcion == "1":
                if not repos_disponibles:
                    print("\n❌ No hay repositorios disponibles en REPO.txt")
                    continue
                
                print(f"\n📂 REPOSITORIOS DISPONIBLES")
                print("-" * 20)
                for i, repo in enumerate(repos_disponibles, 1):
                    print(f"{i}. {repo}")
                
                while True:
                    try:
                        idx = int(input(f"\nSeleccione repositorio {tipo_repo} (1-{len(repos_disponibles)}): "))
                        if 1 <= idx <= len(repos_disponibles):
                            return repos_disponibles[idx-1]
                    except ValueError:
                        pass
                    print("❌ Opción inválida")
            
            elif opcion == "2":
                url = input("\nIngrese URL del repositorio: ").strip()
                if url:
                    return url
                print("❌ URL inválida")
            
            else:
                print("❌ Opción inválida")
                
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego! Proceso interrumpido por el usuario.")
        sys.exit(0)

def procesar_url_repo(url: str) -> str:
    """Procesa la URL del repositorio para obtener el formato usuario/repo"""
    try:
        return GitHubRepo.extraer_usuario_repo(url)
    except Exception as e:
        logger.error(f"Error procesando URL del repo: {str(e)}")
        raise

def comparar_repos(repo1: str, repo2: str) -> Dict[str, Any]:
    """Compara dos repositorios y retorna las métricas"""
    try:
        github_client = GitHubRepo()
        analyzer = CodeAnalyzer()
        
        print(f"\n🔍 Analizando {repo1}...")
        metricas_repo1 = github_client.analizar_repo(repo1)
        
        print(f"\n🔍 Analizando {repo2}...")
        metricas_repo2 = github_client.analizar_repo(repo2)
        
        return {
            "repos": {
                "master": metricas_repo1,
                "comparado": metricas_repo2
            },
            "diferencias": calcular_diferencias(metricas_repo1, metricas_repo2)
        }
    except Exception as e:
        logger.error(f"Error comparando repos: {str(e)}")
        raise

def calcular_diferencias(repo1: Dict[str, Any], repo2: Dict[str, Any]) -> Dict[str, float]:
    """Calcula las diferencias entre las métricas de dos repos"""
    try:
        diferencias = {}
        for categoria in repo1:
            if isinstance(repo1[categoria], dict) and categoria in repo2:
                diferencias[categoria] = {
                    metrica: round(repo1[categoria][metrica] - repo2[categoria][metrica], 3)
                    for metrica in repo1[categoria]
                    if metrica in repo2[categoria]
                }
        return diferencias
    except Exception as e:
        logger.error(f"Error calculando diferencias: {str(e)}")
        return {}

def main():
    try:
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        
        mostrar_menu()
        
        while True:
            print("Formato deseado (1-4): ", end="")
            formato = input().strip()
            if formato in ['1', '2', '3', '4']:
                break
            print("❌ Por favor, seleccione una opción válida (1-4)")
        
        repos_disponibles = cargar_repos_disponibles()
        
        print("\n📂 REPOSITORIO MASTER")
        print("-------------------")
        repo_master = procesar_url_repo(obtener_repo_input("Seleccione una opción (1-2): ", repos_disponibles, "Master"))
        
        print("\n📂 REPOSITORIO A COMPARAR")
        print("------------------------")
        repo_comparado = procesar_url_repo(obtener_repo_input("Seleccione una opción (1-2): ", repos_disponibles, "Comparación"))
        
        print("\n🔍 Analizando repositorios...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        metricas = comparar_repos(repo_master, repo_comparado)
        analyzer = CodeAnalyzer()
        puntuacion = analyzer.calcular_puntuacion_final(metricas["repos"]["master"])
        print(f"\n🏆 Puntuación de empatía del código: {puntuacion}")
        
        exporter = Exporter()
        
        if formato in ["1", "4"]:
            print("\n📝 Generando reporte TXT...")
            exporter.exportar_txt(metricas, timestamp)
            print(f"✅ Reporte TXT generado: export/reporte_{timestamp}.txt")
        
        if formato in ["2", "4"]:
            print("\n📊 Generando reporte JSON...")
            exporter.exportar_json(metricas, timestamp)
            print(f"✅ Reporte JSON generado: export/reporte_{timestamp}.json")
            
        if formato in ["3", "4"]:
            print("\n📈 Generando reporte HTML...")
            exporter.exportar_html(metricas, timestamp)
            print(f"✅ Reporte HTML generado: export/reporte_{timestamp}.html")
            
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego! Proceso interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        raise
    finally:
        print("\n🏁 Proceso finalizado")

if __name__ == "__main__":
    main()