# Guía de Instalación - XPS Analyzer

**Versión:** 0.8.0-beta  
**Sistemas soportados:** Linux, macOS, Windows  
**Python requerido:** 3.10+

Esta guía cubre diferentes métodos de instalación de XPS Analyzer, desde la opción más rápida hasta configuraciones avanzadas.

---

## Instalación Rápida (Recomendada)

La forma más rápida de instalar XPS Analyzer es usando **uv**, el gestor de paquetes Python de nueva generación.

### Paso 1: Instalar uv

**Linux / macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Paso 2: Clonar e Instalar

```bash
# Clonar repositorio
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis

# Instalar dependencias (automáticamente crea venv)
uv sync --group dev --group jupyter

# Verificar instalación
uv run xps-analyzer --version
```

---

## Ejecutar la Interfaz Gráfica (GUI)

Una vez instalado, puedes lanzar la aplicación interactiva de Streamlit para visualizar y procesar tus datos de forma sencilla.

**Con uv (Recomendado):**
```bash
uv run streamlit run src/xps_analyzer/gui/app.py
```

**Con pip/conda:**
```bash
streamlit run src/xps_analyzer/gui/app.py
```

---

## Instalación con Conda

Si ya usas **conda**, esta opción te permite integrar XPS Analyzer con tu stack existente.

### Paso 1: Crear Ambiente

```bash
# Crear ambiente desde archivo
conda env create -f environment.yml

# El ambiente se llamará 'xps-analysis'
conda activate xps-analysis
```

### Paso 2: Instalar Paquete

```bash
# Instalación en modo desarrollo
pip install -e ".[dev]"

# O instalación normal
pip install .
```

### Paso 3: Verificar

```bash
python verify_installation.py
xps-analyzer --version
```

---

## Instalación con pip (Virtualenv)

Para usuarios que prefieren virtualenv tradicional.

### Paso 1: Crear Entorno Virtual

```bash
# Python 3.10 o superior
python3.10 -m venv .venv

# Activar
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Paso 2: Instalar

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar con dependencias de desarrollo
pip install -e ".[dev,jupyter]"
```

### Paso 3: Verificar

```bash
python verify_installation.py
```

---

## Instalación Solo para Uso

Si solo quieres usar el software sin desarrollo:

**Con uv:**

```bash
uv sync  # Sin grupos dev/jupyter
```

**Con pip:**

```bash
pip install .  # Sin [dev]
```

---

## Requisitos del Sistema

### Python

- **Versión mínima:** 3.10
- **Recomendada:** 3.11 o 3.12
- **No soportado:** 3.9 o inferior

### Dependencias Principales

**Obligatorias (instaladas automáticamente):**

- numpy >= 1.21.0
- pandas >= 1.3.0
- matplotlib >= 3.4.0
- scipy >= 1.7.0
- scikit-learn >= 1.0.0
- lmfit >= 1.0.0
- PyYAML >= 6.0
- click >= 8.0.0
- tqdm >= 4.60.0
- pydantic >= 2.12.4
- openpyxl >= 3.1.5
- streamlit >= 1.31.0

**Opcionales (para desarrollo):**

- pytest >= 6.0.0
- pytest-cov >= 2.12.0
- ruff >= 0.1.0
- jupyter >= 1.0.0

---

## Verificación de Instalación

Ejecuta el script de verificación:

```bash
python verify_installation.py
```

**Salida esperada:**

```
...
Instalación EXITOSA.

Comandos disponibles:
  xps-analyzer --help           # Ayuda general
  xps-analyzer show-element <S> # Ver base de datos de elementos
  python -c 'import xps_analyzer'  # Usar en scripts
```

---

## Configuración Post-Instalación

### 1. Configurar Pre-commit Hooks (Solo Desarrollo)

```bash
pre-commit install
```

Esto ejecutará automáticamente ruff y otros checks antes de cada commit.

### 2. Configurar Editor

**VS Code (recomendado):**

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

### 3. Descargar Datos de Ejemplo (Opcional)

```bash
# Los datos de ejemplo están en data/raw/
ls data/raw/samples/
```

---

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'xps_analyzer'"

**Causa:** No instalaste el paquete en modo desarrollo.

**Solución:**

```bash
pip install -e .
```

### Error: "Command 'xps-analyzer' not found"

**Causa:** El script CLI no está en PATH.

**Solución con uv:**

```bash
uv run xps-analyzer --help
```

**Solución con pip:**

```bash
# Reinstalar
pip install -e .

# O usar como módulo
python -m xps_analyzer.cli.main --help
```

### Error: "ImportError: numpy.core.multiarray failed to import"

**Causa:** numpy no compilado correctamente.

**Solución:**

```bash
pip install --force-reinstall numpy
```

### Tests Fallan con Error de Cobertura

**Causa:** pytest-cov no encuentra el módulo.

**Solución:**

```bash
# Reinstalar con coverage
pip install -e ".[dev]"
pytest --no-cov  # Ejecutar sin cobertura temporalmente
```

---

## Desinstalación

**Con uv:**

```bash
rm -rf .venv
```

**Con conda:**

```bash
conda env remove -n xps-analysis
```

**Con pip:**

```bash
pip uninstall xps-analyzer
rm -rf .venv
```

---

## Actualización

### Actualizar a Nueva Versión

**Con uv:**

```bash
git pull
uv sync
```

**Con conda:**

```bash
git pull
conda env update -f environment.yml
```

**Con pip:**

```bash
git pull
pip install -e ".[dev]" --upgrade
```

---

## Instalación en Entornos Especiales

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install .

CMD ["xps-analyzer", "--help"]
```

### Jupyter Notebook (Google Colab)

```python
!git clone https://github.com/JesusF10/xps-data-analysis.git
%cd xps-data-analysis
!pip install -q .
```

---

## Siguientes Pasos

Después de instalar exitosamente:

1. **Lee el README.md** para ejemplos de uso básico
2. **Consulta API_DOCS.md** para referencia completa
3. **Lee DEVELOPMENT.md** si quieres contribuir

---

**Ayuda:** Si encuentras problemas, abre un issue en GitHub:  
https://github.com/JesusF10/xps-data-analysis/issues

**Contacto:** jss.263.fsc@gmail.com
