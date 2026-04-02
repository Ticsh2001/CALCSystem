from enum import Enum, auto
from typing import Union, Any, Optional, Type, TypeVar
from numbers import Number
import numpy as np

T = TypeVar("T", bound="EnumClassAbstraction")

class EnumClassAbstraction:
    """Миксин, реализующий универсальный from_input для Enum‑классов."""
    @classmethod
    def from_input(cls: Type[T], value: Union[str, T]) -> T:
        """Преобразует строку (или сам экземпляр Enum) в объект перечисления."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            norm = value.strip().upper()
            for member in cls:
                if member.name == norm:
                    return member
            raise ValueError(f'Неизвестный {cls.__name__}: {value}')
        raise ValueError(f'Неподдерживаемый тип для {cls.__name__}')
    
    def to_string(self):
        return str(self)

# ---------------------------------------------------------------------------

class ValueStatus(Enum, EnumClassAbstraction):
    """Статусы значений для отслеживания состояния параметра"""
    UNKNOWN   = auto()  # Величина неизвестна
    DEPEND    = auto()  # Значение пришло от связи с другим элементом
    CALCULATED= auto()  # Значение было рассчитано в этом элементе
    FIXED     = auto()  # Значение фиксировано и задано

# ---------------------------------------------------------------------------

class DataType(Enum, EnumClassAbstraction):
    """Типы данных, которыми обмениваются элементы"""
    FLOAT       = auto()  # С плавающей точкой
    LOGIC       = auto()  # Логические
    LOGIC_TRUE  = auto()  # ИСТИНА – конкретный результат логического выражения (для ветвления)
    LOGIC_FALSE = auto()  # ЛОЖЬ – конкретный результат логического выражения (для ветвления)
    TIMESTAMP   = auto()  # Время
    STRING      = auto()  # Строковые данные
    INT         = auto()  # Целочисленные значения

        
class ValueSpec:
    """Спецификаия величины, метаинформация о величине/параметре"""
    def __init__(self, value_name: str = '', dimension: str = ''):
        self.value_name = value_name  # Название величины (давление/температура)
        self.dimension = dimension  # Размерность величины
    
def validate_data(data: Any, dtype: DataType,
                  min_val: Optional[Union[int, float]]=None,
                  max_val: Optional[Union[int, float]]=None):

    # Вспомогательные функции для проверки типов
    def _is_numeric(value: Any):
        """Являются ли данные с типом с плавающей запятой"""
        if isinstance(value, (Number, bool)):
            return True
        if isinstance(value, (list, tuple)):
            return all(_is_numeric(v) for v in value)
        if isinstance(value, np.ndarray):
            return np.issubdtype(value.dtype, np.number)
        return False

    def _is_integer(value):
        """Являются ли данные целочисленными"""
        if isinstance(value, (int, bool)):
            return True
        if isinstance(value, (list, tuple)):
            return all(_is_integer(v) for v in value)
        if isinstance(value, np.ndarray):
            return np.issubdtype(value.dtype, np.integer) or np.issubdtype(value.dtype, np.bool_)
        return False

    def _is_logical(value):
        """Являются ли данные логическими"""
        # Логические: bool, 0/1
        if isinstance(value, bool):
            return True
        if isinstance(value, int) and value in (0, 1):
            return True
        if isinstance(value, (list, tuple)):
            return all(_is_logical(v) for v in value)
        if isinstance(value, np.ndarray):
            # если массив bool или целочисленный с 0/1
            if np.issubdtype(value.dtype, np.bool_):
                return True
            if np.issubdtype(value.dtype, np.integer):
                return np.all((value == 0) | (value == 1))
        return False

    




        
class Value:
    """ Описание параметра
    name - имя параметра
    value - значение параметра
    value_spec - спецификация параметра
    description - описание параметра
    status - статус параметра
    value_type - тип данных в параметре
    store_prev - сохранять ли предыдущее состояние
    min_value - минимальное значение
    max_value - максимальное значение
    """
    def __init__(self, name: str, 
                 value: Any, 
                 value_spec: ValueSpec,
                 description: str = '',
                 status: ValueStatus = ValueStatus.UNKNOWN,
                 value_type: DataType = DataType.FLOAT,
                 store_prev: bool = False,
                 min_value: Optional[Any] = None,
                 max_value: Optional[Any] = None):

        self._name = name
        self._description = description
        self._status = status
        self._value_type = value_type
        self._value_spec = value_spec
        self._store_prev = store_prev
        self._min_value = min_value
        self._max_value = max_value
        self._value = value

        self._prev_value = None
        self._prev_status = ValueStatus.UNKNOWN


    def _validate(self, value: Any):
        '''
        Валидация входящих данных
        будут проверки по типу и по min max если они заданы и если 
        тип хранящихся данных позволяет провести сравнение (например str не получится)
        '''
        if value is None:
            return
        

         

    def update(self, new_value: Any, new_status: Optional[ValueStatus] = None):
        '''Обновление данных в параметре
        new_value - новое значение величины
        new_status - новый статус
        '''
        self._validate(new_value)



    @property
    def value(self) -> Any:
        return self._value
    
    @value.setter
    def value(self, new_value: Any):
        self.update(new_value)


    










