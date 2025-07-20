#!/usr/bin/env python3
"""Debug script para identificar el problema."""

import os
import sys
import time
from datetime import datetime

sys.path.insert(0, 'src')

def main():
    print("=== DEBUG ANALYSIS ===")
    
    # 1. Test GitHub connection
    print("\n1. Testing GitHub connection...")
    try:
        from github_utils import GitHubRepo
        gh = GitHubRepo()
        print("   ✅ GitHub client created")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Test small repo fetch
    print("\n2. Fetching small repository...")
    try:
        start = time.time()
        repo_name = "kennethreitz/setup.py"  # Repo muy pequeño
        print(f"   Fetching {repo_name}...")
        
        result = gh.analizar_repo(repo_name)
        
        elapsed = time.time() - start
        print(f"   ✅ Fetched in {elapsed:.2f}s")
        print(f"   Files analyzed: {result['metadata'].get('archivos_analizados', 0)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. Test analyzer
    print("\n3. Testing language analyzer...")
    try:
        from language_analyzers.factory import AnalyzerFactory
        
        # Create test file
        test_files = {
            'test.py': '''def hello():
    """Say hello."""
    print("Hello, World!")
    
if __name__ == "__main__":
    hello()
'''
        }
        
        start = time.time()
        analysis = AnalyzerFactory.analyze_multi_language_project(test_files)
        elapsed = time.time() - start
        
        print(f"   ✅ Analysis completed in {elapsed:.2f}s")
        print(f"   Languages found: {list(analysis['languages'].keys())}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    main()