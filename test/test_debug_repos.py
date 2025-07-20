#!/usr/bin/env python3
"""
Script para debuggear el problema con los repositorios específicos
"""

import sys
import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(root_dir, 'src'))

from github_utils import GitHubRepo
import time

print("=== TEST DE DEBUG PARA REPOSITORIOS ===\n")

# Repos problemáticos
empresa_repo = "686f6c61/visor-markdown-openrouter-models"
candidato_repo = "Kiura-Team/La-Campana-Frontend"

try:
    print(f"1. Iniciando GitHubRepo...")
    github = GitHubRepo()
    print("   ✓ GitHubRepo inicializado")
    
    print(f"\n2. Analizando repositorio empresa: {empresa_repo}")
    print("   Iniciando análisis...")
    start_time = time.time()
    
    # Intentar obtener solo metadata primero
    import requests
    headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'}
    
    print("   - Obteniendo metadata del repo...")
    response = requests.get(f"https://api.github.com/repos/{empresa_repo}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Repo encontrado: {data['name']}")
        print(f"   - Tamaño: {data['size']} KB")
        print(f"   - Lenguaje principal: {data['language']}")
    else:
        print(f"   ✗ Error al obtener repo: {response.status_code}")
        
    print("\n3. Analizando repositorio candidato: {candidato_repo}")
    response = requests.get(f"https://api.github.com/repos/{candidato_repo}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Repo encontrado: {data['name']}")
        print(f"   - Tamaño: {data['size']} KB")
        print(f"   - Lenguaje principal: {data['language']}")
    else:
        print(f"   ✗ Error al obtener repo: {response.status_code}")
        
    print("\n4. Intentando análisis completo del repo empresa...")
    print("   NOTA: Esto puede tardar si el repo es grande")
    
    # Intentar análisis con timeout
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Análisis tardó más de 30 segundos")
    
    # Solo en sistemas Unix
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
    
    try:
        metrics = github.analizar_repo(empresa_repo)
        elapsed = time.time() - start_time
        print(f"   ✓ Análisis completado en {elapsed:.2f} segundos")
        print(f"   - Archivos analizados: {metrics.get('metadata', {}).get('archivos_analizados', 0)}")
    except TimeoutError:
        print("   ✗ TIMEOUT: El análisis tardó más de 30 segundos")
    except Exception as e:
        print(f"   ✗ ERROR: {type(e).__name__}: {str(e)}")
    
except Exception as e:
    print(f"\n❌ Error general: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()