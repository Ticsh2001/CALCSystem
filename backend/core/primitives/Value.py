from core.primitives.DataType import ValueSpec, ValueStatus, ObjectType, BaseObject, DataType
from typing import Union, Any, Optional, Type, TypeVar
from numbers import Number
import numpy as np
import copy

def validate_data(data: Any, dtype: DataType,
                  min_val: Optional[Union[int, float]]=None,
                  max_val: Optional[Union[int, float]]=None):
    """
    Проверяет данные на соответствие указанному DataType и необязательным ограничениям диапазона.
    Вызывает TypeError, если тип данных не совпадает, ValueError, если вне диапазона.
    """

    # Вспомогательная функция: проверяет, являются ли данные числовыми (совместимыми с float)
    def _is_numeric(value: Any):
        """Проверяет совместимость данных с плавающей запятой."""
        if isinstance(value, (Number, bool)):
            return True
        # Рекурсивная проверка типов контейнеров
        if isinstance(value, (list, tuple)):
            return all(_is_numeric(v) for v in value)
        if isinstance(value, np.ndarray):
            return np.issubdtype(value.dtype, np.number)
        return False

    # Вспомогательная функция: проверяет, являются ли данные целочисленными
    def _is_integer(value):
        """Проверяет совместимость данных с целыми числами."""
        if isinstance(value, (int, bool)):
            return True
        # Рекурсивная проверка типов контейнеров
        if isinstance(value, (list, tuple)):
            return all(_is_integer(v) for v in value)
        if isinstance(value, np.ndarray):
            return np.issubdtype(value.dtype, np.integer) or np.issubdtype(value.dtype, np.bool_)
        return False

    # Вспомогательная функция: проверяет, являются ли данные логическими (булевыми)
    def _is_logical(value):
        """Проверяет совместимость данных с булевым типом (bool, 0/1)."""
        if isinstance(value, bool):
            return True
        # Принимаются целые числа 0 или 1 как логические
        if isinstance(value, int) and value in (0, 1):
            return True
        # Рекурсивная проверка типов контейнеров
        if isinstance(value, (list, tuple)):
            return all(_is_logical(v) for v in value)
        if isinstance(value, np.ndarray):
            # Проверка на булев массив или массив целых чисел, содержащий только 0/1
            if np.issubdtype(value.dtype, np.bool_):
                return True
            if np.issubdtype(value.dtype, np.integer):
                return np.all((value == 0) | (value == 1))
        return False
    
    # Пропуск проверки для значений None
    if data is None:
        return
    
    # Проверка типа на основе DataType
    elif dtype.to_string() == 'FLOAT':
        if not _is_numeric(data):
            raise TypeError('Wrong type of input data')
    elif dtype.to_string() == 'INT':
        if not _is_integer(data):
            raise TypeError('Wrong type of input data')
    elif dtype.to_string() == 'LOGIC':
        if not _is_logical(data):
            raise TypeError('Wrong type of input data')
    elif dtype.to_string() == 'TIMESTAMP':
        if not np.issubdtype(data.dtype, np.datetime64):
            raise TypeError('Wrong type of input data')
    
    # Проверка диапазона для числовых типов
    if (min_val is not None or max_val is not None) and (dtype.to_string() == 'FLOAT' or dtype.to_string() == 'INT'):
        if min_val is not None:
            if np.min(data) < min_val:
                raise ValueError(f"Current value is less than minimum value {min_val}")
        if max_val is not None:
            if np.max(data) > max_val:
                raise ValueError(f"Current value is greater than maximum value {max_val}")


