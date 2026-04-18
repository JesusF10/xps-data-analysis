# Guía de Contribución

¡Gracias por tu interés en contribuir a XPS Analyzer! Este documento te guiará a través del proceso.

---

## Código de Conducta

- Se respetuoso con todos los contribuidores
- Comunicación constructiva y profesional
- Enfócate en el problema, no en las personas
- Acepta críticas constructivas de buen grado

---

## Cómo Contribuir

### Reportar Bugs

**Antes de reportar:**

1. Busca en [issues existentes](https://github.com/JesusF10/xps-data-analysis/issues)
2. Verifica que estás usando la versión más reciente
3. Ejecuta `pytest` para verificar que no son errores locales

**Al reportar incluye:**

- Versión de Python y SO
- Código mínimo para reproducir el bug
- Mensaje de error completo
- Comportamiento esperado vs. actual

**Template:**

```markdown
## Descripción del Bug

[Descripción clara del problema]

## Pasos para Reproducir

1. Ejecutar ...
2. Ver error ...

## Código de Ejemplo

`‎``python
[código mínimo]
`‎``

## Ambiente

- Python: 3.11.5
- SO: Ubuntu 22.04
- xps-analyzer: 0.8.0-beta
```

### Sugerir Nuevas Características

**Antes de sugerir:**

1. Revisa el [ROADMAP.md](ROADMAP.md)
2. Busca en issues existentes
3. Considera si pertenece a Fase 2 o 3

**Template:**

```markdown
## Característica Propuesta

[Descripción clara]

## Motivación

[Por qué es necesaria]

## Solución Propuesta

[Cómo funcionaría]

## Alternativas Consideradas

[Otros enfoques]

## Fase Sugerida

[ ] Fase 1 (Core)
[ ] Fase 2 (Robustez)
[ ] Fase 3 (Avanzado)
```

### Pull Requests

#### Proceso

1. **Fork** el repositorio
2. **Crea rama** desde `main`:
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```
3. **Implementa** cambios siguiendo convenciones
4. **Agrega tests** (OBLIGATORIO)
5. **Actualiza documentación** si es necesario
6. **Ejecuta ruff**:
   ```bash
   ruff format .
   ruff check --fix .
   ```
7. **Ejecuta tests**:
   ```bash
   pytest --cov=src
   ```
8. **Commit** con mensajes descriptivos
9. **Push** a tu fork
10. **Abre PR** con descripción detallada

#### Checklist de PR

Antes de abrir PR, verifica:

- [ ] **Tests agregados** y pasan (coverage >= línea base)
- [ ] **Ruff pasa** sin warnings
- [ ] **Docstrings en español** para nuevas funciones
- [ ] **Type hints** completos
- [ ] **CHANGELOG.md actualizado** (si aplica)
- [ ] **Documentación actualizada** (si cambia API)
- [ ] **Descripción del PR** clara y completa
- [ ] **Issue linkado** (#123)

---

## Estándares de Código

### Idioma

**CRÍTICO:** Todo en español excepto nombres de variables

```python
# [COMPLETADO] CORRECTO
def calibrar_espectro(espectro: XPSSpectrum) -> XPSSpectrum:
    """
    Calibra el espectro XPS usando un elemento de referencia.

    Parámetros
    ----------
    espectro : XPSSpectrum
        Espectro a calibrar.

    Retorna
    -------
    XPSSpectrum
        Espectro calibrado.
    """
    pass

# [PENDIENTE] INCORRECTO
def calibrar_espectro(espectro: XPSSpectrum) -> XPSSpectrum:
    """Calibrates the XPS spectrum."""  # Docstring en inglés
    pass
```

### Formato de Código

**Ruff (obligatorio):**

```bash
# Formatear
ruff format .

# Linting
ruff check --fix .
```

**Convenciones:**

- Longitud de línea: 88 caracteres
- Indentación: 4 espacios
- Strings: comillas dobles (`"texto"`)
- Imports: orden ruff (future -> stdlib -> first-party -> local -> third-party)

### Docstrings

**Estilo:** NumPy/SciPy (español)

```python
def funcion_ejemplo(parametro1: int, parametro2: str = "default") -> bool:
    """
    Descripción breve de una línea.

    Descripción extendida opcional explicando detalles,
    casos especiales, y comportamiento.

    Parámetros
    ----------
    parametro1 : int
        Descripción del parámetro 1.
    parametro2 : str, optional
        Descripción del parámetro 2. Default: "default".

    Retorna
    -------
    bool
        Descripción del valor de retorno.

    Raises
    ------
    ValueError
        Cuando parametro1 es negativo.
    TypeError
        Cuando parametro2 no es string.

    Ejemplos
    --------
    >>> funcion_ejemplo(42, "test")
    True
    >>> funcion_ejemplo(-1)
    Traceback (most recent call last):
    ValueError: parametro1 debe ser positivo

    Notas
    -----
    Información adicional sobre implementación o teoría.

    Ver También
    ------------
    otra_funcion : Función relacionada.
    """
    if parametro1 < 0:
        raise ValueError("parametro1 debe ser positivo")
    return True
```

### Type Hints

**Obligatorio** para todas las funciones públicas:

```python
from typing import Any
from pathlib import Path

def procesar_archivo(
    filepath: Path,
    opciones: dict[str, Any] | None = None
) -> tuple[list[float], dict[str, str]]:
    """..."""
    pass
```

### Tests

**Estructura:**

```python
import pytest
import numpy as np
from xps_analyzer.data_loader import XPSSpectrum

def test_nombre_descriptivo_del_caso():
    """
    Descripción del test: qué verifica y por qué.
    """
    # Arrange (configurar)
    spectrum = XPSSpectrum(
        region_name="C 1s",
        binding_energy=np.array([284.0, 285.0]),
        intensity=np.array([100.0, 120.0]),
        metadata={}
    )

    # Act (ejecutar)
    result = procesar(spectrum)

    # Assert (verificar)
    assert result.region_name == "C 1s"
    assert len(result.binding_energy) == 2
```

**Nombres de tests:**

- Usar `test_` como prefijo
- Descriptivos: `test_calibration_shifts_all_spectra()`
- Un concepto por test
- Tests de error: `test_raises_valueerror_on_empty_array()`

**Cobertura:**

- Nuevas funciones: 100% coverage
- Modificaciones: mantener o mejorar coverage existente
- Verificar con: `pytest --cov=src --cov-report=html`

---

## Prioridades de Contribución

### 🔥 Alta Prioridad (Fase 2 - GUI & Robustez)

**Buscamos activamente contribuciones para:**

- Mejoras en la interfaz interactiva de Streamlit (`src/xps_analyzer/gui/app.py`)
- Migración de modelos de datos restantes a Pydantic
- Validación de resultados con nuevos datasets experimentales
- Tests de integración para el pipeline completo

**Impacto:** Crítico para v0.9.0

### [COMPLETADO] Media Prioridad

- Sustracción de fondo (Shirley, Tougaard)
- Ajuste de picos (Gaussian, Lorentzian, Voigt)
- Cuantificación con factores de sensibilidad
- Exportación a CSV/Excel/JSON

**Recomendación:** Enfócate primero en Fase 1.

---

## Áreas que Necesitan Ayuda

### Etiquetas de Issues

- `good-first-issue` - Ideal para nuevos contribuidores
- `help-wanted` - Buscamos ayuda activamente
- `Phase-1-blocker` - Crítico para próximo release
- `documentation` - Mejoras de docs
- `bug` - Bugs reportados
- `enhancement` - Nuevas características

### Tareas Específicas

**Backend:**

- Implementar Shirley background subtraction
- Implementar peak fitting con lmfit
- Agregar tests para preprocessing

**Testing:**

- Aumentar cobertura de data_loader
- Tests de integración end-to-end
- Property-based tests con hypothesis

**Documentación:**

- Tutoriales para usuarios
- Ejemplos de notebooks
- Documentación de API faltante

**Infraestructura:**

- GitHub Actions para CI/CD
- Pre-commit hooks adicionales
- Docker image

---

## Proceso de Revisión

### Timeline

1. **Revisión inicial:** 1-3 días
2. **Feedback/cambios:** Variable
3. **Aprobación:** Cuando todos los checks pasen
4. **Merge:** Inmediato después de aprobación

### Criterios de Aceptación

**Automáticos:**

- [COMPLETADO] Ruff pasa
- [COMPLETADO] Tests pasan
- [COMPLETADO] Coverage no disminuye

**Manuales:**

- [COMPLETADO] Código sigue convenciones
- [COMPLETADO] Docstrings en español
- [COMPLETADO] Tests significativos (no solo para coverage)
- [COMPLETADO] Cambios alineados con roadmap

### Cambios Requeridos

Si el review solicita cambios:

1. Hacer cambios en tu rama
2. Commit y push
3. El PR se actualiza automáticamente
4. Responder a comentarios cuando esté listo

---

## Convenciones de Git

### Mensajes de Commit

**Formato:**

```
tipo(ámbito): descripción breve

Descripción extendida opcional explicando:
- Qué cambió
- Por qué cambió
- Impacto del cambio

Refs: #123
```

**Tipos:**

- `feat`: Nueva característica
- `fix`: Bug fix
- `docs`: Cambios en documentación
- `style`: Formato (sin cambio de código)
- `refactor`: Refactorización
- `test`: Agregar/modificar tests
- `chore`: Mantenimiento (deps, config)

**Ejemplos:**

```
feat(analysis): implementar Shirley background subtraction

Agrega método iterativo para sustracción de fondo tipo Shirley.
Incluye parámetros configurables (iterations, tolerance).

Tests: 95% coverage del nuevo módulo.
Refs: #42

fix(data_loader): corregir IndexError en calibration.py:56

Antes fallaba cuando elemento de referencia no encontrado.
Ahora lanza ValueError descriptivo.

Refs: #42

docs(readme): simplificar README de 267 a 150 líneas

Enfoque en quick-start. Detalles movidos a docs específicos.
```

### Ramas

**Nomenclatura:**

- `feature/nombre-descriptivo` - Nuevas características
- `fix/issue-123-descripcion` - Bug fixes
- `docs/seccion-modificada` - Solo documentación
- `refactor/modulo-nombre` - Refactorización

---

## Recursos Adicionales

### Documentación

- [DEVELOPMENT.md](DEVELOPMENT.md) - Guía de desarrollo
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del proyecto
- [TESTING.md](TESTING.md) - Estrategia de testing
- [API_DOCS.md](API_DOCS.md) - Referencia de API

### Herramientas

- [Ruff](https://docs.astral.sh/ruff/) - Linter y formatter
- [pytest](https://docs.pytest.org/) - Framework de testing
- [uv](https://docs.astral.sh/uv/) - Package manager

### Contacto

- **Email:** jss.263.fsc@gmail.com
- **GitHub Issues:** Para preguntas sobre contribuciones
- **Discussions:** Para ideas y discusiones generales

---

## Preguntas Frecuentes

**Q: ¿Debo abrir un issue antes de un PR?**  
A: Para cambios grandes (nuevas características), sí. Para bugs pequeños o typos, PR directo está bien.

**Q: ¿Puedo trabajar en múltiples issues?**  
A: Sí, pero usa ramas separadas y PRs separados por issue.

**Q: ¿Qué hago si mi PR está desactualizado con main?**  
A:

```bash
git checkout main
git pull upstream main
git checkout tu-rama
git rebase main
git push --force-with-lease
```

**Q: ¿Cómo agrego tests para código existente sin tests?**  
A: ¡Excelente! Eso cuenta como contribución valiosa. Sigue estructura de tests y apunta a >=80% coverage.

---

¡Gracias por contribuir a XPS Analyzer!
