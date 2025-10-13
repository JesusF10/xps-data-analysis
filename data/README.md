# Directorio de Datos

Este directorio contiene todos los datos relacionados con el proyecto XPS.

## Estructura

### 📁 raw/
Datos crudos sin procesar, directamente desde los instrumentos XPS.

- **samples/**: Datos de muestras experimentales
  - Organizar por proyecto, fecha o tipo de muestra
  - Incluir archivos de metadatos cuando sea posible
- **calibration/**: Datos de calibración de instrumentos
  - Estándares de referencia
  - Muestras de calibración periódica

### 📁 processed/
Datos que han sido procesados y calibrados.

- Datos después de calibración de energía
- Espectros con fondo substraído
- Datos normalizados y suavizados

### 📁 test_data/
Conjunto de datos para pruebas y validación del software.

- Datos de referencia conocidos
- Casos de prueba para algoritmos
- Datos sintéticos para testing

### 📁 results/
Resultados finales del análisis.

- **reports/**: Reportes generados automáticamente
- **plots/**: Gráficas y visualizaciones
- **exports/**: Datos exportados en diferentes formatos

## Convenciones de Nomenclatura

### Archivos de datos:
```
YYYY-MM-DD_[proyecto]_[muestra]_[tipo].[ext]
```

Ejemplo: `2025-10-01_proyecto1_acero_survey.vms`

### Directorios de muestras:
```
[proyecto]/[fecha]/[muestra]
```

Ejemplo: `corrosion_study/2025-10/steel_sample_01/`

## Formatos de Archivo Soportados

- `.vms` - Kratos Axis Ultra
- `.vgx` - Thermo K-Alpha  
- `.xy` - Datos tabulares genéricos
- `.txt` - Texto plano
- `.csv` - Valores separados por comas
- `.xlsx` - Excel (para exportación)

## Respaldo y Versionado

- Los datos crudos NUNCA deben modificarse
- Mantener historial de procesamiento
- Documentar parámetros utilizados
- Respaldo regular en múltiples ubicaciones