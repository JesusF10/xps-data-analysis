# XPS Analyzer - Guía de Desarrollo

**Versión:** 0.1.0  
**Estado:** Fase 0 (35% completado)  
**Última actualización:** Febrero 2026

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
git clone https://github.com/tu-usuario/xps-analyzer.git
cd xps-analyzer

# 3. Crear ambiente e instalar dependencias
uv sync --group dev --group jupyter

# 4. Verificar instalación
uv run python verify_installation.py

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

# Ejecutar script
uv run python scripts/analyze_sample.py
```

### Opción 2: Conda

**Para usuarios con stack científico existente.**

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/xps-analyzer.git
cd xps-analyzer

# 2. Crear ambiente
conda env create -f environment.yml

# 3. Activar ambiente
conda activate xps-analysis

# 4. Instalar en modo desarrollo
pip install -e ".[dev,jupyter]"

# 5. Verificar instalación
python verify_installation.py
```

### Opción 3: pip + venv

**Método tradicional Python.**

```bash
# 1. Crear venv
python -m venv .venv

# 2. Activar
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# 3. Instalar en modo desarrollo
pip install -e ".[dev,jupyter]"

# 4. Verificar
python verify_installation.py
```

### Herramientas Requeridas

**Esenciales:**
- Python 3.10+ (se recomienda 3.12)
- Git 2.30+
- Editor con LSP support (VS Code, PyCharm, Neovim)

**Opcionales:**
- `just` - Task runner (alternativa a Makefile)
- `gh` - GitHub CLI
- `ripgrep` - Búsqueda rápida en código

### Configuración del Editor

