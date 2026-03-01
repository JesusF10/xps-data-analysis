# Directorio de Experimentos

Este directorio contiene notebooks de Jupyter, scripts de experimentación y prototipos para desarrollo y validación de nuevas funcionalidades.

## Estructura

```
experiments/
├── notebooks/          # Jupyter notebooks para análisis interactivo
│   ├── exploratory/    # Análisis exploratorio de datos
│   ├── validation/     # Validación de métodos implementados
│   └── prototypes/     # Prototipos de nuevas características
└── scripts/            # Scripts Python para experimentación
    └── benchmarks/     # Pruebas de rendimiento
```

## Notebooks

### Exploratory
Análisis exploratorio de datos XPS y pruebas de concepto.

**Ejemplos:**
- `01_data_loading_exploration.ipynb` - Exploración de formatos de datos
- `02_element_identification.ipynb` - Tests de identificación automática
- `03_calibration_methods.ipynb` - Comparación de métodos de calibración

### Validation
Validación de métodos implementados contra resultados conocidos o software de referencia.

**Ejemplos:**
- `shirley_background_validation.ipynb` - Validar contra CASA XPS
- `peak_fitting_comparison.ipynb` - Comparar con lmfit directo

### Prototypes
Prototipos de funcionalidad futura antes de integración en el paquete principal.

**Ejemplos:**
- `machine_learning_element_id.ipynb` - Prototipo ML
- `gui_mockups.ipynb` - Diseño de interfaz gráfica

## Scripts

Scripts Python standalone para tareas específicas de experimentación.

**Estructura recomendada:**
```python
#!/usr/bin/env python3
\"\"\"
Descripción del experimento.

Uso:
    python script.py --input data/sample.txt --output results/
\"\"\"
```

## Benchmarks

Medición de performance de diferentes implementaciones.

**Formato:**
```python
import timeit

def benchmark_method_a():
    # ...
    
def benchmark_method_b():
    # ...

if __name__ == "__main__":
    time_a = timeit.timeit(benchmark_method_a, number=1000)
    time_b = timeit.timeit(benchmark_method_b, number=1000)
    print(f"Method A: {time_a:.4f}s")
    print(f"Method B: {time_b:.4f}s")
```

## Convenciones

1. **No commitear datos grandes** - Usar `.gitignore` para datasets
2. **Numerar notebooks** - `01_`, `02_`, etc. para orden lógico
3. **Limpiar outputs** - Antes de commit, limpiar outputs de células
4. **Documentación clara** - Markdown cells explicando cada paso
5. **No usar paths absolutos** - Usar paths relativos al repo

## Jupyter Setup

```bash
# Instalar kernel
uv sync --group jupyter

# Iniciar Jupyter
jupyter notebook experiments/notebooks/
```

---

**Nota:** Este directorio es para experimentación. Código production-ready debe ir en `src/`.
