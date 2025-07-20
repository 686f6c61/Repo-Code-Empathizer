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
        # Pesos base por categoría - 11 categorías (suman 1.0)
        self.category_weights = {
            # Categorías base (8) - 70% del peso total
            'nombres': 0.12,
            'documentacion': 0.12,
            'modularidad': 0.10,
            'complejidad': 0.10,
            'manejo_errores': 0.08,
            'pruebas': 0.08,
            'seguridad': 0.06,
            'consistencia_estilo': 0.04,
            # Categorías avanzadas (3) - 30% del peso total
            'patrones': 0.12,  # Patrones de diseño y anti-patrones
            'rendimiento': 0.10,  # Análisis de performance
            'comentarios': 0.08   # Calidad de comentarios y TODOs
        }
        
        # Matriz de correlación entre categorías (para ajustes más complejos)
        self.category_correlations = {
            'documentacion': {'comentarios': 0.8, 'pruebas': 0.3},
            'modularidad': {'patrones': 0.7, 'complejidad': -0.5},
            'patrones': {'modularidad': 0.7, 'rendimiento': 0.4},
            'seguridad': {'manejo_errores': 0.6, 'pruebas': 0.4},
            'rendimiento': {'complejidad': -0.6, 'patrones': 0.4}
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
            if category in ['patrones', 'rendimiento', 'comentarios']:
                # Categorías avanzadas con cálculo especial
                score = self._calculate_advanced_category_score(
                    empresa_metrics.get(category, {}),
                    candidato_metrics.get(category, {}),
                    category
                )
                category_scores[category] = score
            elif category in empresa_metrics and category in candidato_metrics:
                score, details = self._calculate_category_score(
                    empresa_metrics[category],
                    candidato_metrics[category],
                    category
                )
                category_scores[category] = score
                detailed_scores[category] = details
        
        # Aplicar correlaciones entre categorías
        correlated_scores = self._apply_category_correlations(category_scores)
        
        # Calcular puntuación base con algoritmo complejo
        base_score = self._calculate_complex_base_score(correlated_scores)
        
        # Aplicar factores de ajuste múltiples
        adjusted_score = self._apply_multi_factor_adjustments(
            base_score,
            language_overlap,
            empresa_metrics,
            candidato_metrics,
            category_scores
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
            'interpretation': self._interpret_score(adjusted_score),
            'algorithm_version': '3.0',
            'complexity_factors': {
                'base_score': round(base_score, 2),
                'correlation_adjustment': round(base_score - self._calculate_base_score(category_scores), 2),
                'multi_factor_adjustment': round(adjusted_score - base_score, 2)
            }
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
    
    def _calculate_advanced_category_score(self, empresa_data: Dict[str, Any],
                                         candidato_data: Dict[str, Any],
                                         category: str) -> float:
        """Calcula puntuación para categorías avanzadas"""
        if category == 'patrones':
            return self._calculate_pattern_score(empresa_data, candidato_data)
        elif category == 'rendimiento':
            return self._calculate_performance_score(empresa_data, candidato_data)
        elif category == 'comentarios':
            return self._calculate_comment_score(empresa_data, candidato_data)
        return 0.0
    
    def _calculate_pattern_score(self, empresa_patterns: Dict, candidato_patterns: Dict) -> float:
        """Calcula puntuación de patrones de diseño"""
        if not empresa_patterns or not candidato_patterns:
            return 50.0  # Puntuación neutral si no hay datos
        
        # Puntuación base del candidato
        candidato_score = candidato_patterns.get('pattern_score', 0)
        empresa_score = empresa_patterns.get('pattern_score', 0)
        
        # Comparar cantidad de patrones buenos vs anti-patrones
        candidato_patterns_count = len(candidato_patterns.get('design_patterns', {}))
        candidato_antipatterns_count = len(candidato_patterns.get('anti_patterns', {}))
        
        empresa_patterns_count = len(empresa_patterns.get('design_patterns', {}))
        empresa_antipatterns_count = len(empresa_patterns.get('anti_patterns', {}))
        
        # Calcular ratio de calidad (patrones buenos vs malos)
        candidato_ratio = candidato_patterns_count / (candidato_antipatterns_count + 1)
        empresa_ratio = empresa_patterns_count / (empresa_antipatterns_count + 1)
        
        # Si el candidato tiene mejor ratio que la empresa, bonus
        if candidato_ratio > empresa_ratio:
            bonus = min(20, (candidato_ratio - empresa_ratio) * 10)
            return min(100, candidato_score + bonus)
        else:
            # Penalización por peor ratio
            penalty = min(30, (empresa_ratio - candidato_ratio) * 10)
            return max(0, candidato_score - penalty)
    
    def _calculate_performance_score(self, empresa_perf: Dict, candidato_perf: Dict) -> float:
        """Calcula puntuación de rendimiento"""
        if not empresa_perf or not candidato_perf:
            return 50.0
        
        candidato_score = candidato_perf.get('performance_score', 0)
        empresa_score = empresa_perf.get('performance_score', 0)
        
        # Comparar cantidad de problemas de rendimiento
        candidato_issues = sum(len(v) for v in candidato_perf.get('performance_issues', {}).values())
        empresa_issues = sum(len(v) for v in empresa_perf.get('performance_issues', {}).values())
        
        # Menos problemas es mejor
        if candidato_issues < empresa_issues:
            bonus = min(15, (empresa_issues - candidato_issues) * 3)
            return min(100, candidato_score + bonus)
        else:
            penalty = min(25, (candidato_issues - empresa_issues) * 3)
            return max(0, candidato_score - penalty)
    
    def _calculate_comment_score(self, empresa_comments: Dict, candidato_comments: Dict) -> float:
        """Calcula puntuación de comentarios"""
        if not empresa_comments or not candidato_comments:
            return 50.0
        
        # Obtener métricas de comentarios
        candidato_metrics = candidato_comments.get('comment_metrics', {})
        empresa_metrics = empresa_comments.get('comment_metrics', {})
        
        candidato_quality = candidato_metrics.get('comment_quality_score', 0)
        empresa_quality = empresa_metrics.get('comment_quality_score', 0)
        
        # Comparar cantidad de TODOs/FIXMEs (menos es mejor)
        candidato_todos = sum(len(v) for v in candidato_comments.get('markers', {}).values())
        empresa_todos = sum(len(v) for v in empresa_comments.get('markers', {}).values())
        
        # Score base
        score = candidato_quality
        
        # Ajustar por cantidad de TODOs
        if candidato_todos < empresa_todos:
            score += min(10, (empresa_todos - candidato_todos) * 2)
        else:
            score -= min(15, (candidato_todos - empresa_todos) * 2)
        
        return max(0, min(100, score))
    
    def _apply_category_correlations(self, category_scores: Dict[str, float]) -> Dict[str, float]:
        """Aplica correlaciones entre categorías para un cálculo más complejo"""
        adjusted_scores = category_scores.copy()
        
        for category, correlations in self.category_correlations.items():
            if category in adjusted_scores:
                for correlated_cat, correlation_factor in correlations.items():
                    if correlated_cat in adjusted_scores:
                        # Ajustar puntuación basada en correlación
                        adjustment = (adjusted_scores[correlated_cat] - 50) * correlation_factor * 0.1
                        adjusted_scores[category] = max(0, min(100, 
                            adjusted_scores[category] + adjustment))
        
        return adjusted_scores
    
    def _calculate_complex_base_score(self, category_scores: Dict[str, float]) -> float:
        """Calcula puntuación base con algoritmo complejo"""
        if not category_scores:
            return 0.0
        
        # Separar categorías por importancia
        critical_categories = ['patrones', 'seguridad', 'pruebas']
        important_categories = ['nombres', 'documentacion', 'modularidad', 'complejidad']
        standard_categories = ['manejo_errores', 'rendimiento', 'comentarios', 'consistencia_estilo']
        
        # Calcular puntuaciones por grupo
        critical_score = 0.0
        critical_weight = 0.0
        important_score = 0.0
        important_weight = 0.0
        standard_score = 0.0
        standard_weight = 0.0
        
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.05)
            
            if category in critical_categories:
                critical_score += score * weight
                critical_weight += weight
            elif category in important_categories:
                important_score += score * weight
                important_weight += weight
            else:
                standard_score += score * weight
                standard_weight += weight
        
        # Calcular puntuaciones por grupo
        critical_avg = critical_score / critical_weight if critical_weight > 0 else 0
        important_avg = important_score / important_weight if important_weight > 0 else 0
        standard_avg = standard_score / standard_weight if standard_weight > 0 else 0
        
        # Aplicar fórmula compleja con ponderación no lineal
        # Las categorías críticas tienen mayor impacto
        base_score = (
            critical_avg * 0.45 +  # 45% del peso para categorías críticas
            important_avg * 0.35 + # 35% para importantes
            standard_avg * 0.20    # 20% para estándar
        )
        
        # Penalización por baja puntuación en categorías críticas
        if critical_avg < 50:
            penalty = (50 - critical_avg) * 0.3
            base_score = max(0, base_score - penalty)
        
        # Bonus por excelencia general (todas las categorías > 70)
        if all(score > 70 for score in category_scores.values()):
            base_score = min(100, base_score + 5)
        
        return base_score
    
    def _calculate_base_score(self, category_scores: Dict[str, float]) -> float:
        """Calcula la puntuación base ponderada (versión simple para compatibilidad)"""
        total_score = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.1)
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def _apply_multi_factor_adjustments(self, base_score: float, language_overlap: Dict[str, Any],
                                       empresa_metrics: Dict[str, Any], 
                                       candidato_metrics: Dict[str, Any],
                                       category_scores: Dict[str, float]) -> float:
        """Aplica múltiples factores de ajuste con algoritmo complejo"""
        adjusted_score = base_score
        
        # Factor 1: Coincidencia de lenguajes (peso variable según contexto)
        language_factor = language_overlap['score'] / 100
        language_weight = 0.15  # 15% del impacto total
        
        if language_factor < 0.3:
            # Penalización severa por muy poca coincidencia
            adjusted_score *= (0.5 + language_factor)
        elif language_factor < 0.7:
            # Penalización moderada
            adjusted_score *= (0.8 + language_factor * 0.2)
        else:
            # Bonus por alta coincidencia
            adjusted_score *= (0.95 + language_factor * 0.05)
        
        # Factor 2: Complejidad del match (tamaño y naturaleza del proyecto)
        empresa_files = empresa_metrics.get('metadata', {}).get('archivos_analizados', 0)
        candidato_files = candidato_metrics.get('metadata', {}).get('archivos_analizados', 0)
        
        if empresa_files > 0 and candidato_files > 0:
            size_ratio = min(candidato_files / empresa_files, empresa_files / candidato_files)
            complexity_factor = self._calculate_complexity_factor(size_ratio, empresa_files, candidato_files)
            adjusted_score *= complexity_factor
        
        # Factor 3: Distribución de puntuaciones (consistencia)
        scores_std = np.std(list(category_scores.values())) if category_scores else 0
        consistency_bonus = 0
        
        if scores_std < 15:  # Muy consistente
            consistency_bonus = 3
        elif scores_std < 25:  # Moderadamente consistente
            consistency_bonus = 1
        else:  # Inconsistente
            consistency_bonus = -2
        
        adjusted_score += consistency_bonus
        
        # Factor 4: Excelencia en categorías críticas con ponderación dinámica
        critical_categories = {
            'seguridad': 3.0,      # Mayor peso
            'pruebas': 2.5,
            'patrones': 2.5,
            'documentacion': 2.0,
            'rendimiento': 1.5
        }
        
        excellence_bonus = 0
        deficiency_penalty = 0
        
        for category, weight in critical_categories.items():
            if category in category_scores:
                score = category_scores[category]
                
                if score >= 85:  # Excelente
                    excellence_bonus += weight * 1.5
                elif score >= 70:  # Bueno
                    excellence_bonus += weight * 0.5
                elif score < 50:  # Deficiente
                    deficiency_penalty += weight * 1.5
        
        # Factor 5: Análisis de patrones y anti-patrones
        if 'patrones' in candidato_metrics:
            pattern_data = candidato_metrics['patrones']
            antipattern_count = sum(len(v) for v in pattern_data.get('anti_patterns', {}).values())
            pattern_count = sum(len(v) for v in pattern_data.get('design_patterns', {}).values())
            
            if antipattern_count > 0:
                # Penalización progresiva por anti-patrones
                antipattern_penalty = min(15, antipattern_count * 2)
                adjusted_score -= antipattern_penalty
            
            if pattern_count > 3:
                # Bonus por uso de patrones de diseño
                pattern_bonus = min(5, pattern_count * 0.5)
                adjusted_score += pattern_bonus
        
        # Factor 6: Balance entre todas las métricas
        min_score = min(category_scores.values()) if category_scores else 0
        max_score = max(category_scores.values()) if category_scores else 0
        balance_factor = 1.0
        
        if max_score - min_score > 50:
            # Gran disparidad entre categorías
            balance_factor = 0.95
        elif max_score - min_score < 20:
            # Muy balanceado
            balance_factor = 1.05
        
        adjusted_score *= balance_factor
        
        # Aplicar bonus y penalizaciones finales
        adjusted_score = adjusted_score + excellence_bonus - deficiency_penalty
        
        # Asegurar que el score esté en el rango válido
        return max(0, min(100, adjusted_score))
    
    def _calculate_complexity_factor(self, size_ratio: float, empresa_files: int, 
                                   candidato_files: int) -> float:
        """Calcula factor de complejidad basado en tamaño de proyectos"""
        if size_ratio < 0.2:
            # Proyectos muy diferentes en tamaño
            return 0.85
        elif size_ratio < 0.5:
            # Diferencia moderada
            return 0.92
        elif size_ratio > 0.8:
            # Tamaños similares
            if empresa_files > 50 and candidato_files > 50:
                # Ambos proyectos grandes
                return 1.05
            else:
                return 1.02
        return 1.0
    
    def _apply_adjustments(self, base_score: float, language_overlap: Dict[str, Any],
                          empresa_metrics: Dict[str, Any], 
                          candidato_metrics: Dict[str, Any]) -> float:
        """Versión simplificada para compatibilidad"""
        return self._apply_multi_factor_adjustments(
            base_score, language_overlap, empresa_metrics, 
            candidato_metrics, {}
        )
    
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
            'modularidad': {
                'title': 'Mejorar modularidad',
                'description': 'Organice mejor el código en módulos y componentes',
                'tips': ['Separe responsabilidades en diferentes módulos',
                        'Evite archivos muy grandes',
                        'Use principios SOLID']
            },
            'complejidad': {
                'title': 'Reducir complejidad',
                'description': 'Simplifique el código para mejorar mantenibilidad',
                'tips': ['Divida funciones largas en más pequeñas',
                        'Reduzca niveles de anidación',
                        'Elimine código duplicado']
            },
            'manejo_errores': {
                'title': 'Mejorar manejo de errores',
                'description': 'Implemente mejor gestión de excepciones',
                'tips': ['Use excepciones específicas',
                        'Maneje todos los casos de error',
                        'Registre errores apropiadamente']
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
            },
            'consistencia_estilo': {
                'title': 'Mejorar consistencia de estilo',
                'description': 'Mantenga un estilo de código uniforme',
                'tips': ['Use un linter o formatter',
                        'Siga la guía de estilo del lenguaje',
                        'Sea consistente con indentación y espaciado']
            },
            'patrones': {
                'title': 'Mejorar uso de patrones de diseño',
                'description': 'Aplique patrones de diseño apropiados y evite anti-patrones',
                'tips': ['Estudie los patrones usados en la empresa',
                        'Elimine código god class y spaghetti',
                        'Use patrones apropiados para cada problema']
            },
            'rendimiento': {
                'title': 'Optimizar rendimiento',
                'description': 'Mejore la eficiencia del código',
                'tips': ['Evite loops anidados innecesarios',
                        'Optimice consultas a base de datos',
                        'Use estructuras de datos apropiadas']
            },
            'comentarios': {
                'title': 'Mejorar calidad de comentarios',
                'description': 'Escriba comentarios más útiles y mantenga ratio apropiado',
                'tips': ['Explique el "por qué", no el "qué"',
                        'Mantenga comentarios actualizados',
                        'Resuelva TODOs y FIXMEs pendientes']
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