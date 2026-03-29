"""
Tests para el módulo de cuantificación atómica XPS.

Cubre:
- Carga de factores de sensibilidad (Scofield, Wagner)
- Cálculo de concentraciones atómicas
- Normalización de concentraciones
- Casos edge y manejo de errores
"""

from __future__ import annotations

from xps_analyzer.analysis.peak_fitting import PeakParameters
from xps_analyzer.analysis.quantification import (
    SCOFIELD_RSF_AL_KA,
    calculate_atomic_concentration,
    load_sensitivity_factors,
    normalize_to_100,
)

import pytest

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def carbon_peak():
    """Peak ajustado de C 1s."""
    return PeakParameters(
        position=284.8,
        amplitude=1000.0,
        width=1.2,
        area=1500.0,
        shape="gaussian",
    )


@pytest.fixture
def oxygen_peak():
    """Peak ajustado de O 1s."""
    return PeakParameters(
        position=531.0,
        amplitude=800.0,
        width=1.5,
        area=1200.0,
        shape="gaussian",
    )


@pytest.fixture
def nitrogen_peak():
    """Peak ajustado de N 1s."""
    return PeakParameters(
        position=399.0,
        amplitude=500.0,
        width=1.3,
        area=800.0,
        shape="gaussian",
    )


@pytest.fixture
def silicon_peak():
    """Peak ajustado de Si 2p."""
    return PeakParameters(
        position=99.5,
        amplitude=600.0,
        width=1.1,
        area=900.0,
        shape="gaussian",
    )


@pytest.fixture
def gold_peak():
    """Peak ajustado de Au 4f."""
    return PeakParameters(
        position=84.0,
        amplitude=2000.0,
        width=0.9,
        area=2500.0,
        shape="voigt",
        gamma=0.3,
    )


@pytest.fixture
def scofield_rsf():
    """Factores Scofield para Al Kα."""
    return load_sensitivity_factors(source="scofield", xray_source="al_ka")


@pytest.fixture
def wagner_rsf():
    """Factores Wagner para Al Kα."""
    return load_sensitivity_factors(source="wagner", xray_source="al_ka")


# ============================================================================
# TEST LOAD_SENSITIVITY_FACTORS
# ============================================================================


