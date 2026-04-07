"""
Tests para modelos Pydantic del núcleo de XPS (XPSSpectrum, XPSDataset, XPSSample).

Verifica validación automática avanzada y funcionalidad de las estructuras
de datos principales migradas a Pydantic BaseModel.
"""

import numpy as np
import pytest

from xps_analyzer.models.core import XPSSpectrum, XPSDataset, XPSSample


class TestXPSSpectrum:
    """Tests para XPSSpectrum Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de espectro XPS."""
        energies = np.array([280.0, 285.0, 290.0])
        intensities = np.array([100.0, 1000.0, 200.0])

        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=energies,
            intensity=intensities,
            metadata={"pass_energy": 20},
        )

        assert spectrum.region_name == "C 1s"
        assert len(spectrum.binding_energy) == 3
        assert len(spectrum.intensity) == 3
        assert spectrum.metadata["pass_energy"] == 20

    def test_empty_region_name_fails(self):
        """Test que nombres de región vacíos fallan."""
        with pytest.raises(ValueError, match="region_name no puede estar vacío"):
            XPSSpectrum(
                region_name="   ",
                binding_energy=np.array([280.0, 285.0]),
                intensity=np.array([100.0, 200.0]),
                metadata={},
            )

    def test_negative_binding_energy_fails(self):
        """Test que energías negativas fallan."""
        with pytest.raises(ValueError, match="positiv"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([-10.0, 285.0]),
                intensity=np.array([100.0, 200.0]),
                metadata={},
            )

    def test_negative_intensity_fails(self):
        """Test que intensidades negativas fallan."""
        with pytest.raises(ValueError, match="no negativos"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([280.0, 285.0]),
                intensity=np.array([100.0, -200.0]),
                metadata={},
            )

    def test_mismatched_array_lengths_fail(self):
        """Test que arrays de distinta longitud fallan."""
        with pytest.raises(ValueError, match="misma longitud"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([280.0, 285.0, 290.0]),
                intensity=np.array([100.0, 200.0]),  # Longitud diferente
                metadata={},
            )

    def test_too_few_points_fails(self):
        """Test que espectros con muy pocos puntos fallan."""
        with pytest.raises(ValueError, match="al menos 2 puntos"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([285.0]),
                intensity=np.array([100.0]),
                metadata={},
            )

    def test_unrealistic_energy_range_fails(self):
        """Test que rangos de energía no realistas fallan."""
        # Rango muy grande
        with pytest.raises(ValueError, match="excede rango típico"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([100.0, 3000.0]),  # > 2000 eV
                intensity=np.array([100.0, 200.0]),
                metadata={},
            )

        # Rango muy pequeño
        with pytest.raises(ValueError, match="muy pequeño"):
            XPSSpectrum(
                region_name="C 1s",
                binding_energy=np.array([285.0, 285.5]),  # < 1 eV
                intensity=np.array([100.0, 200.0]),
                metadata={},
            )

    def test_data_property(self):
        """Test propiedad data retorna DataFrame correcto."""
        energies = np.array([280.0, 285.0, 290.0])
        intensities = np.array([100.0, 1000.0, 200.0])

        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=energies,
            intensity=intensities,
            metadata={},
        )

        df = spectrum.data
        assert df.index.name == "binding_energy"
        assert "intensity" in df.columns
        assert len(df) == 3

    def test_copy_method(self):
        """Test método copy crea copia independiente."""
        energies = np.array([280.0, 285.0, 290.0])
        intensities = np.array([100.0, 1000.0, 200.0])

        original = XPSSpectrum(
            region_name="C 1s",
            binding_energy=energies,
            intensity=intensities,
            metadata={"test": "value"},
        )

        copy_spec = original.copy()

        # Verificar que es una copia independiente
        copy_spec.intensity[0] = 999.0
        assert original.intensity[0] == 100.0  # Original no modificado

        copy_spec.metadata["test"] = "modified"
        assert original.metadata["test"] == "value"  # Original no modificado

    def test_energy_range_method(self):
        """Test método get_energy_range."""
        energies = np.array([280.0, 285.0, 290.0])
        intensities = np.array([100.0, 1000.0, 200.0])

        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=energies,
            intensity=intensities,
            metadata={},
        )

        min_e, max_e = spectrum.get_energy_range()
        assert min_e == 280.0
        assert max_e == 290.0

    def test_intensity_stats_method(self):
        """Test método get_intensity_stats."""
        intensities = np.array([100.0, 200.0, 300.0])
        energies = np.array([280.0, 285.0, 290.0])

        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=energies,
            intensity=intensities,
            metadata={},
        )

        stats = spectrum.get_intensity_stats()
        assert stats["max"] == 300.0
        assert stats["min"] == 100.0
        assert stats["mean"] == 200.0


