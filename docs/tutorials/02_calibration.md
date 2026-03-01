# Tutorial 2: Calibración de Espectros XPS

**Nivel:** Intermedio  
**Tiempo estimado:** 15-20 minutos  
**Requisitos:** Tutorial 1 completado

---

## Objetivos

Al completar este tutorial aprenderás a:

1. Entender por qué la calibración es necesaria
2. Calibrar espectros usando elementos de referencia
3. Usar carbono adventicio (C 1s) como referencia estándar
4. Calibrar datasets completos
5. Verificar la calibración

---

## 1. ¿Por Qué Calibrar?

Los espectros XPS pueden tener desplazamientos en la energía de enlace debido a:

- **Carga de la muestra:** Muestras aislantes acumulan carga
- **Deriva del instrumento:** Variaciones en el voltaje de referencia
- **Efectos químicos:** Diferentes estados de oxidación

**Solución:** Calibrar usando un pico de referencia conocido (típicamente C 1s @ 284.8 eV).

---

## 2. Calibración Básica de un Espectro

### Cargar Datos

```python
from xps_analyzer import load_single_file, load_reference_database
from xps_analyzer.preprocessing import calibrate_spectrum
import numpy as np

# Cargar archivo y base de datos
dataset = load_single_file("data/raw/samples/muestra1.txt")
db = load_reference_database()

# Obtener espectro C 1s
c1s = dataset.spectra["C 1s"]
```

### Encontrar el Pico Observado

```python
# Encontrar la posición del pico máximo
max_index = np.argmax(c1s.intensity)
observed_peak = c1s.binding_energy[max_index]

print(f"Pico observado en: {observed_peak:.2f} eV")
```

**Salida esperada:**
```
Pico observado en: 285.6 eV
```

### Calcular el Desplazamiento

```python
# Obtener referencia de carbono
carbon_ref = db.elements["C"]
reference_energy = carbon_ref.binding_energy_most_useful  # 284.8 eV

# Calcular shift
shift = reference_energy - observed_peak
print(f"Desplazamiento: {shift:.2f} eV")
```

**Salida esperada:**
```
Desplazamiento: -0.80 eV
```

### Aplicar Calibración

```python
# Calibrar el espectro (sin modificar el original)
calibrated_c1s = calibrate_spectrum(c1s, shift, inplace=False)

# Verificar
new_peak_index = np.argmax(calibrated_c1s.intensity)
new_peak = calibrated_c1s.binding_energy[new_peak_index]

print(f"Nuevo pico calibrado en: {new_peak:.2f} eV")
print(f"Diferencia con referencia: {abs(new_peak - reference_energy):.3f} eV")
```

**Salida esperada:**
```
Nuevo pico calibrado en: 284.80 eV
Diferencia con referencia: 0.000 eV
```

---

## 3. Calibrar un Dataset Completo

### Método Automático (Recomendado)

```python
from xps_analyzer.preprocessing import calibrate_sample

# Calibrar todos los espectros usando C 1s como referencia
calibrated_dataset = calibrate_sample(
    dataset, 
    carbon_ref, 
    inplace=False
)

# Verificar que todos los espectros fueron calibrados
print("Espectros calibrados:")
for region_name in calibrated_dataset.spectra.keys():
    original = dataset.spectra[region_name]
    calibrated = calibrated_dataset.spectra[region_name]
    
    # Verificar desplazamiento
    shift_applied = calibrated.binding_energy[0] - original.binding_energy[0]
    print(f"  {region_name}: shift = {shift_applied:+.2f} eV")
```

**Salida esperada:**
```
Espectros calibrados:
  survey: shift = -0.80 eV
  C 1s: shift = -0.80 eV
  O 1s: shift = -0.80 eV
  N 1s: shift = -0.80 eV
```

---

## 4. Calibración In-Place vs. Copia

### Crear una Copia (Recomendado)

```python
# No modifica el dataset original
calibrated = calibrate_sample(dataset, carbon_ref, inplace=False)

# El original permanece sin cambios
print(f"Original C 1s pico: {dataset.spectra['C 1s'].binding_energy[500]:.2f} eV")
print(f"Calibrado C 1s pico: {calibrated.spectra['C 1s'].binding_energy[500]:.2f} eV")
```

