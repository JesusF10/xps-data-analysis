# Tutorial 3: Identificación de Elementos

**Nivel:** Intermedio  
**Tiempo estimado:** 20-25 minutos  
**Requisitos:** Tutoriales 1 y 2 completados

---

## Objetivos

Al completar este tutorial aprenderás a:

1. Identificar elementos presentes en una muestra
2. Usar la base de datos de referencia
3. Buscar elementos por energía de enlace
4. Identificar compuestos químicos
5. Interpretar espectros survey

---

## 1. Cargar Base de Datos de Referencia

```python
from xps_analyzer import load_reference_database, load_single_file

# Cargar base de datos
db = load_reference_database()

print(f"Elementos disponibles: {len(db.elements)}")
print(f"Símbolos: {list(db.elements.keys())}")
```

**Salida esperada:**
```
Elementos disponibles: 25
Símbolos: ['C', 'O', 'N', 'Si', 'Al', 'Fe', 'Ti', 'Cu', 'Au', ...]
```

---

## 2. Consultar Información de Elementos

### Información Básica

```python
# Obtener elemento
carbon = db.elements["C"]

print(f"Símbolo: {carbon.symbol}")
print(f"Nombre: {carbon.element}")
print(f"Número atómico: {carbon.atomic_number}")
print(f"Energía de referencia: {carbon.binding_energy_most_useful} eV")
```

**Salida:**
```
Símbolo: C
Nombre: Carbon
Número atómico: 6
Energía de referencia: 284.8 eV
```

### Líneas Fotoelectrónicas

```python
print(f"\nLíneas fotoelectrónicas para {carbon.symbol}:")
for line in carbon.photoelectron_lines:
    print(f"  {line.line}: {line.binding_energy} eV ({line.type})")
```

**Salida:**
```
Líneas fotoelectrónicas para C:
  1s: 284.8 eV (core)
  2s: 19.4 eV (valence)
  2p: 11.3 eV (valence)
```

### Compuestos de Referencia

```python
print(f"\nCompuestos de {carbon.symbol}:")
for comp_name, compound in carbon.compounds.items():
    print(f"  {comp_name}:")
    print(f"    Orbital: {compound.orbital}")
    print(f"    Rango BE: {compound.binding_energy_range}")
    if compound.peak_position:
        print(f"    Posición pico: {compound.peak_position} eV")
```

**Salida:**
```
Compuestos de C:
  Carbonato:
    Orbital: 1s
    Rango BE: (288.0, 290.0)
    Posición pico: 289.0 eV
  C-O (alcohol, éter):
    Orbital: 1s
    Rango BE: (285.5, 286.5)
    Posición pico: 286.0 eV
```

---

## 3. Buscar Elementos por Energía

### Búsqueda Simple

```python
# Buscar qué elementos tienen líneas cerca de 284 eV
candidates = db.search_by_binding_energy(284.0, tolerance=2.0)

print(f"Elementos candidatos para 284.0 ± 2.0 eV:")
for elem in candidates:
    print(f"  {elem.symbol} ({elem.element})")
    # Encontrar qué línea coincide
    for line in elem.photoelectron_lines:
        if abs(line.binding_energy - 284.0) <= 2.0:
            print(f"    → {line.line}: {line.binding_energy} eV")
```

**Salida:**
```
Elementos candidatos para 284.0 ± 2.0 eV:
  C (Carbon)
    → 1s: 284.8 eV
```

### Búsqueda Múltiple

```python
# Identificar múltiples picos
observed_peaks = [284.5, 399.2, 531.0]

print("Identificación de picos observados:\n")
for peak in observed_peaks:
    candidates = db.search_by_binding_energy(peak, tolerance=2.0)
    print(f"Pico en {peak} eV:")
    for elem in candidates:
        print(f"  → Posible: {elem.symbol} {elem.element}")
    print()
```

**Salida:**
```
Identificación de picos observados:

Pico en 284.5 eV:
  → Posible: C Carbon

Pico en 399.2 eV:
  → Posible: N Nitrogen

Pico en 531.0 eV:
  → Posible: O Oxygen
```

---

## 4. Análisis de Espectro Survey

### Identificar Elementos Presentes

```python
from xps_analyzer.reference_data import identify_elements_in_spectrum

# Cargar dataset y obtener survey
dataset = load_single_file("data/raw/samples/muestra1.txt")
survey = dataset.spectra["survey"]

# Identificar elementos
identified = identify_elements_in_spectrum(survey, db, threshold=0.1)

print("Elementos identificados en survey:")
for element_info in identified:
    symbol = element_info['symbol']
    confidence = element_info['confidence']
    peak_energy = element_info['peak_energy']
    
    print(f"  {symbol}: {confidence:.1%} confianza @ {peak_energy:.1f} eV")
```

