# Repo Code Empathizer 🔍


## 📋 Descripción

Repo Code Empathizer es una herramienta de análisis estático que evalúa la "empatía" del código en repositorios. Analiza y compara diferentes métricas de calidad para ayudar a los desarrolladores a crear código más mantenible y comprensible.

## ✨ Características Principales

### 🔄 Análisis Comparativo
- Compara dos repositorios de GitHub simultáneamente
- Genera puntuaciones detalladas por categoría
- Identifica áreas de mejora específicas

### 📊 Formatos de Exportación
- **TXT**: Reportes simples y concisos
- **JSON**: Datos estructurados para análisis posterior
- **HTML**: Visualización interactiva detallada
- **Multi-formato**: Exportación simultánea en todos los formatos

### 🎯 Categorías de Análisis
1. 📝 **Nombres Descriptivos**
   - Evaluación de claridad
   - Consistencia en nomenclatura
   
2. 🔄 **Complejidad**
   - Análisis ciclomático
   - Niveles de anidación
   
3. 📦 **Modularidad**
   - Cohesión y acoplamiento
   - Organización del código
   
4. 📚 **Documentación**
   - Cobertura de docstrings
   - Calidad de comentarios

5. ⚠️ **Manejo de Errores**
   - Tratamiento de excepciones
   - Robustez del código

6. 🧪 **Pruebas**
   - Cobertura de tests
   - Calidad de assertions

7. 🎨 **Estilo**
   - Consistencia de formato

8. 🔒 **Seguridad**
   - Validación de entradas
   - Prácticas seguras

# 📊 Métricas y Cálculo de Empatía

### Grupos de KPIs

#### 1. 📝 Nombres
| KPI | Descripción | Cálculo |
|-----|-------------|----------|
| Descriptividad | Claridad de identificadores | Análisis de nombres (vars, funcs, clases) |
| Consistencia | Adherencia a convenciones | % nombres que siguen estándares |

#### 2. 📚 Documentación
| KPI | Descripción | Cálculo |
|-----|-------------|----------|
| Cobertura docstrings | % código documentado | `funciones_con_docstring / total_funciones` |
| Calidad docs | Completitud de documentación | Bonus por params, returns y ejemplos |

#### 3. 🧩 Modularidad
| KPI | Descripción | Cálculo |
|-----|-------------|----------|
| Funciones/archivo | Densidad de funciones | `total_funciones / total_archivos` |
| Clases/archivo | Densidad de clases | `total_clases / total_archivos` |
| Cohesión | Uso compartido de atributos | % métodos que comparten atributos |
| Acoplamiento | Dependencias externas | Penalización por imports y vars globales |

#### 4. 🔄 Complejidad
| KPI | Descripción | Cálculo |
|-----|-------------|----------|
| Ciclomática | Caminos de ejecución | +1 por cada: if, while, for, and, or |
| Anidación | Profundidad de estructuras | Penalización por niveles > 3 |
| Longitud funciones | Tamaño de funciones | Penalización por > 20 líneas |

#### 5. ⚠️ Manejo de Errores
| KPI | Descripción | Cálculo |
|-----|-------------|----------|
| Cobertura | Uso de try-except | `funcs_con_try_except / total_funcs` |
| Especificidad | Excepciones específicas | Penalización por except genéricos |
| Densidad | Bloques try-except | `total_try_except / total_funcs` |

#### 6. 🧪 Pruebas
| KPI | Descripción | Cálculo |
|-----|-------------|----------|
| Cobertura | Funciones con tests | `funcs_test / total_funcs` |
| Densidad asserts | Aserciones por test | `total_asserts / total_funcs_test` |
| Funciones test | Total de pruebas | Conteo de funciones `test_*` |

#### 7. 🔒 Seguridad
| KPI | Descripción | Cálculo |
|-----|-------------|----------|
| Validación entradas | Verificación de datos | `funcs_con_validacion / total_funcs` |
| Funciones peligrosas | Uso de eval, exec, etc. | Penalización por uso |
| Total validaciones | Cantidad de checks | Suma de todas las validaciones |

#### 8. 📏 Consistencia
| KPI | Descripción | Cálculo |
|-----|-------------|----------|
| Nombres | Convenciones de naming | `nombres_consistentes / total_nombres` |
| Espaciado | Indentación y formato | Análisis con pylint |
| Longitud líneas | Límite de caracteres | % líneas < 80 caracteres |

### 🎯 Cálculo de Empatía

La puntuación final de empatía se calcula como un promedio ponderado de todas las categorías:

```python
empatia = (
    nombres * 0.15 +
    documentacion * 0.15 +
    modularidad * 0.15 +
    complejidad * 0.15 +
    manejo_errores * 0.10 +
    pruebas * 0.10 +
    seguridad * 0.10 +
    consistencia * 0.10
)
```