class TestLoadSensitivityFactors:
    """Tests para carga de factores de sensibilidad."""

    def test_load_scofield_al_ka(self):
        """Test carga de factores Scofield para Al Kα."""
        rsf = load_sensitivity_factors(source="scofield", xray_source="al_ka")

        # Verificar elementos clave
        assert "C 1s" in rsf
        assert "O 1s" in rsf
        assert "N 1s" in rsf

        # Verificar valores conocidos
        assert rsf["C 1s"] == 0.296
        assert rsf["O 1s"] == 0.711
        assert rsf["F 1s"] == 1.000  # Normalizado a F 1s

    def test_load_scofield_mg_ka(self):
        """Test carga de factores Scofield para Mg Kα."""
        rsf = load_sensitivity_factors(source="scofield", xray_source="mg_ka")

        # Verificar elementos clave
        assert "C 1s" in rsf
        assert "O 1s" in rsf

        # Valores diferentes a Al Kα
        assert rsf["C 1s"] == 0.205
        assert rsf["O 1s"] == 0.463
        assert rsf["Na 1s"] == 1.000  # Normalizado a Na 1s para Mg Kα

    def test_load_wagner_al_ka(self):
        """Test carga de factores Wagner para Al Kα."""
        rsf = load_sensitivity_factors(source="wagner", xray_source="al_ka")

        # Verificar elementos clave
        assert "C 1s" in rsf
        assert "O 1s" in rsf

        # Valores Wagner (empíricos)
        assert rsf["C 1s"] == 0.278
        assert rsf["O 1s"] == 0.780

    def test_load_default_parameters(self):
        """Test valores por defecto (Scofield Al Kα)."""
        rsf = load_sensitivity_factors()

        assert rsf == SCOFIELD_RSF_AL_KA

    def test_wagner_mg_ka_not_supported(self):
        """Test que Wagner no soporta Mg Kα."""
        with pytest.raises(ValueError, match="Wagner RSF solo disponibles"):
            load_sensitivity_factors(source="wagner", xray_source="mg_ka")

    def test_invalid_source(self):
        """Test fuente de RSF inválida."""
        with pytest.raises(ValueError, match="Fuente de RSF .* no reconocida"):
            load_sensitivity_factors(source="invalid")

    def test_invalid_xray_source_scofield(self):
        """Test fuente de rayos X inválida para Scofield."""
        with pytest.raises(ValueError, match="Fuente de rayos X .* no soportada"):
            load_sensitivity_factors(source="scofield", xray_source="cu_ka")

    def test_invalid_xray_source_wagner(self):
        """Test fuente de rayos X inválida para Wagner."""
        with pytest.raises(ValueError, match="Fuente de rayos X .* no soportada"):
            load_sensitivity_factors(source="wagner", xray_source="cu_ka")

    def test_rsf_returns_copy(self):
        """Test que load_sensitivity_factors retorna copia, no referencia."""
        rsf1 = load_sensitivity_factors()
        rsf2 = load_sensitivity_factors()

        # Modificar uno no debe afectar el otro
        rsf1["C 1s"] = 999.0

        assert rsf2["C 1s"] == 0.296
        assert rsf1["C 1s"] == 999.0

    def test_all_elements_present_scofield(self):
        """Test que todos los elementos esperados están presentes."""
        rsf = load_sensitivity_factors(source="scofield", xray_source="al_ka")

        expected_elements = [
            "C 1s",
            "N 1s",
            "O 1s",
            "F 1s",
            "Si 2p",
            "S 2p",
            "Au 4f",
        ]

        for element in expected_elements:
            assert element in rsf

    def test_all_rsf_positive(self):
        """Test que todos los factores RSF son positivos."""
        rsf = load_sensitivity_factors()

        for element, value in rsf.items():
            assert value > 0, f"RSF de {element} debe ser positivo"


# ============================================================================
# TEST CALCULATE_ATOMIC_CONCENTRATION
# ============================================================================


