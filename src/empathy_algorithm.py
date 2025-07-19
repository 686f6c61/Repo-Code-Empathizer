"""
Módulo de algoritmo de empatía para comparación empresa-candidato.

Este módulo implementa un algoritmo avanzado para calcular la empatía entre
el código de una empresa y el de un candidato, proporcionando una métrica objetiva
para evaluar la alineación de estilos de programación.

Classes:
    EmpathyAlgorithm: Algoritmo principal para cálculo de empatía.

Example:
    >>> algorithm = EmpathyAlgorithm()
    >>> score = algorithm.calculate_empathy_score(empresa_metrics, candidato_metrics)
    >>> print(f"Empatía: {score['empathy_score']}%")

Author: R. Benítez
Version: 2.0.0
License: MIT
"""
import math
from typing import Dict, List, Any, Tuple
import numpy as np


class EmpathyAlgorithm:
    """
    Algoritmo avanzado para calcular la empatía entre el código de la empresa
    y el código del candidato. Utiliza múltiples factores ponderados y
    técnicas de normalización para proporcionar una métrica precisa.
    """
    
    def __init__(self) -> None:
        """
        Inicializa el algoritmo de empatía con pesos y factores predefinidos.
        
        Los pesos están optimizados para evaluar la compatibilidad entre
        estilos de código en un contexto empresarial.
        """
        # Pesos base por categoría (suman 1.0)
        self.category_weights = {
            'nombres': 0.15,
            'documentacion': 0.15,
            'modularidad': 0.15,
            'complejidad': 0.15,
            'manejo_errores': 0.10,
            'pruebas': 0.10,
            'seguridad': 0.10,
            'consistencia_estilo': 0.10
        }
        
        # Factores de importancia por lenguaje
        self.language_importance = {
            'Python': 1.0,
            'JavaScript': 1.0,
            'TypeScript': 1.1,  # Mayor importancia por tipos
            'Java': 1.0,
            'Go': 1.05,
            'C#': 1.0,
            'C++': 1.1,  # Mayor importancia por complejidad
            'PHP': 0.95,
            'Ruby': 0.95,
            'Swift': 1.05,
            'HTML': 0.8,
            'CSS': 0.8
        }
        
    def calculate_empathy_score(self, empresa_metrics: Dict[str, Any], 
                               candidato_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula la puntuación de empatía entre empresa y candidato.
        
        Este es el método principal que orquesta todo el proceso de cálculo,
        incluyendo análisis por categorías, coincidencia de lenguajes y
        generación de recomendaciones.
        
        Args:
            empresa_metrics: Métricas del repositorio de la empresa.
                Debe contener 'metadata' y métricas por categoría.
            candidato_metrics: Métricas del repositorio del candidato.
                Misma estructura que empresa_metrics.
        
        Returns:
            Dict[str, Any]: Diccionario con los resultados del análisis:
                - empathy_score (float): Puntuación final (0-100)
                - category_scores (Dict[str, float]): Puntuaciones por categoría
                - language_overlap (Dict[str, Any]): Análisis de lenguajes
                - detailed_analysis (Dict[str, Any]): Análisis detallado
                - recommendations (List[Dict]): Recomendaciones para el candidato
                - interpretation (Dict[str, str]): Interpretación del resultado
        
        Raises:
            KeyError: Si faltan métricas requeridas en los parámetros.
            ValueError: Si las métricas tienen formato inválido.
        """
        
        # Extraer lenguajes analizados
        empresa_langs = self._get_languages(empresa_metrics)
        candidato_langs = self._get_languages(candidato_metrics)
        
        # Calcular coincidencia de lenguajes
        language_overlap = self._calculate_language_overlap(empresa_langs, candidato_langs)
        
        # Calcular puntuaciones por categoría
        category_scores = {}
        detailed_scores = {}
        
        for category in self.category_weights.keys():
            if category in empresa_metrics and category in candidato_metrics:
                score, details = self._calculate_category_score(
                    empresa_metrics[category],
                    candidato_metrics[category],
                    category
                )
                category_scores[category] = score
                detailed_scores[category] = details
        
        # Calcular puntuación base
        base_score = self._calculate_base_score(category_scores)
        
        # Aplicar factores de ajuste
        adjusted_score = self._apply_adjustments(
            base_score,
            language_overlap,
            empresa_metrics,
            candidato_metrics
        )
        
        # Generar análisis detallado
        detailed_analysis = self._generate_detailed_analysis(
            category_scores,
            detailed_scores,
            language_overlap
        )
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(
            category_scores,
            detailed_scores,
            empresa_metrics,
            candidato_metrics
        )
        
        return {
            'empathy_score': round(adjusted_score, 2),
            'category_scores': category_scores,
            'language_overlap': language_overlap,
            'detailed_analysis': detailed_analysis,
            'recommendations': recommendations,
            'interpretation': self._interpret_score(adjusted_score)
        }
    
    def _get_languages(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Extrae los lenguajes analizados de las métricas.
        
        Args:
            metrics: Diccionario de métricas con metadata.
        
        Returns:
            List[str]: Lista de lenguajes analizados.
        """
        if 'metadata' in metrics:
            return metrics['metadata'].get('lenguajes_analizados', [])
        return []
    
    def _calculate_language_overlap(self, empresa_langs: List[str], 
                                   candidato_langs: List[str]) -> Dict[str, Any]:
        """
        Calcula la coincidencia de lenguajes entre empresa y candidato.
        
        Evalúa cuántos lenguajes de la empresa domina el candidato y
        penaliza si el candidato usa demasiados lenguajes adicionales
        (puede indicar falta de enfoque).
        
        Args:
            empresa_langs: Lenguajes usados por la empresa.
            candidato_langs: Lenguajes del candidato.
        
        Returns:
            Dict[str, Any]: Diccionario con:
                - score: Porcentaje de coincidencia (0-100)
                - overlap: Lenguajes en común
                - missing: Lenguajes que le faltan al candidato
                - extra: Lenguajes adicionales del candidato
        """
        if not empresa_langs:
            return {'score': 0, 'overlap': [], 'missing': []}
        
        overlap = set(empresa_langs) & set(candidato_langs)
        missing = set(empresa_langs) - set(candidato_langs)
        extra = set(candidato_langs) - set(empresa_langs)
        
        # Puntuación basada en coincidencia
        overlap_score = len(overlap) / len(empresa_langs) * 100
        
        # Penalización por lenguajes extra (puede indicar falta de foco)
        if extra and len(extra) > len(empresa_langs) * 0.5:
            overlap_score *= 0.9
        
        return {
            'score': overlap_score,
            'overlap': list(overlap),
            'missing': list(missing),
            'extra': list(extra)
        }
    
    def _calculate_category_score(self, empresa_values: Dict[str, float],
                                 candidato_values: Dict[str, float],
                                 category: str) -> Tuple[float, Dict[str, Any]]:
        """Calcula la puntuación para una categoría específica"""
        if not empresa_values or not candidato_values:
            return 0.0, {}
        
        scores = []
        details = {}
        
        for metric, empresa_value in empresa_values.items():
            if metric in candidato_values:
                candidato_value = candidato_values[metric]
                
                # Calcular similitud usando diferentes métodos según la métrica
                if category == 'complejidad':
                    # Para complejidad, valores más bajos son mejores
                    similarity = self._inverse_similarity(empresa_value, candidato_value)
                elif category in ['pruebas', 'documentacion', 'seguridad']:
                    # Para estas categorías, queremos que el candidato iguale o supere
                    similarity = self._threshold_similarity(empresa_value, candidato_value)
                else:
                    # Para otras categorías, buscamos similitud directa
                    similarity = self._cosine_similarity(empresa_value, candidato_value)
                
                scores.append(similarity)
                details[metric] = {
                    'empresa': empresa_value,
                    'candidato': candidato_value,
                    'similarity': similarity
                }
        
        # Calcular puntuación promedio ponderada
        if scores:
            category_score = sum(scores) / len(scores) * 100
        else:
            category_score = 0.0
        
        return category_score, details
    
    def _cosine_similarity(self, a: float, b: float) -> float:
        """
        Calcula similitud coseno entre dos valores escalares.
        
        Utilizada para métricas donde valores similares son deseables.
        
        Args:
            a: Valor de la empresa.
            b: Valor del candidato.
        
        Returns:
            float: Similitud entre 0 y 1 (1 = idénticos).
        """
        if a == 0 and b == 0:
            return 1.0
        if a == 0 or b == 0:
            return 0.0
        
        # Normalizar a vectores unitarios y calcular similitud
        dot_product = a * b
        magnitude = math.sqrt(a**2) * math.sqrt(b**2)
        
        if magnitude == 0:
            return 0.0
        
        similarity = dot_product / magnitude
        return min(1.0, max(0.0, similarity))
    
    def _inverse_similarity(self, a: float, b: float) -> float:
        """Calcula similitud inversa (para métricas donde menor es mejor)"""
        if a == 0 and b == 0:
            return 1.0
        
        # Calcular diferencia absoluta normalizada
        max_val = max(a, b)
        if max_val == 0:
            return 1.0
        
        diff = abs(a - b) / max_val
        return 1.0 - diff
    
    def _threshold_similarity(self, empresa: float, candidato: float) -> float:
        """Calcula similitud con umbral (candidato debe igualar o superar)"""
        if empresa == 0:
            return 1.0 if candidato == 0 else 0.5
        
        if candidato >= empresa:
            # Supera el estándar
            return min(1.0, 0.8 + (candidato - empresa) * 0.2)
        else:
            # No alcanza el estándar
            ratio = candidato / empresa
            return ratio * 0.8  # Máximo 80% si no alcanza
    
    def _calculate_base_score(self, category_scores: Dict[str, float]) -> float:
        """Calcula la puntuación base ponderada"""
        total_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.1)
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def _apply_adjustments(self, base_score: float, language_overlap: Dict[str, Any],
                          empresa_metrics: Dict[str, Any], 
                          candidato_metrics: Dict[str, Any]) -> float:
        """Aplica ajustes a la puntuación base"""
        adjusted_score = base_score
        
        # Ajuste por coincidencia de lenguajes
        language_factor = language_overlap['score'] / 100
        if language_factor < 0.5:
            # Penalización significativa si hay poca coincidencia de lenguajes
            adjusted_score *= 0.7
        else:
            adjusted_score *= (0.9 + language_factor * 0.1)
        
        # Ajuste por tamaño del proyecto
        empresa_files = empresa_metrics.get('metadata', {}).get('archivos_analizados', 0)
        candidato_files = candidato_metrics.get('metadata', {}).get('archivos_analizados', 0)
        
        if empresa_files > 0 and candidato_files > 0:
            size_ratio = min(candidato_files / empresa_files, empresa_files / candidato_files)
            if size_ratio < 0.3:
                # Proyectos muy diferentes en tamaño
                adjusted_score *= 0.95
        
        # Bonus por excelencia en áreas críticas
        critical_categories = ['seguridad', 'pruebas', 'documentacion']
        excellence_bonus = 0
        
        for category in critical_categories:
            if category in candidato_metrics:
                candidato_avg = self._get_category_average(candidato_metrics[category])
                empresa_avg = self._get_category_average(empresa_metrics.get(category, {}))
                
                if candidato_avg > empresa_avg * 1.2:  # 20% mejor
                    excellence_bonus += 2
        
        adjusted_score = min(100, adjusted_score + excellence_bonus)
        
        return adjusted_score
    
    def _get_category_average(self, category_metrics: Dict[str, float]) -> float:
        """Calcula el promedio de una categoría"""
        if not category_metrics:
            return 0.0
        
        values = [v for v in category_metrics.values() if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0.0
    
    def _generate_detailed_analysis(self, category_scores: Dict[str, float],
                                   detailed_scores: Dict[str, Dict],
                                   language_overlap: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un análisis detallado de la comparación"""
        
        # Identificar fortalezas y debilidades
        strengths = []
        weaknesses = []
        
        for category, score in category_scores.items():
            if score >= 80:
                strengths.append({
                    'category': category,
                    'score': score,
                    'description': f"Excelente alineación en {category}"
                })
            elif score < 60:
                weaknesses.append({
                    'category': category,
                    'score': score,
                    'description': f"Necesita mejorar en {category}"
                })
        
        # Análisis de lenguajes
        language_analysis = {
            'alignment': language_overlap['score'],
            'missing_languages': language_overlap['missing'],
            'recommendation': self._get_language_recommendation(language_overlap)
        }
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'language_analysis': language_analysis,
            'overall_alignment': self._calculate_overall_alignment(category_scores)
        }
    
    def _generate_recommendations(self, category_scores: Dict[str, float],
                                 detailed_scores: Dict[str, Dict],
                                 empresa_metrics: Dict[str, Any],
                                 candidato_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera recomendaciones específicas para el candidato"""
        recommendations = []
        
        # Recomendaciones por categoría
        for category, score in category_scores.items():
            if score < 70:
                details = detailed_scores.get(category, {})
                rec = self._get_category_recommendation(category, score, details)
                if rec:
                    recommendations.append(rec)
        
        # Recomendaciones de lenguaje
        languages = self._get_languages(empresa_metrics)
        candidato_langs = self._get_languages(candidato_metrics)
        
        missing_langs = set(languages) - set(candidato_langs)
        if missing_langs:
            recommendations.append({
                'priority': 'high',
                'category': 'languages',
                'title': 'Lenguajes faltantes',
                'description': f"Considere añadir proyectos en: {', '.join(missing_langs)}",
                'impact': 'Alto impacto en la puntuación de empatía'
            })
        
        # Ordenar por prioridad
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations
    
    def _get_category_recommendation(self, category: str, score: float, 
                                    details: Dict[str, Any]) -> Dict[str, Any]:
        """Genera recomendación específica para una categoría"""
        recommendations_map = {
            'nombres': {
                'title': 'Mejorar nomenclatura',
                'description': 'Use nombres más descriptivos siguiendo las convenciones de la empresa',
                'tips': ['Use camelCase o snake_case consistentemente', 
                        'Evite abreviaciones', 
                        'Use nombres que expresen intención']
            },
            'documentacion': {
                'title': 'Aumentar documentación',
                'description': 'Añada más comentarios y documentación al código',
                'tips': ['Documente todas las funciones públicas',
                        'Añada comentarios en lógica compleja',
                        'Use formato de documentación estándar del lenguaje']
            },
            'pruebas': {
                'title': 'Implementar más pruebas',
                'description': 'Aumente la cobertura de pruebas unitarias',
                'tips': ['Añada tests para casos edge',
                        'Implemente tests de integración',
                        'Use TDD para nuevo código']
            },
            'seguridad': {
                'title': 'Mejorar prácticas de seguridad',
                'description': 'Implemente validaciones y prácticas seguras',
                'tips': ['Valide todas las entradas de usuario',
                        'Use consultas parametrizadas',
                        'Evite exponer información sensible']
            }
        }
        
        if category in recommendations_map:
            rec = recommendations_map[category].copy()
            rec['priority'] = 'high' if score < 50 else 'medium'
            rec['category'] = category
            rec['current_score'] = score
            rec['impact'] = f"Puede mejorar la puntuación en {round(70 - score)}%"
            return rec
        
        return None
    
    def _get_language_recommendation(self, language_overlap: Dict[str, Any]) -> str:
        """Genera recomendación sobre lenguajes"""
        if language_overlap['score'] >= 80:
            return "Excelente cobertura de lenguajes"
        elif language_overlap['score'] >= 60:
            return "Buena cobertura, considere añadir los lenguajes faltantes"
        else:
            return "Cobertura insuficiente de lenguajes requeridos por la empresa"
    
    def _calculate_overall_alignment(self, category_scores: Dict[str, float]) -> str:
        """Calcula el nivel general de alineación"""
        if not category_scores:
            return "Sin datos"
        
        avg_score = sum(category_scores.values()) / len(category_scores)
        
        if avg_score >= 85:
            return "Excelente"
        elif avg_score >= 70:
            return "Bueno"
        elif avg_score >= 55:
            return "Aceptable"
        else:
            return "Necesita mejora"
    
    def _interpret_score(self, score: float) -> Dict[str, Any]:
        """
        Interpreta la puntuación de empatía y genera recomendación de contratación.
        
        Args:
            score: Puntuación de empatía (0-100).
        
        Returns:
            Dict[str, Any]: Diccionario con:
                - level: Nivel de empatía (Excelente, Bueno, etc.)
                - description: Descripción del nivel
                - recommendation: Recomendación de contratación
                - color: Color hex para visualización
        """
        if score >= 90:
            return {
                'level': 'Excelente',
                'description': 'El candidato tiene un estilo de código muy alineado con la empresa',
                'recommendation': 'Candidato altamente recomendado',
                'color': '#000000'
            }
        elif score >= 75:
            return {
                'level': 'Bueno',
                'description': 'Buena alineación con algunas áreas de mejora',
                'recommendation': 'Candidato recomendado con capacitación menor',
                'color': '#333333'
            }
        elif score >= 60:
            return {
                'level': 'Aceptable',
                'description': 'Alineación moderada, requiere adaptación',
                'recommendation': 'Candidato viable con plan de capacitación',
                'color': '#666666'
            }
        elif score >= 45:
            return {
                'level': 'Bajo',
                'description': 'Baja alineación con el estilo de la empresa',
                'recommendation': 'Requiere capacitación significativa',
                'color': '#999999'
            }
        else:
            return {
                'level': 'Muy Bajo',
                'description': 'Estilo de código muy diferente al de la empresa',
                'recommendation': 'No recomendado sin capacitación extensiva',
                'color': '#CCCCCC'
            }