#!/usr/bin/env python3
"""
Script de verificación para XPS Analyzer.
Verifica que todas las dependencias estén instaladas correctamente.
"""

import sys
from importlib import import_module
from pathlib import Path


def check_python_version():
    """Verifica la versión de Python."""
    print(f"Python: {sys.version}")

    if sys.version_info < (3, 8):
        print("ERROR: Se requiere Python 3.8 o superior")
        return False
    else:
        print("Versión de Python compatible")
        return True


def check_core_dependencies():
    """Verifica las dependencias principales."""
    core_deps = {
        "numpy": "NumPy - Arrays numéricos",
        "pandas": "Pandas - Manipulación de datos",
        "matplotlib": "Matplotlib - Visualización básica",
        "scipy": "SciPy - Computación científica",
        "click": "Click - CLI framework",
    }

    print("\nVerificando dependencias principales:")
    all_ok = True

    for module, description in core_deps.items():
        try:
            mod = import_module(module)
            version = getattr(mod, "__version__", "unknown")
            print(f"{module} ({version}) - {description}")
        except ImportError:
            print(f"{module} - {description} - NO ENCONTRADO")
            all_ok = False

    return all_ok


def check_optional_dependencies():
    """Verifica las dependencias opcionales."""
    optional_deps = {
        "jupyter": "JupyterLab - Notebooks interactivos",
        "plotly": "Plotly - Visualización interactiva",
        "pytest": "PyTest - Framework de testing",
        "mypy": "MyPy - Type checking",
        "ruff": "Ruff - Linter y formatter",
    }

    print("\nVerificando dependencias opcionales:")

    for module, description in optional_deps.items():
        try:
            mod = import_module(module)
            version = getattr(mod, "__version__", "unknown")
            print(f"{module} ({version}) - {description}")
        except ImportError:
            print(f"{module} - {description} - NO INSTALADO (opcional)")


def check_xps_analyzer():
    """Verifica que XPS Analyzer esté instalado correctamente."""
    print("\nVerificando XPS Analyzer:")

    try:
        import xps_analyzer

        print(f"xps_analyzer ({xps_analyzer.__version__}) - Paquete principal")

        # Verificar módulos principales
        from xps_analyzer.data_loader import load_single_file

        print("data_loader - Módulo de carga de datos")

        from xps_analyzer.reference_data import ReferenceDatabase

        print("reference_data - Base de datos de referencia")

        return True

    except ImportError as e:
        print(f"❌ XPS Analyzer no está instalado correctamente: {e}")
        return False


def check_cli():
    """Verifica que el CLI esté disponible."""
    print("\nVerificando CLI:")

    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, "-m", "xps_analyzer.cli.main", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("CLI disponible: xps-analyzer")
            return True
        else:
            print(f"Error en CLI: {result.stderr}")
            return False

    except Exception as e:
        print(f"CLI no disponible: {e}")
        return False


def main():
    """Función principal de verificación."""
    print("=" * 60)
    print("XPS Analyzer - Verificación de Instalación")
    print("=" * 60)

    checks = [
        check_python_version,
        check_core_dependencies,
        check_xps_analyzer,
        check_cli,
    ]

    results = []
    for check in checks:
        results.append(check())

    # Dependencias opcionales (no afectan el resultado final)
    check_optional_dependencies()

    print("\n" + "=" * 60)
    if all(results):
        print("Instalación EXITOSA.")
        print("\nComandos disponibles:")
        print("  xps-analyzer --help      # Ayuda general")
        print("  xps-analyzer reference   # Ver base de datos")
        print("  python -c 'import xps_analyzer'  # Usar en scripts")
    else:
        print("Hay problemas con la instalación. Ver errores arriba.")
        print("\nSoluciones sugeridas:")
        print("  1. Reinstalar: uv sync")
        print("  2. Verificar Python >= 3.8")
        print("  3. Consultar README.md para instrucciones")

        return 1

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