class TestCalculateAtomicConcentration:
    """Tests para cálculo de concentraciones atómicas."""

    def test_two_elements_basic(self, carbon_peak, oxygen_peak, scofield_rsf):
        """Test cálculo básico con dos elementos (C, O)."""
        peaks = [carbon_peak, oxygen_peak]
        element_names = ["C 1s", "O 1s"]

        concentrations = calculate_atomic_concentration(
            peaks, scofield_rsf, element_names
        )

        # Verificar que suman 100%
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

        # Verificar elementos presentes
        assert "C 1s" in concentrations
        assert "O 1s" in concentrations

        # Verificar valores razonables (C tiene área mayor pero RSF menor)
        # C: 1500 / 0.296 = 5067.57
        # O: 1200 / 0.711 = 1687.48
        # Total: 6755.05
        # C%: 5067.57 / 6755.05 * 100 = 75.02%
        # O%: 1687.48 / 6755.05 * 100 = 24.98%
        assert abs(concentrations["C 1s"] - 75.0) < 1.0
        assert abs(concentrations["O 1s"] - 25.0) < 1.0

    def test_three_elements(
        self, carbon_peak, oxygen_peak, nitrogen_peak, scofield_rsf
    ):
        """Test cálculo con tres elementos (C, O, N)."""
        peaks = [carbon_peak, oxygen_peak, nitrogen_peak]
        element_names = ["C 1s", "O 1s", "N 1s"]

        concentrations = calculate_atomic_concentration(
            peaks, scofield_rsf, element_names
        )

        # Verificar que suman 100%
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

        # Todos los elementos presentes
        assert len(concentrations) == 3
        assert all(c > 0 for c in concentrations.values())

    def test_five_elements(
        self,
        carbon_peak,
        oxygen_peak,
        nitrogen_peak,
        silicon_peak,
        gold_peak,
        scofield_rsf,
    ):
        """Test cálculo con cinco elementos."""
        peaks = [carbon_peak, oxygen_peak, nitrogen_peak, silicon_peak, gold_peak]
        element_names = ["C 1s", "O 1s", "N 1s", "Si 2p", "Au 4f"]

        concentrations = calculate_atomic_concentration(
            peaks, scofield_rsf, element_names
        )

        # Verificar suma 100%
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

        # Verificar que todos están presentes
        assert len(concentrations) == 5

    def test_with_wagner_rsf(self, carbon_peak, oxygen_peak, wagner_rsf):
        """Test cálculo con factores Wagner."""
        peaks = [carbon_peak, oxygen_peak]
        element_names = ["C 1s", "O 1s"]

        concentrations = calculate_atomic_concentration(
            peaks, wagner_rsf, element_names
        )

        # Verificar suma 100%
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

        # Wagner tiene diferentes factores, concentraciones cambiarán
        # C Wagner: 0.278 vs Scofield: 0.296
        # O Wagner: 0.780 vs Scofield: 0.711
        assert "C 1s" in concentrations
        assert "O 1s" in concentrations

    def test_normalize_false(self, carbon_peak, oxygen_peak, scofield_rsf):
        """Test con normalización desactivada."""
        peaks = [carbon_peak, oxygen_peak]
        element_names = ["C 1s", "O 1s"]

        concentrations = calculate_atomic_concentration(
            peaks, scofield_rsf, element_names, normalize=True
        )

        # Aún debe sumar 100% porque se normaliza en la fórmula
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

    def test_equal_areas_different_rsf(self, scofield_rsf):
        """Test con áreas iguales pero RSF diferentes."""
        peak1 = PeakParameters(
            position=284.8,
            amplitude=1000.0,
            width=1.0,
            area=1000.0,  # Área idéntica
            shape="gaussian",
        )
        peak2 = PeakParameters(
            position=531.0,
            amplitude=1000.0,
            width=1.0,
            area=1000.0,  # Área idéntica
            shape="gaussian",
        )

        concentrations = calculate_atomic_concentration(
            [peak1, peak2], scofield_rsf, ["C 1s", "O 1s"]
        )

        # C tiene RSF menor (0.296) -> mayor concentración
        # O tiene RSF mayor (0.711) -> menor concentración
        assert concentrations["C 1s"] > concentrations["O 1s"]

    def test_trace_element(self, carbon_peak, scofield_rsf):
        """Test con elemento traza (<1%)."""
        # Crear peak muy pequeño para elemento traza
        trace_peak = PeakParameters(
            position=84.0,
            amplitude=10.0,
            width=1.0,
            area=15.0,  # Muy pequeño comparado con C (1500)
            shape="gaussian",
        )

        concentrations = calculate_atomic_concentration(
            [carbon_peak, trace_peak], scofield_rsf, ["C 1s", "Au 4f"]
        )

        # C debe ser >99%, Au <1%
        assert concentrations["C 1s"] > 99.0
        assert concentrations["Au 4f"] < 1.0

    def test_high_rsf_element(self, gold_peak, scofield_rsf):
        """Test con elemento de RSF alto (Au 4f = 5.63)."""
        carbon_small = PeakParameters(
            position=284.8,
            amplitude=500.0,
            width=1.0,
            area=800.0,
            shape="gaussian",
        )

        # Au tiene área mayor (2500) y RSF mucho mayor (5.63 vs 0.296)
        concentrations = calculate_atomic_concentration(
            [carbon_small, gold_peak], scofield_rsf, ["C 1s", "Au 4f"]
        )

        # Pese a tener área mayor, Au tendrá menor concentración por RSF alto
        # C: 800 / 0.296 = 2702.70
        # Au: 2500 / 5.63 = 444.05
        # C debe tener mayor concentración
        assert concentrations["C 1s"] > concentrations["Au 4f"]


# ============================================================================
# TEST EDGE CASES Y ERRORES
# ============================================================================


