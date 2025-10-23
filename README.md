# XPS Data Analysis

Software automatizado para análisis de datos de espectroscopía de fotoelectrones de rayos X (XPS), 
desarrollado como proyecto de servicio social en el área de química y metalurgia.

## Descripción del Proyecto

Este repositorio contiene el desarrollo completo de un software en Python para el análisis automatizado de datos XPS, incluyendo:

- **Carga automática** de datos desde formatos específicos de XPS
- **Por determinar**

## Estructura del Repositorio

```
xps-data-analysis/
├── src/                        # Código fuente principal
│   ├── xps_analyzer/           # Paquete principal del software
│   │   ├── data_loader/        # Carga de datos XPS
│   │   ├── preprocessing/      # Preprocesamiento de datos
│   │   ├── analysis/           # Algoritmos de análisis
│   │   ├── visualization/      # Generación de gráficas
│   │   ├── export/             # Exportación de resultados
│   │   └── utils/              # Utilidades generales
│   ├── gui/                    # Interfaz gráfica
│   └── cli/                    # Interfaz de línea de comandos
│
├── data/                       # Datos del proyecto
│   ├── raw/                    # Datos crudos XPS
│   │   ├── samples/            # Datos por muestra
│   │   └── calibration/        # Datos de calibración
│   ├── processed/              # Datos procesados
│   ├── test_data/              # Datos para pruebas
│   └── results/                # Resultados de análisis
│       ├── reports/            # Reportes generados
│       ├── plots/              # Gráficas generadas
│       └── exports/            # Datos exportados
│
├── experiments/                # Experimentos y prototipos
│   ├── notebooks/              # Jupyter notebooks
│   │   ├── exploratory/        # Análisis exploratorio
│   │   ├── validation/         # Validación de métodos
│   │   └── prototypes/         # Prototipos de algoritmos
│   ├── scripts/                # Scripts de experimentación
│   └── benchmarks/             # Pruebas de rendimiento
│
├── tests/                      # Pruebas del software
│   ├── unit/                   # Pruebas unitarias
│   ├── integration/            # Pruebas de integración
│   └── data/                   # Datos para pruebas
│
├── tools/                      # Herramientas auxiliares
│   ├── data_conversion/        # Conversión de formatos
│   ├── validation/             # Validación de datos
│   └── automation/             # Scripts de automatización
│
├── config/                     # Configuraciones (Por determinar)
│
├── reports/                    # Reportes del servicio social
│
├── pyproject.toml              # Configuración del proyecto
├── setup.py                    # Configuración del paquete
└── .gitignore                  # Archivos a ignorar
```

## Instalación

### Requisitos del sistema

- **Python**: 3.8 o superior
- **Sistema operativo**: Linux, macOS, Windows
- **Gestor de paquetes**: Se recomienda `uv` (más rápido) o `pip`

### Instalación rápida

#### Para usuarios finales:

```bash
uv pip install git+https://github.com/JesusF10/xps-data-analysis.git
```

#### Para interactivo con Jupyter:

```bash
# Incluye soporte para notebooks de Jupyter
uv pip install "git+https://github.com/JesusF10/xps-data-analysis.git[jupyter]"
```

### Instalación para desarrollo

```bash
# 1. Clonar el repositorio
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis

# 2. Instalar en modo desarrollo con todas las dependencias
uv pip install -e ".[dev,docs,jupyter]"

# 3. Configurar hooks de pre-commit (opcional)
pre-commit install
```

### 📋 Grupos de dependencias disponibles

| Grupo | Comando | Incluye | Cuándo usar |
|-------|---------|---------|-------------|
| **Base** | `uv pip install xps-analyzer` | Funcionalidad básica | Uso normal, scripts automatizados |
| **Jupyter** | `.[jupyter]` | Notebooks, widgets interactivos | Análisis exploratorio, visualización |
| **Desarrollo** | `.[dev]` | Testing, linting, type checking | Contribuir al código |
| **Documentación** | `.[docs]` | Sphinx, temas, generadores | Generar/editar documentación |

### Verificar la instalación

```bash
# Verificar que el paquete se instaló correctamente
xps-analyzer --help

# Verificar en Python
python -c "import xps_analyzer; print(xps_analyzer.__version__)"
```

### Herramientas de desarrollo adicionales

Si instalaste con `[dev]`, tienes acceso a:

```bash
# Ejecutar tests
pytest

# Linting y formateo de código
ruff check .
ruff format .

# Type checking
mypy src/

# Limpiar archivos generados
make clean  # o python -c "import shutil; shutil.rmtree('__pycache__', ignore_errors=True)"
```

### Con pip

```bash
# Instalación básica
pip install git+https://github.com/JesusF10/xps-data-analysis.git

# Con dependencias opcionales
pip install "git+https://github.com/JesusF10/xps-data-analysis.git[jupyter]"

# Desarrollo
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis
pip install -e ".[dev,docs,jupyter]"
```

### Uso básico

***Pendiente***

## Contexto Académico

Este proyecto forma parte de un proyecto de **servicio social** en el área de **química y metalurgia**, con el objetivo de:
- Automatizar el análisis de datos XPS para investigación en materiales
- Desarrollar herramientas computacionales para caracterización superficial
- Aplicar técnicas de ciencia de datos a problemas de química analítica
- Crear software reutilizable para la comunidad científica

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Autor

**Jesus Flores Lacarra**

Estudiante de la Lic. en Ciencias de la Computación

Servicio Social

Universidad de Sonora

Email: jss.263.fsc@gmail.com

*Desarrollado para la comunidad científica*
