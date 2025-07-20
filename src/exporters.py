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

from typing import Dict, Any, List
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

                # Nuevas métricas: Patrones, Rendimiento y Comentarios
                f.write("\n" + "=" * 80 + "\n")
                f.write("ANÁLISIS AVANZADO\n")
                f.write("=" * 80 + "\n\n")
                
                # Análisis de Patrones
                if 'patrones' in metricas['repos'].get('empresa', {}) or 'patrones' in metricas['repos'].get('candidato', {}):
                    f.write("PATRONES DE DISEÑO Y ANTI-PATRONES\n")
                    f.write("-" * 35 + "\n\n")
                    
                    empresa_patterns = metricas['repos'].get('empresa', {}).get('patrones', {})
                    candidato_patterns = metricas['repos'].get('candidato', {}).get('patrones', {})
                    
                    # Comparar patrones de diseño
                    f.write("Patrones de Diseño Detectados:\n")
                    all_patterns = set()
                    if empresa_patterns:
                        all_patterns.update(empresa_patterns.get('design_patterns', {}).keys())
                    if candidato_patterns:
                        all_patterns.update(candidato_patterns.get('design_patterns', {}).keys())
                    
                    for pattern in sorted(all_patterns):
                        emp_count = len(empresa_patterns.get('design_patterns', {}).get(pattern, []))
                        cand_count = len(candidato_patterns.get('design_patterns', {}).get(pattern, []))
                        f.write(f"  • {pattern.title()}: Empresa: {emp_count}, Candidato: {cand_count}\n")
                    
                    # Anti-patrones
                    f.write("\nAnti-patrones Detectados:\n")
                    all_antipatterns = set()
                    if empresa_patterns:
                        all_antipatterns.update(empresa_patterns.get('anti_patterns', {}).keys())
                    if candidato_patterns:
                        all_antipatterns.update(candidato_patterns.get('anti_patterns', {}).keys())
                    
                    for antipattern in sorted(all_antipatterns):
                        emp_count = len(empresa_patterns.get('anti_patterns', {}).get(antipattern, []))
                        cand_count = len(candidato_patterns.get('anti_patterns', {}).get(antipattern, []))
                        f.write(f"  • {antipattern.replace('_', ' ').title()}: Empresa: {emp_count}, Candidato: {cand_count}\n")
                    
                    # Scores
                    emp_score = empresa_patterns.get('pattern_score', 0) if empresa_patterns else 0
                    cand_score = candidato_patterns.get('pattern_score', 0) if candidato_patterns else 0
                    f.write(f"\nScore de Patrones: Empresa: {emp_score:.1f}, Candidato: {cand_score:.1f}\n\n")
                
                # Análisis de Rendimiento
                if 'rendimiento' in metricas['repos'].get('empresa', {}) or 'rendimiento' in metricas['repos'].get('candidato', {}):
                    f.write("ANÁLISIS DE RENDIMIENTO\n")
                    f.write("-" * 22 + "\n\n")
                    
                    empresa_perf = metricas['repos'].get('empresa', {}).get('rendimiento', {})
                    candidato_perf = metricas['repos'].get('candidato', {}).get('rendimiento', {})
                    
                    # Problemas de rendimiento
                    f.write("Problemas de Rendimiento Detectados:\n")
                    all_issues = set()
                    if empresa_perf:
                        all_issues.update(empresa_perf.get('performance_issues', {}).keys())
                    if candidato_perf:
                        all_issues.update(candidato_perf.get('performance_issues', {}).keys())
                    
                    for issue in sorted(all_issues):
                        emp_count = len(empresa_perf.get('performance_issues', {}).get(issue, []))
                        cand_count = len(candidato_perf.get('performance_issues', {}).get(issue, []))
                        f.write(f"  • {issue.replace('_', ' ').title()}: Empresa: {emp_count}, Candidato: {cand_count}\n")
                    
                    # Scores
                    emp_score = empresa_perf.get('performance_score', 0) if empresa_perf else 0
                    cand_score = candidato_perf.get('performance_score', 0) if candidato_perf else 0
                    f.write(f"\nScore de Rendimiento: Empresa: {emp_score:.1f}, Candidato: {cand_score:.1f}\n\n")
                
                # Análisis de Comentarios
                if 'comentarios' in metricas['repos'].get('empresa', {}) or 'comentarios' in metricas['repos'].get('candidato', {}):
                    f.write("ANÁLISIS DE COMENTARIOS Y DOCUMENTACIÓN\n")
                    f.write("-" * 38 + "\n\n")
                    
                    empresa_comments = metricas['repos'].get('empresa', {}).get('comentarios', {})
                    candidato_comments = metricas['repos'].get('candidato', {}).get('comentarios', {})
                    
                    # Métricas de comentarios
                    f.write("Métricas de Comentarios:\n")
                    emp_metrics = empresa_comments.get('comment_metrics', {}) if empresa_comments else {}
                    cand_metrics = candidato_comments.get('comment_metrics', {}) if candidato_comments else {}
                    
                    f.write(f"  • Ratio de comentarios: Empresa: {emp_metrics.get('comment_ratio', 0):.1f}%, Candidato: {cand_metrics.get('comment_ratio', 0):.1f}%\n")
                    f.write(f"  • Cobertura de documentación: Empresa: {emp_metrics.get('documentation_coverage', 0):.1f}%, Candidato: {cand_metrics.get('documentation_coverage', 0):.1f}%\n")
                    
                    # Marcadores
                    f.write("\nMarcadores Encontrados:\n")
                    all_markers = set()
                    if empresa_comments:
                        all_markers.update(empresa_comments.get('markers', {}).keys())
                    if candidato_comments:
                        all_markers.update(candidato_comments.get('markers', {}).keys())
                    
                    for marker in sorted(all_markers):
                        emp_count = len(empresa_comments.get('markers', {}).get(marker, []))
                        cand_count = len(candidato_comments.get('markers', {}).get(marker, []))
                        f.write(f"  • {marker.upper()}: Empresa: {emp_count}, Candidato: {cand_count}\n")
                    
                    # Scores
                    emp_score = empresa_comments.get('comment_score', 0) if empresa_comments else 0
                    cand_score = candidato_comments.get('comment_score', 0) if candidato_comments else 0
                    f.write(f"\nScore de Comentarios: Empresa: {emp_score:.1f}, Candidato: {cand_score:.1f}\n\n")

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
                # Si tenemos análisis de empatía, usar el dashboard con Bootstrap
                if 'empathy_analysis' in metricas:
                    template = env.get_template('dashboard_bootstrap.html')
                else:
                    # Mantener compatibilidad con formato antiguo
                    template = env.get_template('dashboard.html')
            else:
                # Usar siempre el dashboard Bootstrap para HTML
                if 'empathy_analysis' in metricas:
                    template = env.get_template('dashboard_bootstrap.html')
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

    def exportar_equipo(self, resultados_equipo: Dict[str, Any], timestamp: str) -> None:
        """Genera un reporte especial para análisis de equipo."""
        try:
            archivo_salida = os.path.join('export', f"equipo_{timestamp}.html")
            
            # Preparar datos para el template
            candidatos_ordenados = sorted(
                resultados_equipo['candidatos'].items(),
                key=lambda x: x[1]['empathy_score'],
                reverse=True
            )
            
            # Crear resumen comparativo
            comparacion = []
            for nombre, datos in candidatos_ordenados:
                comparacion.append({
                    'nombre': nombre,
                    'score': datos['empathy_score'],
                    'nivel': datos['empathy_analysis']['interpretation']['level'],
                    'color': datos['empathy_analysis']['interpretation']['color'],
                    'recomendacion': datos['empathy_analysis']['interpretation']['recommendation'],
                    'fortalezas': [s for s in datos['empathy_analysis']['detailed_analysis']['strengths'] if s['score'] >= 80],
                    'debilidades': [s for s in datos['empathy_analysis']['detailed_analysis']['weaknesses'] if s['score'] < 60],
                    'lenguajes': datos['analisis']['metadata'].get('lenguajes_analizados', []),
                    'category_scores': datos['empathy_analysis']['category_scores'],
                    'duplicacion': datos['analisis'].get('duplicacion', {}),
                    'dependencias': datos['analisis'].get('dependencias', {}),
                    'patrones': datos['analisis'].get('patrones', {}),
                    'rendimiento': datos['analisis'].get('rendimiento', {}),
                    'comentarios': datos['analisis'].get('comentarios', {}),
                    'metadata': datos['analisis']['metadata']
                })
            
            # Generar HTML personalizado para equipo
            html_content = self._generar_html_equipo(
                resultados_equipo['empresa'],
                comparacion,
                timestamp
            )
            
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # También generar JSON para análisis posterior
            json_file = os.path.join('export', f"equipo_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(resultados_equipo, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Reporte de equipo generado: {archivo_salida}")
            
        except Exception as e:
            logger.error(f"Error generando reporte de equipo: {str(e)}")
            raise
    
    def _generar_html_equipo(self, empresa_data: Dict, candidatos: List[Dict], timestamp: str) -> str:
        """Genera HTML personalizado para reporte de equipo con información detallada."""
        
        # Preparar datos para gráficos
        categorias = ['nombres', 'documentacion', 'modularidad', 'complejidad', 'manejo_errores', 'pruebas', 'seguridad', 'consistencia_estilo']
        categorias_labels = [cat.replace('_', ' ').title() for cat in categorias]
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de Equipo - Code Empathizer</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: #000000;
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .empresa-info {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }}
        
        .empresa-info h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        
        .chart-section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        
        .candidato-card {{
            background: #f8f9fa;
            padding: 30px;
            margin: 20px 0;
            border-radius: 10px;
            border-left: 5px solid #333;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }}
        
        .candidato-card.top {{
            border-left-color: #000;
            background: #f0f0f0;
        }}
        
        .candidato-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .candidato-nombre {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .candidato-score {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        
        .metricas-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .metrica-item {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        
        .metrica-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        
        .metrica-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        
        .fortalezas-debilidades {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        
        .lista-items {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
        
        .lista-items h4 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .lista-items ul {{
            list-style: none;
            padding: 0;
        }}
        
        .lista-items li {{
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .lista-items li:last-child {{
            border-bottom: none;
        }}
        
        .score-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 10px;
            background: #e0e0e0;
            color: #333;
        }}
        
        .lenguajes {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        
        .lenguaje-tag {{
            background: #e0e0e0;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        .posicion {{
            display: inline-block;
            width: 50px;
            height: 50px;
            background: #333;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 50px;
            font-weight: bold;
            font-size: 1.2em;
            margin-right: 15px;
        }}
        
        .posicion.gold {{ background: #FFD700; color: #333; }}
        .posicion.silver {{ background: #C0C0C0; color: #333; }}
        .posicion.bronze {{ background: #CD7F32; color: white; }}
        
        .info-adicional {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .info-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
        
        .info-card h5 {{
            color: #666;
            margin-bottom: 10px;
            font-size: 1em;
            text-transform: uppercase;
        }}
        
        .info-card p {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        
        .comparacion-tabla {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
            position: sticky;
            top: 0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px 0;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Análisis de Equipo</h1>
            <p>Evaluación comparativa de candidatos</p>
            <p style="margin-top: 10px; opacity: 0.8;">Generado el {self.format_date(timestamp)}</p>
        </div>
        
        <div class="empresa-info">
            <h2>Empresa de Referencia</h2>
            <p><strong>Repositorio:</strong> {empresa_data['metadata']['nombre']}</p>
            <p><strong>URL:</strong> <a href="{empresa_data['metadata']['url']}" target="_blank">{empresa_data['metadata']['url']}</a></p>
            <p><strong>Lenguaje Principal:</strong> {empresa_data['metadata']['lenguaje_principal']}</p>
            <p><strong>Archivos Analizados:</strong> {empresa_data['metadata']['archivos_analizados']}</p>
            <p><strong>Tamaño:</strong> {empresa_data['metadata']['tamano_kb']} KB</p>
        </div>
        
        <!-- Gráfico Comparativo -->
        <div class="chart-section">
            <h2>Comparación Visual de Candidatos</h2>
            <div class="chart-container">
                <canvas id="comparisonChart"></canvas>
            </div>
        </div>
        
        <!-- Tabla Comparativa -->
        <div class="comparacion-tabla">
            <h2>Tabla Comparativa Detallada</h2>
            <table>
                <thead>
                    <tr>
                        <th>Métrica</th>
"""
        
        # Headers de candidatos
        for candidato in candidatos:
            html += f"<th>{candidato['nombre']}</th>"
        
        html += """
                    </tr>
                </thead>
                <tbody>
"""
        
        # Filas de métricas
        for categoria in categorias:
            html += f"<tr><td><strong>{categoria.replace('_', ' ').title()}</strong></td>"
            for candidato in candidatos:
                score = candidato['category_scores'].get(categoria, 0)
                html += f"<td>{score:.1f}%</td>"
            html += "</tr>"
        
        # Agregar métricas adicionales
        html += """
                    <tr><td><strong>Duplicación de Código</strong></td>
"""
        for candidato in candidatos:
            dup = candidato.get('duplicacion', {})
            porcentaje = dup.get('porcentaje_global', 'N/A')
            html += f"<td>{porcentaje}%</td>" if porcentaje != 'N/A' else "<td>N/A</td>"
        
        html += """
                    </tr>
                    <tr><td><strong>Dependencias Totales</strong></td>
"""
        for candidato in candidatos:
            deps = candidato.get('dependencias', {})
            total = deps.get('total_dependencies', 'N/A')
            html += f"<td>{total}</td>"
        
        html += """
                    </tr>
                    <tr><td><strong>Score de Patrones</strong></td>
"""
        for candidato in candidatos:
            patrones = candidato.get('patrones', {})
            score = patrones.get('pattern_score', 'N/A')
            html += f"<td>{score:.1f}</td>" if score != 'N/A' else "<td>N/A</td>"
        
        html += """
                    </tr>
                    <tr><td><strong>Score de Rendimiento</strong></td>
"""
        for candidato in candidatos:
            perf = candidato.get('rendimiento', {})
            score = perf.get('performance_score', 'N/A')
            html += f"<td>{score:.1f}</td>" if score != 'N/A' else "<td>N/A</td>"
        
        html += """
                    </tr>
                    <tr><td><strong>Score de Comentarios</strong></td>
"""
        for candidato in candidatos:
            comments = candidato.get('comentarios', {})
            score = comments.get('comment_score', 'N/A')
            html += f"<td>{score:.1f}</td>" if score != 'N/A' else "<td>N/A</td>"
        
        html += """
                    </tr>
                    <tr><td><strong>Archivos Analizados</strong></td>
"""
        for candidato in candidatos:
            archivos = candidato['metadata'].get('archivos_analizados', 'N/A')
            html += f"<td>{archivos}</td>"
        
        html += """
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- Detalles de cada candidato -->
        <h2 style="text-align: center; margin: 30px 0;">Análisis Detallado por Candidato</h2>
"""
        
        # Agregar cada candidato con información detallada
        for i, candidato in enumerate(candidatos):
            posicion_class = ''
            if i == 0:
                posicion_class = 'gold'
            elif i == 1:
                posicion_class = 'silver'
            elif i == 2:
                posicion_class = 'bronze'
            
            card_class = 'candidato-card'
            if i == 0:
                card_class += ' top'
            
            html += f"""
            <div class="{card_class}">
                <div class="candidato-header">
                    <div>
                        <span class="posicion {posicion_class}">{i + 1}</span>
                        <span class="candidato-nombre">{candidato['nombre']}</span>
                    </div>
                    <div class="candidato-score" style="color: {candidato['color']}">
                        {candidato['score']:.1f}%
                    </div>
                </div>
                
                <p><strong>Nivel:</strong> {candidato['nivel']}</p>
                <p><strong>Recomendación:</strong> {candidato['recomendacion']}</p>
                <p><strong>URL:</strong> <a href="{candidato['metadata']['url']}" target="_blank">{candidato['metadata']['url']}</a></p>
                
                <!-- Métricas principales -->
                <div class="metricas-grid">
                    <div class="metrica-item">
                        <div class="metrica-label">Documentación</div>
                        <div class="metrica-value">{candidato['category_scores']['documentacion']:.1f}%</div>
                    </div>
                    <div class="metrica-item">
                        <div class="metrica-label">Pruebas</div>
                        <div class="metrica-value">{candidato['category_scores']['pruebas']:.1f}%</div>
                    </div>
                    <div class="metrica-item">
                        <div class="metrica-label">Complejidad</div>
                        <div class="metrica-value">{candidato['category_scores']['complejidad']:.1f}%</div>
                    </div>
                    <div class="metrica-item">
                        <div class="metrica-label">Seguridad</div>
                        <div class="metrica-value">{candidato['category_scores']['seguridad']:.1f}%</div>
                    </div>
                </div>
                
                <!-- Fortalezas y Debilidades -->
                <div class="fortalezas-debilidades">
                    <div class="lista-items">
                        <h4>Fortalezas ({len(candidato["fortalezas"])})</h4>
                        <ul>
"""
            
            # Listar fortalezas
            for fortaleza in candidato['fortalezas'][:5]:  # Mostrar máximo 5
                html += f"""
                            <li>
                                {fortaleza['category'].replace('_', ' ').title()}
                                <span class="score-badge">{fortaleza['score']:.1f}%</span>
                            </li>
"""
            
            html += """
                        </ul>
                    </div>
                    <div class="lista-items">
                        <h4>Áreas de Mejora ({len(candidato["debilidades"])})</h4>
                        <ul>
"""
            
            # Listar debilidades
            for debilidad in candidato['debilidades'][:5]:  # Mostrar máximo 5
                html += f"""
                            <li>
                                {debilidad['category'].replace('_', ' ').title()}
                                <span class="score-badge">{debilidad['score']:.1f}%</span>
                            </li>
"""
            
            html += """
                        </ul>
                    </div>
                </div>
                
                <!-- Información adicional -->
                <div class="info-adicional">
"""
            
            # Duplicación
            if candidato.get('duplicacion'):
                dup = candidato['duplicacion']
                html += f"""
                    <div class="info-card">
                        <h5>Duplicación de Código</h5>
                        <p>{dup.get('porcentaje_global', 'N/A')}%</p>
                        <small>{dup.get('bloques_encontrados', 0)} bloques duplicados</small>
                    </div>
"""
            
            # Dependencias
            if candidato.get('dependencias'):
                deps = candidato['dependencias']
                html += f"""
                    <div class="info-card">
                        <h5>Dependencias</h5>
                        <p>{deps.get('total_dependencies', 0)}</p>
                        <small>{deps.get('external_dependencies', 0)} externas</small>
                    </div>
"""
            
            # Archivos
            html += f"""
                    <div class="info-card">
                        <h5>Archivos Analizados</h5>
                        <p>{candidato['metadata']['archivos_analizados']}</p>
                        <small>{candidato['metadata']['tamano_kb']} KB total</small>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <strong>Lenguajes:</strong>
                    <div class="lenguajes">
                        {''.join([f'<span class="lenguaje-tag">{lang}</span>' for lang in candidato['lenguajes']])}
                    </div>
                </div>
            </div>
"""
        
        html += """
        <div class="footer">
            <p>Generado por Code Empathizer v2.0 - R. Benítez | 
            <a href="https://github.com/686f6c61/Repo-Code-Empathizer">GitHub</a></p>
        </div>
    </div>
    
    <script>
        // Gráfico comparativo
        const ctx = document.getElementById('comparisonChart').getContext('2d');
        
        const data = {
            labels: """ + str(categorias_labels) + """,
            datasets: [
"""
        
        # Agregar datasets para cada candidato
        colors = ['rgba(0, 0, 0, 0.8)', 'rgba(100, 100, 100, 0.8)', 'rgba(150, 150, 150, 0.8)', 'rgba(200, 200, 200, 0.8)']
        for idx, candidato in enumerate(candidatos):
            scores = [candidato['category_scores'].get(cat, 0) for cat in categorias]
            html += f"""
                {{
                    label: '{candidato['nombre']}',
                    data: {scores},
                    backgroundColor: '{colors[idx % len(colors)]}',
                    borderColor: '{colors[idx % len(colors)]}',
                    borderWidth: 2
                }},
"""
        
        html += """
            ]
        };
        
        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Comparación de Métricas por Categoría'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
        return html