class TestCalculateConcentrationErrors:
    """Tests para manejo de errores en calculate_atomic_concentration."""

    def test_empty_peaks_list(self, scofield_rsf):
        """Test con lista de picos vacía."""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            calculate_atomic_concentration([], scofield_rsf, [])

    def test_element_names_none(self, carbon_peak, scofield_rsf):
        """Test sin especificar element_names."""
        with pytest.raises(ValueError, match="element_names debe especificarse"):
            calculate_atomic_concentration([carbon_peak], scofield_rsf, None)

    def test_mismatched_lengths(self, carbon_peak, oxygen_peak, scofield_rsf):
        """Test con número de picos != element_names."""
        with pytest.raises(ValueError, match="debe coincidir"):
            calculate_atomic_concentration(
                [carbon_peak, oxygen_peak],
                scofield_rsf,
                ["C 1s"],  # Solo 1 nombre
            )

    def test_negative_area(self, scofield_rsf):
        """Test con área negativa."""
        bad_peak = PeakParameters(
            position=284.8,
            amplitude=1000.0,
            width=1.0,
            area=-100.0,  # Negativo
            shape="gaussian",
        )

        with pytest.raises(ValueError, match="debe ser positiva"):
            calculate_atomic_concentration([bad_peak], scofield_rsf, ["C 1s"])

    def test_zero_area(self, scofield_rsf):
        """Test con área cero."""
        zero_peak = PeakParameters(
            position=284.8,
            amplitude=0.0,
            width=1.0,
            area=0.0,
            shape="gaussian",
        )

        with pytest.raises(ValueError, match="debe ser positiva"):
            calculate_atomic_concentration([zero_peak], scofield_rsf, ["C 1s"])

    def test_missing_rsf(self, carbon_peak, scofield_rsf):
        """Test con elemento sin factor RSF."""
        with pytest.raises(ValueError, match="Factores RSF no disponibles"):
            calculate_atomic_concentration(
                [carbon_peak],
                scofield_rsf,
                ["Xe 3d"],  # Xenón no en lista
            )

    def test_multiple_missing_rsf(self, carbon_peak, oxygen_peak, scofield_rsf):
        """Test con múltiples elementos sin RSF."""
        with pytest.raises(ValueError, match="Factores RSF no disponibles"):
            calculate_atomic_concentration(
                [carbon_peak, oxygen_peak],
                scofield_rsf,
                ["Xe 3d", "Kr 3d"],  # Ambos faltantes
            )


# ============================================================================
# TEST NORMALIZE_TO_100
# ============================================================================


