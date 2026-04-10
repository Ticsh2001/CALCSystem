import pytest
import numpy as np
import copy
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.primitives.DataType import (
    Value, ValueSpec, ValueStatus, DataType, validate_data
)


class TestValueSpec:
    def test_creation_with_defaults(self):
        spec = ValueSpec()
        assert spec.value_name == ''
        assert spec.dimension == ''

    def test_creation_with_values(self):
        spec = ValueSpec(value_name='pressure', dimension='Pa')
        assert spec.value_name == 'pressure'
        assert spec.dimension == 'Pa'

    def test_from_dict(self):
        spec = ValueSpec.from_dict({'value_name': 'temp', 'dimension': 'K'})
        assert spec.value_name == 'temp'
        assert spec.dimension == 'K'

    def test_from_dict_with_defaults(self):
        spec = ValueSpec.from_dict({})
        assert spec.value_name == ''
        assert spec.dimension == ''


class TestValueStatus:
    def test_from_input_enum(self):
        assert ValueStatus.from_input(ValueStatus.CALCULATED) == ValueStatus.CALCULATED

    def test_from_input_string_uppercase(self):
        assert ValueStatus.from_input('CALCULATED') == ValueStatus.CALCULATED

    def test_from_input_string_lowercase(self):
        assert ValueStatus.from_input('calculated') == ValueStatus.CALCULATED

    def test_from_input_string_with_spaces(self):
        assert ValueStatus.from_input('  FIXED  ') == ValueStatus.FIXED

    def test_from_input_invalid_raises(self):
        with pytest.raises(ValueError):
            ValueStatus.from_input('INVALID')

    def test_from_input_unsupported_type(self):
        with pytest.raises(ValueError):
            ValueStatus.from_input(123)


class TestDataType:
    def test_from_input_string(self):
        assert DataType.from_input('FLOAT') == DataType.FLOAT
        assert DataType.from_input('int') == DataType.INT
        assert DataType.from_input('logic') == DataType.LOGIC

    def test_from_input_enum(self):
        assert DataType.from_input(DataType.STRING) == DataType.STRING

    def test_all_types_accessible(self):
        assert DataType.FLOAT is not None
        assert DataType.LOGIC is not None
        assert DataType.LOGIC_TRUE is not None
        assert DataType.LOGIC_FALSE is not None
        assert DataType.TIMESTAMP is not None
        assert DataType.STRING is not None
        assert DataType.INT is not None


class TestValidateData:
    def test_validate_float_with_float(self):
        validate_data(1.5, DataType.FLOAT)
        validate_data(0.0, DataType.FLOAT)
        validate_data(-10.5, DataType.FLOAT)

    def test_validate_float_with_int(self):
        validate_data(5, DataType.FLOAT)

    def test_validate_float_with_bool(self):
        validate_data(True, DataType.FLOAT)

    def test_validate_int_with_int(self):
        validate_data(5, DataType.INT)

    def test_validate_int_with_bool(self):
        validate_data(True, DataType.INT)

    def test_validate_logic_with_bool(self):
        validate_data(True, DataType.LOGIC)
        validate_data(False, DataType.LOGIC)

    def test_validate_logic_with_0_1(self):
        validate_data(0, DataType.LOGIC)
        validate_data(1, DataType.LOGIC)

    def test_validate_none_skipped(self):
        validate_data(None, DataType.FLOAT)
        validate_data(None, DataType.INT)

    def test_validate_float_wrong_type(self):
        with pytest.raises(TypeError):
            validate_data('string', DataType.FLOAT)

    def test_validate_int_wrong_type(self):
        with pytest.raises(TypeError):
            validate_data(1.5, DataType.INT)

    def test_validate_range_min(self):
        validate_data(5, DataType.FLOAT, min_val=0)
        with pytest.raises(ValueError):
            validate_data(-1, DataType.FLOAT, min_val=0)

    def test_validate_range_max(self):
        validate_data(5, DataType.FLOAT, max_val=10)
        with pytest.raises(ValueError):
            validate_data(15, DataType.FLOAT, max_val=10)


class TestValueInit:
    def test_basic_float_value(self):
        val = Value('test', 1.5, ValueSpec('x', 'm'))
        assert val.value == 1.5
        assert val.name == 'test'
        assert val.value_type == DataType.FLOAT
        assert val.status == 'UNKNOWN'

    def test_with_string_type(self):
        val = Value('test', 5, ValueSpec(), value_type='INT')
        assert val.value_type == DataType.INT
        assert val.value == 5

    def test_with_string_status(self):
        val = Value('test', 1.0, ValueSpec(), status='FIXED')
        assert val.status == 'FIXED'
        assert val._status == ValueStatus.FIXED

    def test_with_dict_spec(self):
        val = Value('test', 1.0, {'value_name': 'y', 'dimension': 'kg'})
        assert val.spec.value_name == 'y'
        assert val.spec.dimension == 'kg'

    def test_with_description(self):
        val = Value('test', 1.0, ValueSpec(), description='A test value')
        assert val.description == 'A test value'

    def test_init_int_value(self):
        val = Value('count', 42, ValueSpec(), value_type=DataType.INT)
        assert val.value == 42
        assert val.value_type == DataType.INT

    def test_init_bool_value(self):
        val = Value('flag', True, ValueSpec(), value_type=DataType.LOGIC)
        assert val.value is True

    def test_init_numpy_array(self):
        arr = np.array([1.0, 2.0, 3.0])
        val = Value('arr', arr, ValueSpec())
        assert np.array_equal(val.value, arr)

    def test_init_list(self):
        val = Value('list', [1, 2, 3], ValueSpec(), value_type='INT')
        assert val.value == [1, 2, 3]