### Modificar In-Place (Avanzado)

```python
# CUIDADO: Modifica el dataset original
calibrate_sample(dataset, carbon_ref, inplace=True)

# Ahora el dataset original está calibrado
print(f"Dataset calibrado in-place")
```

**Advertencia:** `inplace=True` modifica permanentemente los datos. Úsalo solo si estás seguro.

---

## 5. Usar Otros Elementos de Referencia

### Oxígeno como Referencia

```python
# Obtener referencia de oxígeno
oxygen_ref = db.elements["O"]

# Calibrar usando O 1s
calibrated = calibrate_sample(dataset, oxygen_ref, inplace=False)

print(f"Calibrado usando O 1s @ {oxygen_ref.binding_energy_most_useful} eV")
```

### ¿Cuándo Usar Otros Elementos?

- **Oro (Au 4f):** Muestras conductivas, patrón interno
- **Silicio (Si 2p):** Sustratos de silicio
- **Cobre (Cu 2p):** Muestras metálicas

**Nota:** C 1s (carbono adventicio) es el estándar más común porque aparece en casi todas las muestras.

---

## 6. Verificar la Calibración

### Comparar Antes y Después

```python
import matplotlib.pyplot as plt

# Obtener espectros
original = dataset.spectra["C 1s"]
calibrated_spec = calibrated.spectra["C 1s"]

# Plotear ambos
plt.figure(figsize=(10, 6))
plt.plot(original.binding_energy, original.intensity, 
         label="Original", alpha=0.7)
plt.plot(calibrated_spec.binding_energy, calibrated_spec.intensity, 
         label="Calibrado", alpha=0.7, linestyle='--')

# Marcar referencia
plt.axvline(x=284.8, color='red', linestyle=':', 
            label='Referencia C 1s (284.8 eV)')

plt.xlabel("Energía de Enlace (eV)")
plt.ylabel("Intensidad (cuentas)")
plt.title("Comparación: Original vs. Calibrado")
plt.legend()
plt.gca().invert_xaxis()
plt.show()
```

### Verificar Múltiples Picos

```python
# Tabla de verificación
print("Verificación de Calibración:")
print("-" * 60)

# Elementos esperados y sus energías
expected = {
    "C 1s": 284.8,
    "O 1s": 531.0,
    "N 1s": 399.0
}

for region, expected_energy in expected.items():
    if region in calibrated.spectra:
        spectrum = calibrated.spectra[region]
        max_idx = np.argmax(spectrum.intensity)
        observed = spectrum.binding_energy[max_idx]
        diff = observed - expected_energy
        
        print(f"{region:10s} | Esperado: {expected_energy:6.1f} eV | "
              f"Observado: {observed:6.2f} eV | Δ = {diff:+.2f} eV")
```

**Salida esperada:**
```
Verificación de Calibración:
------------------------------------------------------------
C 1s       | Esperado:  284.8 eV | Observado: 284.80 eV | Δ = +0.00 eV
O 1s       | Esperado:  531.0 eV | Observado: 531.35 eV | Δ = +0.35 eV
N 1s       | Esperado:  399.0 eV | Observado: 399.12 eV | Δ = +0.12 eV
```

**Interpretación:**
- Δ < 0.5 eV: Calibración excelente
- Δ < 1.0 eV: Calibración aceptable
- Δ > 1.0 eV: Revisar calibración o considerar estados químicos diferentes

---

## 7. Calibrar Múltiples Archivos

```python
from xps_analyzer.data_loader import load_all_data

# Cargar todos los archivos
datasets = load_all_data("data/raw/samples/")

# Calibrar cada uno
calibrated_datasets = {}

for filename, dataset in datasets.items():
    try:
        # Verificar que tiene C 1s
        if "C 1s" in dataset.spectra:
            calibrated = calibrate_sample(dataset, carbon_ref, inplace=False)
            calibrated_datasets[filename] = calibrated
            print(f"✓ {filename} calibrado")
        else:
            print(f"✗ {filename} - no tiene espectro C 1s")
    except Exception as e:
        print(f"✗ {filename} - error: {e}")

print(f"\nTotal calibrados: {len(calibrated_datasets)}/{len(datasets)}")
```

---

## 8. Guardar Datos Calibrados

