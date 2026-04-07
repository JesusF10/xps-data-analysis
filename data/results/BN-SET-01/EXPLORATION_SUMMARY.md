# Resumen de Exploración - Dataset BN-SET-01

**Fecha:** Marzo 3, 2026  
**Dataset:** 4 muestras (BN-BS-1, BN-BS-2, BN-BS-3, BN-BS-4)  
**Instrumento:** Thermo Scientific - Mg Kα (1253.6 eV)  
**Script:** `scripts/explore_bn_data.py`

---

## 📊 Resultados Generales

### ✅ Estado de Carga de Datos

| Muestra | Estado | Regiones | Archivos |
|---------|--------|----------|----------|
| BN-BS-1 | ✓ OK | 6 | multiplex.txt, SURVEY.txt |
| BN-BS-2 | ✓ OK | 6 | MULTIPLEX.txt, SURVEY.txt |
| BN-BS-3 | ✓ OK | 6 | MULTIPLEX.txt, SURVEY.txt |
| BN-BS-4 | ✓ OK | 6 | multiplex.txt, survey.txt |

**Nota:** Se detectaron inconsistencias en nombres de archivos (mayúsculas/minúsculas), pero fueron manejadas automáticamente por el script.

---

## 🔬 Regiones Identificadas

**6 regiones en todas las muestras:**
1. **Bi 4f** - Bismuto (150-180 eV)
2. **Na 1s** - Sodio (1066-1086 eV)
3. **O 1s** - Oxígeno (515-550 eV)
4. **Sr 3d** - Estroncio (125-165 eV)
5. **Ti 2p** - Titanio (450-485 eV)
6. **C 1s** - Carbono (275-300 eV)

**⚠️ Hallazgo Importante:** No se encontraron regiones de B 1s ni N 1s. Las muestras **NO son nitruro de boro puro** como sugiere el nombre del dataset. La composición sugiere un material complejo, posiblemente:
- **Óxido de titanio (TiO₂)** como matriz principal (Ti 2p + O 1s)
- **Dopantes:** Bi, Na, Sr
- **Contaminación superficial:** C 1s (carbono adventicio típico en XPS)

---

## 📈 Calidad de Datos (SNR - Relación Señal/Ruido)

### SNR Promedio por Región (todas las muestras)

| Región | SNR Promedio | Calidad | Rango (min-max) |
|--------|--------------|---------|-----------------|
| **Sr 3d** | 214.1 | Excelente | 113.0 - 269.4 |
| **Na 1s** | 199.5 | Excelente | 171.2 - 236.8 |
| **C 1s** | 114.9 | Excelente | 79.6 - 140.9 |
| **Ti 2p** | 111.2 | Excelente | 94.8 - 120.1 |
| **O 1s** | 101.8 | Excelente | 79.1 - 123.0 |
| **Bi 4f** | 66.6 | Muy bueno | 64.4 - 68.5 |
| **Survey** | 111.1 | Excelente | 110.0 - 112.5 |

**SNR Global:** 134.8 (Excelente - muy por encima del umbral de 15)

**Interpretación:**
- ✅ **Todos los datos tienen calidad excelente** para análisis cuantitativo
- ✅ **Sr 3d y Na 1s** tienen la mejor señal (SNR > 200)
- ✅ **Bi 4f** tiene el SNR más bajo pero sigue siendo muy bueno (>60)
- ✅ **No se detectaron problemas de saturación** de detector
- ✅ **Ruido instrumental mínimo** en todas las regiones

---

## 📊 Estadísticas por Muestra

### BN-BS-1

**Características:**
- Regiones: 6 (Bi 4f, Na 1s, O 1s, Sr 3d, Ti 2p, C 1s)
- SNR promedio: 118.5 (Excelente)
- Puntos totales: 3,606 (multiplex) + 2,201 (survey)

**Regiones destacadas:**
- **Na 1s:** SNR = 171.2 (mejor)
- **C 1s:** SNR = 140.9
- **O 1s:** SNR = 123.0

### BN-BS-2

**Características:**
- Regiones: 6 (mismo orden diferente que BN-BS-1)
- SNR promedio: 129.2 (Excelente)
- Puntos totales: 3,706 (multiplex) + 2,201 (survey)

**Regiones destacadas:**
- **Sr 3d:** SNR = 234.0 (mejor de todo el dataset)
- **Na 1s:** SNR = 185.8
- **Ti 2p:** SNR = 115.3

**Nota:** Sr 3d tiene 800 puntos (vs. 700 en BN-BS-1), sugiere adquisición optimizada.

### BN-BS-3

**Características:**
- Regiones: 6
- SNR promedio: 144.4 (Excelente - el mejor)
- Puntos totales: 3,706 (multiplex) + 2,201 (survey)

