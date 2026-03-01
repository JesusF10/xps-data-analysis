# Guía de Instalación - XPS Analyzer

**Versión:** 0.1.0  
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

**¡Listo!** En 2 comandos tienes todo configurado.

---

## Instalación con Conda

Si ya usas conda para ciencia de datos, esta opción te permite integrar XPS Analyzer con tu stack existente.

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
- click >= 8.0.0

**Opcionales (para desarrollo):**
- pytest >= 6.0.0
- pytest-cov >= 2.12.0
- ruff >= 0.1.0
- jupyter >= 1.0.0

### Espacio en Disco
- **Instalación básica:** ~100 MB
- **Con dependencias dev:** ~300 MB
- **Con datos de ejemplo:** ~500 MB

---

## Verificación de Instalación

Ejecuta el script de verificación:

```bash
python verify_installation.py
```

**Salida esperada:**
```
[OK] Python 3.11.5 detectado
[OK] numpy 1.24.3 instalado
[OK] pandas 2.0.3 instalado
[OK] matplotlib 3.7.2 instalado
[OK] scipy 1.11.1 instalado
[OK] click 8.1.6 instalado
[OK] Comando xps-analyzer disponible
[OK] Directorio data/ existe

Instalación correcta!
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

### Problemas con Conda en macOS ARM (M1/M2)

**Problema:** Algunas librerías científicas no optimizadas para ARM.

**Solución:** Usar Rosetta o instalar versión nativa:
```bash
# Forzar arquitectura ARM64
CONDA_SUBDIR=osx-arm64 conda env create -f environment.yml
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

### Clúster de HPC

```bash
# Usar python del módulo del sistema
module load python/3.11

# Instalación sin sudo
pip install --user -e .
```

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
2. **Explora `examples/`** para notebooks de Jupyter
3. **Consulta API_DOCS.md** para referencia completa
4. **Lee DEVELOPMENT.md** si quieres contribuir

---

**Ayuda:** Si encuentras problemas, abre un issue en GitHub:  
https://github.com/JesusF10/xps-data-analysis/issues

**Contacto:** jss.263.fsc@gmail.com