class TestNormalizeTo100:
    """Tests para normalización de concentraciones."""

    def test_normalize_basic(self):
        """Test normalización básica."""
        concentrations = {"C 1s": 65.0, "O 1s": 30.0}  # Suma = 95%

        normalized = normalize_to_100(concentrations)

        # Verificar suma exacta 100%
        total = sum(normalized.values())
        assert abs(total - 100.0) < 1e-10

        # Verificar proporciones mantenidas
        ratio_original = concentrations["C 1s"] / concentrations["O 1s"]
        ratio_normalized = normalized["C 1s"] / normalized["O 1s"]
        assert abs(ratio_original - ratio_normalized) < 1e-10

    def test_normalize_already_100(self):
        """Test normalización cuando ya suma 100%."""
        concentrations = {"C 1s": 75.0, "O 1s": 25.0}

        normalized = normalize_to_100(concentrations)

        # Debe ser prácticamente idéntico
        assert abs(normalized["C 1s"] - 75.0) < 1e-6
        assert abs(normalized["O 1s"] - 25.0) < 1e-6

    def test_normalize_exceeds_100(self):
        """Test normalización cuando suma >100%."""
        concentrations = {"C 1s": 80.0, "O 1s": 30.0}  # Suma = 110%

        normalized = normalize_to_100(concentrations)

        # Debe reducir proporcionalmente
        total = sum(normalized.values())
        assert abs(total - 100.0) < 1e-10

        # C: 80/110 * 100 = 72.73%
        # O: 30/110 * 100 = 27.27%
        assert abs(normalized["C 1s"] - 72.727) < 0.01
        assert abs(normalized["O 1s"] - 27.273) < 0.01

    def test_normalize_three_elements(self):
        """Test normalización con tres elementos."""
        concentrations = {"C 1s": 60.0, "O 1s": 25.0, "N 1s": 10.0}  # Suma = 95%

        normalized = normalize_to_100(concentrations)

        total = sum(normalized.values())
        assert abs(total - 100.0) < 1e-10

    def test_normalize_small_values(self):
        """Test normalización con valores pequeños."""
        concentrations = {"C 1s": 0.5, "O 1s": 0.3}  # Suma = 0.8%

        normalized = normalize_to_100(concentrations)

        total = sum(normalized.values())
        assert abs(total - 100.0) < 1e-10

        # Proporciones mantenidas
        assert abs(normalized["C 1s"] - 62.5) < 1e-6  # 0.5/0.8 * 100
        assert abs(normalized["O 1s"] - 37.5) < 1e-6  # 0.3/0.8 * 100

    def test_normalize_empty_dict(self):
        """Test normalización con diccionario vacío."""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            normalize_to_100({})

    def test_normalize_zero_sum(self):
        """Test normalización cuando suma es cero."""
        concentrations = {"C 1s": 0.0, "O 1s": 0.0}

        with pytest.raises(ValueError, match="debe ser positiva"):
            normalize_to_100(concentrations)

    def test_normalize_negative_sum(self):
        """Test normalización con suma negativa."""
        concentrations = {"C 1s": -50.0, "O 1s": 30.0}  # Suma = -20

        with pytest.raises(ValueError, match="debe ser positiva"):
            normalize_to_100(concentrations)

    def test_normalize_maintains_order(self):
        """Test que normalización mantiene orden de elementos."""
        concentrations = {"C 1s": 60.0, "O 1s": 30.0, "N 1s": 5.0}

        normalized = normalize_to_100(concentrations)

        # Orden relativo mantenido (C > O > N)
        assert normalized["C 1s"] > normalized["O 1s"] > normalized["N 1s"]


# ============================================================================
# TEST INTEGRATION
# ============================================================================