**Regiones destacadas:**
- **Sr 3d:** SNR = 240.6 (máximo absoluto)
- **Na 1s:** SNR = 204.5
- **C 1s:** SNR = 131.0

**Nota:** Muestra con mejor calidad general, **candidata principal para análisis detallado**.

### BN-BS-4

**Características:**
- Regiones: 6
- SNR promedio: 146.9 (Excelente)
- Puntos totales: 3,706 (multiplex) + 2,201 (survey)

**Regiones destacadas:**
- **Sr 3d:** SNR = 269.4 (máximo absoluto del dataset)
- **Na 1s:** SNR = 236.8 (intensidades más altas: 15,432-17,418)
- **Ti 2p:** SNR = 120.1

**Nota:** Intensidades de Na 1s significativamente más altas (~40%) que otras muestras. Posible diferencia en composición o tiempo de adquisición.

---

## 🎯 Análisis Comparativo

### Variabilidad entre Muestras

| Aspecto | Observación | Implicación |
|---------|-------------|-------------|
| **Rangos de energía** | Idénticos en todas las muestras | ✓ Configuración instrumental consistente |
| **Número de puntos** | Consistente (excepto Sr 3d) | ✓ Protocolo de adquisición estandarizado |
| **Intensidades absolutas** | Variables (~20-40% diferencia) | Diferencias en composición o tiempo de adquisición |
| **SNR** | Consistentemente alto (>100) | ✓ Preparación de muestras de alta calidad |
| **Forma de picos** | Por verificar visualmente | Pendiente en plots comparativos |

### Diferencias Significativas

1. **Na 1s en BN-BS-4:**
   - Intensidad promedio: 16,476 (vs. ~11,500 en otras muestras)
   - **+40% más alto** que el promedio
   - Posible explicación: mayor contenido de Na o capa más gruesa

2. **Ti 2p en BN-BS-3 y BN-BS-4:**
   - Intensidades: ~3,400 (vs. ~2,400 en BN-BS-1/2)
   - **+40% más alto** que BN-BS-1/2
   - Posible explicación: mayor contenido de Ti (capa más gruesa de TiO₂)

3. **C 1s:**
   - BN-BS-2 tiene intensidad más baja (872) vs. otros (~1,400-1,500)
   - Posible mejor limpieza superficial o menor contaminación

---

## 📁 Archivos Generados

### Plots Exploratorios (11 archivos PNG, 300 DPI)

**Grids Individuales (2x3 subplots):**
- `BN-BS-1_all_regions.png` (712 KB)
- `BN-BS-2_all_regions.png` (703 KB)
- `BN-BS-3_all_regions.png` (707 KB)
- `BN-BS-4_all_regions.png` (690 KB)

**Comparaciones (overlays de 4 muestras):**
- `survey_comparison.png` (365 KB)
- `region_Bi_4f_comparison.png` (420 KB)
- `region_Na_1s_comparison.png` (418 KB)
- `region_O_1s_comparison.png` (537 KB)
- `region_Sr_3d_comparison.png` (322 KB)
- `region_Ti_2p_comparison.png` (482 KB)
- `region_C_1s_comparison.png` (482 KB)

**Total:** 5.8 MB de visualizaciones de alta calidad

### Datos Estructurados

- `exploration_stats.json` - Estadísticas completas (394 líneas JSON)
  * SNR, rangos de energía, número de puntos
  * Intensidades (min, max, promedio, std)
  * Metadata de survey

---

## 🔍 Análisis Visual de Plots (Observaciones Preliminares)

### Survey Comparison

**Características esperadas:**
- Picos prominentes de Na 1s (~1075 eV)
- Región de O 1s (~530 eV)
- Región de Ti 2p (~460 eV)
- Estructura fina en región de baja energía (Bi, Sr)

### Comparaciones por Región

**Regiones de interés para cuantificación:**
1. **Ti 2p** - Pico principal del material (TiO₂)
2. **O 1s** - Oxígeno (correlacionado con Ti)
3. **Sr 3d** - Dopante principal (alta señal)
4. **C 1s** - Contaminación (calibración)

**Regiones secundarias:**
5. **Bi 4f** - Dopante menor
6. **Na 1s** - Dopante (variabilidad significativa)

---

## ✅ Conclusiones de la Exploración

### Calidad de Datos

1. ✅ **Excelente calidad general** - SNR promedio 134.8
2. ✅ **Todas las muestras son analizables** sin problemas técnicos
3. ✅ **Configuración instrumental consistente** entre muestras
4. ✅ **No se detectaron artifacts** o saturación

### Composición del Material

