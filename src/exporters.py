"""
Módulo de exportación de resultados.

Provee funcionalidad para exportar los resultados del análisis de empatía
en múltiples formatos: TXT, JSON y HTML (reporte y dashboard).

Classes:
    Exporter: Clase principal para exportar resultados.

Author: R. Benítez
Version: 2.0.0
License: MIT
"""

from typing import Dict, Any
import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)

class Exporter:
    """
    Gestor de exportación de resultados en múltiples formatos.
    
    Soporta exportación a texto plano, JSON y HTML con plantillas
    personalizadas para visualización interactiva.
    """
    def format_date(self, value: Any) -> str:
        """
        Filtro Jinja2 para formatear fechas.
        
        Args:
            value: Fecha en formato ISO string o datetime object.
        
        Returns:
            str: Fecha formateada como DD/MM/YYYY HH:MM:SS.
        """
        try:
            if isinstance(value, str):
                date = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                date = value
            return date.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            return value

    def exportar_txt(self, metricas: Dict[str, Any], timestamp: str) -> None:
        """
        Exporta los resultados a archivo de texto plano.
        
        Genera un informe detallado con formato de tabla que incluye:
        - Información de repositorios
        - Puntuación de empatía
        - Métricas por categoría
        - Recomendaciones
        
        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.
        
        Raises:
            IOError: Si no se puede escribir el archivo.
        """
        try:
            os.makedirs('export', exist_ok=True)
            output_path = f'export/reporte_{timestamp}.txt'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Encabezado
                f.write("=" * 80 + "\n")
                f.write("ANÁLISIS DE EMPATÍA EMPRESA-CANDIDATO\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

                # Verificar estructura de métricas
                if not metricas or 'repos' not in metricas:
                    f.write("❌ No hay datos para analizar\n")
                    return

                # Información de repositorios
                f.write("-" * 80 + "\n")
                f.write("RESUMEN DE REPOSITORIOS\n")
                f.write("-" * 80 + "\n\n")

                for repo_tipo, repo_data in metricas['repos'].items():
                    if not repo_data:
                        continue
                        
                    label = "EMPRESA (Master)" if repo_tipo == "empresa" else "CANDIDATO"
                    f.write(f"📂 {label}\n")
                    f.write("=" * 50 + "\n")
                    
                    # Metadata
                    meta = repo_data.get('metadata', {})
                    if meta:
                        f.write(f"• Repositorio: {meta.get('nombre', 'N/A')}\n")
                        f.write(f"• URL: {meta.get('url', 'N/A')}\n")
                        f.write(f"• Descripción: {meta.get('descripcion', 'N/A')}\n")
                        f.write(f"• Lenguaje principal: {meta.get('lenguaje_principal', 'N/A')}\n")
                        if 'lenguajes_analizados' in meta:
                            f.write(f"• Lenguajes analizados: {', '.join(meta['lenguajes_analizados'])}\n")
                        f.write(f"• Archivos analizados: {meta.get('archivos_analizados', 0)}\n")
                        f.write(f"• Tamaño: {meta.get('tamano_kb', 0)} KB\n\n")

                # Análisis de empatía si existe
                if 'empathy_analysis' in metricas:
                    analysis = metricas['empathy_analysis']
                    f.write("\n" + "=" * 80 + "\n")
                    f.write("RESULTADO DEL ANÁLISIS DE EMPATÍA\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # Puntuación principal
                    score = analysis['empathy_score']
                    interpretation = analysis['interpretation']
                    f.write(f"📊 PUNTUACIÓN DE EMPATÍA: {score}%\n")
                    f.write(f"   Nivel: {interpretation['level']}\n")
                    f.write(f"   {interpretation['description']}\n")
                    f.write(f"   Recomendación: {interpretation['recommendation']}\n\n")
                    
                    # Puntuaciones por categoría
                    f.write("📈 Puntuaciones por Categoría:\n")
                    f.write("-" * 40 + "\n")
                    for categoria, score in analysis['category_scores'].items():
                        emoji = "✅" if score >= 80 else "🟡" if score >= 60 else "🔴"
                        f.write(f"  • {categoria.replace('_', ' ').title()}: {score:.1f}% {emoji}\n")
                    
                    # Coincidencia de lenguajes
                    lang_overlap = analysis['language_overlap']
                    f.write(f"\n🔤 Coincidencia de Lenguajes: {lang_overlap['score']:.1f}%\n")
                    if lang_overlap['missing']:
                        f.write(f"  ⚠️  Lenguajes faltantes del candidato: {', '.join(lang_overlap['missing'])}\n")
                    
                    # Recomendaciones
                    if analysis['recommendations']:
                        f.write("\n💡 Recomendaciones para el Candidato:\n")
                        f.write("-" * 40 + "\n")
                        for i, rec in enumerate(analysis['recommendations'], 1):
                            f.write(f"\n{i}. {rec['title']}\n")
                            f.write(f"   {rec['description']}\n")
                            if 'tips' in rec:
                                for tip in rec['tips']:
                                    f.write(f"   - {tip}\n")
                
                # Análisis comparativo detallado por categoría
                f.write("\n" + "=" * 80 + "\n")
                f.write("MÉTRICAS DETALLADAS POR CATEGORÍA\n")
                f.write("=" * 80 + "\n\n")

                categorias = [
                    "nombres", "documentacion", "modularidad", "complejidad",
                    "manejo_errores", "pruebas", "consistencia_estilo", "seguridad"
                ]

                for categoria in categorias:
                    f.write(f"\n{categoria.upper()}\n")
                    f.write("-" * len(categoria) + "\n\n")
                    
                    # Tabla comparativa
                    f.write("┌" + "─" * 30 + "┬" + "─" * 15 + "┬" + "─" * 15 + "┐\n")
                    f.write("│ Métrica" + " " * 23 + "│ Empresa" + " " * 7 + "│ Candidato" + " " * 5 + "│\n")
                    f.write("├" + "─" * 30 + "┼" + "─" * 15 + "┼" + "─" * 15 + "┤\n")
                    
                    # Valores de cada repositorio
                    empresa_data = metricas['repos'].get('empresa', {}).get(categoria, {})
                    candidato_data = metricas['repos'].get('candidato', {}).get(categoria, {})
                    
                    # Obtener todas las métricas únicas de ambos repos
                    all_metrics = set(empresa_data.keys()) | set(candidato_data.keys())
                    
                    for metrica in sorted(all_metrics):
                        empresa_val = f"{empresa_data.get(metrica, 0):.3f}"
                        candidato_val = f"{candidato_data.get(metrica, 0):.3f}"
                        metrica_name = metrica.replace('_', ' ').title()
                        
                        # Alinear valores
                        f.write(f"│ {metrica_name:<30}")
                        f.write(f"│ {empresa_val:>15}")
                        f.write(f"│ {candidato_val:>15}│\n")
                    
                    f.write("└" + "─" * 30 + "┴" + "─" * 15 + "┴" + "─" * 15 + "┘\n")
                    
                    # Diferencias
                    if 'diferencias' in metricas and categoria in metricas['diferencias']:
                        f.write("\nDiferencias:\n")
                        for metrica, diff in metricas['diferencias'][categoria].items():
                            signo = "+" if diff > 0 else ""
                            f.write(f"• {metrica.replace('_', ' ').title()}: {signo}{diff:.3f}\n")
                    f.write("\n")

                # Conclusión basada en análisis de empatía
                if 'empathy_analysis' in metricas:
                    f.write("\n" + "=" * 80 + "\n")
                    f.write("CONCLUSIÓN Y DECISIÓN DE CONTRATACIÓN\n")
                    f.write("=" * 80 + "\n\n")
                    
                    analysis = metricas['empathy_analysis']
                    score = analysis['empathy_score']
                    interpretation = analysis['interpretation']
                    
                    f.write(f"📊 Puntuación Final de Empatía: {score}%\n")
                    f.write(f"🏆 Nivel: {interpretation['level']}\n")
                    f.write(f"📝 Evaluación: {interpretation['description']}\n")
                    f.write(f"✅ Decisión: {interpretation['recommendation']}\n\n")
                    
                    # Fortalezas y debilidades
                    if 'detailed_analysis' in analysis:
                        detailed = analysis['detailed_analysis']
                        
                        if detailed.get('strengths'):
                            f.write("💪 FORTALEZAS DEL CANDIDATO:\n")
                            for strength in detailed['strengths']:
                                f.write(f"  • {strength['category'].replace('_', ' ').title()}: {strength['score']:.1f}%\n")
                            f.write("\n")
                        
                        if detailed.get('weaknesses'):
                            f.write("📋 ÁREAS DE MEJORA:\n")
                            for weakness in detailed['weaknesses']:
                                f.write(f"  • {weakness['category'].replace('_', ' ').title()}: {weakness['score']:.1f}%\n")
                            f.write("\n")
                
        except Exception as e:
            logger.error(f"Error generando reporte TXT: {str(e)}")
            raise

    def exportar_json(self, metricas: Dict[str, Any], timestamp: str) -> None:
        """
        Exporta los resultados a formato JSON.
        
        Útil para procesamiento posterior o integración con otras
        herramientas.
        
        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.
        
        Raises:
            IOError: Si no se puede escribir el archivo.
        """
        try:
            os.makedirs('export', exist_ok=True)
            output_path = f'export/reporte_{timestamp}.json'
            
            # Añadir timestamp al objeto de métricas
            datos_export = {
                "timestamp": timestamp,
                "metricas": metricas
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(datos_export, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error generando reporte JSON: {str(e)}")
            raise

    def exportar_html(self, metricas: Dict[str, Any], timestamp: str, dashboard: bool = False) -> None:
        """
        Exporta los resultados a formato HTML.
        
        Puede generar un reporte estático o un dashboard interactivo
        con gráficos usando Chart.js.
        
        Args:
            metricas: Diccionario con los resultados del análisis.
            timestamp: Marca de tiempo para el nombre del archivo.
            dashboard: Si True, genera dashboard interactivo.
        
        Raises:
            IOError: Si no se puede escribir el archivo.
            TemplateNotFound: Si no encuentra las plantillas HTML.
        """
        try:
            # Para mantener compatibilidad, mapear empresa/candidato a A/B si es necesario
            if 'empresa' in metricas.get('repos', {}):
                # Nuevo formato empresa/candidato
                pass
            elif 'A' in metricas.get('repos', {}):
                # Formato antiguo A/B - mantener compatibilidad
                pass
            else:
                logger.error("Formato de métricas no reconocido")

            # Obtener la ruta del directorio de templates
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_dir = os.path.join(root_dir, "templates")
            
            env = Environment(loader=FileSystemLoader(template_dir))
            env.filters['date'] = self.format_date
            env.filters['format_date'] = self.format_date

            # Seleccionar plantilla según el tipo y formato de datos
            if dashboard:
                # Si tenemos análisis de empatía, usar el nuevo dashboard
                if 'empathy_analysis' in metricas:
                    template = env.get_template('dashboard_empathy.html')
                else:
                    # Mantener compatibilidad con formato antiguo
                    template = env.get_template('dashboard.html')
            else:
                template = env.get_template('informe_template.html')
            
            datos_template = {
                "titulo": "Análisis de Empatía de Código",
                "fecha_generacion": timestamp,
                "timestamp": timestamp,  # Añadido para compatibilidad con las plantillas
                "metricas": metricas,
                "categorias": [
                    "nombres", "complejidad", "modularidad", "documentacion",
                    "manejo_errores", "pruebas", "consistencia_estilo", "seguridad"
                ]
            }
            
            html_content = template.render(**datos_template)
            
            os.makedirs('export', exist_ok=True)
            output_path = f'export/reporte_{timestamp}.html'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            logger.error(f"Error generando reporte HTML: {str(e)}")
            raise