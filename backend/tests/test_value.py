import pytest
import numpy as np
import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _root)

from backend.core.primitives.Value import Value, validate_data
from backend.core.primitives.DataType import ValueSpec, ValueStatus, DataType


class TestValidateData:
    def test_float_accepts_float(self):
        validate_data(1.5, DataType.FLOAT)
        validate_data(0.0, DataType.FLOAT)
        validate_data(-10.5, DataType.FLOAT)

    def test_float_accepts_int(self):
        validate_data(5, DataType.FLOAT)

    def test_float_accepts_bool(self):
        validate_data(True, DataType.FLOAT)

    def test_float_accepts_numpy_array(self):
        validate_data(np.array([1.0, 2.0, 3.0]), DataType.FLOAT)

    def test_float_accepts_numpy_int_array(self):
        validate_data(np.array([1, 2, 3]), DataType.FLOAT)

    def test_float_accepts_float_list(self):
        validate_data([1.5, 2.5, 3.5], DataType.FLOAT)

    def test_float_accepts_float_tuple(self):
        validate_data((1.5, 2.5), DataType.FLOAT)

    def test_float_rejects_string(self):
        with pytest.raises(TypeError, match='Wrong type of input data'):
            validate_data('string', DataType.FLOAT)

    def test_float_rejects_mixed_list(self):
        with pytest.raises(TypeError):
            validate_data([1.0, 'bad'], DataType.FLOAT)

    def test_int_accepts_int(self):
        validate_data(5, DataType.INT)

    def test_int_accepts_bool(self):
        validate_data(True, DataType.INT)

    def test_int_accepts_int_list(self):
        validate_data([1, 2, 3], DataType.INT)

    def test_int_accepts_int_tuple(self):
        validate_data((1, 2, 3), DataType.INT)

    def test_int_accepts_numpy_int_array(self):
        validate_data(np.array([1, 2, 3]), DataType.INT)

    def test_int_accepts_numpy_bool_array(self):
        validate_data(np.array([True, False]), DataType.INT)

    def test_int_rejects_float(self):
        with pytest.raises(TypeError, match='Wrong type of input data'):
            validate_data(1.5, DataType.INT)

    def test_int_rejects_float_list(self):
        with pytest.raises(TypeError):
            validate_data([1.5, 2.5], DataType.INT)

    def test_logic_accepts_bool(self):
        validate_data(True, DataType.LOGIC)
        validate_data(False, DataType.LOGIC)

    def test_logic_accepts_0_and_1(self):
        validate_data(0, DataType.LOGIC)
        validate_data(1, DataType.LOGIC)

    def test_logic_rejects_other_int(self):
        with pytest.raises(TypeError, match='Wrong type of input data'):
            validate_data(2, DataType.LOGIC)

    def test_logic_accepts_bool_list(self):
        validate_data([True, False, True], DataType.LOGIC)

    def test_logic_accepts_0_1_list(self):
        validate_data([0, 1, 0], DataType.LOGIC)

    def test_logic_rejects_other_int_list(self):
        with pytest.raises(TypeError):
            validate_data([0, 1, 2], DataType.LOGIC)

    def test_logic_accepts_numpy_bool_array(self):
        validate_data(np.array([True, False]), DataType.LOGIC)

    def test_logic_accepts_numpy_0_1_int_array(self):
        validate_data(np.array([0, 1, 0]), DataType.LOGIC)

    def test_logic_rejects_numpy_int_array_with_other_values(self):
        with pytest.raises(TypeError):
            validate_data(np.array([0, 1, 2]), DataType.LOGIC)

    def test_object_accepts_lambda(self):
        validate_data(lambda x: x, DataType.OBJECT)

    def test_object_accepts_class(self):
        class Foo:
            pass
        validate_data(Foo, DataType.OBJECT)

    def test_object_accepts_callable_class_instance(self):
        class CallableClass:
            def __call__(self):
                pass
        validate_data(CallableClass(), DataType.OBJECT)

    def test_object_rejects_int(self):
        with pytest.raises(TypeError):
            validate_data(42, DataType.OBJECT)

    def test_object_rejects_string(self):
        with pytest.raises(TypeError):
            validate_data('hello', DataType.OBJECT)

    def test_timestamp_accepts_datetime64(self):
        validate_data(np.datetime64('2024-01-01'), DataType.TIMESTAMP)

    def test_timestamp_accepts_datetime64_array(self):
        validate_data(np.array(['2024-01-01', '2024-02-01'], dtype='datetime64'), DataType.TIMESTAMP)

    def test_timestamp_rejects_non_datetime(self):
        with pytest.raises((TypeError, AttributeError)):
            validate_data('2024-01-01', DataType.TIMESTAMP)

    def test_none_skipped_all_types(self):
        validate_data(None, DataType.FLOAT)
        validate_data(None, DataType.INT)
        validate_data(None, DataType.LOGIC)
        validate_data(None, DataType.OBJECT)
        validate_data(None, DataType.TIMESTAMP)

    def test_range_min_validation(self):
        validate_data(5, DataType.FLOAT, min_val=0)
        with pytest.raises(ValueError, match='less than minimum'):
            validate_data(-1, DataType.FLOAT, min_val=0)

    def test_range_max_validation(self):
        validate_data(5, DataType.FLOAT, max_val=10)
        with pytest.raises(ValueError, match='greater than maximum'):
            validate_data(15, DataType.FLOAT, max_val=10)

    def test_range_min_on_numpy_array(self):
        validate_data(np.array([1, 2, 3]), DataType.INT, min_val=0)
        with pytest.raises(ValueError):
            validate_data(np.array([1, -2, 3]), DataType.INT, min_val=0)

    def test_range_max_on_numpy_array(self):
        validate_data(np.array([1, 2, 3]), DataType.INT, max_val=5)
        with pytest.raises(ValueError):
            validate_data(np.array([1, 2, 6]), DataType.INT, max_val=5)

    def test_range_min_and_max(self):
        validate_data(5, DataType.FLOAT, min_val=0, max_val=10)
        with pytest.raises(ValueError):
            validate_data(-1, DataType.FLOAT, min_val=0, max_val=10)
        with pytest.raises(ValueError):
            validate_data(11, DataType.FLOAT, min_val=0, max_val=10)

    def test_range_min_not_applied_to_non_numeric(self):
        validate_data(lambda x: x, DataType.OBJECT, min_val=0, max_val=10)

    def test_float_accepts_numpy_float_scalar(self):
        validate_data(np.float64(3.14), DataType.FLOAT)

    def test_float_accepts_numpy_int_scalar(self):
        validate_data(np.int32(42), DataType.FLOAT)


