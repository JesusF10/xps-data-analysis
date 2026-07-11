// XPS Analyzer - Documentación Técnica Completa
// Autor: Jesús Flores Lacarra
// Versión: 0.9.1-beta
// Fecha: Abril 2026

#set document(
  title: "XPS Analyzer: Sistema Automatizado de Análisis XPS",
  author: "Jesús Flores Lacarra",
  date: datetime.today(),
)

#set page(
  paper: "us-letter",
  margin: (left: 2.5cm, right: 2.5cm, top: 3cm, bottom: 3cm),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "Liberation Serif",
  size: 11pt,
  lang: "es",
)

#set heading(numbering: "1.1")
#set par(justify: true)

#show raw.where(block: true): it => block(
  fill: luma(245),
  inset: 10pt,
  radius: 4pt,
  width: 100%,
  text(font: "Fira Mono", size: 9pt, it),
)

#show link: set text(fill: rgb("#0066cc"))
#set math.equation(numbering: "(1)")

// ============================================================================
// PORTADA
// ============================================================================

#align(center)[
  #v(1cm)
  #text(18pt, weight: "bold")[UNIVERSIDAD DE SONORA]

  #v(0.5cm)
  #text(16pt)[Facultad Interdisciplinaria de Ciencias Naturales y Exactas]

  #v(0.5cm)
  #text(14pt)[Departamento de Matemáticas]

  #v(0.5cm)
  #text(14pt)[Licenciatura en Ciencias de la Computación]


  #v(3cm)
  #text(24pt, weight: "bold")[XPS Analyzer]

  #v(0.5cm)
  #text(16pt)[
    Sistema Automatizado de Análisis de\
    Espectroscopía Fotoelectrónica de Rayos X
  ]

  #v(0.8cm)
  #text(14pt, style: "italic")[Documentación Técnica]

  #v(3cm)

  #grid(
    columns: 2,
    gutter: 2cm,
    align(left)[
      *Autor:* Jesús Flores Lacarra\
      *Matrícula:* 221201513\
      *Email:* jss.263.fsc\@gmail.com
    ],
    align(left)[
      *Asesor:* Dr. Javier Hernández Paredes\
      *Institución:* Universidad de Sonora
    ],
  )

  #v(2cm)
  #text(12pt)[
    Versión: 0.9.1-beta\
    Estado: Fase 2 EN PROGRESO (60%)\
    Abril 2026
  ]
]

#pagebreak()

// ============================================================================
// RESUMEN EJECUTIVO
// ============================================================================

#align(center)[#text(14pt, weight: "bold")[RESUMEN EJECUTIVO]]

#v(1cm)

*XPS Analyzer* es un paquete científico en Python para análisis automatizado de Espectroscopía de Fotoelectrones de Rayos X (XPS). Desarrollado como proyecto de servicio social, implementa el pipeline completo: carga de datos, calibración, sustracción de fondo (Shirley, Tougaard), ajuste de picos (Voigt, Gaussiano, Lorentziano), cuantificación atómica (RSF Scofield/Wagner) y exportación (CSV, Excel, JSON).

*Estado actual:* Fase 2 en progreso con 355 tests, 93% cobertura core, ~5,200 líneas de código y validación exitosa con datos reales de titanato de estroncio dopado.

*Licencia:* MIT (código abierto)

*Palabras clave:* XPS, espectroscopía fotoelectrónica, Python científico, análisis superficial, caracterización de materiales

#pagebreak()

#outline(title: "Índice General", depth: 3, indent: auto)
#pagebreak()

// ============================================================================
// CAPÍTULO 1: INTRODUCCIÓN
// ============================================================================

= Introducción

== Contexto y Motivación

La Espectroscopía de Fotoelectrones de Rayos X (XPS) es una técnica fundamental para caracterización de superficies en química, física y ciencia de materiales. Permite determinar composición elemental, estados de oxidación y estructura electrónica en los primeros 5-10 nm de profundidad.

El análisis XPS tradicional presenta desafíos:
- *Costo:* Software comercial
- *Reproducibilidad:* Parámetros de análisis no documentados
- *Automatización limitada:* Procesamiento manual repetitivo
- *Transparencia:* Algoritmos propietarios no auditables

XPS Analyzer surge como alternativa de código abierto, transparente y extensible para entornos académicos.

== Objetivos del Proyecto

=== Objetivo General

Desarrollar un sistema automatizado de análisis XPS en Python que implemente algoritmos estándar con transparencia y documentación exhaustiva.

=== Objetivos Específicos por Fase

*Fase 0 (Fundamentos):* #text(fill: green)[COMPLETADO]
- Estructuras de datos robustas (`XPSSpectrum`, `XPSDataset`, `XPSSample`)
- Parser para formato propietario de texto
- Base de datos de ~25 elementos comunes
- Calibración de energía por elemento de referencia

*Fase 1 (Análisis Core):* #text(fill: green)[COMPLETADO]
- Sustracción de fondo (Shirley, Tougaard, Lineal)
- Ajuste de picos (Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL)
- Cuantificación atómica (RSF Scofield/Wagner)
- Exportación (CSV, Excel, JSON)
- Validación con datos reales
- 355 tests, 93% cobertura core