class TestXPSDataset:
    """Tests para XPSDataset Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de dataset XPS."""
        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0, 290.0]),
            intensity=np.array([100.0, 1000.0, 200.0]),
            metadata={},
        )

        dataset = XPSDataset(
            filename="sample1.txt",
            header={"date": "2024-03-15"},
            spectra={"C 1s": spectrum},
        )

        assert dataset.filename == "sample1.txt"
        assert "C 1s" in dataset.spectra
        assert dataset.header["date"] == "2024-03-15"

    def test_empty_filename_fails(self):
        """Test que filenames vacíos fallan."""
        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="filename no puede estar vacío"):
            XPSDataset(filename="   ", header={}, spectra={"C 1s": spectrum})

    def test_empty_spectra_fails(self):
        """Test que diccionarios de espectros vacíos fallan."""
        with pytest.raises(ValueError):
            XPSDataset(
                filename="sample1.txt",
                header={},
                spectra={},  # Vacío
            )

    def test_inconsistent_spectrum_names_fail(self):
        """Test que nombres inconsistentes entre clave y espectro fallan."""
        spectrum = XPSSpectrum(
            region_name="C 1s",  # Nombre en espectro
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="Inconsistencia"):
            XPSDataset(
                filename="sample1.txt",
                header={},
                spectra={"O 1s": spectrum},  # Clave diferente
            )

    def test_invalid_filename_characters_fail(self):
        """Test que caracteres inválidos en filename fallan."""
        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )

        with pytest.raises(ValueError, match="caracteres inválidos"):
            XPSDataset(
                filename="sample<>:.txt",  # Caracteres inválidos
                header={},
                spectra={"C 1s": spectrum},
            )

    def test_get_spectrum_method(self):
        """Test método get_spectrum."""
        spectrum1 = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )
        spectrum2 = XPSSpectrum(
            region_name="O 1s",
            binding_energy=np.array([530.0, 535.0]),
            intensity=np.array([300.0, 400.0]),
            metadata={},
        )

        dataset = XPSDataset(
            filename="sample1.txt",
            header={},
            spectra={"C 1s": spectrum1, "O 1s": spectrum2},
        )

        # Existente
        c_spec = dataset.get_spectrum("C 1s")
        assert c_spec is not None
        assert c_spec.region_name == "C 1s"

        # No existente
        n_spec = dataset.get_spectrum("N 1s")
        assert n_spec is None

    def test_list_regions_method(self):
        """Test método list_regions retorna lista ordenada."""
        spectrum1 = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )
        spectrum2 = XPSSpectrum(
            region_name="O 1s",
            binding_energy=np.array([530.0, 535.0]),
            intensity=np.array([300.0, 400.0]),
            metadata={},
        )

        dataset = XPSDataset(
            filename="sample1.txt",
            header={},
            spectra={"O 1s": spectrum2, "C 1s": spectrum1},  # Orden aleatorio
        )

        regions = dataset.list_regions()
        assert regions == ["C 1s", "O 1s"]  # Ordenado alfabéticamente


