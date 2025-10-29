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
├── pyproject.toml              # Configuración del proyecto
├── README.md                   # Documentación principal
├── environment.yml              # Entorno Conda para desarrollo
├── setup.py                    # Configuración del paquete
├── verify_installation.py      # Script para verificar instalación
└── .gitignore                  # Archivos a ignorar
```

## Instalación

### Requisitos del sistema

- **Python**: 3.8 o superior
- **Sistema operativo**: Linux, macOS, Windows
- **Gestores de paquetes recomendados**: 
  - [`uv`](https://docs.astral.sh/uv/) (más rápido, recomendado)
  - [`conda`](https://docs.conda.io/) (para gestión de entornos científicos)
  - `pip` (estándar de Python)

---

## Instalación para Usuarios Finales

### Con uv (Recomendado)

```bash
# Instalación básica
uv pip install git+https://github.com/JesusF10/xps-data-analysis.git

# Con soporte para Jupyter notebooks
uv pip install "git+https://github.com/JesusF10/xps-data-analysis.git[jupyter]"

# Con todas las dependencias opcionales
uv pip install "git+https://github.com/JesusF10/xps-data-analysis.git[jupyter,docs]"
```

### Con conda

```bash
# Crear entorno conda con Python científico
conda create -n xps-analysis python=3.11 numpy pandas matplotlib scipy -c conda-forge
conda activate xps-analysis

# Instalar el paquete
pip install git+https://github.com/JesusF10/xps-data-analysis.git

# O con dependencias opcionales
pip install "git+https://github.com/JesusF10/xps-data-analysis.git[jupyter]"
```

### Con pip estándar

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar el paquete
pip install git+https://github.com/JesusF10/xps-data-analysis.git
```

---

## Instalación para Desarrollo

### Con uv (Método rápido)

```bash
# 1. Clonar el repositorio
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis

# 2. Instalar todas las dependencias de desarrollo
uv sync --group dev --group docs --group jupyter

# 3. Verificar instalación
uv run xps-analyzer --help
uv run verify_installation.py
```

### Con conda

```bash
# 1. Clonar repositorio
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis

# 2. Crear entorno conda con dependencias científicas
conda env create -f environment.yml  # Si existe
# O manualmente:
conda create -n xps-dev python=3.11 numpy pandas matplotlib scipy jupyter pytest -c conda-forge
conda activate xps-dev

# 3. Instalar en modo desarrollo
pip install -e ".[dev,docs,jupyter]"

# 4. Configurar pre-commit hooks
pre-commit install
```

### Con pip + venv

```bash
# 1. Clonar y crear entorno
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Actualizar pip y instalar
pip install --upgrade pip
pip install -e ".[dev,docs,jupyter]"

# 3. Configurar desarrollo
pre-commit install
```

---

## Grupos de Dependencias

| Grupo | Instalación | Incluye | Cuándo usar |
|-------|-------------|---------|-------------|
| **Base** | `xps-analyzer` | numpy, pandas, matplotlib, scipy | Uso básico, análisis automatizado |
| **jupyter** | `[jupyter]` | jupyterlab, widgets, plotly | Análisis interactivo, exploración |
| **dev** | `[dev]` | pytest, ruff, mypy, pre-commit | Desarrollo, testing, linting |
| **docs** | `[docs]` | sphinx, furo, myst-parser | Generar documentación |

### Comandos de instalación por uso:

```bash
# Usuario final básico
uv pip install xps-analyzer

# Análisis interactivo con notebooks
uv pip install "xps-analyzer[jupyter]"

# Desarrollo completo
uv sync --group dev --group docs --group jupyter

# Conda + desarrollo
conda create -n xps-dev python=3.11 -c conda-forge
conda activate xps-dev
pip install -e ".[dev,jupyter,docs]"
```

---

## Verificación de Instalación

```bash
# Verificar comando CLI
xps-analyzer --help
xps-analyzer reference

# Verificar en Python
python -c "import xps_analyzer; print(f'Versión: {xps_analyzer.__version__}')"

# Verificar dependencias opcionales
python -c "import matplotlib, pandas, numpy; print('Dependencias básicas OK')"

# Si instalaste jupyter
python -c "import jupyter; print('Jupyter disponible')"
```

### Script de Verificación Completa

Incluimos un script que verifica automáticamente toda la instalación:

```bash
# Ejecutar verificación completa
python verify_installation.py

# O con uv
uv run python verify_installation.py
```

Este script verifica:
- Versión de Python compatible
- Dependencias principales instaladas
- XPS Analyzer funcionando correctamente  
- CLI disponible y funcional
- Dependencias opcionales (Jupyter, herramientas de desarrollo)

---

## Herramientas de Desarrollo

Si instalaste con dependencias de desarrollo (`[dev]` o `--group dev`):

```bash
# Testing
uv run pytest                    # Con uv
pytest                          # Directo

# Linting y formateo
uv run ruff check src/          # Verificar código
uv run ruff format src/         # Formatear código

# Type checking
uv run mypy src/

# Pre-commit (verificaciones automáticas)
pre-commit run --all-files

# Generar documentación
cd docs/
make html                       # O: sphinx-build -b html . _build/html
```

---

### Uso básico

***Pendiente***

---

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
