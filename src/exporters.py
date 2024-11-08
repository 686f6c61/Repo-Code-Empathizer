from typing import Dict, Any
import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)

class Exporter:
    @staticmethod
    def format_date(value):
        """Filtro personalizado para formatear fechas"""
        try:
            if isinstance(value, str):
                date = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                date = value
            return date.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            return value

    def exportar_txt(self, metricas: Dict[str, Any], timestamp: str) -> None:
        """Exporta los resultados a TXT en formato de informe comparativo"""
        try:
            os.makedirs('export', exist_ok=True)
            output_path = f'export/reporte_{timestamp}.txt'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Encabezado
                f.write("=" * 80 + "\n")
                f.write("ANÁLISIS COMPARATIVO DE EMPATÍA DE CÓDIGO\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Fecha de generación: {timestamp}\n\n")

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
                        
                    f.write(f"📂 REPOSITORIO {repo_tipo.upper()}\n")
                    f.write("=" * 50 + "\n")
                    
                    # Metadata
                    meta = repo_data.get('metadata', {})
                    if meta:
                        f.write(f"• Nombre: {meta.get('nombre', 'N/A')}\n")
                        f.write(f"• URL: {meta.get('url', 'N/A')}\n")
                        f.write(f"• Descripción: {meta.get('descripcion', 'N/A')}\n")
                        f.write(f"• Fecha de creación: {meta.get('fecha_creacion', 'N/A')}\n")
                        f.write(f"• Último push: {meta.get('fecha_ultimo_push', 'N/A')}\n")
                        f.write(f"• Lenguaje principal: {meta.get('lenguaje_principal', 'N/A')}\n")
                        f.write(f"• Tamaño: {meta.get('tamano_kb', 0)} KB\n\n")

                # Análisis comparativo por categoría
                f.write("\n" + "=" * 80 + "\n")
                f.write("ANÁLISIS COMPARATIVO POR CATEGORÍA\n")
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
                    f.write("│ Métrica" + " " * 23 + "│ Master" + " " * 8 + "│ Comparado" + " " * 6 + "│\n")
                    f.write("├" + "─" * 30 + "┼" + "─" * 15 + "┼" + "─" * 15 + "┤\n")
                    
                    # Valores de cada repositorio
                    master_data = metricas['repos']['master'].get(categoria, {})
                    comp_data = metricas['repos']['comparado'].get(categoria, {})
                    
                    for metrica in master_data.keys():
                        master_val = f"{master_data.get(metrica, 0):.3f}"
                        comp_val = f"{comp_data.get(metrica, 0):.3f}"
                        metrica_name = metrica.replace('_', ' ').title()
                        
                        # Alinear valores
                        f.write(f"│ {metrica_name:<30}")
                        f.write(f"│ {master_val:>15}")
                        f.write(f"│ {comp_val:>15}│\n")
                    
                    f.write("└" + "─" * 30 + "┴" + "─" * 15 + "┴" + "─" * 15 + "┘\n")
                    
                    # Diferencias
                    if 'diferencias' in metricas and categoria in metricas['diferencias']:
                        f.write("\nDiferencias:\n")
                        for metrica, diff in metricas['diferencias'][categoria].items():
                            signo = "+" if diff > 0 else ""
                            f.write(f"• {metrica.replace('_', ' ').title()}: {signo}{diff:.3f}\n")
                    f.write("\n")

                # Conclusión
                f.write("\n" + "=" * 80 + "\n")
                f.write("CONCLUSIÓN\n")
                f.write("=" * 80 + "\n\n")
                
                # Calcular puntuación total
                master_total = sum(
                    sum(valores.values())
                    for categoria, valores in metricas['repos']['master'].items()
                    if isinstance(valores, dict) and categoria != 'metadata'
                )
                comp_total = sum(
                    sum(valores.values())
                    for categoria, valores in metricas['repos']['comparado'].items()
                    if isinstance(valores, dict) and categoria != 'metadata'
                )
                
                f.write(f"Puntuación total Master: {master_total:.2f}\n")
                f.write(f"Puntuación total Comparado: {comp_total:.2f}\n")
                diferencia = master_total - comp_total
                f.write(f"Diferencia total: {'+' if diferencia > 0 else ''}{diferencia:.2f}\n\n")
                
                # Recomendaciones
                f.write("RECOMENDACIONES\n")
                f.write("-" * 15 + "\n")
                for categoria in categorias:
                    if categoria in metricas['diferencias']:
                        diffs = metricas['diferencias'][categoria]
                        peores_metricas = sorted(diffs.items(), key=lambda x: x[1])[:3]
                        if peores_metricas:
                            f.write(f"\n• {categoria.title()}:\n")
                            for metrica, valor in peores_metricas:
                                if valor < 0:
                                    f.write(f"  - Mejorar {metrica.replace('_', ' ').lower()} ({valor:.3f})\n")
                
        except Exception as e:
            logger.error(f"Error generando reporte TXT: {str(e)}")
            raise

    def exportar_json(self, metricas: Dict[str, Any], timestamp: str) -> None:
        """Exporta los resultados a JSON"""
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

    def exportar_html(self, metricas: Dict[str, Any], timestamp: str) -> None:
        """Exporta los resultados a HTML"""
        try:
            # Calcular puntuaciones totales
            metricas['puntuacion_master'] = sum(
                sum(valores.values())
                for categoria, valores in metricas['repos']['master'].items()
                if isinstance(valores, dict) and categoria != 'metadata'
            )
            
            metricas['puntuacion_comparado'] = sum(
                sum(valores.values())
                for categoria, valores in metricas['repos']['comparado'].items()
                if isinstance(valores, dict) and categoria != 'metadata'
            )

            # Verificar estructura de métricas
            if not metricas or 'repos' not in metricas:
                logger.error("Estructura de métricas inválida")
                metricas = {
                    'repos': {
                        'master': {
                            'metadata': {
                                'nombre': 'N/A',
                                'url': '#',
                                'descripcion': 'No disponible',
                                'fecha_creacion': datetime.now().isoformat(),
                                'fecha_ultimo_push': datetime.now().isoformat(),
                                'lenguaje_principal': 'N/A',
                                'tamano_kb': 0
                            }
                        },
                        'comparado': {
                            'metadata': {
                                'nombre': 'N/A',
                                'url': '#',
                                'descripcion': 'No disponible',
                                'fecha_creacion': datetime.now().isoformat(),
                                'fecha_ultimo_push': datetime.now().isoformat(),
                                'lenguaje_principal': 'N/A',
                                'tamano_kb': 0
                            }
                        }
                    },
                    'diferencias': {}
                }

            # Asegurar que existan las claves necesarias
            for repo_tipo in ['master', 'comparado']:
                if repo_tipo not in metricas['repos'] or not metricas['repos'][repo_tipo]:
                    metricas['repos'][repo_tipo] = {
                        'metadata': {
                            'nombre': 'N/A',
                            'url': '#',
                            'descripcion': 'No disponible',
                            'fecha_creacion': datetime.now().isoformat(),
                            'fecha_ultimo_push': datetime.now().isoformat(),
                            'lenguaje_principal': 'N/A',
                            'tamano_kb': 0
                        }
                    }

            # Obtener la ruta del directorio de templates
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_dir = os.path.join(root_dir, "templates")
            
            env = Environment(loader=FileSystemLoader(template_dir))
            env.filters['date'] = self.format_date
            
            template = env.get_template('informe_template.html')
            
            datos_template = {
                "titulo": "Análisis de Empatía de Código",
                "fecha_generacion": timestamp,
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