**Salida esperada:**
```
Elementos identificados en survey:
  C: 95.2% confianza @ 284.8 eV
  O: 87.3% confianza @ 531.2 eV
  N: 65.4% confianza @ 399.5 eV
  Si: 45.2% confianza @ 103.4 eV
```

### Interpretar Confianza

- **> 80%:** Muy probable - pico claro e intenso
- **60-80%:** Probable - pico visible pero puede haber interferencia
- **40-60%:** Posible - pico débil o solapado
- **< 40%:** Incierto - verificar con espectro de alta resolución

---

## 5. Identificación de Compuestos

### Buscar Estados Químicos

```python
from xps_analyzer.reference_data import suggest_compounds

# Obtener espectro de alta resolución
c1s = dataset.spectra["C 1s"]

# Buscar compuestos de carbono
compounds = suggest_compounds(c1s, db, element_symbol="C")

print("Compuestos sugeridos para C 1s:")
for comp in compounds:
    print(f"\n{comp['compound_name']}:")
    print(f"  Posición esperada: {comp['expected_position']} eV")
    print(f"  Posición observada: {comp['observed_position']:.2f} eV")
    print(f"  Match score: {comp['score']:.2f}")
```

**Salida esperada:**
```
Compuestos sugeridos para C 1s:

C-C/C-H (sp2/sp3):
  Posición esperada: 284.8 eV
  Posición observada: 284.75 eV
  Match score: 0.95

C-O (alcohol):
  Posición esperada: 286.0 eV
  Posición observada: 286.15 eV
  Match score: 0.82

C=O (carbonilo):
  Posición esperada: 287.5 eV
  Posición observada: 287.65 eV
  Match score: 0.78
```

---

## 6. Análisis Completo de Muestra

### Pipeline Completo

```python
from xps_analyzer.preprocessing import calibrate_sample

# 1. Cargar datos
dataset = load_single_file("data/raw/samples/muestra1.txt")

# 2. Calibrar
carbon_ref = db.elements["C"]
calibrated = calibrate_sample(dataset, carbon_ref, inplace=False)

# 3. Identificar elementos en survey
survey = calibrated.spectra["survey"]
elements = identify_elements_in_spectrum(survey, db, threshold=0.4)

print("=== ANÁLISIS COMPLETO DE MUESTRA ===\n")
print(f"Archivo: {dataset.filename}")
print(f"Espectros: {list(dataset.spectra.keys())}\n")

print("Elementos detectados:")
for elem in elements:
    symbol = elem['symbol']
    confidence = elem['confidence']
    peak = elem['peak_energy']
    
    # Obtener nombre completo
    element_ref = db.elements.get(symbol)
    name = element_ref.element if element_ref else "Desconocido"
    
    print(f"  [{symbol:2s}] {name:15s} | {confidence:5.1%} @ {peak:6.1f} eV")

# 4. Análisis detallado de regiones de alta resolución
print("\nAnálisis de espectros de alta resolución:")
for region_name, spectrum in calibrated.spectra.items():
    if region_name != "survey":
        # Extraer símbolo del elemento (ej: "C 1s" -> "C")
        symbol = region_name.split()[0]
        
        if symbol in db.elements:
            print(f"\n{region_name}:")
            compounds = suggest_compounds(spectrum, db, element_symbol=symbol)
            
            if compounds:
                for comp in compounds[:3]:  # Top 3
                    print(f"  - {comp['compound_name']}: "
                          f"score {comp['score']:.2f}")
            else:
                print("  (no se encontraron compuestos)")
```

---

## 7. Exportar Resultados de Identificación

### Crear Reporte

```python
from pathlib import Path
import json

def create_identification_report(dataset, db, output_path):
    """Crea reporte JSON de identificación."""
    
    report = {
        "filename": dataset.filename,
        "timestamp": "2024-01-15T10:30:00",
        "elements": {},
        "spectra": {}
    }
    
    # Identificar elementos en survey
    if "survey" in dataset.spectra:
        survey = dataset.spectra["survey"]
        elements = identify_elements_in_spectrum(survey, db)
        
        for elem in elements:
            symbol = elem['symbol']
            report["elements"][symbol] = {
                "confidence": float(elem['confidence']),
                "peak_energy": float(elem['peak_energy']),
                "element_name": db.elements[symbol].element
            }
    
    # Analizar espectros de alta resolución
    for region_name, spectrum in dataset.spectra.items():
        if region_name != "survey":
            symbol = region_name.split()[0]
            
            if symbol in db.elements:
                compounds = suggest_compounds(spectrum, db, symbol)
                
                report["spectra"][region_name] = {
                    "element": symbol,
                    "compounds": [
                        {
                            "name": c['compound_name'],
                            "score": float(c['score']),
                            "expected_position": float(c['expected_position']),
                            "observed_position": float(c['observed_position'])
                        }
                        for c in compounds
                    ]
                }
    
    # Guardar
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Reporte guardado en: {output_path}")

# Uso
create_identification_report(
    calibrated, 
    db, 
    "data/results/reports/muestra1_identification.json"
)
```

