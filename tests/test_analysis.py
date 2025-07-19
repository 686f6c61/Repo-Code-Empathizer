#!/usr/bin/env python3
"""
Script de prueba para analizar repositorios con múltiples lenguajes
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from github_utils import GitHubRepo
from language_analyzers.factory import AnalyzerFactory
from exporters import Exporter
from cache_manager import CacheManager

# Cargar variables de entorno
load_dotenv()


def test_language_detection():
    """Probar la detección de lenguajes"""
    print("\n🔍 Probando detección de lenguajes...")
    
    test_files = {
        'main.py': 'def hello(): pass',
        'app.js': 'function hello() {}',
        'server.go': 'package main',
        'index.php': '<?php echo "hello"; ?>',
        'app.rb': 'def hello; end',
        'main.swift': 'func hello() {}',
        'Program.cs': 'class Program {}',
        'main.cpp': 'int main() { return 0; }'
    }
    
    for filename, content in test_files.items():
        analyzer = AnalyzerFactory.get_analyzer_for_file(filename)
        if analyzer:
            print(f"✅ {filename} -> {analyzer.get_language_name()}")
        else:
            print(f"❌ {filename} -> No se detectó analizador")


def analyze_small_repo(repo_name: str):
    """Analizar un repositorio pequeño"""
    print(f"\n📊 Analizando repositorio: {repo_name}")
    
    try:
        github_repo = GitHubRepo()
        cache_manager = CacheManager(ttl_hours=1)
        
        # Analizar repositorio
        start_time = datetime.now()
        result = github_repo.analizar_repo(repo_name)
        end_time = datetime.now()
        
        if result:
            print(f"✅ Análisis completado en {(end_time - start_time).total_seconds():.2f} segundos")
            
            # Mostrar resumen
            metadata = result.get('metadata', {})
            print(f"\n📋 Información del repositorio:")
            print(f"  • Nombre: {metadata.get('nombre', 'N/A')}")
            print(f"  • Lenguaje principal: {metadata.get('lenguaje_principal', 'N/A')}")
            
            if 'lenguajes_analizados' in metadata:
                print(f"  • Lenguajes analizados: {', '.join(metadata['lenguajes_analizados'])}")
                print(f"  • Archivos analizados: {metadata.get('archivos_analizados', 0)}")
                print(f"  • Puntuación de empatía: {metadata.get('empathy_score_global', 0) * 100:.1f}%")
            
            # Mostrar métricas por categoría
            print(f"\n📊 Métricas principales:")
            for categoria in ['nombres', 'documentacion', 'complejidad', 'pruebas', 'seguridad']:
                if categoria in result:
                    valores = result[categoria]
                    if isinstance(valores, dict) and valores:
                        promedio = sum(v for v in valores.values() if isinstance(v, (int, float))) / len(valores)
                        print(f"  • {categoria.capitalize()}: {promedio * 100:.1f}%")
            
            # Guardar resultado detallado
            output_file = f"test_results_{repo_name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado guardado en: {output_file}")
            
            return result
        else:
            print(f"❌ Error al analizar el repositorio")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de Repo Code Empathizer")
    print("=" * 60)
    
    # Probar detección de lenguajes
    test_language_detection()
    
    # Lista de repositorios pequeños para probar (con diferentes lenguajes)
    test_repos = [
        "sindresorhus/is-plain-obj",  # JavaScript pequeño
        "kelseyhightower/envconfig",  # Go pequeño
        "psf/requests-html",          # Python pequeño
        "JakeWharton/butterknife",    # Java
        "rails/jbuilder",             # Ruby
        "ReactiveX/RxSwift",          # Swift
        "dotnet/format",              # C#
        "nlohmann/json",              # C++ (puede ser grande)
        "slim/slim",                  # PHP
        "microsoft/TypeScript-Node-Starter"  # TypeScript
    ]
    
    # Analizar solo los primeros 3 repos para la prueba
    results = {}
    for repo in test_repos[:3]:
        result = analyze_small_repo(repo)
        if result:
            results[repo] = result
    
    # Generar reporte comparativo si hay al menos 2 resultados
    if len(results) >= 2:
        print("\n📄 Generando reporte comparativo...")
        
        repo_keys = list(results.keys())
        comparison_data = {
            'repos': {
                'A': results[repo_keys[0]],
                'B': results[repo_keys[1]]
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Exportar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exporter = Exporter()
        
        try:
            exporter.exportar_html(comparison_data, timestamp, dashboard=True)
            print("✅ Dashboard HTML generado en: export/")
        except Exception as e:
            print(f"⚠️  Error generando dashboard: {e}")
        
        try:
            exporter.exportar_json(comparison_data, timestamp)
            print("✅ Reporte JSON generado en: export/")
        except Exception as e:
            print(f"⚠️  Error generando JSON: {e}")
    
    print("\n✨ Pruebas completadas")


if __name__ == "__main__":
    main()