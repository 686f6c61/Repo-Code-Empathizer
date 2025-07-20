#!/usr/bin/env python3
"""
Script para probar el análisis local con los repositorios problemáticos
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
os.chdir(root_dir)

print("=== TEST DE ANÁLISIS LOCAL ===\n")

# Repos problemáticos
empresa_repo = "686f6c61/visor-markdown-openrouter-models"
candidato_repo = "Kiura-Team/La-Campana-Frontend"

print("📊 Repositorios a analizar:")
print(f"   Empresa: {empresa_repo} (59MB)")
print(f"   Candidato: {candidato_repo} (134MB)")
print("\n🚀 Usando análisis local (clonando repositorios)...")
print("   Nota: El clonado puede tardar dependiendo de tu conexión\n")

import subprocess

cmd = [
    'python', 'src/main.py',
    '--empresa', empresa_repo,
    '--candidato', candidato_repo,
    '--output', 'txt',
    '--local',  # Usar análisis local
    '--no-cache'
]

print(f"Ejecutando: {' '.join(cmd)}")
print("-" * 60)

start = time.time()

try:
    # Ejecutar con subprocess para ver output en tiempo real
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Mostrar output línea por línea
    for line in process.stdout:
        print(line, end='')
    
    # Esperar a que termine
    process.wait()
    
    elapsed = time.time() - start
    
    if process.returncode == 0:
        print(f"\n✅ Análisis completado exitosamente en {elapsed:.1f} segundos!")
    else:
        print(f"\n❌ Error: El proceso terminó con código {process.returncode}")
        
except KeyboardInterrupt:
    print("\n\n⚠️  Análisis interrumpido por el usuario")
    process.terminate()
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")

print("\n💡 Ventajas del análisis local:")
print("   - Más rápido para repositorios grandes")
print("   - No está limitado por la API de GitHub")
print("   - Puede analizar todos los archivos del repositorio")
print("   - Los archivos se eliminan automáticamente al terminar")