---

## 8. Visualización de Identificación

### Marcar Picos Identificados

```python
import matplotlib.pyplot as plt

# Obtener survey
survey = calibrated.spectra["survey"]

# Identificar elementos
elements = identify_elements_in_spectrum(survey, db, threshold=0.4)

# Plotear survey
plt.figure(figsize=(12, 6))
plt.plot(survey.binding_energy, survey.intensity, color='blue', alpha=0.7)

# Marcar elementos identificados
colors = ['red', 'green', 'orange', 'purple', 'brown']
for i, elem in enumerate(elements):
    peak_energy = elem['peak_energy']
    symbol = elem['symbol']
    confidence = elem['confidence']
    
    # Línea vertical
    plt.axvline(x=peak_energy, color=colors[i % len(colors)], 
                linestyle='--', alpha=0.6)
    
    # Etiqueta
    plt.text(peak_energy, plt.ylim()[1] * 0.9, 
             f"{symbol}\n{confidence:.0%}",
             ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor=colors[i % len(colors)], alpha=0.3))

plt.xlabel("Energía de Enlace (eV)")
plt.ylabel("Intensidad (cuentas)")
plt.title("Survey con Elementos Identificados")
plt.gca().invert_xaxis()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## 9. Casos Especiales

### Elementos con Múltiples Líneas Visibles

```python
# Ejemplo: Hierro (Fe) tiene 2p3/2 y 2p1/2 (doublet)
iron = db.elements["Fe"]

print(f"Líneas de {iron.element}:")
for line in iron.photoelectron_lines:
    print(f"  {line.line}: {line.binding_energy} eV")

if iron.spin_orbital_splitting:
    print(f"Spin-orbit splitting: {iron.spin_orbital_splitting} eV")
```

### Elementos con Solapamiento

```python
# Verificar solapamiento entre elementos
def check_overlap(energy1, energy2, tolerance=2.0):
    return abs(energy1 - energy2) < tolerance

# Ejemplo: Verificar si Ti 2p y N 1s pueden solaparse
ti = db.elements["Ti"]
n = db.elements["N"]

ti_2p = next(line.binding_energy for line in ti.photoelectron_lines 
             if line.line == "2p3/2")
n_1s = next(line.binding_energy for line in n.photoelectron_lines 
            if line.line == "1s")

if check_overlap(ti_2p, n_1s):
    print(f"ADVERTENCIA: Ti 2p ({ti_2p} eV) puede solaparse con N 1s ({n_1s} eV)")
    print("  → Usar espectro de alta resolución para distinguir")
```

---

## 10. Mejores Prácticas

### DO:
1. **Calibrar ANTES de identificar** para resultados precisos
2. **Usar survey para identificación inicial** y espectros de alta resolución para confirmar
3. **Considerar contexto de la muestra** (composición esperada)
4. **Verificar múltiples líneas** cuando sea posible

### DON'T:
1. **No confiar únicamente en survey** para identificación definitiva
2. **No ignorar picos débiles** (pueden ser elementos en baja concentración)
3. **No asumir pureza** - considerar contaminación
4. **No identificar sin calibrar** primero

---

## Resumen

En este tutorial aprendiste a:

- Usar la base de datos de referencia con `load_reference_database()`
- Buscar elementos por energía con `search_by_binding_energy()`
- Identificar elementos en surveys con `identify_elements_in_spectrum()`
- Sugerir compuestos químicos con `suggest_compounds()`
- Crear reportes de identificación
- Visualizar elementos identificados
- Manejar casos especiales (solapamientos, múltiples líneas)

---

## Próximos Pasos

- **Análisis Cuantitativo:** Calcular concentraciones atómicas (Fase 1)
- **Peak Fitting:** Deconvolución de picos (Fase 1)
- **Machine Learning:** Identificación automática avanzada (Fase 3)

---

## Solución de Problemas

### No Se Identifican Elementos Esperados

```python
# Reducir threshold
elements = identify_elements_in_spectrum(survey, db, threshold=0.2)

# O buscar manualmente
peak_energy = 399.5  # Tu pico observado
candidates = db.search_by_binding_energy(peak_energy, tolerance=3.0)
```

### Falsos Positivos

```python
# Aumentar threshold
elements = identify_elements_in_spectrum(survey, db, threshold=0.6)

# Verificar con espectros de alta resolución
if "N 1s" in dataset.spectra:
    print("Nitrógeno confirmado con espectro de alta resolución")
```

### Elemento No Está en Base de Datos

```python
# Verificar elementos disponibles
print(f"Elementos: {list(db.elements.keys())}")

# Si falta, agregar manualmente (ver API_DOCS.md)
# O reportar en GitHub Issues para futuras versiones
```

---

**Versión:** 0.5.0-alpha  
**Última actualización:** Marzo 2026