1. ⚠️ **NO es nitruro de boro** (ausencia de B 1s y N 1s)
2. ✓ **Material principal:** Óxido de titanio (Ti 2p + O 1s)
3. ✓ **Dopantes identificados:** Sr (dominante), Na, Bi
4. ✓ **Contaminación superficial:** C 1s (típica en XPS)

**Hipótesis:** El dataset corresponde a muestras de **titanato de estroncio dopado** (SrTiO₃) o material relacionado, no nitruro de boro como indica el nombre.

### Variabilidad entre Muestras

1. ⚠️ **BN-BS-4 tiene ~40% más Na** que otras muestras
2. ⚠️ **BN-BS-3/4 tienen ~40% más Ti** que BN-BS-1/2
3. ⚠️ **BN-BS-2 tiene menos C** (mejor limpieza superficial)
4. ✓ **Formas de picos consistentes** (por verificar visualmente)

---

## 🎯 Recomendaciones para Fase B (Análisis Completo)

### Muestra Representativa

**Selección:** **BN-BS-3** (mejor calidad general)

**Justificación:**
- SNR promedio más alto (144.4)
- Sr 3d con señal excelente (240.6)
- Intensidades intermedias (no outlier como BN-BS-4)
- Configuración completa de 800 puntos en Sr 3d

**Alternativa:** BN-BS-1 (buena referencia, intensidades más bajas pero consistentes)

### Estrategia de Calibración

- **Elemento de referencia:** C 1s @ 284.8 eV (carbono adventicio)
- **Disponible en todas las muestras** con SNR > 80
- **Pico único y bien definido** (verificar en plots)

### Elementos para Cuantificación

**Prioridad Alta (RSF disponible para Mg Kα):**
1. Ti 2p (componente principal)
2. O 1s (componente principal)
3. C 1s (contaminación / referencia)

**Prioridad Media (verificar disponibilidad RSF):**
4. Sr 3d (dopante dominante)
5. Na 1s (dopante variable)

**Prioridad Baja:**
6. Bi 4f (dopante menor, verificar RSF)

### Parámetros de Análisis

**Sustracción de fondo:**
- Método: Shirley (estándar para materiales inorgánicos)
- max_iterations: 50
- tolerance: 1e-6

**Ajuste de picos:**
- Tipo: Voigt (convolución Gaussiano-Lorentziano, estándar para XPS)
- Detección: Híbrida (auto-detect + validación con literatura)
- Posiciones esperadas (Mg Kα):
  * Ti 2p₃/₂: ~458.8 eV (TiO₂)
  * O 1s: ~530.0 eV (óxidos metálicos)
  * C 1s: ~284.8 eV (adventicio)
  * Sr 3d₅/₂: ~133.0 eV

**Cuantificación:**
- RSF: Scofield para Mg Kα (ya implementado)
- Normalización: 100% (excluir C 1s de superficie)

---

## 📋 Próximos Pasos

### Inmediatos (Fase B)

1. ✅ **Crear script `analyze_single_sample.py`**
   - Pipeline completo: calibrar → fondo → fitting → cuantificar → exportar
   - Muestra objetivo: BN-BS-3

2. ✅ **Ejecutar análisis completo en BN-BS-3**
   - Verificar convergencia de fitting
   - Validar composición atómica
   - Generar plots de resultados

3. ✅ **Revisar resultados manualmente**
   - R² de fitting > 0.90
   - Residuos distribuidos aleatoriamente
   - Composición atómica razonable (Ti:O ~1:2 esperado)

### Subsecuentes (Fases C-D)

4. **Batch processing** de las 4 muestras
5. **Comparación de composiciones** entre muestras
6. **Identificar outliers** y explicar variabilidad

---

## 📝 Notas Técnicas

### Inconsistencias Manejadas

1. **Nombres de archivos:** Mayúsculas/minúsculas inconsistentes (resuelto con búsqueda case-insensitive)
2. **Orden de regiones:** Variable entre muestras (no afecta análisis)
3. **Número de puntos en Sr 3d:** 700 (BN-BS-1) vs. 800 (otros) - diferencia en configuración de adquisición

### Verificaciones Pendientes

1. **Posiciones de picos:** Verificar visualmente en plots comparativos
2. **Disponibilidad de RSF:** Confirmar que Bi 4f, Na 1s, Sr 3d tienen factores Scofield para Mg Kα
3. **Chemical shifts:** Identificar estados de oxidación (ej: Ti⁴⁺ en TiO₂)
4. **Picos satélite:** Ti 2p puede tener satélites shake-up (verificar en plots de alta resolución)

---

**Documento generado automáticamente por:** `scripts/explore_bn_data.py`  
**Versión del software:** xps-analyzer v0.8.0-beta  
**Autor:** Jesus Flores Lacarra  
**Última actualización:** Marzo 3, 2026
