#!/usr/bin/env python3
"""
Script para analizar repositorios grandes con feedback de progreso
"""

import sys
import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(root_dir, 'src'))

import subprocess
import time

print("=== ANÁLISIS DE REPOSITORIOS GRANDES ===\n")

empresa_repo = "686f6c61/visor-markdown-openrouter-models"
candidato_repo = "Kiura-Team/La-Campana-Frontend"

print(f"📊 Información de los repositorios:")
print(f"   Empresa: {empresa_repo} (60MB)")
print(f"   Candidato: {candidato_repo} (137MB)")
print(f"\n⚠️  NOTA: Este análisis puede tardar varios minutos debido al tamaño de los repos\n")

print("🚀 Iniciando análisis con formato TXT (más rápido)...")
print("   Esto puede tardar 2-5 minutos...\n")

# Cambiar al directorio raíz
os.chdir(root_dir)

# Activar el entorno virtual y ejecutar
cmd = [
    'python', 'src/main.py',
    '--empresa', empresa_repo,
    '--candidato', candidato_repo,
    '--output', 'txt',
    '--no-cache'
]

print(f"Ejecutando: {' '.join(cmd)}")
print("-" * 60)

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
    
    if process.returncode == 0:
        print("\n✅ Análisis completado exitosamente!")
    else:
        print(f"\n❌ Error: El proceso terminó con código {process.returncode}")
        
except KeyboardInterrupt:
    print("\n\n⚠️  Análisis interrumpido por el usuario")
    process.terminate()
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")

print("\n💡 SUGERENCIAS:")
print("1. Si el análisis tarda demasiado, considera:")
print("   - Usar --languages para limitar los lenguajes a analizar")
print("   - Analizar repositorios más pequeños")
print("   - Aumentar el timeout en la configuración")
print("2. Los archivos de salida estarán en la carpeta 'export/'")