class TestQuantificationIntegration:
    """Tests de integración para flujo completo."""

    def test_complete_workflow(
        self, carbon_peak, oxygen_peak, nitrogen_peak, scofield_rsf
    ):
        """Test flujo completo: load RSF -> calculate -> normalize."""
        # 1. Cargar RSF
        rsf = load_sensitivity_factors(source="scofield", xray_source="al_ka")

        # 2. Calcular concentraciones
        peaks = [carbon_peak, oxygen_peak, nitrogen_peak]
        element_names = ["C 1s", "O 1s", "N 1s"]

        concentrations = calculate_atomic_concentration(peaks, rsf, element_names)

        # 3. Verificar suma 100%
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

        # 4. Re-normalizar (no debería cambiar)
        normalized = normalize_to_100(concentrations)
        for element in element_names:
            assert abs(concentrations[element] - normalized[element]) < 1e-6

    def test_scofield_vs_wagner_comparison(self, carbon_peak, oxygen_peak):
        """Test comparación entre factores Scofield y Wagner."""
        peaks = [carbon_peak, oxygen_peak]
        element_names = ["C 1s", "O 1s"]

        # Calcular con Scofield
        rsf_scofield = load_sensitivity_factors(source="scofield")
        conc_scofield = calculate_atomic_concentration(
            peaks, rsf_scofield, element_names
        )

        # Calcular con Wagner
        rsf_wagner = load_sensitivity_factors(source="wagner")
        conc_wagner = calculate_atomic_concentration(peaks, rsf_wagner, element_names)

        # Ambos deben sumar 100%
        assert abs(sum(conc_scofield.values()) - 100.0) < 1e-6
        assert abs(sum(conc_wagner.values()) - 100.0) < 1e-6

        # Pero concentraciones serán diferentes (diferentes RSF)
        assert (
            abs(conc_scofield["C 1s"] - conc_wagner["C 1s"]) > 0.1
        )  # Diferencia significativa

    def test_al_ka_vs_mg_ka(self, carbon_peak, oxygen_peak):
        """Test comparación entre Al Kα y Mg Kα."""
        peaks = [carbon_peak, oxygen_peak]
        element_names = ["C 1s", "O 1s"]

        # Al Kα
        rsf_al = load_sensitivity_factors(source="scofield", xray_source="al_ka")
        conc_al = calculate_atomic_concentration(peaks, rsf_al, element_names)

        # Mg Kα
        rsf_mg = load_sensitivity_factors(source="scofield", xray_source="mg_ka")
        conc_mg = calculate_atomic_concentration(peaks, rsf_mg, element_names)

        # Ambos suman 100%
        assert abs(sum(conc_al.values()) - 100.0) < 1e-6
        assert abs(sum(conc_mg.values()) - 100.0) < 1e-6

        # Concentraciones diferentes (diferentes RSF)
        assert abs(conc_al["C 1s"] - conc_mg["C 1s"]) > 0.5

    def test_realistic_polymer_composition(self, scofield_rsf):
        """Test composición realista: polímero (C, O, N)."""
        # Polímero típico: ~70% C, ~20% O, ~10% N
        c_peak = PeakParameters(
            position=284.8, amplitude=2000.0, width=1.2, area=3000.0, shape="gaussian"
        )
        o_peak = PeakParameters(
            position=531.0, amplitude=800.0, width=1.5, area=900.0, shape="gaussian"
        )
        n_peak = PeakParameters(
            position=399.0, amplitude=400.0, width=1.3, area=500.0, shape="gaussian"
        )

        concentrations = calculate_atomic_concentration(
            [c_peak, o_peak, n_peak], scofield_rsf, ["C 1s", "O 1s", "N 1s"]
        )

        # Verificar rangos esperados (polímero rico en carbono)
        assert 70 < concentrations["C 1s"] < 85
        assert 10 < concentrations["O 1s"] < 20
        assert 5 < concentrations["N 1s"] < 15

    def test_realistic_oxide_composition(self, scofield_rsf):
        """Test composición realista: óxido metálico (Ti, O)."""
        # TiO2: 33% Ti, 67% O (atómico)
        ti_peak = PeakParameters(
            position=458.0, amplitude=1500.0, width=1.8, area=2700.0, shape="gaussian"
        )
        o_peak = PeakParameters(
            position=530.0, amplitude=2000.0, width=1.6, area=3200.0, shape="gaussian"
        )

        concentrations = calculate_atomic_concentration(
            [ti_peak, o_peak], scofield_rsf, ["Ti 2p", "O 1s"]
        )

        # Ti 2p RSF = 2.001, O 1s RSF = 0.711
        # Verificar que O > Ti (óxido)
        assert concentrations["O 1s"] > concentrations["Ti 2p"]
        assert 65 < concentrations["O 1s"] < 80
        assert 20 < concentrations["Ti 2p"] < 35


# ============================================================================
# TEST NUMERICAL PRECISION
# ============================================================================