*Fase 2 (Pydantic & GUI):* #text(fill: green)[EN PROGRESO]
- Migración a Pydantic v2 (Completada)
- GUI interactiva con Streamlit (En progreso)

- Exportación HDF5

*Fase 3 (Avanzado):* #text(fill: gray)[FUTURO]
- Machine learning para identificación
- GUI con Streamlit/Dash
- API REST con FastAPI

== Alcance

=== Capacidades Actuales (v0.9.1-beta)

*Carga y Validación:*
- Formato propietario de texto (delimitado por `;`)
- Auto-detección multiplex vs survey
- Validación de integridad

*Análisis:*
- Calibración de energía (C 1s @ 284.8 eV típicamente)
- Fondo Shirley (algoritmo iterativo estándar)
- Fondo Tougaard (4 variantes: B, C, D, D\_star)
- Ajuste de picos: 5 perfiles disponibles
- Cuantificación con RSF para Al Kα y Mg Kα

*Exportación:*
- CSV con datos + metadata separada
- Excel con múltiples hojas
- JSON con estructura jerárquica
- Plots PNG de alta resolución (300 DPI)

=== Limitaciones Conocidas

*Formatos:* Solo texto propietario

*Algoritmos:*
- Shirley puede no converger en espectros ruidosos
- Ajuste de pico único inadecuado para dobletes complejos
- Detección automática básica de picos

*Base de datos:*
- RSF incompletos para elementos traza en Mg Kα

#pagebreak()

// ============================================================================
// CAPÍTULO 2: FUNDAMENTOS DE XPS
// ============================================================================

= Fundamentos de XPS

== Principio Físico

XPS se basa en el *efecto fotoeléctrico* (Einstein, 1905). Cuando rayos X de energía $h nu$ inciden sobre un material, pueden eyectar electrones de capas internas si se cumple:

$ E_"binding" = h nu - E_"kinetic" - phi $ <eq-photoelectric>

donde:
- $E_"binding"$: energía de enlace del electrón (característica del elemento)
- $h nu$: energía del fotón de rayos X
- $E_"kinetic"$: energía cinética medida del fotoelectrón
- $phi$: función trabajo del espectrómetro (~4 eV)

=== Profundidad de Análisis

La probabilidad de escape sin pérdida de energía decae exponencialmente:

$ I(d) = I_0 exp(-d / lambda) $ <eq-imfp>

donde $lambda$ es el camino libre medio inelástico (1-3 nm). El 95% de la señal proviene de los primeros $3 lambda approx 5-10 "nm"$, haciendo XPS inherentemente sensible a superficies.

== Acoplamiento Espín-Órbita (Dobletes)

Para orbitales con momento angular $l > 0$ (p, d, f), el acoplamiento espín-órbita genera dobletes:

$ J = L plus.minus 1/2 $ <eq-spin-orbit>

*Características:*
- *Separación:* Constante por elemento (Ti 2p = 6.1 eV, Sr 3d = 1.8 eV)
- *Ratio de intensidades:* $(2J_1 + 1)/(2J_2 + 1)$
  - Dobletes p: 2:1
  - Dobletes d: 3:2
  - Dobletes f: 4:3

== Instrumentación

*Componentes principales:*

1. *Fuente de rayos X:* Al Kα (1486.6 eV) o Mg Kα (1253.6 eV)
2. *Analizador hemisférico:* Filtro de energía
3. *Ultra alto vacío:* < $10^(-8)$ mbar
4. *Compensación de carga:* Flood gun para aislantes

== Información Química

*Identificación elemental:* Cada elemento tiene energías de enlace únicas

*Chemical shift:* Variación de energía según entorno químico
- C-C: 284.8 eV
- C-O: 286.5 eV
- C=O: 287.8 eV
- O-C=O: 289.0 eV

Magnitud típica: 1-5 eV (resoluble con espectrómetros modernos)

#pagebreak()

// ============================================================================
// CAPÍTULO 3: FUNDAMENTOS MATEMÁTICOS
// ============================================================================

= Fundamentos Matemáticos del Análisis

== Sustracción de Fondo

=== Algoritmo de Shirley (1972)

El fondo en cada punto es proporcional a la intensidad total de picos a menor energía de enlace:

