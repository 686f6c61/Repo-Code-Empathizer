#!/usr/bin/env python3
"""
Test directo de git clone
"""

import subprocess
import tempfile
import os
import time
import shutil

print("=== TEST DE GIT CLONE ===\n")

# Crear directorio temporal
temp_dir = tempfile.mkdtemp(prefix="test_clone_")
print(f"📁 Directorio temporal: {temp_dir}")

repo_url = "https://github.com/expressjs/express.git"
print(f"📥 Clonando: {repo_url}")

start = time.time()

try:
    # Intentar clonar con salida en tiempo real
    cmd = ['git', 'clone', '--depth', '1', '--single-branch', repo_url, os.path.join(temp_dir, 'express')]
    print(f"   Comando: {' '.join(cmd)}")
    print("   Clonando...", flush=True)
    
    # Usar Popen para ver el progreso
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Leer salida línea por línea
    for line in process.stdout:
        print(f"   Git: {line.strip()}", flush=True)
    
    process.wait()
    elapsed = time.time() - start
    
    if process.returncode == 0:
        print(f"\n✅ Clonado exitosamente en {elapsed:.1f} segundos")
        
        # Ver tamaño
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(os.path.join(temp_dir, 'express')):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
                    file_count += 1
        
        print(f"   📊 Tamaño: {total_size/1024/1024:.1f} MB")
        print(f"   📄 Archivos: {file_count}")
    else:
        print(f"\n❌ Error al clonar: código {process.returncode}")
        
except Exception as e:
    print(f"\n❌ Excepción: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    # Limpiar
    print("\n🧹 Limpiando...")
    try:
        shutil.rmtree(temp_dir)
        print("   ✅ Limpiado")
    except:
        print("   ❌ Error al limpiar")