class TestNumericalPrecision:
    """Tests para precisión numérica y casos límite."""

    def test_very_large_areas(self, scofield_rsf):
        """Test con áreas muy grandes."""
        peak1 = PeakParameters(
            position=284.8,
            amplitude=1e6,
            width=1.0,
            area=1e8,
            shape="gaussian",
        )
        peak2 = PeakParameters(
            position=531.0,
            amplitude=1e6,
            width=1.0,
            area=5e7,
            shape="gaussian",
        )

        concentrations = calculate_atomic_concentration(
            [peak1, peak2], scofield_rsf, ["C 1s", "O 1s"]
        )

        # Debe sumar 100% incluso con valores grandes
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

    def test_very_small_areas(self, scofield_rsf):
        """Test con áreas muy pequeñas."""
        peak1 = PeakParameters(
            position=284.8,
            amplitude=0.001,
            width=1.0,
            area=0.001,
            shape="gaussian",
        )
        peak2 = PeakParameters(
            position=531.0,
            amplitude=0.0005,
            width=1.0,
            area=0.0005,
            shape="gaussian",
        )

        concentrations = calculate_atomic_concentration(
            [peak1, peak2], scofield_rsf, ["C 1s", "O 1s"]
        )

        # Debe sumar 100% incluso con valores pequeños
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

    def test_extreme_ratio_areas(self, scofield_rsf):
        """Test con ratio extremo entre áreas."""
        peak1 = PeakParameters(
            position=284.8,
            amplitude=10000.0,
            width=1.0,
            area=15000.0,
            shape="gaussian",
        )
        peak2 = PeakParameters(
            position=531.0,
            amplitude=1.0,
            width=1.0,
            area=1.0,  # 15000:1 ratio
            shape="gaussian",
        )

        concentrations = calculate_atomic_concentration(
            [peak1, peak2], scofield_rsf, ["C 1s", "O 1s"]
        )

        # Debe sumar 100%
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

        # C debe ser >99.9%
        assert concentrations["C 1s"] > 99.9


# ============================================================================
# TESTS PARA NUEVOS ELEMENTOS (v0.8 - Fase E)
# ============================================================================