Cada categoría se evalúa en una escala de 0 a 1, donde:
- 0.0-0.3: Necesita mejora significativa
- 0.3-0.6: Cumple estándares básicos
- 0.6-0.8: Buenas prácticas
- 0.8-1.0: Excelente empatía

## 📊 Resultados de Análisis

### Ejemplo de Métricas Reales

```json
{
  "nombres": {
    "descriptividad": 0.81          // Qué tan descriptivos son los nombres (0-1)
  },
  "documentacion": {
    "cobertura_docstrings": 0.25    // % de código documentado
  },
  "modularidad": {
    "funciones_por_archivo": 2.6,    // Promedio de funciones/archivo
    "clases_por_archivo": 0.0,       // Promedio de clases/archivo
    "cohesion_promedio": 0.0,        // Qué tan cohesionadas están las clases
    "acoplamiento_promedio": 0.4     // Nivel de dependencias entre módulos
  },
  "complejidad": {
    "complejidad_ciclomatica": 0.58, // Complejidad del código (mejor cerca de 1)
    "max_nivel_anidacion": 0.0,      // Profundidad máxima de anidación
    "longitud_promedio_funciones": 0.85 // Tamaño apropiado de funciones
  },
  "manejo_errores": {
    "cobertura_manejo_errores": 0.0,   // % código con manejo de errores
    "especificidad_excepciones": 0.0,   // Uso de excepciones específicas
    "densidad_try_except": 0.0          // Cantidad de bloques try-except
  },
  "pruebas": {
    "cobertura_pruebas": 0.0,          // % código cubierto por tests
    "densidad_asserts": 0.0,           // Cantidad de aserciones por test
    "funciones_test": 0.0              // Número de funciones de prueba
  },
  "seguridad": {
    "validacion_entradas": 0.0,        // Validación de inputs
    "uso_funciones_peligrosas": 1.2,   // Evita funciones inseguras
    "total_validaciones": 0.0          // Total de validaciones implementadas
  },
  "consistencia_estilo": {
    "consistencia_nombres": 0.67,      // Adherencia a convenciones de nombres
    "espaciado_consistente": 0.38,     // Formato consistente
    "longitud_lineas_consistente": 0.77 // Líneas de longitud apropiada
  }
}
```

### 📈 Interpretación de Resultados

#### Escala de Evaluación
- 🔴 0.0-0.3: Necesita mejora urgente
- 🟡 0.3-0.6: Cumple estándares mínimos
- 🟢 0.6-0.8: Buenas prácticas
- 🌟 0.8-1.0: Excelente implementación

#### Puntos Destacados
- **Nombres**: Excelente descriptividad (0.81)
- **Documentación**: Necesita mejora significativa (0.25)
- **Modularidad**: Buen balance de funciones por archivo (2.6)
- **Complejidad**: Mantenible y legible (0.58)
- **Seguridad**: Excelente evitación de funciones peligrosas (1.2)
- **Consistencia**: Buena adherencia a estándares de código (0.77)

#### Áreas de Mejora
1. 📚 Aumentar cobertura de documentación
2. ⚠️ Implementar manejo de errores
3. 🧪 Añadir pruebas unitarias
4. 🔒 Mejorar validación de entradas

### 🎯 Puntuación Final de Empatía

La puntuación se calcula ponderando cada categoría:

```python
empatia_final = (
    nombres * 0.15 +              # 0.81 * 0.15 = 0.122
    documentacion * 0.15 +        # 0.25 * 0.15 = 0.038
    modularidad * 0.15 +          # 0.40 * 0.15 = 0.060
    complejidad * 0.15 +          # 0.58 * 0.15 = 0.087
    manejo_errores * 0.10 +       # 0.00 * 0.10 = 0.000
    pruebas * 0.10 +             # 0.00 * 0.10 = 0.000
    seguridad * 0.10 +           # 1.20 * 0.10 = 0.120
    consistencia * 0.10          # 0.77 * 0.10 = 0.077
)                               # Total = 0.504 (Cumple estándares básicos)
``` 

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.8+
- Git
- Token de GitHub con permisos de lectura

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/686f6c61/code-empathizer.git
cd code-empathizer

# Configurar entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar token
cp .env.example .env
# Editar .env y añadir: GITHUB_TOKEN=tu_token_aquí
```

### Uso Básico

```bash
python3 src/main.py
```

## 📊 Ejemplos de Análisis

### Reporte HTML
![Ejemplo de Reporte](docs/images/report-example.png)

#
## 📁 Estructura del Proyecto

```
code-empathizer/
├── src/
│   ├── main.py           # Punto de entrada
│   ├── github_utils.py   # Utilidades GitHub
│   ├── analyzers.py      # Analizadores
│   └── exporters.py      # Exportadores
├── tests/                # Tests unitarios
├── docs/                 # Documentación
├── export/              # Reportes generados
├── requirements.txt     # Dependencias
└── .env                # Configuración
```


## 📜 Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## 👥 Autores

- **@686f6c61** - *Desarrollo inicial* - [GitHub](https://github.com/686f6c61)

