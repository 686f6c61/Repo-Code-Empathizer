#!/usr/bin/env python3
"""
Prueba simple del análisis local
"""

import sys
import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(root_dir, 'src'))

from local_analyzer import LocalRepoAnalyzer
import time

print("=== PRUEBA SIMPLE DE ANÁLISIS LOCAL ===\n")

# Repositorio más pequeño para prueba
test_repo = "expressjs/express"  # Framework Express.js (~11MB)

print(f"📊 Probando con repositorio pequeño: {test_repo}")
print("   Este es un repositorio de ~2MB para verificar que funciona\n")

try:
    analyzer = LocalRepoAnalyzer()
    
    start = time.time()
    print("🚀 Iniciando análisis local...")
    
    result = analyzer.analizar_repo_local(test_repo, max_files=50)
    
    elapsed = time.time() - start
    
    print(f"\n✅ Análisis completado en {elapsed:.1f} segundos")
    print(f"   - Archivos analizados: {result['metadata']['archivos_analizados']}")
    print(f"   - Lenguaje principal: {result['metadata']['lenguaje_principal']}")
    print(f"   - Tamaño: {result['metadata']['tamano_kb']/1024:.1f} MB")
    
    # Limpiar todo
    analyzer.limpiar_todo()
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()