```python
import pickle
from pathlib import Path

# Crear directorio de salida
output_dir = Path("data/processed/calibrated/")
output_dir.mkdir(parents=True, exist_ok=True)

# Guardar dataset calibrado
output_file = output_dir / "muestra1_calibrated.pkl"
with open(output_file, 'wb') as f:
    pickle.dump(calibrated, f)

print(f"Dataset calibrado guardado en: {output_file}")
```

### Cargar Datos Calibrados

```python
# Cargar después
with open(output_file, 'rb') as f:
    loaded_dataset = pickle.load(f)

print(f"Dataset cargado: {loaded_dataset.filename}")
```

---

## 9. Casos Especiales

### Sin Carbono Adventicio

Si tu muestra no tiene carbono adventicio:

```python
# Opción 1: Usar otro elemento común
if "O 1s" in dataset.spectra:
    oxygen_ref = db.elements["O"]
    calibrated = calibrate_sample(dataset, oxygen_ref, inplace=False)

# Opción 2: Calibración manual con shift conocido
known_shift = -1.2  # eV (obtenido de otra fuente)
for region_name, spectrum in dataset.spectra.items():
    calibrated_spec = calibrate_spectrum(spectrum, known_shift, inplace=False)
    # ... procesar
```

### Múltiples Estados de Carbono

Si el C 1s muestra múltiples picos:

```python
# Usar el pico de menor energía (carbono sp2/sp3)
c1s = dataset.spectra["C 1s"]

# Encontrar región de interés (280-286 eV)
mask = (c1s.binding_energy >= 280) & (c1s.binding_energy <= 286)
region_energies = c1s.binding_energy[mask]
region_intensities = c1s.intensity[mask]

# Pico máximo en esa región
max_idx = np.argmax(region_intensities)
observed_peak = region_energies[max_idx]

# Calibrar usando ese pico
shift = 284.8 - observed_peak
calibrated = calibrate_spectrum(c1s, shift, inplace=False)
```

---

## 10. Mejores Prácticas

### DO:
1. **Siempre verificar la calibración** comparando con valores esperados
2. **Usar `inplace=False`** para conservar datos originales
3. **Documentar el elemento de referencia** usado
4. **Calibrar ANTES de análisis cuantitativo**

### DON'T:
1. **No calibrar múltiples veces** (acumula errores)
2. **No usar picos contaminados** como referencia
3. **No ignorar advertencias** de elementos no encontrados
4. **No calibrar datos ya calibrados**

---

## Resumen

En este tutorial aprendiste a:

- Entender la necesidad de calibración en XPS
- Calibrar espectros individuales con `calibrate_spectrum()`
- Calibrar datasets completos con `calibrate_sample()`
- Usar diferentes elementos de referencia
- Verificar la calidad de la calibración
- Manejar casos especiales (múltiples picos, sin C adventicio)
- Guardar y cargar datos calibrados

---

## Próximos Pasos

- **Tutorial 3:** [Identificación de Elementos](03_element_identification.md)
- **Análisis Avanzado:** Peak fitting (disponible en Fase 1)

---

## Solución de Problemas

### Error: "Elemento de referencia 'X' no encontrado"

```python
# Verificar espectros disponibles
print(f"Espectros: {list(dataset.spectra.keys())}")

# Verificar que el elemento coincide con el nombre de región
# Correcto: "C" busca "C 1s", "C 2s", "C 2p", etc.
```

### Error: "no tiene binding_energy_most_useful definido"

```python
# Verificar que el elemento tiene valor de referencia
element = db.elements["C"]
if element.binding_energy_most_useful is None:
    print("Elemento sin energía de referencia definida")
    # Usar línea específica
    line = element.photoelectron_lines[0]
    reference_energy = line.binding_energy
```

### Calibración Produce Valores Extraños

```python
# Verificar que el pico detectado es correcto
c1s = dataset.spectra["C 1s"]
max_idx = np.argmax(c1s.intensity)
peak = c1s.binding_energy[max_idx]

if peak < 280 or peak > 290:
    print(f"Advertencia: Pico en {peak:.1f} eV está fuera del rango esperado")
    print("Revisar datos o usar calibración manual")
```

---

**Versión:** 0.5.0-alpha  
**Última actualización:** Marzo 2026