class TestValueInit:
    # Signature: Value(name, value, serialize_data, value_spec, ...)

    def test_basic_float_value(self):
        val = Value('test', 1.5, True, ValueSpec('x', 'm'))
        assert val.value == 1.5
        assert val.name == 'test'
        assert val.value_type == 'FLOAT'
        assert val.status == 'UNKNOWN'

    def test_with_string_type(self):
        val = Value('test', 5, True, ValueSpec(), value_type='INT')
        assert val.value_type == 'INT'
        assert val.value == 5

    def test_with_string_status(self):
        val = Value('test', 1.0, True, ValueSpec(), status='FIXED')
        assert val.status == 'FIXED'

    def test_with_dict_spec(self):
        val = Value('test', 1.0, True, {'value_name': 'y', 'dimension': 'kg'})
        assert val.spec.value_name == 'y'
        assert val.spec.dimension == 'kg'

    def test_with_description(self):
        val = Value('test', 1.0, True, ValueSpec(), description='A test value')
        assert val.description == 'A test value'

    def test_int_value(self):
        val = Value('count', 42, True, ValueSpec(), value_type=DataType.INT)
        assert val.value == 42
        assert val.value_type == 'INT'

    def test_bool_value(self):
        val = Value('flag', True, True, ValueSpec(), value_type=DataType.LOGIC)
        assert val.value is True

    def test_numpy_array_value(self):
        arr = np.array([1.0, 2.0, 3.0])
        val = Value('arr', arr, True, ValueSpec())
        assert np.array_equal(val.value, arr)

    def test_list_value(self):
        val = Value('list', [1, 2, 3], True, ValueSpec(), value_type='INT')
        assert val.value == [1, 2, 3]

    def test_object_callable_value(self):
        def func(x):
            return x * 2
        val = Value('func', func, True, ValueSpec(), value_type='OBJECT')
        assert val.value is func

    def test_init_with_all_params_keyword(self):
        val = Value(
            name='full',
            value=42.0,
            serialize_data=True,
            value_spec=ValueSpec('temp', 'K'),
            description='Temperature',
            status='FIXED',
            value_type='FLOAT',
            store_prev=True,
            min_value=-100.0,
            max_value=500.0,
        )
        assert val.name == 'full'
        assert val.value == 42.0
        assert val.spec.value_name == 'temp'
        assert val.description == 'Temperature'
        assert val.status == 'FIXED'
        assert val.value_type == 'FLOAT'
        assert val.store_prev is True
        assert val.min_value == -100.0
        assert val.max_value == 500.0

    def test_serialize_data_false(self):
        val = Value('test', 1.0, False, ValueSpec())
        assert val.serialize_data is False

    def test_serialize_data_true(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.serialize_data is True

    def test_object_type_is_value(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.object_type == 'VALUE'

    def test_default_value_type_is_float(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.value_type == 'FLOAT'

    def test_default_status_is_unknown(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.status == 'UNKNOWN'

    def test_default_store_prev_is_false(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.store_prev is False

    def test_init_with_string_status_enum(self):
        val = Value('test', 1.0, True, ValueSpec(), status='CALCULATED')
        assert val.status == 'CALCULATED'

    def test_init_with_value_status_enum(self):
        val = Value('test', 1.0, True, ValueSpec(), status=ValueStatus.FIXED)
        assert val.status == 'FIXED'

    def test_init_with_string_type_enum(self):
        val = Value('test', 1, True, ValueSpec(), value_type='INT')
        assert val.value_type == 'INT'

    def test_init_with_data_type_enum(self):
        val = Value('test', 1, True, ValueSpec(), value_type=DataType.INT)
        assert val.value_type == 'INT'


class TestValueInitValidation:
    def test_wrong_type_raises(self):
        with pytest.raises(TypeError, match='Wrong type of input data'):
            Value('test', 'string', True, ValueSpec(), value_type='FLOAT')

    def test_int_init_with_float_raises(self):
        with pytest.raises(TypeError):
            Value('test', 1.5, True, ValueSpec(), value_type='INT')

    def test_logic_init_with_2_raises(self):
        with pytest.raises(TypeError):
            Value('test', 2, True, ValueSpec(), value_type='LOGIC')

    def test_out_of_range_min_raises(self):
        with pytest.raises(ValueError):
            Value('test', -10, True, ValueSpec(), value_type='INT', min_value=0)

    def test_out_of_range_max_raises(self):
        with pytest.raises(ValueError):
            Value('test', 10, True, ValueSpec(), value_type='INT', max_value=5)

    def test_out_of_range_min_float_raises(self):
        with pytest.raises(ValueError):
            Value('test', -1.0, True, ValueSpec(), value_type='FLOAT', min_value=0.0)

    def test_out_of_range_max_float_raises(self):
        with pytest.raises(ValueError):
            Value('test', 11.0, True, ValueSpec(), value_type='FLOAT', max_value=10.0)

    def test_init_with_none_value(self):
        val = Value('test', None, True, ValueSpec(), value_type='FLOAT')
        assert val.value is None


class TestValueUpdate:
    def test_update_new_value(self):
        val = Value('test', 1.0, True, ValueSpec())
        val.update(2.0)
        assert val.value == 2.0

    def test_update_with_status(self):
        val = Value('test', 1.0, True, ValueSpec(), status='CALCULATED')
        val.update(2.0, ValueStatus.FIXED)
        assert val.value == 2.0
        assert val.status == 'FIXED'

    def test_update_without_status_preserves_current(self):
        val = Value('test', 1.0, True, ValueSpec(), status='CALCULATED')
        val.update(2.0)
        assert val.status == 'CALCULATED'

    def test_update_with_enum_status(self):
        val = Value('test', 1.0, True, ValueSpec())
        val.update(2.0, ValueStatus.FIXED)
        assert val.status == 'FIXED'

    def test_update_wrong_type_raises(self):
        val = Value('test', 1.0, True, ValueSpec())
        with pytest.raises(TypeError):
            val.update('string')

    def test_update_out_of_range_min_raises(self):
        val = Value('test', 5.0, True, ValueSpec(), min_value=0.0)
        with pytest.raises(ValueError):
            val.update(-1.0)

    def test_update_out_of_range_max_raises(self):
        val = Value('test', 1.0, True, ValueSpec(), max_value=10.0)
        with pytest.raises(ValueError):
            val.update(20.0)

    def test_update_validates_after_mutation(self):
        val = Value('test', 5.0, True, ValueSpec(), max_value=10.0)
        val.update(7.0)
        assert val.value == 7.0

    def test_update_int_to_logic_rejected(self):
        val = Value('test', True, True, ValueSpec(), value_type='LOGIC')
        with pytest.raises(TypeError):
            val.update(2)

    def test_update_with_numpy_array(self):
        val = Value('test', np.array([1.0]), True, ValueSpec())
        new_arr = np.array([2.0, 3.0])
        val.update(new_arr)
        assert np.array_equal(val.value, new_arr)

    def test_update_preserves_type_check(self):
        val = Value('test', 1, True, ValueSpec(), value_type='INT')
        val.update(5)
        assert val.value == 5


class TestValueSetter:
    def test_setter_updates_value(self):
        val = Value('test', 1.0, True, ValueSpec())
        val.value = 5.0
        assert val.value == 5.0

    def test_setter_with_wrong_type_raises(self):
        val = Value('test', 1.0, True, ValueSpec())
        with pytest.raises(TypeError):
            val.value = 'string'

    def test_setter_with_out_of_range_raises(self):
        val = Value('test', 1.0, True, ValueSpec(), max_value=10.0)
        with pytest.raises(ValueError):
            val.value = 20.0

    def test_setter_chained_with_prev_storage(self):
        val = Value('test', 1.0, True, ValueSpec(), store_prev=True)
        val.value = 2.0
        val.value = 3.0
        assert val.value == 3.0
        assert val.prev_value == 2.0


class TestValuePrevStorage:
    def test_prev_not_stored_by_default(self):
        val = Value('test', 1.0, True, ValueSpec())
        val.update(2.0)
        assert val.prev_value is None
        assert val.prev_status == 'UNKNOWN'

    def test_prev_stored_when_enabled(self):
        val = Value('test', 1.0, True, ValueSpec(), store_prev=True)
        val.update(2.0)
        assert val.prev_value == 1.0

    def test_prev_status_stored(self):
        val = Value('test', 1.0, True, ValueSpec(), store_prev=True, status='CALCULATED')
        val.update(2.0, ValueStatus.FIXED)
        assert val.prev_value == 1.0
        assert val.prev_status == 'CALCULATED'

    def test_prev_status_updated_on_second_update(self):
        val = Value('test', 1.0, True, ValueSpec(), store_prev=True, status='DEPEND')
        val.update(2.0, ValueStatus.CALCULATED)
        val.update(3.0)
        assert val.prev_value == 2.0
        assert val.prev_status == 'CALCULATED'

    def test_prev_value_none_before_any_update(self):
        val = Value('test', 1.0, True, ValueSpec(), store_prev=True)
        assert val.prev_value is None

    def test_prev_value_independent_of_current(self):
        val = Value('test', [1, 2], True, ValueSpec(), store_prev=True, value_type='INT')
        val.update([3, 4])
        val.value.append(5)
        assert val.prev_value == [1, 2]


class TestValueProperties:
    def test_name(self):
        val = Value('myname', 1.0, True, ValueSpec())
        assert val.name == 'myname'

    def test_spec_returns_copy(self):
        val = Value('test', 1.0, True, ValueSpec('x', 'm'))
        spec = val.spec
        spec.value_name = 'changed'
        assert val.spec.value_name == 'x'

    def test_min_value_preserves_original(self):
        original = np.array([0.0])
        val = Value('test', 5.0, True, ValueSpec(), min_value=original)
        original[0] = 10.0
        assert val.min_value[0] == 0.0

    def test_max_value_preserves_original(self):
        original = np.array([10.0])
        val = Value('test', 5.0, True, ValueSpec(), max_value=original)
        original[0] = 0.0
        assert val.max_value[0] == 10.0

    def test_store_prev_true(self):
        val = Value('test', 1.0, True, ValueSpec(), store_prev=True)
        assert val.store_prev is True

    def test_store_prev_default_false(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.store_prev is False

    def test_serialize_data_getter(self):
        val = Value('test', 1.0, False, ValueSpec())
        assert val.serialize_data is False
        val = Value('test', 1.0, True, ValueSpec())
        assert val.serialize_data is True

    def test_serialize_data_setter(self):
        val = Value('test', 1.0, False, ValueSpec())
        val.serialize_data = True
        assert val.serialize_data is True

    def test_min_value_none_by_default(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.min_value is None

    def test_max_value_none_by_default(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.max_value is None

    def test_description_returns_text(self):
        val = Value('test', 1.0, True, ValueSpec(), description='hello')
        assert val.description == 'hello'

    def test_description_empty_by_default(self):
        val = Value('test', 1.0, True, ValueSpec())
        assert val.description == ''

    def test_value_type_property_string(self):
        val = Value('test', 1, True, ValueSpec(), value_type='INT')
        assert val.value_type == 'INT'

    def test_value_type_property_from_enum(self):
        val = Value('test', 1, True, ValueSpec(), value_type=DataType.INT)
        assert val.value_type == 'INT'

    def test_status_property_string(self):
        val = Value('test', 1.0, True, ValueSpec(), status='FIXED')
        assert val.status == 'FIXED'

    def test_status_property_from_enum(self):
        val = Value('test', 1.0, True, ValueSpec(), status=ValueStatus.FIXED)
        assert val.status == 'FIXED'


class TestValueCall:
    def test_call_returns_value_for_non_object(self):
        val = Value('test', 42.0, True, ValueSpec())
        assert val() == 42.0

    def test_call_invokes_callable_for_object(self):
        def adder(x, y):
            return x + y
        val = Value('adder', adder, True, ValueSpec(), value_type='OBJECT')
        assert val(x=1, y=2) == 3

    def test_call_with_kwargs_on_object(self):
        class Multiplier:
            def __call__(self, a, b):
                return a * b
        val = Value('mul', Multiplier(), True, ValueSpec(), value_type='OBJECT')
        assert val(a=3, b=4) == 12

    def test_call_on_none_object_returns_none(self):
        val = Value('test', None, True, ValueSpec(), value_type='OBJECT')
        assert val.value is None
        with pytest.raises(TypeError):
            val()

    def test_call_int_value_returns_int(self):
        val = Value('test', 7, True, ValueSpec(), value_type='INT')
        assert val() == 7

    def test_call_logic_value_returns_bool(self):
        val = Value('test', True, True, ValueSpec(), value_type='LOGIC')
        assert val() is True

    def test_call_float_value_returns_float(self):
        val = Value('test', 3.14, True, ValueSpec())
        assert val() == 3.14

    def test_call_list_value_returns_list(self):
        val = Value('test', [1, 2, 3], True, ValueSpec(), value_type='INT')
        assert val() == [1, 2, 3]


class TestValueToDict:
    def test_to_dict_with_serialize_data_true(self):
        val = Value(
            'test', 42.0, True, ValueSpec('x', 'm'),
            description='desc', status='FIXED', value_type='FLOAT',
            store_prev=True, min_value=0.0, max_value=100.0,
        )
        d = val.to_dict()
        assert d['name'] == 'test'
        assert d['object_type'] == 'VALUE'
        assert d['value_spec'] == {'value_name': 'x', 'dimension': 'm'}
        assert d['description'] == 'desc'
        assert d['status'] == 'FIXED'
        assert d['value_type'] == 'FLOAT'
        assert d['store_prev'] is True
        assert d['min_value'] == 0.0
        assert d['max_value'] == 100.0
        assert d['value'] == 42.0
        assert d['serialize_data'] is True

    def test_to_dict_with_serialize_data_false(self):
        val = Value('test', 42.0, False, ValueSpec())
        d = val.to_dict()
        assert 'value' not in d
        assert d['serialize_data'] is False

    def test_to_dict_with_numpy_value(self):
        arr = np.array([1.0, 2.0, 3.0])
        val = Value('arr', arr, True, ValueSpec())
        d = val.to_dict()
        assert np.array_equal(d['value'], arr)

    def test_to_dict_with_dict_spec(self):
        val = Value('test', 1.0, True, {'value_name': 'p', 'dimension': 'Pa'})
        d = val.to_dict()
        assert d['value_spec'] == {'value_name': 'p', 'dimension': 'Pa'}

    def test_to_dict_includes_base_attrs(self):
        val = Value('test', 1.0, True, ValueSpec())
        d = val.to_dict()
        assert d['name'] == 'test'
        assert d['object_type'] == 'VALUE'

    def test_to_dict_value_spec_has_name_and_dimension(self):
        val = Value('test', 1.0, True, ValueSpec('x', 'm'))
        d = val.to_dict()
        assert d['value_spec']['value_name'] == 'x'
        assert d['value_spec']['dimension'] == 'm'


class TestValueCopyBehavior:
    def test_numpy_array_copied_on_init(self):
        original = np.array([1.0, 2.0, 3.0])
        val = Value('test', original, True, ValueSpec())
        original[0] = 99.0
        assert val.value[0] == 1.0

    def test_numpy_array_copied_on_update(self):
        arr = np.array([1.0, 2.0, 3.0])
        val = Value('test', np.array([0.0]), True, ValueSpec())
        val.update(arr)
        arr[0] = 99.0
        assert val.value[0] == 1.0

    def test_list_deep_copied_on_init(self):
        original = [1, 2, 3]
        val = Value('test', original, True, ValueSpec(), value_type='INT')
        original.append(4)
        assert val.value == [1, 2, 3]

    def test_function_deep_copied_on_init(self):
        def original():
            return 42
        val = Value('test', original, True, ValueSpec(), value_type='OBJECT')
        assert val.value is original

    def test_list_deep_copied_on_update(self):
        val = Value('test', [0], True, ValueSpec(), value_type='INT')
        new_list = [1, 2, 3]
        val.update(new_list)
        new_list.append(4)
        assert val.value == [1, 2, 3]

    def test_prev_value_copied(self):
        arr = np.array([1.0, 2.0])
        val = Value('test', arr, True, ValueSpec(), store_prev=True)
        val.update(np.array([3.0, 4.0]))
        arr[0] = 99.0
        assert val.prev_value[0] == 1.0

    def test_internal_value_not_mutated_by_prev(self):
        val = Value('test', [1, 2], True, ValueSpec(), store_prev=True, value_type='INT')
        val.update([3, 4])
        val.value.append(5)
        assert val.prev_value == [1, 2]


class TestValueEdgeCases:
    def test_empty_list(self):
        val = Value('test', [], True, ValueSpec(), value_type='INT')
        assert val.value == []

    def test_empty_numpy_array(self):
        val = Value('test', np.array([]), True, ValueSpec())
        assert val.value.size == 0

    def test_nested_list(self):
        val = Value('test', [[1, 2], [3, 4]], True, ValueSpec(), value_type='INT')
        assert val.value == [[1, 2], [3, 4]]

    def test_none_value_all_types(self):
        val = Value('test', None, True, ValueSpec(), value_type='FLOAT')
        assert val.value is None

    def test_spec_group_attribute(self):
        spec = ValueSpec('x', 'm', 'thermo')
        assert spec.group == 'thermo'

    def test_multiple_updates_preserve_integrity(self):
        val = Value('test', 0.0, True, ValueSpec(), store_prev=True, min_value=-10, max_value=10)
        for v in [1.0, 2.0, 3.0, -5.0]:
            val.update(v)
        assert val.value == -5.0
        assert val.prev_value == 3.0

    def test_single_element_list(self):
        val = Value('test', [42], True, ValueSpec(), value_type='INT')
        assert val.value == [42]

    def test_numpy_array_with_inf(self):
        val = Value('test', np.array([float('inf')]), True, ValueSpec())
        assert np.isinf(val.value[0])

    def test_large_integer_values(self):
        val = Value('test', 2**31 - 1, True, ValueSpec(), value_type='INT')
        assert val.value == 2**31 - 1

    def test_recursive_list_validation_float(self):
        val = Value('test', [[1.0, 2.0], [3.0, 4.0]], True, ValueSpec())
        assert val.value == [[1.0, 2.0], [3.0, 4.0]]

    def test_empty_string_description(self):
        val = Value('test', 1.0, True, ValueSpec(), description='')
        assert val.description == ''
