#!/usr/bin/env python3
"""
Debug del análisis local paso a paso
"""

import sys
import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

sys.path.insert(0, os.path.join(root_dir, 'src'))

print("=== DEBUG ANÁLISIS LOCAL ===\n")

# Paso 1: Importar
print("1. Importando módulos...")
try:
    from local_analyzer import LocalRepoAnalyzer
    print("   ✓ LocalRepoAnalyzer importado")
except Exception as e:
    print(f"   ✗ Error importando: {e}")
    sys.exit(1)

# Paso 2: Crear analizador
print("\n2. Creando analizador...")
try:
    analyzer = LocalRepoAnalyzer()
    print("   ✓ Analizador creado")
    print(f"   - Directorio temporal: {analyzer.temp_base}")
except Exception as e:
    print(f"   ✗ Error creando analizador: {e}")
    sys.exit(1)

# Paso 3: Clonar repositorio pequeño
print("\n3. Probando clonado...")
test_repo = "mrdoob/three.js"  # ~25MB
print(f"   Repositorio: {test_repo}")

import time
start = time.time()

try:
    # Llamar directamente al método de clonado
    import tempfile
    temp_dir = tempfile.mkdtemp()
    print(f"   Directorio temporal: {temp_dir}")
    
    success = analyzer._clone_repo(test_repo, temp_dir)
    elapsed = time.time() - start
    
    if success:
        print(f"   ✓ Clonado exitoso en {elapsed:.1f}s")
        
        # Ver contenido
        import os
        files = []
        for root, dirs, filenames in os.walk(temp_dir):
            files.extend(filenames)
        print(f"   - Archivos totales: {len(files)}")
    else:
        print(f"   ✗ Clonado falló después de {elapsed:.1f}s")
    
    # Limpiar
    import shutil
    shutil.rmtree(temp_dir)
    
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Debug completado")