class TestXPSSample:
    """Tests para XPSSample Pydantic."""

    def test_valid_creation(self):
        """Test creación válida de muestra XPS."""
        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )
        dataset = XPSDataset(
            filename="sample1.txt", header={}, spectra={"C 1s": spectrum}
        )

        sample = XPSSample(sample_name="Test_Sample", datasets={"sample1.txt": dataset})

        assert sample.sample_name == "Test_Sample"
        assert "sample1.txt" in sample.datasets

    def test_empty_sample_name_fails(self):
        """Test que nombres de muestra vacíos fallan."""
        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )
        dataset = XPSDataset(
            filename="sample1.txt", header={}, spectra={"C 1s": spectrum}
        )

        with pytest.raises(ValueError, match="sample_name no puede estar vacío"):
            XPSSample(sample_name="   ", datasets={"sample1.txt": dataset})

    def test_empty_datasets_fails(self):
        """Test que diccionarios de datasets vacíos fallan."""
        with pytest.raises(ValueError):
            XPSSample(
                sample_name="Test_Sample",
                datasets={},  # Vacío
            )

    def test_inconsistent_dataset_filenames_fail(self):
        """Test que filenames inconsistentes fallan."""
        spectrum = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )
        dataset = XPSDataset(
            filename="sample1.txt",  # Filename en dataset
            header={},
            spectra={"C 1s": spectrum},
        )

        with pytest.raises(ValueError, match="Inconsistencia"):
            XPSSample(
                sample_name="Test_Sample",
                datasets={"sample2.txt": dataset},  # Clave diferente
            )

    def test_find_spectra_by_region_method(self):
        """Test método find_spectra_by_region."""
        # Dataset 1
        c1s_spec1 = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([100.0, 200.0]),
            metadata={},
        )
        dataset1 = XPSDataset(
            filename="file1.txt", header={}, spectra={"C 1s": c1s_spec1}
        )

        # Dataset 2
        c1s_spec2 = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0]),
            intensity=np.array([150.0, 250.0]),
            metadata={},
        )
        o1s_spec2 = XPSSpectrum(
            region_name="O 1s",
            binding_energy=np.array([530.0, 535.0]),
            intensity=np.array([300.0, 400.0]),
            metadata={},
        )
        dataset2 = XPSDataset(
            filename="file2.txt",
            header={},
            spectra={"C 1s": c1s_spec2, "O 1s": o1s_spec2},
        )

        sample = XPSSample(
            sample_name="Test_Sample",
            datasets={"file1.txt": dataset1, "file2.txt": dataset2},
        )

        # Buscar C 1s (presente en ambos)
        c1s_results = sample.find_spectra_by_region("C 1s")
        assert len(c1s_results) == 2
        assert "file1.txt" in c1s_results
        assert "file2.txt" in c1s_results

        # Buscar O 1s (solo en file2)
        o1s_results = sample.find_spectra_by_region("O 1s")
        assert len(o1s_results) == 1
        assert "file2.txt" in o1s_results

        # Buscar N 1s (no presente)
        n1s_results = sample.find_spectra_by_region("N 1s")
        assert len(n1s_results) == 0

    def test_get_sample_statistics_method(self):
        """Test método get_sample_statistics."""
        spectrum1 = XPSSpectrum(
            region_name="C 1s",
            binding_energy=np.array([280.0, 285.0, 290.0]),  # 3 puntos
            intensity=np.array([100.0, 200.0, 150.0]),
            metadata={},
        )
        spectrum2 = XPSSpectrum(
            region_name="O 1s",
            binding_energy=np.array([530.0, 535.0]),  # 2 puntos
            intensity=np.array([300.0, 400.0]),
            metadata={},
        )
        dataset = XPSDataset(
            filename="file1.txt",
            header={},
            spectra={"C 1s": spectrum1, "O 1s": spectrum2},
        )

        sample = XPSSample(sample_name="Test_Sample", datasets={"file1.txt": dataset})

        stats = sample.get_sample_statistics()
        assert stats["sample_name"] == "Test_Sample"
        assert stats["total_datasets"] == 1
        assert stats["total_spectra"] == 2
        assert stats["total_data_points"] == 5  # 3 + 2
        assert set(stats["unique_regions"]) == {"C 1s", "O 1s"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