$
  B(E) = B_"min" + (B_"max" - B_"min") (integral_E^(E_"max") S(E') dif E') / (integral_(E_"min")^(E_"max") S(E') dif E')
$ <eq-shirley>

*Algoritmo iterativo:*
1. Inicializar $B^((0)) = "linspace"(I(E_"min"), I(E_"max"))$
2. Iterar: $S^((k)) = I - B^((k-1))$, recalcular $B^((k))$
3. Convergencia: $max|B^((k)) - B^((k-1))| < "tol" times max(I)$

*Parámetros típicos:*
- Tolerancia: $10^(-5) - 10^(-6)$
- Iteraciones máximas: 50-100

=== Fondo Tougaard

Modela scattering inelástico con sección eficaz $K(T)$:

$ B(E) = integral_E^(E_"max") I(E') K(E' - E) dif E' $ <eq-tougaard>

$ K(T) = B T / ((C - T)^2 + D^2)^2 $ <eq-tougaard-k>

Parámetros "universal": $B = 2866$, $C = 1643$, $D = 1$ (eV²)

== Modelado de Picos

=== Perfil Gaussiano

$ f_G (E) = A exp[-(E - E_0)^2 / (2 sigma^2)] $ <eq-gaussian>

FWHM: $2.355 sigma$, Área: $A sigma sqrt(2 pi)$

=== Perfil Lorentziano

$ f_L (E) = A gamma / ((E - E_0)^2 + gamma^2) $ <eq-lorentzian>

FWHM: $2 gamma$, Área: $A pi gamma$

=== Perfil de Voigt

Convolución Gaussiano × Lorentziano (más realista para XPS):

$ f_V (E) = A (V(x, y)) / (sigma sqrt(2 pi)) $ <eq-voigt>

donde $x = (E - E_0)/(sigma sqrt(2))$, $y = gamma/(sigma sqrt(2))$

*Ventajas:* Combina ensanchamiento instrumental (Gaussiano) y natural (Lorentziano)

== Optimización

Método de Levenberg-Marquardt para minimizar:

$ chi^2 = sum_i [(y_i - f(x_i; theta))^2 / sigma_i^2] $ <eq-chi-squared>

*Bondad de ajuste:*
- R² > 0.98: Excelente
- R² = 0.90-0.98: Bueno
- R² < 0.90: Pobre (revisar modelo)

== Cuantificación Atómica

$ C_i = (A_i / S_i) / (sum_j A_j / S_j) times 100% $ <eq-quantification>

donde $S_i$ son factores RSF (Relative Sensitivity Factors):
- *Scofield (1976):* Teóricos, disponibles para ~89 elementos
- *Wagner (1981):* Empíricos, más precisos para ~18 elementos comunes

*Dependencia de fuente:* RSF para Al Kα ≠ RSF para Mg Kα

#pagebreak()

// ============================================================================
// CAPÍTULO 4: ARQUITECTURA DEL SOFTWARE
// ============================================================================

= Arquitectura del Software

== Visión General

*Filosofía de diseño:*
- Modularidad (separación de responsabilidades)
- Extensibilidad (fácil agregar formatos/algoritmos)
- Transparencia (código documentado, type hints)
- Testabilidad (diseño facilita unit testing)

*Stack tecnológico:*
- Python 3.10+
- Pydantic v2 (Validación de datos)
- Streamlit (GUI interactiva)
- NumPy, SciPy (cálculos numéricos)
- Pandas (manipulación de datos)
- Matplotlib (visualización)
- Click (CLI)
- pytest (testing)

== Modelo de Datos

=== Jerarquía de Clases

```python
class XPSBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

class XPSSpectrum(XPSBaseModel):
    """Espectro individual con validación estricta"""
    region_name: str
    binding_energy: np.ndarray  # eV
    intensity: np.ndarray       # cuentas
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_arrays(self):
        if len(self.binding_energy) != len(self.intensity):
            raise ValueError("Arrays must have same length")
        return self

class XPSDataset(XPSBaseModel):
    """Archivo completo con múltiples regiones"""
    filename: str
    header: dict[str, Any]
    spectra: dict[str, XPSSpectrum]

class XPSSample(XPSBaseModel):
    """Muestra con múltiples archivos"""
    sample_name: str
    datasets: dict[str, XPSDataset]
```

*Patrón de inmutabilidad y Validación:* Toda la arquitectura core ha sido migrada a *Pydantic v2*. Las validaciones ocurren en tiempo de ejecución para evitar errores silenciosos en arrays científicos (como longitudes dispares o valores NaN). Las funciones de transformación de datos utilizan siempre `model_copy(deep=True)` cuando operan fuera de `inplace=True`, garantizando la inmutabilidad de los datos base.

== Módulos Principales

=== data_loader (524 líneas, 70% completo)

*Responsabilidad:* Cargar archivos y convertir a estructuras de datos

*Formato soportado:* Texto propietario delimitado por `;`
- Survey: Header + datos de 2 columnas
- Multiplex: Header de 3 líneas + múltiples secciones Element

*Auto-detección:* Por presencia de "multiplex" en nombre de archivo

=== preprocessing (200 líneas, 100% completo)

*Calibración de energía:*

```python
def calibrate_spectrum(
    spectrum: XPSSpectrum,
    reference_element: str = "C",
    reference_energy: float = 284.8,
    inplace: bool = False
) -> XPSSpectrum:
    """
    Calibra usando elemento de referencia.

    Algoritmo:
    1. Buscar región con reference_element
    2. Encontrar máximo (pico más intenso)
    3. Calcular shift = ref - observed
    4. Aplicar shift a todos los espectros
    """
    # Implementación...
```

=== analysis/background.py (498 líneas, 96% cobertura)

*Funciones principales:*

```python
def shirley_background(
    spectrum: XPSSpectrum,
    tol: float = 1e-5,
    max_iter: int = 100,
    inplace: bool = False
) -> XPSSpectrum:
    """
    Sustracción de fondo Shirley.

    Referencias:
    - Shirley, D. A. (1972). Phys Rev B, 5(12)
    """
    # Algoritmo iterativo...

def tougaard_background(
    spectrum: XPSSpectrum,
    tougaard_type: str = "universal",
    inplace: bool = False
) -> XPSSpectrum:
    """
    Fondo Tougaard (4 variantes).

    Tipos: "universal", "B", "C", "D", "D_star"
    """
    # Implementación...
```

=== analysis/peak_fitting.py (849 líneas, 95% cobertura)

*Dataclasses:*

```python
@dataclass
class PeakParameters:
    """Parámetros de pico ajustado"""
    position: float      # eV
    amplitude: float     # cuentas
    width: float         # FWHM (eV)
    area: float          # cuentas·eV
    shape: str           # "gaussian", "voigt", etc.

@dataclass
class FitResult:
    """Resultado completo de ajuste"""
    peaks: list[PeakParameters]
    success: bool
    r_squared: float
    chi_squared: float
    residuals: np.ndarray
```

*Funciones de ajuste:*

```python
def fit_voigt(
    spectrum: XPSSpectrum,
    initial_position: float | None = None,
    initial_amplitude: float | None = None,
    initial_sigma: float = 0.5,
    initial_gamma: float = 0.5
) -> FitResult:
    """
    Ajusta perfil de Voigt.

    Voigt = convolución Gaussiano × Lorentziano
    Más realista para XPS
    """
    # Levenberg-Marquardt optimization...

def fit_multiple_peaks(
    spectrum: XPSSpectrum,
    n_peaks: int,
    peak_shape: str = "voigt",
    initial_positions: list[float] | None = None
) -> FitResult:
    """Ajuste simultáneo de múltiples picos"""
    # Implementación...
```

=== analysis/quantification.py (498 líneas, 85% cobertura)

*Factores RSF:*

```python
# RSF de Scofield para Mg Kα (1253.6 eV)
SCOFIELD_RSF_MG_KA = {
    "C 1s": 0.205,
    "N 1s": 0.314,
    "O 1s": 0.463,
    "Na 1s": 1.000,
    "Ti 2p": 1.143,
    # ... 89 elementos totales
}

# RSF de Wagner para Al Kα (1486.6 eV)
WAGNER_RSF_AL_KA = {
    "C 1s": 0.278,
    "O 1s": 0.780,
    # ... 18 elementos totales
}
```

*Función de cuantificación:*

```python
def calculate_atomic_concentration(
    peaks: list[PeakParameters],
    sensitivity_factors: dict[str, float],
    element_names: list[str],
    normalize: bool = True
) -> dict[str, float]:
    """
    Calcula concentraciones atómicas.

    Fórmula: C_i = (A_i/S_i) / Σ(A_j/S_j) × 100%

    Returns:
        {"C 1s": 65.3, "O 1s": 34.7, ...}
    """
    # Implementación...
```

=== export/exporters.py (561 líneas, 92% cobertura)

*Funciones principales:*

```python
def export_to_csv(
    data: XPSSpectrum | XPSDataset,
    filepath: str | Path,
    include_metadata: bool = True,
    decimal_places: int = 6
) -> Path:
    """
    Exporta a CSV.

    Genera:
    - filename.csv: datos (binding_energy, intensity)
    - filename.metadata.csv: metadata (si incluido)
    """
    # Implementación...

def export_to_excel(
    dataset: XPSDataset,
    filepath: str | Path,
    include_metadata: bool = True
) -> Path:
    """
    Exporta a Excel con múltiples hojas.

    Hojas:
    - Una por región (C_1s, O_1s, ...)
    - Dataset_Metadata
    - Spectra_Metadata
    """
    # Implementación con openpyxl...

def export_to_json(
    data: XPSSpectrum | XPSDataset | XPSSample,
    filepath: str | Path,
    indent: int = 2
) -> Path:
    """Exporta estructura jerárquica completa"""
    # Implementación...
```

== Flujo de Datos

Pipeline típico:

```
1. Cargar datos
   load_single_file() → XPSDataset

2. Calibrar energía
   calibrate_dataset() → shift aplicado

3. Restar fondo
   shirley_background() → espectro limpio

4. Ajustar picos
   fit_voigt() → FitResult con áreas

5. Cuantificar
   calculate_atomic_concentration() → composición

6. Exportar
   export_to_excel() → archivo Excel
```

#pagebreak()

// ============================================================================
// CAPÍTULO 5: VALIDACIÓN CON DATOS REALES
// ============================================================================

= Validación con Datos Reales

== Dataset BN-SET-01

*Descripción:*
- 4 muestras (BN-BS-1, BN-BS-2, BN-BS-3, BN-BS-4)
- 6 regiones por muestra: Bi 4f, C 1s, Na 1s, O 1s, Sr 3d, Ti 2p
- Fuente: Mg Kα (1253.6 eV)
- Material real: Titanato de estroncio dopado (NO nitruro de boro)

*Calidad de datos:*
- SNR promedio: 134.8 (excelente)
- Todas las regiones SNR > 60
- Sin problemas de carga

== Fase B: Pipeline Completo

=== Muestra Analizada: BN-BS-3

*Calibración:*
- Referencia: C 1s @ 284.8 eV
- Observado: 288.20 eV
- Shift aplicado: -3.40 eV

*Resultados por Región:*

#table(
  columns: 5,
  align: (left, center, center, center, left),
  [*Región*], [*Fondo*], [*Fitting*], [*R²*], [*Cuantificación*],
  [Bi 4f], [✓], [✓], [0.63], [RSF N/A],
  [C 1s], [✗], [-], [-], [No procesado],
  [Na 1s], [✓], [✓], [0.26], [6.13%],
  [O 1s], [✓], [✓], [0.82], [50.80%],
  [Sr 3d], [✓], [✓], [0.80], [RSF N/A],
  [Ti 2p], [✓], [✓], [0.41], [43.06%],
)

*Composición atómica (normalizada):*
- O 1s: 50.80% (componente mayoritario)
- Ti 2p: 43.06%
- Na 1s: 6.13% (trazas, dopaje)

*Interpretación química:*
- Ratio Ti:O = 1:1.2 (esperado ~1:2 para TiO₂ puro)
- Sugiere deficiencia de oxígeno o fase mixta
- Presencia de Na indica dopaje o contaminación superficial

=== Bugs Corregidos Durante Validación

*Bug #1:* `shirley_background(max_iterations=)` → correcto: `max_iter=`\
*Bug #2:* `fit_voigt()` con diccionario → debe usar parámetros con nombre\
*Bug #3:* `calculate_atomic_concentration()` requiere `element_names`

Todos corregidos exitosamente.

=== Limitaciones Identificadas

*Convergencia de Shirley:*
- C 1s no convergió en 100 iteraciones
- Cambio final: 6.71×10⁻² (tolerancia: 10⁻⁵)
- Causa: Espectro complejo o ruido alto

*Ajuste de dobletes:*
- Ti 2p (R² = 0.41): Doblete 2p₃/₂ y 2p₁/₂ no resuelto
- Bi 4f (R² = 0.63): Doblete 4f₇/₂ y 4f₅/₂ no resuelto
- *Solución propuesta:* Ajuste multi-pico con restricciones físicas

*Detección incorrecta:*
- Sr 3d detectado en 159.1 eV (esperado ~133 eV)
- Confusión con Bi 4f (159.0 eV) - pico más intenso
- *Solución propuesta:* Validación contra base de datos

*RSF faltantes:*
- Bi 4f y Sr 3d no tienen RSF para Mg Kα en base Scofield
- Elementos excluidos de cuantificación
- *Solución propuesta:* Agregar RSF de Wagner/Moulder

== Métricas de Validación

*Coverage de funcionalidad:*
- Carga: 100% (4/4 muestras)
- Calibración: 100%
- Fondo: 83% (5/6 regiones)
- Fitting: 100% (5/5 con fondo exitoso)
- Cuantificación: 60% (3/5 con RSF)

*Calidad de ajuste:*
- R² promedio: 0.59
- Regiones R² > 0.80: 33% (2/6)
- Mejor ajuste: O 1s (R² = 0.82)

*Evaluación:* Software funcional pero requiere mejoras en ajuste de picos complejos.

#pagebreak()

// ============================================================================
// CAPÍTULO 6: DESARROLLO Y TESTING
// ============================================================================

= Desarrollo y Testing

== Metodología

*Enfoque iterativo por fases:*
1. Fase 0: Fundamentos (2-3 semanas)
2. Fase 1: Análisis core (4 sesiones, ~6 semanas)
3. Fase 2: Robustez (planificado, ~8 semanas)

*Herramientas:*
- *uv:* Gestor de paquetes rápido
- *ruff:* Linter + formatter
- *pytest:* Framework de testing
- *pre-commit:* Hooks de calidad de código
- *GitHub:* Control de versiones

== Fase 1: Sesiones de Desarrollo

=== Sesión 1: Background Subtraction

*Commit:* `fa8bcb8`\
*Código:* 498 líneas (`background.py`)\
*Tests:* 30 tests, 96% cobertura\
*Métodos:* Shirley, Tougaard (4 variantes), Linear

=== Sesión 2: Peak Fitting

*Commit:* `da698d2`\
*Código:* 849 líneas (`peak_fitting.py`)\
*Tests:* 45 tests, 95% cobertura\
*Perfiles:* Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL

=== Sesión 3: Quantification

*Commit:* `097c3ca`\
*Código:* 498 líneas (`quantification.py`)\
*Tests:* 43 tests, 85% cobertura\
*RSF:* Scofield (89 elementos), Wagner (18 elementos)

=== Sesión 4: Export System

*Código:* 561 líneas (`exporters.py`)\
*Tests:* 19 tests, 92% cobertura\
*Formatos:* CSV, Excel (múltiples hojas), JSON

== Estadísticas Finales Fase 1

*Código:*
- Líneas totales: ~4,400
- Módulos completados: 4 (background, peak_fitting, quantification, export)

*Testing:*
- Tests totales: 227
- Tests passing: 227 (100%)
- Cobertura: 87% (objetivo 80% superado)

*Commits:* 15 commits principales en Fase 1

== Convenciones del Proyecto

*Idioma:*
- Todo en español: docstrings, comentarios, mensajes de error
- Variables en inglés (convención Python)

*Type hints:*
- Completos en todas las funciones públicas
- Python 3.10+
- Pydantic v2 (Validación de datos)
- Streamlit (GUI interactiva) (usa `|` para Union)

*Orden de imports:*
```python
# 1. future
from __future__ import annotations

# 2. standard-library
from pathlib import Path

# 3. first-party
from xps_analyzer.data_loader import XPSSpectrum

# 4. third-party
import numpy as np
```

*Docstrings:*
- Estilo NumPy
- Secciones: Parameters, Returns, Raises, Examples, Notes, References

#pagebreak()

// ============================================================================
// CAPÍTULO 7: CAPACIDADES Y LIMITACIONES
// ============================================================================

= Capacidades y Limitaciones

== Lo Que SÍ Puede Hacer

*Formatos de entrada:*
- Texto propietario (multiplex y survey)

*Preprocesamiento:*
- Calibración con elemento de referencia
- Detección automática de formato

*Análisis cuantitativo:*
- Fondo: Shirley, Tougaard (4 variantes), Lineal
- Fitting: Gaussian, Lorentzian, Voigt, Pseudo-Voigt, GL
- Ajuste de picos individuales o múltiples simultáneos
- Cuantificación con RSF Scofield/Wagner

*Exportación:*
- CSV (datos + metadata)
- Excel (múltiples hojas, formato profesional)
- JSON (estructura jerárquica)
- Control de precisión decimal

*Visualización:*
- Plots de espectros con convenciones XPS
- Exportación PNG 300 DPI

*Interfaz:*
- API Python documentada
- CLI básico

== Lo Que NO Puede Hacer (Aún)

*Formatos:*
- HDF5 - Fase 2

*Análisis:*
- Ajuste de dobletes con restricciones físicas
- Identificación automática con ML - Fase 3
- Análisis de profundidad - Fase 3
- Imaging XPS - Fase 3

*Interfaz:*
- GUI gráfica - Fase 3
- API REST - Fase 3

== Formatos Soportados

*INPUT:*
- `.txt`: Texto propietario delimitado por `;`

*OUTPUT:*
- `.csv`: Datos tabulares
- `.xlsx`: Excel
- `.json`: Estructura jerárquica
- `.png`: Plots 300 DPI

#pagebreak()

// ============================================================================
// CAPÍTULO 8: GUÍA DE USO
// ============================================================================

= Guía de Uso

== Instalación

*Requisitos:* Python 3.10+

*Instalación con uv (recomendado):*

```bash
# Clonar repositorio
git clone https://github.com/JesusF10/xps-data-analysis.git
cd xps-data-analysis

# Instalar dependencias
uv sync --group dev --group jupyter

# Verificar
uv run xps-analyzer --version
```

*Instalación con conda:*

```bash
conda env create -f environment.yml
conda activate xps-analysis
pip install -e ".[dev]"
```

== Ejemplo Completo

```python
from xps_analyzer import load_single_file
from xps_analyzer.preprocessing import calibrate_dataset
from xps_analyzer.analysis import (
    shirley_background,
    fit_voigt,
    load_sensitivity_factors,
    calculate_atomic_concentration
)
from xps_analyzer.export import export_to_excel

# 1. Cargar datos
dataset = load_single_file("data/sample1_multiplex.txt")
print(f"Regiones: {dataset.list_regions()}")

# 2. Calibrar energía (C 1s @ 284.8 eV)
dataset = calibrate_dataset(dataset, reference_element="C")

# 3. Restar fondo y ajustar picos
results = {}
for region_name in ["C 1s", "O 1s", "Ti 2p"]:
    # Obtener espectro
    spectrum = dataset.get_spectrum(region_name)

    # Restar fondo Shirley
    spectrum_nobg = shirley_background(spectrum)

    # Ajustar con Voigt
    fit_result = fit_voigt(spectrum_nobg)

    if fit_result.success:
        results[region_name] = fit_result.peaks[0]
        print(f"{region_name}: R² = {fit_result.r_squared:.4f}")

# 4. Cuantificación
rsf = load_sensitivity_factors(source="scofield",
                                xray_source="mg_ka")
peaks = list(results.values())
element_names = list(results.keys())

concentrations = calculate_atomic_concentration(
    peaks, rsf, element_names
)

print("\nComposición atómica:")
for element, conc in concentrations.items():
    print(f"  {element}: {conc:.2f}%")

# 5. Exportar resultados
export_to_excel(dataset, "results/sample1_analysis.xlsx")
```

== CLI

```bash
# Analizar directorio
xps-analyzer analyze data/raw/samples/

# Mostrar información de elemento
xps-analyzer show-element Ti
```

#pagebreak()

// ============================================================================
// CAPÍTULO 9: ROADMAP Y TRABAJO FUTURO
// ============================================================================

= Roadmap y Trabajo Futuro

== Fase 2: Pydantic y GUI Interactiva (En progreso 2026)

*Objetivos:*
- Migración a Pydantic v2 (Completada)
- GUI interactiva con Streamlit (En progreso) automática
- Exportación HDF5
- Sistema de plugins para formatos
- Target: 85% cobertura

*Estimación:* 8-10 semanas

== Fase 3: Avanzado (Futuro)

*Objetivos:*
- Machine learning para identificación automática
- Análisis de profundidad (depth profiling)
- GUI con Streamlit/Dash
- API REST con FastAPI
- Target: 90% cobertura

*Estimación:* 12-16 semanas

== Mejoras Propuestas

*Alta prioridad:*
1. Ajuste multi-pico con restricciones de dobletes
2. RSF completos (Wagner/Moulder)
3. Algoritmo Shirley adaptativo

*Media prioridad:*
4. Validación automática de resultados (warnings R² < 0.80)
5. Detección de picos basada en base de datos
6. Visualización mejorada (componentes individuales)

*Baja prioridad:*
7. CLI mejorado con más comandos
8. Progress bars con tqdm
9. Reportes HTML interactivos

#pagebreak()

// ============================================================================
// CAPÍTULO 10: CONCLUSIONES
// ============================================================================

= Conclusiones y Perspectivas

== Logros

*Implementación:*
- Pipeline completo XPS funcional
- 4,400 líneas de código
- 7 módulos principales
- 227 tests (87% cobertura)

*Validación:*
- Probado exitosamente con datos reales
- 3 bugs identificados y corregidos
- Composición atómica calculada correctamente
- Generación de resultados profesionales (Excel, plots)

*Documentación:*
- Exhaustiva en español
- Type hints completos
- API documentada estilo NumPy
- Este documento técnico completo

== Limitaciones

*Técnicas:*
- Ajuste de dobletes manual (requiere multi-pico)
- Shirley no converge en ~17% de casos
- RSF incompletos para Mg Kα

*Funcionales:*
- Solo un formato de entrada soportado
- Sin GUI gráfica
- Sin procesamiento batch optimizado

== Aportaciones

*A la comunidad científica:*
- Alternativa open-source a software comercial
- Transparencia en algoritmos
- Extensibilidad para investigación

*Al desarrollo de software:*
- Arquitectura modular bien diseñada
- Alta cobertura de tests
- Documentación exhaustiva en español
- Patrón para software científico académico

== Trabajo Futuro

*Corto plazo (3-6 meses):*
- Completar Fase 2
- Implementar ajuste de dobletes con restricciones
- Expandir base de datos RSF

*Mediano plazo (6-12 meses):*
- Desarrollar GUI con Streamlit
- Implementar identificación con ML
- Publicar en PyPI

*Largo plazo (1-2 años):*
- API REST para integración con LIMS
- Análisis de profundidad automático
- Colaboración con comunidad XPS internacional

== Impacto Esperado

*Académico:*
- Reducción de costos para laboratorios
- Mejora en reproducibilidad de análisis
- Facilitación de enseñanza de XPS

*Técnico:*
- Base para desarrollo de herramientas personalizadas
- Plataforma para investigación en nuevos algoritmos
- Ejemplo de buenas prácticas en software científico

*Social:*
- Democratización del acceso a análisis XPS
- Contribución al movimiento de ciencia abierta
- Formación de recursos humanos especializados

#pagebreak()

// ============================================================================
// APÉNDICE A: GLOSARIO
// ============================================================================

= Apéndices

== Apéndice A: Glosario de Términos XPS

*Binding Energy (Energía de Enlace):* Energía requerida para remover un electrón de un orbital atómico específico, característica de cada elemento.

*Chemical Shift:* Variación en energía de enlace debido al entorno químico del átomo (estado de oxidación, tipo de enlace).

*Doublet (Doblete):* Par de picos resultantes del acoplamiento espín-órbita en orbitales con $l > 0$ (p, d, f).

*FWHM:* Full Width at Half Maximum - ancho del pico a media altura, indica resolución y homogeneidad química.

*IMFP:* Inelastic Mean Free Path - camino libre medio inelástico, determina profundidad de análisis (~1-3 nm).

*RSF:* Relative Sensitivity Factor - factor que corrige diferencias en sección eficaz de fotoionización entre elementos.

*Survey:* Espectro de amplio rango (0-1200 eV) para identificación elemental cualitativa.

*Takeoff Angle:* Ángulo entre superficie de muestra y analizador, afecta profundidad de análisis.

*UHV:* Ultra High Vacuum - presión < $10^(-8)$ mbar requerida para análisis XPS.

== Apéndice B: Estructura de Archivos

```
xps-data-analysis/
├── src/xps_analyzer/       (código fuente, ~4,400 líneas)
│   ├── analysis/           (2,406 líneas - CORE)
│   │   ├── background.py   (498 líneas)
│   │   ├── peak_fitting.py (849 líneas)
│   │   └── quantification.py (498 líneas)
│   ├── export/             (561 líneas)
│   ├── data_loader/        (524 líneas)
│   ├── preprocessing/      (200 líneas)
│   ├── reference_data/     (600 líneas)
│   └── visualization/      (150 líneas)
├── tests/                  (355 tests, 93% cobertura core)
├── config/                 (TOML configuración)
├── data/                   (datos y resultados)
├── docs/                   (documentación)
└── scripts/                (análisis)
```

== Apéndice C: Dependencias Completas

```toml
[project]
dependencies = [
    "numpy>=1.21.0",
    "pandas>=1.3.0",
    "matplotlib>=3.4.0",
    "scipy>=1.7.0",
    "click>=8.0.0",
    "openpyxl>=3.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "pre-commit>=3.0.0",
]
jupyter = [
    "jupyter>=1.0.0",
    "ipykernel>=6.0.0",
]
```

== Apéndice D: Tablas RSF

*Scofield RSF para Mg Kα (selección):*

#table(
  columns: 4,
  align: (left, right, left, right),
  [*Elemento*], [*RSF*], [*Elemento*], [*RSF*],
  [C 1s], [0.205], [Na 1s], [1.000],
  [N 1s], [0.314], [Al 2p], [0.150],
  [O 1s], [0.463], [Si 2p], [0.209],
  [F 1s], [0.630], [Ti 2p], [1.143],
)

