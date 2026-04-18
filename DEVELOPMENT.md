# XPS Analyzer - Guía de Desarrollo

**Versión:** 0.8.0-beta  
**Estado:** Fase 2 (25% completado)  
**Última actualización:** Abril 2026

Esta guía proporciona el workflow completo para desarrolladores que contribuyen al proyecto XPS Analyzer.

---

## Tabla de Contenidos

1. [Configuración del Entorno](#configuración-del-entorno)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Workflow de Desarrollo](#workflow-de-desarrollo)
4. [Estándares de Código](#estándares-de-código)
5. [Patrones de Validación](#patrones-de-validación)
6. [Testing](#testing)
7. [Documentación](#documentación)
8. [Git Workflow](#git-workflow)
9. [Debugging](#debugging)
10. [Troubleshooting](#troubleshooting)

---

## Configuración del Entorno

### Opción 1: uv (Recomendado)

**uv** es un gestor de paquetes moderno, 10-100x más rápido que pip.

```bash
# 1. Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar repositorio
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis

# 3. Crear ambiente e instalar dependencias
uv sync --group dev --group jupyter

# 4. Verificar instalación
uv run xps-analyzer --version

# 5. Ejecutar tests
uv run pytest tests/
```

**Comandos comunes con uv:**
```bash
# Ejecutar sin activar venv
uv run xps-analyzer --help
uv run pytest tests/

# Agregar dependencia
uv add numpy  # Producción
uv add --group dev pytest  # Desarrollo

# Actualizar dependencias
uv sync

# Lanzar GUI Interactiva
uv run streamlit run src/xps_analyzer/gui/app.py
```

### Opción 2: Conda

**Para usuarios con stack científico existente.**

```bash
# 1. Clonar repositorio
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis

# 2. Crear ambiente
conda env create -f environment.yml

# 3. Activar ambiente
conda activate xps-analysis

# 4. Instalar en modo desarrollo
pip install -e ".[dev,jupyter]"

# 5. Verificar instalación
python verify_installation.py
```

---

## Estructura del Proyecto

```
xps-data-analysis/
├── src/xps_analyzer/           # Código fuente principal
│   ├── __init__.py            # API pública
│   ├── data_loader/           # Carga de datos
│   ├── preprocessing/         # Preprocesamiento (Calibración)
│   ├── analysis/              # Análisis espectral (Fondo, Ajuste, Cuantificación)
│   ├── gui/                   # Interfaz gráfica interactiva (Streamlit)
│   ├── export/                # Exportación (CSV, Excel, JSON)
│   ├── reference_data/        # Base de datos de elementos
│   ├── visualization/         # Plotting estilo científico
│   ├── cli/                   # Interfaz de línea de comandos
│   ├── config/                # Sistema de configuración (TOML)
│   └── utils/                 # Utilidades generales
│
├── tests/                      # Tests (355 tests unitarios)
│   ├── test_data_loader.py
│   ├── test_background.py
│   ├── test_peak_fitting.py
│   ├── test_quantification.py
│   ├── test_visualization.py
│   └── test_export.py
│
├── data/                       # Datos
│   ├── raw/                   # Datos originales (NO MODIFICAR)
│   ├── processed/             # Datos procesados
│   ├── test_data/             # Datos para tests
│   └── results/               # Resultados de análisis
│
├── pyproject.toml             # Configuración del proyecto
├── environment.yml            # Ambiente Conda
├── README.md                  # Quick start
├── ARCHITECTURE.md            # Arquitectura técnica
├── DEVELOPMENT.md             # Esta guía
├── TESTING.md                 # Estrategia de testing (Cobertura 93%)
├── CONTRIBUTING.md            # Guía de contribución
├── CHANGELOG.md               # Historial de cambios
├── ROADMAP.md                 # Plan de desarrollo
└── CONTEXT.md                 # Contexto completo para IA
```

### Navegación Rápida

**Archivos clave para modificar:**
- `src/xps_analyzer/gui/app.py` - Interfaz gráfica principal (Streamlit)
- `src/xps_analyzer/analysis/peak_fitting.py` - Ajuste de picos
- `src/xps_analyzer/data_loader/core.py` - Estructuras de datos (Próxima migración Pydantic)
- `src/xps_analyzer/visualization/plotting.py` - Estilos de ploteo científico

---

## Workflow de Desarrollo

### 1. Crear Branch para Feature/Bug

```bash
# Actualizar main
git checkout main
git pull origin main

# Crear branch
git checkout -b feature/nombre-descriptivo
# o
git checkout -b fix/descripcion-bug
```

### 2. Hacer Cambios

**Ciclo típico:**
```bash
# 1. Editar código
vim src/xps_analyzer/gui/app.py

# 2. Ejecutar tests relevantes
uv run pytest tests/test_visualization.py -v

# 3. Formatear código
uv run ruff format .

# 4. Lint
uv run ruff check --fix .
```

### 3. Ejecutar Tests Completos

**Antes de push:**
```bash
# Tests completos
uv run pytest tests/ -v

# Con cobertura
uv run pytest --cov=src --cov-report=html
```

---

## Patrones de Validación

### Migración en Progreso: Pydantic

Actualmente estamos migrando de validación manual en dataclasses (`__post_init__`) a modelos **Pydantic**. 

**Guía de migración:** Ver `CHANGELOG.md` sección `[0.3.0]`. 
Al modificar archivos en `src/xps_analyzer/data_loader/core.py`, priorizar el uso de `BaseModel` de Pydantic.

---

## Testing

Ver `TESTING.md` para estrategia completa. Actualmente contamos con **355 tests pasando** y una cobertura global del **93%**.

### Ejecutar Tests

```bash
uv run pytest tests/ -v
uv run pytest --cov=src --cov-report=term-missing
```

---

**Última actualización:** Abril 2026  
**Próxima revisión:** Después de completar Fase 2 (Pydantic Migration)  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
