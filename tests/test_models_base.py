import pytest
import numpy as np
from pydantic import ValidationError
from xps_analyzer.models.base import XPSBaseModel, NumpyArrayValidator, XPSValidators

# NumpyArrayValidator.validate_positive_array
def test_numpy_array_validator_validate_positive_array():
    val = NumpyArrayValidator.validate_positive_array(np.array([1, 2, 3]), "test_field")
    assert np.array_equal(val, np.array([1, 2, 3]))

    val = NumpyArrayValidator.validate_positive_array([1, 2, 3], "test_field")
    assert np.array_equal(val, np.array([1, 2, 3]))

    with pytest.raises(ValueError, match="no puede estar vacío"):
        NumpyArrayValidator.validate_positive_array(np.array([]), "test_field")

    with pytest.raises(ValueError, match="solo valores finitos"):
        NumpyArrayValidator.validate_positive_array(np.array([1, np.inf, 3]), "test_field")

    with pytest.raises(ValueError, match="solo valores positivos"):
        NumpyArrayValidator.validate_positive_array(np.array([1, -2, 3]), "test_field")

# NumpyArrayValidator.validate_finite_array
def test_numpy_array_validator_validate_finite_array():
    val = NumpyArrayValidator.validate_finite_array(np.array([1, -2, 3]), "test_field")
    assert np.array_equal(val, np.array([1, -2, 3]))

    val = NumpyArrayValidator.validate_finite_array([1, -2, 3], "test_field")
    assert np.array_equal(val, np.array([1, -2, 3]))

    with pytest.raises(ValueError, match="no puede estar vacío"):
        NumpyArrayValidator.validate_finite_array(np.array([]), "test_field")

    with pytest.raises(ValueError, match="solo valores finitos"):
        NumpyArrayValidator.validate_finite_array(np.array([1, np.inf, 3]), "test_field")

# NumpyArrayValidator.validate_matching_lengths
def test_numpy_array_validator_validate_matching_lengths():
    NumpyArrayValidator.validate_matching_lengths(np.array([1, 2]), np.array([3, 4]), "field1", "field2")
    with pytest.raises(ValueError, match="deben tener la misma longitud"):
        NumpyArrayValidator.validate_matching_lengths(np.array([1, 2]), np.array([3]), "field1", "field2")

# XPSValidators.validate_binding_energy
def test_xps_validators_validate_binding_energy():
    val = XPSValidators.validate_binding_energy(np.array([1, 2]))
    assert np.array_equal(val, np.array([1, 2]))

# XPSValidators.validate_intensity
def test_xps_validators_validate_intensity():
    val = XPSValidators.validate_intensity(np.array([0, 1, 2]))
    assert np.array_equal(val, np.array([0, 1, 2]))

    val = XPSValidators.validate_intensity([0, 1, 2])
    assert np.array_equal(val, np.array([0, 1, 2]))

    with pytest.raises(ValueError, match="intensity no puede estar vacío"):
        XPSValidators.validate_intensity(np.array([]))

    with pytest.raises(ValueError, match="intensity debe contener solo valores finitos"):
        XPSValidators.validate_intensity(np.array([1, np.inf]))

    with pytest.raises(ValueError, match="intensity debe contener solo valores no negativos"):
        XPSValidators.validate_intensity(np.array([-1, 0]))

# XPSValidators.validate_region_name
def test_xps_validators_validate_region_name():
    assert XPSValidators.validate_region_name(" C 1s ") == "C 1s"
    
    with pytest.raises(TypeError, match="region_name debe ser string"):
        XPSValidators.validate_region_name(123)
        
    with pytest.raises(ValueError, match="region_name no puede estar vacío"):
        XPSValidators.validate_region_name("   ")

# XPSValidators.validate_element_symbol
def test_xps_validators_validate_element_symbol():
    assert XPSValidators.validate_element_symbol("c") == "C"
    assert XPSValidators.validate_element_symbol("fe") == "Fe"
    assert XPSValidators.validate_element_symbol(" fE ") == "Fe"
    
    with pytest.raises(TypeError, match="symbol debe ser string"):
        XPSValidators.validate_element_symbol(123)

    with pytest.raises(ValueError, match="symbol no puede estar vacío"):
        XPSValidators.validate_element_symbol("   ")

    with pytest.raises(ValueError, match="symbol debe tener máximo 2 caracteres"):
        XPSValidators.validate_element_symbol("Carbon")

def test_xpsbase_model_extra_forbid():
    class DummyModel(XPSBaseModel):
        name: str

    m = DummyModel(name="test")
    with pytest.raises(ValidationError):
        m.extra_attr = 123

def test_xpsbase_model_validate_assignment():
    class DummyModel(XPSBaseModel):
        val: int
    
    m = DummyModel(val=1)
    with pytest.raises(ValidationError):
        m.val = "not a number"