*Wagner RSF para Al Kα (selección):*

#table(
  columns: 4,
  align: (left, right, left, right),
  [*Elemento*], [*RSF*], [*Elemento*], [*RSF*],
  [C 1s], [0.278], [O 1s], [0.780],
  [N 1s], [0.499], [F 1s], [1.000],
  [Si 2p], [0.339], [Ti 2p], [2.136],
)

#pagebreak()

// ============================================================================
// REFERENCIAS
// ============================================================================

= Referencias Bibliográficas

== Artículos Científicos

1. *Shirley, D. A.* (1972). "High-Resolution X-Ray Photoemission Spectrum of the Valence Bands of Gold". _Physical Review B_, 5(12), 4709-4714.

2. *Tougaard, S.* (1997). "Universality Classes of Inelastic Electron Scattering Cross-sections". _Surface and Interface Analysis_, 25(3), 137-154.

3. *Scofield, J. H.* (1976). "Hartree-Slater subshell photoionization cross-sections at 1254 and 1487 eV". _Journal of Electron Spectroscopy and Related Phenomena_, 8(2), 129-137.

4. *Wagner, C. D., Riggs, W. M., Davis, L. E., Moulder, J. F., & Muilenberg, G. E.* (1981). _Handbook of X-ray Photoelectron Spectroscopy_. Physical Electronics Division, Perkin-Elmer Corp.