class TestValueInitValidation:
    def test_wrong_type_raises(self):
        with pytest.raises(TypeError):
            Value('test', 'string', ValueSpec(), value_type='FLOAT')

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            Value('test', 10, ValueSpec(), value_type='INT', max_value=5)


class TestValueUpdate:
    def test_update_value(self):
        val = Value('test', 1.0, ValueSpec())
        val.update(2.0)
        assert val.value == 2.0

    def test_update_with_status(self):
        val = Value('test', 1.0, ValueSpec(), status='CALCULATED')
        val.update(2.0, ValueStatus.FIXED)
        assert val.value == 2.0
        assert val.status == 'FIXED'

    def test_update_without_status_keeps_current(self):
        val = Value('test', 1.0, ValueSpec(), status='CALCULATED')
        val.update(2.0)
        assert val.status == 'CALCULATED'

    def test_update_wrong_type_raises(self):
        val = Value('test', 1.0, ValueSpec())
        with pytest.raises(TypeError):
            val.update('string')

    def test_update_out_of_range_raises(self):
        val = Value('test', 1.0, ValueSpec(), max_value=10)
        with pytest.raises(ValueError):
            val.update(20.0)


class TestValuePrevStorage:
    def test_prev_not_stored_by_default(self):
        val = Value('test', 1.0, ValueSpec())
        val.update(2.0)
        assert val.prev_value is None

    def test_prev_stored_when_enabled(self):
        val = Value('test', 1.0, ValueSpec(), store_prev=True)
        val.update(2.0)
        assert val.prev_value == 1.0

    def test_prev_status_stored(self):
        val = Value('test', 1.0, ValueSpec(), store_prev=True, status='CALCULATED')
        val.update(2.0, ValueStatus.FIXED)
        assert val.prev_status == 'CALCULATED'

    def test_prev_status_when_new_status_provided(self):
        val = Value('test', 1.0, ValueSpec(), store_prev=True, status=ValueStatus.CALCULATED)
        val.update(2.0, ValueStatus.FIXED)
        assert val.prev_status == 'CALCULATED'


class TestValueProperties:
    def test_name_property(self):
        val = Value('myname', 1.0, ValueSpec())
        assert val.name == 'myname'

    def test_spec_property(self):
        val = Value('test', 1.0, ValueSpec('pressure', 'Pa'))
        assert val.spec.value_name == 'pressure'
        assert val.spec.dimension == 'Pa'

    def test_spec_is_copy(self):
        val = Value('test', 1.0, ValueSpec('x', 'm'))
        spec = val.spec
        spec.value_name = 'changed'
        assert val.spec.value_name == 'x'

    def test_min_value_property(self):
        val = Value('test', 5.0, ValueSpec(), min_value=0.0)
        assert val.min_value == 0.0

    def test_max_value_property(self):
        val = Value('test', 5.0, ValueSpec(), max_value=10.0)
        assert val.max_value == 10.0

    def test_store_prev_property(self):
        val = Value('test', 1.0, ValueSpec(), store_prev=True)
        assert val.store_prev is True

    def test_value_setter(self):
        val = Value('test', 1.0, ValueSpec())
        val.value = 5.0
        assert val.value == 5.0


class TestValueCopyBehavior:
    def test_internal_value_not_modified(self):
        original = np.array([1.0, 2.0, 3.0])
        val = Value('test', original, ValueSpec())
        original[0] = 99.0
        assert val.value[0] == 1.0

    def test_update_with_numpy_array(self):
        arr = np.array([1.0, 2.0, 3.0])
        val = Value('test', np.array([0.0]), ValueSpec())
        val.update(arr)
        arr[0] = 99.0
        assert val.value[0] == 1.0

    def test_list_deep_copy(self):
        original = [1, 2, 3]
        val = Value('test', original, ValueSpec(), value_type='INT')
        original.append(4)
        assert val.value == [1, 2, 3]

    def test_min_value_returns_copy(self):
        original = np.array([0.0])
        val = Value('test', 5.0, ValueSpec(), min_value=original)
        returned = val.min_value
        returned[0] = 10.0
        assert val.min_value[0] == 0.0

    def test_max_value_returns_copy(self):
        original = np.array([10.0])
        val = Value('test', 5.0, ValueSpec(), max_value=original)
        returned = val.max_value
        returned[0] = 0.0
        assert val.max_value[0] == 10.0
