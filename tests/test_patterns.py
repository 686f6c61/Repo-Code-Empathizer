#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del pattern analyzer
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pattern_analyzer import PatternAnalyzer

# Código de prueba con patrones conocidos
test_code_python = '''
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        pass

class UserFactory:
    def create_user(self, user_type):
        if user_type == "admin":
            return AdminUser()
        elif user_type == "regular":
            return RegularUser()
        return None

class Observable:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)

@property
def name(self):
    return self._name

@staticmethod
def validate_email(email):
    return "@" in email
'''

test_code_javascript = '''
class AppInstance {
    static instance = null;
    
    static getInstance() {
        if (!this.instance) {
            this.instance = new AppInstance();
        }
        return this.instance;
    }
}

class ProductFactory {
    createProduct(type) {
        switch(type) {
            case 'A':
                return new ProductA();
            case 'B':
                return new ProductB();
        }
    }
}

// Observer pattern
eventEmitter.on('data', function(data) {
    console.log(data);
});

eventEmitter.emit('data', {value: 123});
'''

def test_pattern_detection():
    analyzer = PatternAnalyzer()
    
    print("="*60)
    print("PRUEBA DE DETECCIÓN DE PATRONES")
    print("="*60)
    
    # Test con código Python
    print("\n1. Analizando código Python:")
    print("-" * 40)
    
    files_python = {
        'test.py': test_code_python
    }
    
    results_python = analyzer.analyze_patterns(files_python)
    
    print(f"Patrones de diseño encontrados: {dict(results_python['design_patterns'])}")
    print(f"Anti-patrones encontrados: {dict(results_python['anti_patterns'])}")
    print(f"Score de patrones: {results_python['pattern_score']}")
    print(f"Resumen: {results_python['summary']}")
    
    # Test con código JavaScript
    print("\n2. Analizando código JavaScript:")
    print("-" * 40)
    
    files_js = {
        'test.js': test_code_javascript
    }
    
    results_js = analyzer.analyze_patterns(files_js)
    
    print(f"Patrones de diseño encontrados: {dict(results_js['design_patterns'])}")
    print(f"Anti-patrones encontrados: {dict(results_js['anti_patterns'])}")
    print(f"Score de patrones: {results_js['pattern_score']}")
    print(f"Resumen: {results_js['summary']}")
    
    # Test con archivo vacío
    print("\n3. Analizando archivo vacío:")
    print("-" * 40)
    
    files_empty = {
        'empty.py': ''
    }
    
    results_empty = analyzer.analyze_patterns(files_empty)
    
    print(f"Patrones de diseño encontrados: {dict(results_empty['design_patterns'])}")
    print(f"Anti-patrones encontrados: {dict(results_empty['anti_patterns'])}")
    print(f"Score de patrones: {results_empty['pattern_score']}")
    print(f"Resumen: {results_empty['summary']}")
    
    # Test con múltiples archivos
    print("\n4. Analizando múltiples archivos:")
    print("-" * 40)
    
    files_multiple = {
        'singleton.py': test_code_python,
        'factory.js': test_code_javascript,
        'empty.txt': 'Just some text',
        'other.py': 'def hello(): pass'
    }
    
    results_multiple = analyzer.analyze_patterns(files_multiple)
    
    print(f"Patrones de diseño encontrados: {dict(results_multiple['design_patterns'])}")
    print(f"Anti-patrones encontrados: {dict(results_multiple['anti_patterns'])}")
    print(f"Score de patrones: {results_multiple['pattern_score']}")
    print(f"Estructura del proyecto: {results_multiple['structure_analysis']}")
    
    # Verificar si los patrones específicos fueron detectados
    print("\n5. Verificación detallada de patrones:")
    print("-" * 40)
    
    if 'singleton' in results_python['design_patterns']:
        print("✅ Singleton detectado en Python")
        for location in results_python['design_patterns']['singleton']:
            print(f"   - Archivo: {location['file']}, Línea: {location['line']}")
    else:
        print("❌ Singleton NO detectado en Python")
    
    if 'factory' in results_python['design_patterns']:
        print("✅ Factory detectado en Python")
        for location in results_python['design_patterns']['factory']:
            print(f"   - Archivo: {location['file']}, Línea: {location['line']}")
    else:
        print("❌ Factory NO detectado en Python")
    
    if 'observer' in results_python['design_patterns']:
        print("✅ Observer detectado en Python")
        for location in results_python['design_patterns']['observer']:
            print(f"   - Archivo: {location['file']}, Línea: {location['line']}")
    else:
        print("❌ Observer NO detectado en Python")

if __name__ == "__main__":
    test_pattern_detection()