class Value(BaseObject):
    """
    Контейнерный класс параметра/значения.
    Инкапсулирует параметр с его значением, типом, статусом и метаданными.
    
    Атрибуты:
        name: Имя параметра
        value: Текущее значение параметра
        value_spec: Спецификация, содержащая имя и размерность
        description: Читаемое описание
        status: Текущий статус (как было получено значение)
        value_type: Тип данных значения
        store_prev: Сохранять ли предыдущее значение
        min_value: Минимально допустимое значение (для числовых типов)
        max_value: Максимально допустимое значение (для числовых типов)
    """
    def __init__(self, name: str, 
                 value: Any, 
                 value_spec: Union[ValueSpec, dict],
                 description: str = '',
                 status: Union[ValueStatus, str] = ValueStatus.UNKNOWN,
                 value_type: Union[DataType, str] = DataType.FLOAT,
                 store_prev: bool = False,
                 min_value: Optional[Any] = None,
                 max_value: Optional[Any] = None):
        
        super().__init__(name, ObjectType.VALUE)
        self._description = description
        # Преобразование строкового статуса в enum ValueStatus при необходимости
        self._status = ValueStatus.from_input(status)
        # Преобразование строкового типа данных в enum DataType при необходимости
        self._value_type = DataType.from_input(value_type)
        # Обработка value_spec как объекта ValueSpec или словаря
        if isinstance(value_spec, ValueSpec):
            self._value_spec = value_spec
        else:
            self._value_spec = ValueSpec.from_dict(value_spec)
        self._store_prev = store_prev
        self._min_value = self._copy_value(min_value)
        self._max_value = self._copy_value(max_value)
        # Проверка начального значения на соответствие типу и ограничениям диапазона
        validate_data(value, self._value_type, self._min_value, self._max_value)
        self._value = self._copy_value(value)
        self._prev_value = None
        self._prev_status = ValueStatus.UNKNOWN

    @staticmethod
    def _copy_value(val):
        """Создаёт независимую копию значения (глубокое копирование для контейнеров)."""
        if isinstance(val, np.ndarray):
            return np.copy(val)
        elif isinstance(val, (list, dict, set)):
            return copy.deepcopy(val)
        else:
            return val

      
    def update(self, new_value: Any, new_status: Optional[ValueStatus] = None):
        """
        Обновляет значение параметра и при необходимости его статус.
        Проверяет новое значение на соответствие типу и ограничениям диапазона.
        
        Аргументы:
            new_value: Новое значение для параметра
            new_status: Новый статус (необязательно, по умолчанию сохраняется текущий)
        """
        validate_data(new_value, self._value_type, self._min_value, self._max_value)
        # Сохранение предыдущего значения, если включено (для отслеживания изменений)
        if self._store_prev:
            self._prev_value = self._copy_value(self._value)
            self._prev_status = self._status
        self._value = self._copy_value(new_value)
        if new_status is not None:
            self._status = new_status

    @property
    def value(self) -> Any:
        """Возвращает текущее значение параметра."""
        return self._value
    
    @value.setter
    def value(self, new_value: Any):
        """Устанавливает новое значение с помощью метода update."""
        self.update(new_value)

    @property
    def status(self) -> str:
        """Возвращает статус в виде строки."""
        return self._status.to_string()
        
    @property
    def spec(self) -> ValueSpec:
        """Возвращает копию спецификации значения."""
        return ValueSpec(self._value_spec.value_name, self._value_spec.dimension)
    
    @property
    def description(self) -> str:
        """Возвращает описание параметра."""
        return self._description
    
    @property
    def value_type(self) -> DataType:
        """Возвращает тип данных значения."""
        return self._value_type.to_string()
    
    @property
    def store_prev(self) -> bool:
        """Возвращает, включено ли сохранение предыдущего значения."""
        return self._store_prev
    
    @property
    def min_value(self) -> Optional[Any]:
        """Возвращает копию минимально допустимого значения."""
        return self._min_value
    
    @property
    def max_value(self) -> Optional[Any]:
        """Возвращает копию максимально допустимого значения."""
        return self._max_value
    
    @property
    def prev_value(self) -> Optional[Any]:
        """Возвращает предыдущее значение (None, если не сохранено)."""
        return self._prev_value
    
    @property
    def prev_status(self) -> str:
        """Возвращает предыдущий статус в виде строки."""
        return self._prev_status.to_string()

    def to_dict(self) -> dict:
        """Сериализует объект Value в словарь."""
        result = {**super().to_dict(),  **{'value': self._value,
                                           'value_spec': {
                                               'value_name': self._value_spec.value_name,
                                               'dimension': self._value_spec.dimension},
                                           'description': self._description,
                                           'status': self._status.to_string(),
                                           'value_type': self._value_type.to_string(),
                                           'store_prev': self._store_prev,
                                           'min_value': self._min_value,
                                           'max_value': self._max_value}}
        return result
