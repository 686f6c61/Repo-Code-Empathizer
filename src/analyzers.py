import ast
import logging
import copy
from typing import Dict, Any, List, Set
import re

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    def __init__(self):
        self.metricas = {
            'nombres': {'descriptividad': 0.0},
            'documentacion': {'cobertura_docstrings': 0.0},
            'modularidad': {
                'funciones_por_archivo': 0.0,
                'clases_por_archivo': 0.0,
                'cohesion_promedio': 0.0,
                'acoplamiento_promedio': 0.0
            },
            'complejidad': {
                'complejidad_ciclomatica': 0.0,
                'nivel_anidacion_max': 0.0,
                'longitud_promedio_funciones': 0.0
            },
            'manejo_errores': {
                'cobertura': 0.0,
                'especificidad': 0.0,
                'densidad': 0.0
            },
            'pruebas': {
                'cobertura_pruebas': 0.0,
                'densidad_asserts': 0.0,
                'funciones_test': 0.0
            },
            'seguridad': {
                'validacion_entradas': 0.0,
                'uso_funciones_peligrosas': 1.0,
                'total_validaciones': 0.0
            },
            'consistencia_estilo': {
                'consistencia_nombres': 0.0,
                'espaciado_consistente': 0.0,
                'longitud_lineas_consistente': 0.0
            }
        }

    def analizar_archivo(self, contenido: str) -> Dict[str, Dict[str, float]]:
        """Analiza un archivo y retorna sus métricas"""
        try:
            tree = ast.parse(contenido)
            metricas = copy.deepcopy(self.metricas)
            
            # Análisis de nombres
            metricas['nombres']['descriptividad'] = self._analizar_nombres(tree)
            
            # Análisis de documentación
            metricas['documentacion']['cobertura_docstrings'] = self._analizar_documentacion(tree)
            
            # Análisis de modularidad
            metricas['modularidad'].update(self._analizar_modularidad(tree))
            
            # Análisis de complejidad
            metricas['complejidad'].update(self._analizar_complejidad(tree, contenido))
            
            # Análisis de manejo de errores
            metricas['manejo_errores'].update(self._analizar_manejo_errores(tree))
            
            # Análisis de pruebas
            metricas['pruebas'].update(self._analizar_pruebas(tree))
            
            # Análisis de seguridad
            metricas['seguridad'].update(self._analizar_seguridad(tree))
            
            # Análisis de consistencia de estilo
            metricas['consistencia_estilo'].update(self._analizar_consistencia_estilo(tree, contenido))
            
            return metricas
        except Exception as e:
            logger.error(f"Error analizando archivo: {str(e)}")
            return self.metricas

    def _analizar_nombres(self, tree: ast.AST) -> float:
        """Analiza la descriptividad de los nombres"""
        total_nombres = 0
        nombres_descriptivos = 0
        
        class NombresVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                nonlocal total_nombres, nombres_descriptivos
                total_nombres += 1
                if len(node.id) > 3 and not node.id in {'temp', 'var', 'foo', 'bar'}:
                    nombres_descriptivos += 1
                self.generic_visit(node)
        
        NombresVisitor().visit(tree)
        return float(nombres_descriptivos / total_nombres if total_nombres > 0 else 0.0)

    def _analizar_documentacion(self, tree: ast.AST) -> float:
        """Analiza la cobertura de docstrings"""
        total_funciones = 0
        funciones_documentadas = 0
        
        class DocVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                nonlocal total_funciones, funciones_documentadas
                total_funciones += 1
                if ast.get_docstring(node):
                    funciones_documentadas += 1
                self.generic_visit(node)
        
        DocVisitor().visit(tree)
        return float(funciones_documentadas / total_funciones if total_funciones > 0 else 0.0)

    def _analizar_modularidad(self, tree: ast.AST) -> Dict[str, float]:
        """Analiza la modularidad del código"""
        total_funciones = 0
        total_clases = 0
        imports = set()
        atributos_por_clase = {}
        
        class ModularidadVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                nonlocal total_funciones
                total_funciones += 1
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                nonlocal total_clases
                total_clases += 1
                atributos = set()
                for n in ast.walk(node):
                    if isinstance(n, ast.Attribute):
                        atributos.add(n.attr)
                atributos_por_clase[node.name] = atributos
                self.generic_visit(node)
                
            def visit_Import(self, node):
                for n in node.names:
                    imports.add(n.name)
                    
            def visit_ImportFrom(self, node):
                if node.module:
                    imports.add(node.module)
        
        ModularidadVisitor().visit(tree)
        
        # Calcular cohesión
        cohesion = 0.0
        if atributos_por_clase:
            for atributos in atributos_por_clase.values():
                if atributos:
                    cohesion += len(atributos) / (total_funciones if total_funciones > 0 else 1)
            cohesion /= len(atributos_por_clase)
            
        # Calcular acoplamiento
        acoplamiento = 1.0 - (len(imports) / (total_funciones + total_clases) if (total_funciones + total_clases) > 0 else 0)
        
        return {
            'funciones_por_archivo': float(total_funciones),
            'clases_por_archivo': float(total_clases),
            'cohesion_promedio': min(1.0, cohesion),
            'acoplamiento_promedio': max(0.0, acoplamiento)
        }

    def _analizar_complejidad(self, tree: ast.AST, contenido: str) -> Dict[str, float]:
        """Analiza la complejidad del código"""
        complejidad = 0
        max_anidacion = 0
        lineas_por_funcion = []
        
        class ComplejidadVisitor(ast.NodeVisitor):
            def __init__(self):
                self.nivel_actual = 0
                
            def visit_If(self, node):
                nonlocal complejidad
                complejidad += 1
                self.nivel_actual += 1
                nonlocal max_anidacion
                max_anidacion = max(max_anidacion, self.nivel_actual)
                self.generic_visit(node)
                self.nivel_actual -= 1
                
            def visit_While(self, node):
                nonlocal complejidad
                complejidad += 1
                self.nivel_actual += 1
                nonlocal max_anidacion
                max_anidacion = max(max_anidacion, self.nivel_actual)
                self.generic_visit(node)
                self.nivel_actual -= 1
                
            def visit_For(self, node):
                nonlocal complejidad
                complejidad += 1
                self.nivel_actual += 1
                nonlocal max_anidacion
                max_anidacion = max(max_anidacion, self.nivel_actual)
                self.generic_visit(node)
                self.nivel_actual -= 1
                
            def visit_FunctionDef(self, node):
                lineas = len(node.body)
                lineas_por_funcion.append(lineas)
                self.generic_visit(node)
        
        ComplejidadVisitor().visit(tree)
        
        # Normalizar métricas
        complejidad_norm = 1.0 - (complejidad / 10.0 if complejidad <= 10 else 1.0)
        anidacion_norm = 1.0 - (max_anidacion / 3.0 if max_anidacion <= 3 else 1.0)
        longitud_norm = 1.0
        if lineas_por_funcion:
            promedio_lineas = sum(lineas_por_funcion) / len(lineas_por_funcion)
            longitud_norm = 1.0 - (promedio_lineas / 20.0 if promedio_lineas <= 20 else 1.0)
        
        return {
            'complejidad_ciclomatica': float(complejidad_norm),
            'nivel_anidacion_max': float(anidacion_norm),
            'longitud_promedio_funciones': float(longitud_norm)
        }

    def _analizar_manejo_errores(self, tree: ast.AST) -> Dict[str, float]:
        """Analiza el manejo de errores en el código"""
        total_funciones = 0
        funciones_con_try = 0
        total_try = 0
        try_especificos = 0
        
        class ErrorVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                nonlocal total_funciones
                total_funciones += 1
                tiene_try = False
                for n in ast.walk(node):
                    if isinstance(n, ast.Try):
                        tiene_try = True
                        break
                if tiene_try:
                    nonlocal funciones_con_try
                    funciones_con_try += 1
                self.generic_visit(node)
                
            def visit_Try(self, node):
                nonlocal total_try, try_especificos
                total_try += 1
                for handler in node.handlers:
                    if handler.type is not None:
                        try_especificos += 1
                self.generic_visit(node)
        
        ErrorVisitor().visit(tree)
        
        cobertura = funciones_con_try / total_funciones if total_funciones > 0 else 0.0
        especificidad = try_especificos / total_try if total_try > 0 else 0.0
        densidad = total_try / total_funciones if total_funciones > 0 else 0.0
        
        return {
            'cobertura': float(cobertura),
            'especificidad': float(especificidad),
            'densidad': float(densidad)
        }

    def _analizar_pruebas(self, tree: ast.AST) -> Dict[str, float]:
        """Analiza las pruebas en el código"""
        total_funciones = 0
        funciones_test = 0
        total_asserts = 0
        
        class TestVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                nonlocal total_funciones, funciones_test, total_asserts
                total_funciones += 1
                if node.name.startswith('test_'):
                    funciones_test += 1
                    for n in ast.walk(node):
                        if isinstance(n, ast.Assert):
                            total_asserts += 1
                self.generic_visit(node)
        
        TestVisitor().visit(tree)
        
        cobertura = funciones_test / total_funciones if total_funciones > 0 else 0.0
        densidad = total_asserts / funciones_test if funciones_test > 0 else 0.0
        
        return {
            'cobertura_pruebas': float(cobertura),
            'densidad_asserts': float(densidad),
            'funciones_test': float(funciones_test)
        }

    def _analizar_seguridad(self, tree: ast.AST) -> Dict[str, float]:
        """Analiza la seguridad del código"""
        total_funciones = 0
        funciones_con_validacion = 0
        total_validaciones = 0
        usa_funciones_peligrosas = False
        
        class SeguridadVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                nonlocal total_funciones, funciones_con_validacion, total_validaciones
                total_funciones += 1
                tiene_validacion = False
                for n in ast.walk(node):
                    if isinstance(n, ast.Call):
                        if isinstance(n.func, ast.Name):
                            if n.func.id in {'isinstance', 'type', 'hasattr'}:
                                tiene_validacion = True
                                total_validaciones += 1
                    elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                        if n.func.id in {'eval', 'exec', 'globals'}:
                            nonlocal usa_funciones_peligrosas
                            usa_funciones_peligrosas = True
                if tiene_validacion:
                    funciones_con_validacion += 1
                self.generic_visit(node)
        
        SeguridadVisitor().visit(tree)
        
        validacion = funciones_con_validacion / total_funciones if total_funciones > 0 else 0.0
        seguridad = 0.0 if usa_funciones_peligrosas else 1.0
        
        return {
            'validacion_entradas': float(validacion),
            'uso_funciones_peligrosas': float(seguridad),
            'total_validaciones': float(total_validaciones)
        }

    def _analizar_consistencia_estilo(self, tree: ast.AST, contenido: str) -> Dict[str, float]:
        """Analiza la consistencia del estilo en el código"""
        total_nombres = 0
        nombres_consistentes = 0
        lineas = contenido.splitlines()
        lineas_espaciado_correcto = 0
        lineas_longitud_correcta = 0
        
        class EstiloVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                nonlocal total_nombres, nombres_consistentes
                total_nombres += 1
                # Verificar snake_case para variables/funciones
                if re.match(r'^[a-z][a-z0-9_]*$', node.id):
                    nombres_consistentes += 1
                # Verificar PascalCase para clases
                elif re.match(r'^[A-Z][a-zA-Z0-9]*$', node.id):
                    nombres_consistentes += 1
                self.generic_visit(node)
        
        EstiloVisitor().visit(tree)
        
        # Analizar espaciado
        for linea in lineas:
            if not linea.strip():
                continue
            if not re.search(r'\s{2,}', linea.rstrip()):
                lineas_espaciado_correcto += 1
            if len(linea) <= 80:
                lineas_longitud_correcta += 1
                
        consistencia_nombres = nombres_consistentes / total_nombres if total_nombres > 0 else 0.0
        espaciado = lineas_espaciado_correcto / len(lineas) if lineas else 0.0
        longitud = lineas_longitud_correcta / len(lineas) if lineas else 0.0
        
        return {
            'consistencia_nombres': float(consistencia_nombres),
            'espaciado_consistente': float(espaciado),
            'longitud_lineas_consistente': float(longitud)
        }

    def calcular_diferencias(self, metricas_master: Dict[str, Any], metricas_comparado: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Calcula las diferencias entre las métricas de dos repositorios"""
        diferencias = {}
        
        try:
            for categoria in self.metricas.keys():
                if categoria in metricas_master and categoria in metricas_comparado:
                    diferencias[categoria] = {}
                    for metrica in self.metricas[categoria].keys():
                        if metrica in metricas_master[categoria] and metrica in metricas_comparado[categoria]:
                            try:
                                valor_master = float(metricas_master[categoria][metrica])
                                valor_comparado = float(metricas_comparado[categoria][metrica])
                                diferencias[categoria][metrica] = round(valor_master - valor_comparado, 3)
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Error convirtiendo valores para {categoria}.{metrica}: {str(e)}")
                                diferencias[categoria][metrica] = 0.0
        except Exception as e:
            logger.error(f"Error calculando diferencias: {str(e)}")
            raise

        return diferencias

    def calcular_puntuacion_final(self, metricas: Dict[str, Any]) -> float:
        """Calcula la puntuación final de un repositorio"""
        try:
            puntuacion = 0.0
            for categoria, valores in metricas.items():
                if isinstance(valores, dict) and categoria != 'metadata':
                    for valor in valores.values():
                        # Convertir a float antes de sumar
                        puntuacion += float(valor)
            return puntuacion
        except Exception as e:
            logger.error(f"Error calculando puntuación final: {str(e)}")
            raise

    def generar_recomendaciones(self, metricas: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en las métricas más bajas"""
        recomendaciones = []
        umbrales = {
            'nombres': {
                'descriptividad': (0.7, 'Mejorar la descriptividad de los nombres de variables y funciones')
            },
            'documentacion': {
                'cobertura_docstrings': (0.8, 'Aumentar la cobertura de documentación con docstrings')
            },
            'modularidad': {
                'cohesion_promedio': (0.6, 'Mejorar la cohesión entre métodos y atributos de clase'),
                'acoplamiento_promedio': (0.7, 'Reducir el acoplamiento entre módulos')
            },
            'complejidad': {
                'complejidad_ciclomatica': (0.7, 'Reducir la complejidad ciclomática refactorizando funciones complejas'),
                'nivel_anidacion_max': (0.8, 'Reducir el nivel de anidación de estructuras de control'),
                'longitud_promedio_funciones': (0.7, 'Reducir la longitud de las funciones dividiéndolas en funciones más pequeñas')
            },
            'manejo_errores': {
                'cobertura': (0.6, 'Aumentar la cobertura de manejo de errores'),
                'especificidad': (0.8, 'Usar excepciones más específicas en lugar de genéricas')
            },
            'pruebas': {
                'cobertura_pruebas': (0.7, 'Aumentar la cobertura de pruebas unitarias'),
                'densidad_asserts': (0.6, 'Incrementar el número de aserciones en las pruebas')
            },
            'seguridad': {
                'validacion_entradas': (0.7, 'Mejorar la validación de entradas en las funciones'),
                'uso_funciones_peligrosas': (1.0, 'Evitar el uso de funciones potencialmente peligrosas')
            },
            'consistencia_estilo': {
                'consistencia_nombres': (0.8, 'Mantener una convención de nombres consistente'),
                'espaciado_consistente': (0.9, 'Mantener un espaciado consistente en el código'),
                'longitud_lineas_consistente': (0.9, 'Mantener líneas de código dentro del límite de 80 caracteres')
            }
        }

        for categoria, metricas_categoria in metricas.items():
            if categoria in umbrales and isinstance(metricas_categoria, dict):
                for metrica, valor in metricas_categoria.items():
                    if metrica in umbrales[categoria]:
                        umbral, recomendacion = umbrales[categoria][metrica]
                        try:
                            if float(valor) < umbral:
                                recomendaciones.append(recomendacion)
                        except (ValueError, TypeError):
                            logger.warning(f"Valor no numérico encontrado para {categoria}.{metrica}: {valor}")
                            continue

        return recomendaciones