**VS Code (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

**PyCharm:**
1. Settings -> Project -> Python Interpreter -> Seleccionar `.venv`
2. Settings -> Tools -> External Tools -> Agregar Ruff
3. Settings -> Editor -> Code Style -> Python -> Tab size: 4

---

## Estructura del Proyecto

```
xps-data-analysis/
├── src/xps_analyzer/           # Código fuente principal
│   ├── __init__.py            # API pública
│   ├── data_loader/           # Carga de datos
│   ├── preprocessing/         # Preprocesamiento
│   ├── analysis/              # Análisis espectral (VACÍO)
│   ├── reference_data/        # Base de datos de elementos
│   ├── visualization/         # Plotting
│   ├── export/                # Exportación (VACÍO)
│   ├── cli/                   # Interfaz de línea de comandos
│   ├── config/                # Sistema de configuración (PLANEADO)
│   └── utils/                 # Utilidades (VACÍO)
│
├── tests/                      # Tests
│   ├── unit/                  # Tests unitarios
│   ├── integration/           # Tests de integración
│   ├── fixtures/              # Datos de prueba
│   └── test_data_loader.py   # Tests actuales
│
├── data/                       # Datos
│   ├── raw/                   # Datos originales (NO MODIFICAR)
│   ├── processed/             # Datos procesados
│   ├── test_data/             # Datos para tests
│   └── results/               # Resultados de análisis
│
├── config/                     # Archivos de configuración
│   ├── default_settings.toml
│   ├── instrument_profiles.toml
│   └── element_database.toml
│
├── docs/                       # Documentación
│   ├── tutorials/             # Tutoriales
│   ├── api/                   # Referencia API
│   └── examples/              # Ejemplos
│
├── experiments/                # Notebooks y scripts experimentales
│   ├── notebooks/
│   └── scripts/
│
├── tools/                      # Scripts auxiliares
│   ├── data_conversion/
│   └── validation/
│
├── pyproject.toml             # Configuración del proyecto
├── environment.yml            # Ambiente Conda
├── uv.lock                    # Lock file de uv
├── README.md                  # Quick start
├── ARCHITECTURE.md            # Arquitectura técnica
├── DEVELOPMENT.md             # Esta guía
├── TESTING.md                 # Estrategia de testing
├── CONTRIBUTING.md            # Guía de contribución
├── CHANGELOG.md               # Historial de cambios
├── ROADMAP.md                 # Plan de desarrollo
└── CONTEXT.md                 # Contexto completo para IA

```

### Navegación Rápida

**Archivos clave para modificar:**
- `src/xps_analyzer/data_loader/core.py` - Estructuras de datos principales
- `src/xps_analyzer/preprocessing/calibration.py` - Calibración de energía
- `src/xps_analyzer/reference_data/elements.py` - Base de datos de elementos
- `src/xps_analyzer/cli/main.py` - Comandos CLI

**Archivos de configuración:**
- `pyproject.toml` - Dependencias, metadata, configuración de herramientas
- `config/default_settings.toml` - Parámetros de análisis por defecto
- `.pre-commit-config.yaml` - Hooks de pre-commit

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

**Convención de nombres:**
- `feature/` - Nueva funcionalidad
- `fix/` - Corrección de bug
- `refactor/` - Refactorización
- `docs/` - Solo documentación
- `test/` - Agregar/mejorar tests

### 2. Hacer Cambios

**Ciclo típico:**
```bash
# 1. Editar código
vim src/xps_analyzer/analysis/peak_detection.py

# 2. Ejecutar tests relevantes
uv run pytest tests/test_analysis.py -v

# 3. Verificar cobertura
uv run pytest --cov=src/xps_analyzer/analysis --cov-report=term-missing

# 4. Formatear código
uv run ruff format .

# 5. Lint
uv run ruff check --fix .

# 6. Verificar type hints (opcional)
uv run ty check src/
```

### 3. Commit de Cambios

**Mensaje de commit:**
```bash
git add src/xps_analyzer/analysis/peak_detection.py
git add tests/test_analysis.py
git commit -m "feat: agregar detección básica de picos

- Implementa algoritmo scipy.signal.find_peaks
- Agrega parámetros threshold y min_distance
- Incluye tests con datos sintéticos
- Relacionado con Issue #15"
```

**Formato de mensajes:**
```
<tipo>: <descripción breve>

<cuerpo opcional explicando el por qué>

<footer opcional: referencias a issues>
```

**Tipos de commit:**
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `refactor:` - Refactorización sin cambio de funcionalidad
- `docs:` - Solo cambios en documentación
- `test:` - Agregar/modificar tests
- `style:` - Cambios de formato (no afectan código)
- `perf:` - Mejoras de rendimiento
- `chore:` - Cambios en build, CI, herramientas

### 4. Ejecutar Tests Completos

**Antes de push:**
```bash
# Tests completos
uv run pytest tests/ -v

# Con cobertura
uv run pytest --cov=src --cov-report=html

# Solo tests afectados (rápido)
uv run pytest tests/test_analysis.py::test_find_peaks -v

# Ver reporte de cobertura
open htmlcov/index.html  # Mac/Linux
# o
start htmlcov/index.html  # Windows
```

### 5. Push y Crear Pull Request

```bash
# Push branch
git push -u origin feature/nombre-descriptivo

# Crear PR con GitHub CLI
gh pr create --title "Agregar detección de picos" --body "Implementa algoritmo básico de detección de picos usando scipy.signal.find_peaks. Resuelve #15."

# O crear PR manualmente en GitHub web
```

---

## Estándares de Código

### Idioma

**CRÍTICO:** Todo el código debe estar en español (excepto nombres de variables).

```python
# [COMPLETADO] CORRECTO
def calibrar_espectro(espectro: XPSSpectrum, elemento_referencia: str) -> XPSSpectrum:
    """
    Calibra un espectro XPS usando un elemento de referencia.
    
    Parámetros
    ----------
    espectro : XPSSpectrum
        El espectro a calibrar.
    elemento_referencia : str
        Símbolo del elemento de referencia (ej: "C").
    
    Retorna
    -------
    XPSSpectrum
        Espectro calibrado con energías corregidas.
    
    Ejemplos
    --------
    >>> spectrum = dataset.spectra["C 1s"]
    >>> calibrated = calibrar_espectro(spectrum, "C")
    """
    pass

# [PENDIENTE] INCORRECTO - docstring en inglés
def calibrar_espectro(espectro: XPSSpectrum) -> XPSSpectrum:
    """Calibrates an XPS spectrum using a reference element."""
    pass
```

### Type Hints

**Obligatorio en todas las funciones públicas:**

```python
from typing import Any
from collections.abc import Sequence
import numpy as np
from numpy.typing import NDArray

# [COMPLETADO] CORRECTO - type hints completos
def procesar_espectros(
    espectros: Sequence[XPSSpectrum],
    energia_min: float,
    energia_max: float,
    opciones: dict[str, Any] | None = None
) -> list[XPSSpectrum]:
    """Procesa múltiples espectros en un rango de energía."""
    if opciones is None:
        opciones = {}
    # ...

# [COMPLETADO] CORRECTO - type hints con NumPy
def calcular_derivada(
    energias: NDArray[np.float64],
    intensidades: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Calcula la derivada numérica."""
    return np.gradient(intensidades, energias)

# [PENDIENTE] INCORRECTO - sin type hints
def procesar_espectros(espectros, energia_min, energia_max, opciones=None):
    pass
```

### Docstrings

**Estilo NumPy (obligatorio):**

```python
def ajustar_picos(
    espectro: XPSSpectrum,
    posiciones_iniciales: list[float],
    formas_pico: list[str] | None = None,
    fondo: str = "shirley",
    max_iteraciones: int = 1000,
    tolerancia: float = 1e-6
) -> FitResult:
    """
    Ajusta picos gaussianos/lorentzianos/voigt a un espectro XPS.
    
    Usa el algoritmo Levenberg-Marquardt para minimizar el error cuadrático
    medio entre el espectro experimental y el modelo de picos.
    
    Parámetros
    ----------
    espectro : XPSSpectrum
        Espectro XPS a ajustar.
    posiciones_iniciales : list[float]
        Posiciones iniciales de picos en eV.
    formas_pico : list[str] | None, optional
        Formas de pico para cada posición: "gaussian", "lorentzian", "voigt".
        Si None, usa "voigt" para todos. Default: None.
    fondo : str, default "shirley"
        Método de sustracción de fondo: "shirley", "tougaard", "linear".
    max_iteraciones : int, default 1000
        Número máximo de iteraciones del algoritmo de ajuste.
    tolerancia : float, default 1e-6
        Tolerancia para convergencia del ajuste.
    
    Retorna
    -------
    FitResult
        Objeto con los resultados del ajuste:
        - peak_params: Parámetros ajustados de cada pico
        - fitted_curve: Curva ajustada total
        - residuals: Diferencia entre datos y ajuste
        - chi_squared: Bondad de ajuste (χ²)
        - success: Si el ajuste convergió
    
    Lanza
    -----
    ValueError
        Si `posiciones_iniciales` está vacío.
        Si `formas_pico` tiene longitud diferente a `posiciones_iniciales`.
    FitError
        Si el ajuste no converge después de `max_iteraciones`.
    
    Notas
    -----
    - El espectro debe tener al menos 50 puntos para un ajuste robusto
    - Las posiciones iniciales deben estar dentro del rango de energías
    - Los picos Voigt combinan contribuciones gaussianas (resolución) y
      lorentzianas (tiempo de vida)
    
    Ejemplos
    --------
    >>> from xps_analyzer import load_single_file
    >>> from xps_analyzer.analysis import ajustar_picos
    >>> 
    >>> dataset = load_single_file("data/raw/muestra.txt")
    >>> espectro = dataset.spectra["C 1s"]
    >>> 
    >>> # Ajustar 3 picos en C 1s
    >>> resultado = ajustar_picos(
    ...     espectro=espectro,
    ...     posiciones_iniciales=[284.8, 286.5, 288.9],
    ...     formas_pico=["voigt", "voigt", "voigt"],
    ...     fondo="shirley"
    ... )
    >>> 
    >>> print(f"χ² = {resultado.chi_squared:.4f}")
    >>> print(f"Picos: {resultado.peak_params}")
    
    Referencias
    ----------
    .. [1] Shirley, D. A. "High-Resolution X-Ray Photoemission Spectrum of
           the Valence Bands of Gold", Phys. Rev. B 5, 4709 (1972)
    .. [2] Tougaard, S. "Practical guide to the use of backgrounds in
           quantitative XPS", Surface Science 730, 141141 (2023)
    
    Ver También
    ------------
    subtract_background : Sustracción de fondo standalone
    find_peaks : Detección automática de picos
    """
    pass
```

**Secciones requeridas:**
- Descripción breve (1 línea)
- `Parámetros` - Todos los parámetros con tipos y descripciones
- `Retorna` - Tipo y descripción del valor de retorno
- `Ejemplos` - Al menos un ejemplo funcional
- `Lanza` (opcional) - Excepciones que puede lanzar
- `Notas` (opcional) - Detalles de implementación
- `Referencias` (opcional) - Publicaciones científicas

### Convenciones de Naming

```python
# Variables y funciones: snake_case
binding_energy = 284.8
def calcular_desplazamiento():
    pass

# Clases: PascalCase
class XPSSpectrum:
    pass

# Constantes: UPPER_SNAKE_CASE
DEFAULT_TOLERANCE = 2.0
MAX_ITERATIONS = 1000

# Módulos: snake_case
# peak_detection.py, background_subtraction.py

# Variables privadas: _prefijo
_cache_interno = {}
def _helper_privado():
    pass
```

### Imports

**Orden configurado en `pyproject.toml` (ruff):**

```python
# 1. Future imports
from __future__ import annotations

# 2. Standard library
from pathlib import Path
from typing import Any
import json

# 3. First-party (xps_analyzer)
from xps_analyzer.data_loader import XPSSpectrum, XPSDataset
from xps_analyzer.reference_data import load_reference_database

# 4. Local (imports relativos)
from .core import parse_metadata
from .validation import validate_energy_range

# 5. Third-party
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
```

**Ejecución automática con ruff:**
```bash
uv run ruff check --select I --fix .
```

---

## Patrones de Validación

### Fase 0: Validación Manual

**Estado actual:** Usando `__post_init__` en dataclasses.

```python
from dataclasses import dataclass, field
from typing import Any
import numpy as np

@dataclass
class XPSSpectrum:
    """Espectro XPS con validación manual."""
    region_name: str
    binding_energy: np.ndarray
    intensity: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validación ejecutada después de __init__."""
        # 1. Arrays deben tener misma longitud
        if len(self.binding_energy) != len(self.intensity):
            raise ValueError(
                f"binding_energy ({len(self.binding_energy)} puntos) e "
                f"intensity ({len(self.intensity)} puntos) deben tener "
                f"la misma longitud"
            )
        
        # 2. Arrays no pueden estar vacíos
        if len(self.binding_energy) == 0:
            raise ValueError("Los arrays no pueden estar vacíos")
        
        # 3. Energías deben ser positivas
        if np.any(self.binding_energy <= 0):
            raise ValueError(
                "binding_energy debe contener solo valores positivos"
            )
        
        # 4. Nombre de región no puede estar vacío
        if not self.region_name or not self.region_name.strip():
            raise ValueError("region_name no puede estar vacío")
```

**Cuándo usar:**
- Fase 0 y Fase 1
- Validación simple de tipos primitivos
- Cuando quieres control total sobre mensajes de error

### Fase 2: Migración a Pydantic

**Planeado para v0.3.0** (ver `CHANGELOG.md`).

```python
from pydantic import BaseModel, Field, field_validator, model_validator
import numpy as np
from numpy.typing import NDArray
from typing import Any

class XPSSpectrum(BaseModel):
    """Espectro XPS con validación Pydantic."""
    
    region_name: str = Field(
        ..., 
        min_length=1,
        description="Nombre de la región espectral"
    )
    binding_energy: NDArray[np.float64] = Field(
        ...,
        description="Energías de enlace en eV"
    )
    intensity: NDArray[np.float64] = Field(
        ...,
        description="Intensidades en cuentas arbitrarias"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True  # Permite NumPy arrays
    
    @field_validator("binding_energy")
    @classmethod
    def validate_positive_energies(cls, v: NDArray) -> NDArray:
        """Valida que las energías sean positivas."""
        if len(v) == 0:
            raise ValueError("binding_energy no puede estar vacío")
        if np.any(v <= 0):
            raise ValueError("binding_energy debe contener solo valores positivos")
        return v
    
    @model_validator(mode="after")
    def validate_matching_lengths(self):
        """Valida que arrays tengan la misma longitud."""
        if len(self.binding_energy) != len(self.intensity):
            raise ValueError(
                f"binding_energy ({len(self.binding_energy)}) e intensity "
                f"({len(self.intensity)}) deben tener la misma longitud"
            )
        return self
    
    # Métodos de negocio
    def copy(self) -> "XPSSpectrum":
        """Crea copia profunda."""
        return XPSSpectrum(
            region_name=self.region_name,
            binding_energy=self.binding_energy.copy(),
            intensity=self.intensity.copy(),
            metadata=self.metadata.copy()
        )
```

**Ventajas de Pydantic:**
- [COMPLETADO] Validación automática de tipos
- [COMPLETADO] Mensajes de error detallados
- [COMPLETADO] Serialización JSON automática
- [COMPLETADO] JSON schema generation
- [COMPLETADO] Integración con FastAPI (futuro)

**Guía de migración completa:** Ver `CHANGELOG.md` sección `[0.3.0]`.

### Validación de Inputs en Funciones

```python
def ajustar_picos(
    espectro: XPSSpectrum,
    posiciones_iniciales: list[float],
    formas_pico: list[str] | None = None,
    max_iteraciones: int = 1000
) -> FitResult:
    """Ajusta picos a un espectro."""
    
    # Validar parámetros
    if not posiciones_iniciales:
        raise ValueError("posiciones_iniciales no puede estar vacío")
    
    if max_iteraciones <= 0:
        raise ValueError(f"max_iteraciones debe ser > 0, recibido: {max_iteraciones}")
    
    if formas_pico is not None:
        if len(formas_pico) != len(posiciones_iniciales):
            raise ValueError(
                f"formas_pico ({len(formas_pico)}) debe tener la misma "
                f"longitud que posiciones_iniciales ({len(posiciones_iniciales)})"
            )
        
        formas_validas = {"gaussian", "lorentzian", "voigt"}
        for forma in formas_pico:
            if forma not in formas_validas:
                raise ValueError(
                    f"Forma de pico inválida: '{forma}'. "
                    f"Opciones: {formas_validas}"
                )
    
    # Implementación
    ...
```

---

## Testing

Ver `TESTING.md` para estrategia completa. Aquí un resumen:

### Ejecutar Tests

```bash
# Todos los tests
uv run pytest tests/

# Con verbose
uv run pytest tests/ -v

# Con cobertura
uv run pytest --cov=src --cov-report=html

# Test específico
uv run pytest tests/test_data_loader.py::test_parse_metadata_basic -v

# Tests que coinciden con patrón
uv run pytest tests/ -k "calibration" -v

# Stop al primer fallo
uv run pytest tests/ -x

# Ver print statements
uv run pytest tests/ -s
```

### Escribir Tests

**Estructura básica:**

```python
# tests/test_analysis.py
import pytest
import numpy as np
from xps_analyzer.data_loader import XPSSpectrum
from xps_analyzer.analysis import find_peaks

def test_find_peaks_basic():
    """Test básico de detección de picos."""
    # Arrange: preparar datos
    energy = np.linspace(280, 295, 100)
    intensity = np.exp(-((energy - 284.8) ** 2) / 2)  # Pico gaussiano
    spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=energy,
        intensity=intensity
    )
    
    # Act: ejecutar función
    peaks = find_peaks(spectrum, threshold=0.5)
    
    # Assert: verificar resultados
    assert len(peaks) == 1
    assert 284.5 < peaks[0] < 285.0  # Pico cerca de 284.8

def test_find_peaks_no_peaks():
    """Test cuando no hay picos."""
    energy = np.linspace(280, 295, 100)
    intensity = np.ones(100) * 0.1  # Flat
    spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=energy,
        intensity=intensity
    )
    
    peaks = find_peaks(spectrum, threshold=0.5)
    assert len(peaks) == 0

def test_find_peaks_invalid_threshold():
    """Test con threshold inválido."""
    spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.linspace(280, 295, 100),
        intensity=np.ones(100)
    )
    
    with pytest.raises(ValueError, match="threshold debe estar entre 0 y 1"):
        find_peaks(spectrum, threshold=1.5)
```

**Fixtures para datos compartidos:**

```python
# tests/conftest.py
import pytest
import numpy as np
from xps_analyzer.data_loader import XPSSpectrum, XPSDataset

@pytest.fixture
def simple_spectrum():
    """Espectro simple para tests."""
    return XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.linspace(280, 295, 100),
        intensity=np.exp(-((np.linspace(280, 295, 100) - 284.8) ** 2) / 2)
    )

@pytest.fixture
def sample_dataset():
    """Dataset completo para tests."""
    c1s = XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.linspace(280, 295, 100),
        intensity=np.random.rand(100)
    )
    o1s = XPSSpectrum(
        region_name="O 1s",
        binding_energy=np.linspace(525, 540, 100),
        intensity=np.random.rand(100)
    )
    return XPSDataset(
        filename="test.txt",
        header={"sample_name": "test_sample"},
        spectra={"C 1s": c1s, "O 1s": o1s}
    )

# Uso en tests
def test_con_fixture(simple_spectrum):
    """Test usando fixture."""
    assert len(simple_spectrum.binding_energy) == 100
```

---

## Documentación

### Generar Documentación Automática

**Futuro (Fase 2):** Usando Sphinx + sphinx-autodoc.

```bash
# Instalar dependencias
uv add --group docs sphinx sphinx-autodoc-typehints sphinx-rtd-theme

# Generar docs
cd docs/
sphinx-quickstart
sphinx-apidoc -o api/ ../src/xps_analyzer/
make html

# Ver docs
open _build/html/index.html
```

### Actualizar Documentación

**Cuándo actualizar:**
- Al agregar nueva funcionalidad pública -> actualizar `API_DOCS.md` o docstring
- Al cambiar comportamiento -> actualizar docstring + `CHANGELOG.md`
- Al cambiar arquitectura -> actualizar `ARCHITECTURE.md`
- Al agregar dependencia -> actualizar `README.md` instalación

---

## Git Workflow

### Branch Strategy

```
main (producción)
  ↑
  └── develop (integración)
        ↑
        ├── feature/peak-fitting
        ├── fix/calibration-bug
        └── refactor/validation-pydantic
```

### Comandos Comunes

```bash
# Ver estado
git status

# Ver cambios
git diff
git diff --staged

# Agregar cambios selectivos
git add -p

# Commit
git commit -m "feat: agregar detección de picos"

# Amend último commit (solo local)
git commit --amend

# Ver log
git log --oneline --graph --all

# Rebase interactivo (limpiar historia local)
git rebase -i HEAD~3

# Actualizar con main
git checkout feature/mi-branch
git fetch origin
git rebase origin/main
```

### Pre-commit Hooks

**Instalar:**
```bash
uv add --group dev pre-commit
pre-commit install
```

**Ejecutar manualmente:**
```bash
pre-commit run --all-files
```

**Configuración (`.pre-commit-config.yaml`):**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
```

---

## Debugging

### Debugging con pytest

```python
# tests/test_analysis.py

def test_fit_peaks_debug():
    """Test con debugging."""
    spectrum = ...
    
    # Opción 1: Usar breakpoint()
    breakpoint()  # Python 3.7+
    result = fit_peaks(spectrum)
    
    # Opción 2: Print condicional
    import os
    if os.getenv("DEBUG"):
        print(f"Spectrum shape: {spectrum.binding_energy.shape}")
        print(f"Max intensity: {spectrum.intensity.max()}")
    
    assert result.success
```

**Ejecutar con debugging:**
```bash
# Entrar a debugger en breakpoint()
uv run pytest tests/test_analysis.py::test_fit_peaks_debug -s

# Ejecutar con prints
DEBUG=1 uv run pytest tests/ -s
```

### Debugging con VS Code

**Configuración (`.vscode/launch.json`):**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "XPS Analyzer CLI",
      "type": "python",
      "request": "launch",
      "module": "xps_analyzer.cli.main",
      "args": ["analyze", "data/raw/samples/"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Logging

```python
import logging

# Configuración en módulo
logger = logging.getLogger(__name__)

def ajustar_picos(espectro: XPSSpectrum) -> FitResult:
    """Ajusta picos con logging."""
    logger.info(f"Iniciando ajuste para {espectro.region_name}")
    logger.debug(f"Espectro tiene {len(espectro.binding_energy)} puntos")
    
    try:
        resultado = _fit_internal(espectro)
        logger.info(f"Ajuste exitoso: χ²={resultado.chi_squared:.4f}")
        return resultado
    except FitError as e:
        logger.error(f"Ajuste falló: {e}")
        raise
```

**Configurar nivel de logging:**
```python
# En CLI o scripts
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
```

---

## Troubleshooting

### Problema: Tests fallan con ModuleNotFoundError

```bash
# Error
ModuleNotFoundError: No module named 'xps_analyzer'

# Solución: Instalar en modo desarrollo
uv sync --group dev
# o
pip install -e .
```

### Problema: Import errors en VS Code

```bash
# Error: VS Code no encuentra módulos

# Solución 1: Seleccionar intérprete correcto
Ctrl+Shift+P -> "Python: Select Interpreter" -> .venv/bin/python

# Solución 2: Reiniciar language server
Ctrl+Shift+P -> "Python: Restart Language Server"

# Solución 3: Regenerar archivos de cache
rm -rf .venv/
uv sync --group dev
```

### Problema: Pre-commit hooks fallan

```bash
# Error: Ruff encuentra problemas

# Ver errores
pre-commit run --all-files

# Auto-fix
uv run ruff check --fix .
uv run ruff format .

# Bypass temporal (emergencias solamente)
git commit --no-verify -m "fix: emergency fix"
```

### Problema: Tests pasan localmente pero fallan en CI

```bash
# Posibles causas:
# 1. Dependencias desactualizadas
uv sync

# 2. Tests dependientes de orden
pytest tests/ --random-order

# 3. Tests dependientes de archivos locales
# Usar fixtures con datos embebidos

# 4. Diferencias de plataforma (Windows vs Linux)
# Usar pathlib.Path en lugar de strings
```

### Problema: Errores de tipo con NumPy arrays

```python
# Error: Type checker no reconoce NumPy operations

# Solución: Usar numpy.typing
from numpy.typing import NDArray
import numpy as np

def procesar(data: NDArray[np.float64]) -> NDArray[np.float64]:
    return data * 2

# Si el error persiste, agregar type: ignore
result = data * 2  # type: ignore[operator]
```

---

## Referencias

### Documentos Relacionados
- `TESTING.md` - Estrategia completa de testing
- `ARCHITECTURE.md` - Arquitectura técnica detallada
- `CONTRIBUTING.md` - Guía de contribución
- `CONTEXT.md` - Contexto completo del proyecto

### Herramientas
- **uv** - https://github.com/astral-sh/uv
- **Ruff** - https://docs.astral.sh/ruff/
- **pytest** - https://docs.pytest.org/
- **Pydantic** - https://docs.pydantic.dev/

### Estilo de Código
- **PEP 8** - https://pep8.org/
- **NumPy docstring style** - https://numpydoc.readthedocs.io/
- **Type hints** - https://docs.python.org/3/library/typing.html

---

**Última actualización:** Febrero 2026  
**Próxima revisión:** Después de completar Fase 1  
**Mantenedor:** Jesus Flores Lacarra (jss.263.fsc@gmail.com)
