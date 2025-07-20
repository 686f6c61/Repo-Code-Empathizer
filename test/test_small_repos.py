#!/usr/bin/env python3
"""
Script para probar con repositorios más pequeños
"""

import sys
import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(root_dir, 'src'))

os.chdir(root_dir)

print("=== TEST CON REPOSITORIOS PEQUEÑOS ===\n")

# Repos más pequeños para prueba
empresa_repo = "sindresorhus/awesome"  # ~2MB
candidato_repo = "kamranahmedse/developer-roadmap"  # ~5MB

print(f"📊 Probando con repositorios más pequeños:")
print(f"   Empresa: {empresa_repo}")
print(f"   Candidato: {candidato_repo}")
print(f"\n🚀 Iniciando análisis...\n")

import subprocess

cmd = [
    'python', 'src/main.py',
    '--empresa', empresa_repo,
    '--candidato', candidato_repo,
    '--output', 'txt',
    '--no-cache'
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        print("\n✅ Análisis completado exitosamente!")
        print("\nSalida:")
        print(result.stdout)
    else:
        print(f"\n❌ Error: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print("\n❌ Timeout después de 2 minutos")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")