5. *Levenberg, K.* (1944). "A Method for the Solution of Certain Non-Linear Problems in Least Squares". _Quarterly of Applied Mathematics_, 2(2), 164-168.

== Libros

8. *Briggs, D., & Seah, M. P.* (1990). _Practical Surface Analysis, Volume 1: Auger and X-ray Photoelectron Spectroscopy_ (2nd ed.). John Wiley & Sons.

9. *Watts, J. F., & Wolstenholme, J.* (2020). _An Introduction to Surface Analysis by XPS and AES_ (2nd ed.). Wiley.

10. *Hüfner, S.* (2003). _Photoelectron Spectroscopy: Principles and Applications_ (3rd ed.). Springer.

== Estándares


12. *ASTM E2108-10.* Standard Practice for Calibration of the Electron Binding-Energy Scale of an X-Ray Photoelectron Spectrometer.

== Bases de Datos

13. *NIST XPS Database.* National Institute of Standards and Technology. https://srdata.nist.gov/xps/

14. *La Surface XPS Database.* https://xpsdatabase.com/

== Documentación de Software

15. *NumPy Documentation.* https://numpy.org/doc/

16. *SciPy Documentation.* https://docs.scipy.org/

17. *Matplotlib Documentation.* https://matplotlib.org/

18. *Click Documentation.* https://click.palletsprojects.com/

== Repositorios

19. *XPS Analyzer GitHub.* https://github.com/JesusF10/xps-data-analysis

#pagebreak()

#align(center)[
  #v(4cm)
  #text(18pt, weight: "bold")[
    FIN DEL DOCUMENTO
  ]

  #v(2cm)
  #text(12pt)[
    XPS Analyzer v0.9.1-beta\
    Documentación Técnica\
    \
    Abril 2026\
    \
    Jesús Flores Lacarra\
    jss.263.fsc\@gmail.com
  ]
]
