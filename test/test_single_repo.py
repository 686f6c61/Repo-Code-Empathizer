#!/usr/bin/env python3
"""
Script para debuggear análisis de un solo repositorio
"""

import sys
import os
from dotenv import load_dotenv
import time

# Cargar .env desde la raíz del proyecto
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(root_dir, 'src'))

from github_utils import GitHubRepo

print("=== TEST DE UN SOLO REPOSITORIO ===\n")

repo_test = "torvalds/linux"  # Repo muy grande para test extremo

try:
    print("1. Iniciando GitHubRepo...")
    github = GitHubRepo()
    print("   ✓ GitHubRepo inicializado")
    
    print(f"\n2. Analizando repositorio: {repo_test}")
    print("   Este es un test extremo con un repo muy grande...")
    
    start = time.time()
    print("\n   Iniciando análisis...")
    
    # Analizar repo
    metrics = github.analizar_repo(repo_test)
    
    elapsed = time.time() - start
    print(f"\n✅ Análisis completado en {elapsed:.2f} segundos")
    print(f"   - Archivos analizados: {metrics['metadata'].get('archivos_analizados', 0)}")
    print(f"   - Tamaño del repo: {metrics['metadata']['tamano_kb']/1024:.1f} MB")
    
    if 'nota_limite' in metrics['metadata']:
        print(f"   - Nota: {metrics['metadata']['nota_limite']}")

except KeyboardInterrupt:
    print("\n\n⚠️  Análisis interrumpido por el usuario")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()