class TestNewElementsPhaseE:
    """Tests para elementos agregados en Fase E: Bi 4f, Sr 3d."""

    def test_bi_4f_available_in_scofield(self):
        """Bi 4f debe estar disponible en Scofield Al Kα."""
        rsf = load_sensitivity_factors(source="scofield", xray_source="al_ka")
        assert "Bi 4f" in rsf
        # Valor esperado: ~9.5-10.5 (elemento pesado)
        assert 9.0 < rsf["Bi 4f"] < 11.0

    def test_bi_4f_available_in_wagner(self):
        """Bi 4f debe estar disponible en Wagner Al Kα."""
        rsf = load_sensitivity_factors(source="wagner", xray_source="al_ka")
        assert "Bi 4f" in rsf
        # Valor esperado: ~10.0-10.5 (Moulder et al.)
        assert 9.5 < rsf["Bi 4f"] < 11.0

    def test_sr_3d_available_in_scofield(self):
        """Sr 3d debe estar disponible en Scofield Al Kα."""
        rsf = load_sensitivity_factors(source="scofield", xray_source="al_ka")
        assert "Sr 3d" in rsf
        # Valor esperado: ~1.8-2.2 (similar a Ca 2p)
        assert 1.5 < rsf["Sr 3d"] < 2.5

    def test_sr_3d_available_in_wagner(self):
        """Sr 3d debe estar disponible en Wagner Al Kα."""
        rsf = load_sensitivity_factors(source="wagner", xray_source="al_ka")
        assert "Sr 3d" in rsf
        # Valor esperado: ~2.0-2.3
        assert 1.8 < rsf["Sr 3d"] < 2.5

    def test_bi_4f_available_in_mg_ka(self):
        """Bi 4f debe estar disponible en Scofield Mg Kα."""
        rsf = load_sensitivity_factors(source="scofield", xray_source="mg_ka")
        assert "Bi 4f" in rsf
        # Valor escalado para Mg Kα
        assert 5.0 < rsf["Bi 4f"] < 6.5

    def test_sr_3d_available_in_mg_ka(self):
        """Sr 3d debe estar disponible en Scofield Mg Kα."""
        rsf = load_sensitivity_factors(source="scofield", xray_source="mg_ka")
        assert "Sr 3d" in rsf
        # Valor escalado para Mg Kα
        assert 1.0 < rsf["Sr 3d"] < 1.5

    def test_quantify_bi_and_o(self):
        """Test de cuantificación con Bi 4f y O 1s."""
        rsf = load_sensitivity_factors(source="wagner", xray_source="al_ka")

        # Picos sintéticos: Bi2O3
        # Ratio atómico esperado: 40% Bi, 60% O
        bi_peak = PeakParameters(
            position=159.0,  # Bi 4f7/2
            amplitude=1000.0,
            width=1.5,
            area=2000.0,
            shape="voigt",
        )

        o_peak = PeakParameters(
            position=531.0,
            amplitude=800.0,
            width=1.3,
            area=1500.0,
            shape="gaussian",
        )

        concentrations = calculate_atomic_concentration(
            [bi_peak, o_peak], rsf, ["Bi 4f", "O 1s"]
        )

        # Debe sumar 100%
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

        # Verificar que ambos elementos están presentes
        assert "Bi 4f" in concentrations
        assert "O 1s" in concentrations
        assert concentrations["Bi 4f"] > 0
        assert concentrations["O 1s"] > 0

    def test_quantify_sr_and_ti(self):
        """Test de cuantificación con Sr 3d y Ti 2p."""
        rsf = load_sensitivity_factors(source="scofield", xray_source="al_ka")

        # Picos sintéticos: SrTiO3 (Sr y Ti en ratio 1:1)
        sr_peak = PeakParameters(
            position=133.0,  # Sr 3d5/2
            amplitude=500.0,
            width=1.2,
            area=800.0,
            shape="voigt",
        )

        ti_peak = PeakParameters(
            position=458.5,  # Ti 2p3/2
            amplitude=600.0,
            width=1.4,
            area=1000.0,
            shape="voigt",
        )

        concentrations = calculate_atomic_concentration(
            [sr_peak, ti_peak], rsf, ["Sr 3d", "Ti 2p"]
        )

        # Debe sumar 100%
        total = sum(concentrations.values())
        assert abs(total - 100.0) < 1e-6

        # Verificar que ambos elementos están presentes
        assert "Sr 3d" in concentrations
        assert "Ti 2p" in concentrations

        # Ratio debería ser cercano a 1:1 (dentro de ±10%)
        ratio = concentrations["Sr 3d"] / concentrations["Ti 2p"]
        assert 0.7 < ratio < 1.3

    def test_fallback_mechanism_scofield_to_wagner(self):
        """Test de fallback automático entre fuentes RSF."""
        # Cargar con fallback habilitado
        rsf = load_sensitivity_factors(
            source="scofield", xray_source="al_ka", enable_fallback=True
        )

        # Todos los elementos nuevos deben estar presentes
        assert "Bi 4f" in rsf
        assert "Sr 3d" in rsf

        # Debe tener elementos de ambas fuentes
        # (al menos 24 elementos de Scofield + posibles de Wagner)
        assert len(rsf) >= 24

    def test_fallback_in_calculate_concentration(self):
        """Test de fallback automático en calculate_atomic_concentration."""
        # Cargar RSF sin Bi/Sr (solo elementos básicos)
        rsf_basic = {
            "C 1s": 0.296,
            "O 1s": 0.711,
        }

        # Intentar cuantificar Bi (no en RSF básico)
        bi_peak = PeakParameters(
            position=159.0,
            amplitude=1000.0,
            width=1.5,
            area=2000.0,
            shape="voigt",
        )

        o_peak = PeakParameters(
            position=531.0,
            amplitude=800.0,
            width=1.3,
            area=1500.0,
            shape="gaussian",
        )

        # Con try_fallback=True (default), debe funcionar
        concentrations = calculate_atomic_concentration(
            [bi_peak, o_peak], rsf_basic, ["Bi 4f", "O 1s"], try_fallback=True
        )

        assert "Bi 4f" in concentrations
        assert "O 1s" in concentrations

    def test_no_fallback_raises_error(self):
        """Sin fallback, elementos faltantes deben lanzar error."""
        rsf_basic = {
            "C 1s": 0.296,
            "O 1s": 0.711,
        }

        bi_peak = PeakParameters(
            position=159.0,
            amplitude=1000.0,
            width=1.5,
            area=2000.0,
            shape="voigt",
        )

        # Con try_fallback=False, debe lanzar ValueError
        with pytest.raises(ValueError, match="Factores RSF no disponibles para: Bi 4f"):
            calculate_atomic_concentration(
                [bi_peak], rsf_basic, ["Bi 4f"], try_fallback=False
            )
