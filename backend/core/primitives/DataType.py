from __future__ import annotations
from enum import Enum, auto
from typing import Union, Any, Optional, Type, TypeVar

from numbers import Number
import numpy as np
import copy

# Типовая переменная для обобщённых методов класса Enum
T = TypeVar("T", bound="EnumClassAbstraction")

class EnumClassAbstraction:
    """
    Миксин, предоставляющий универсальный метод from_input для классов Enum.
    Позволяет преобразовывать строковые представления или экземпляры Enum в члены Enum.
    """
    @classmethod
    def from_input(cls: Type[T], value: Union[str, T]) -> T:
        """
        Преобразует строку (или экземпляр Enum) в объект Enum.
        Обрабатывает регистронезависимое сопоставление и проверяет тип входных данных.
        """
        # Если уже экземпляр Enum, вернуть как есть
        if isinstance(value, cls):
            return value
        # Нормализация строкового ввода: удаление пробелов и преобразование в верхний регистр
        if isinstance(value, str):
            norm = value.strip().upper()
            for member in cls:
                if member.name == norm:
                    return member
            raise ValueError(f'Unknown {cls.__name__}: {value}')
        raise ValueError(f'Unsupported type for {cls.__name__}')
    
    def to_string(self):
        """Преобразует член Enum в строковое представление."""
        return self.name

# ---------------------------------------------------------------------------

class ValueStatus(EnumClassAbstraction, Enum):
    """
    Значения статуса для отслеживания состояния/происхождения значения параметра.
    Используется для определения способа получения значения (вычислено, задано и т.д.).
    """
    UNKNOWN   = auto()  # Значение неизвестно/не задано
    DEPEND    = auto()  # Значение получено из связи с другим элементом
    CALCULATED= auto()  # Значение вычислено внутри этого элемента
    FIXED     = auto()  # Значение фиксировано и явно задано

# ---------------------------------------------------------------------------

class DataType(EnumClassAbstraction, Enum):
    """
    Типы данных, которыми могут обмениваться элементы.
    Определяет систему типов для значений в системе расчётов.
    """
    FLOAT       = auto()  # Числа с плавающей запятой
    LOGIC       = auto()  # Логические значения
    LOGIC_TRUE  = auto()  # TRUE - специфический результат логического выражения (для ветвления)
    LOGIC_FALSE = auto()  # FALSE - специфический результат логического выражения (для ветвления)
    TIMESTAMP   = auto()  # Значения даты/времени
    STRING      = auto()  # Текстовые данные
    INT         = auto()  # Целочисленные значения
    OBJECT      = auto()  # Объект

class ObjectType(EnumClassAbstraction, Enum):
    """
    Типы объектов, которые на фундаментально работают в системе.
    """
    UNKNOWN = auto()
    VALUE = auto()  # Параметры
    ELEMENT = auto()  # Элементы
    PORT = auto()  # Порты
    STORAGE = auto() #Хранилище
    PLUGIN = auto()  #Плагин

class BaseObject:
    def __init__(self, name, object_type: Union[ObjectType, str]=ObjectType.UNKNOWN):
        self._name = name
        self._object_type = ObjectType.from_input(object_type)

    @property
    def name(self):
        return self._name
    
    @property
    def object_type(self):
        return self._object_type.to_string()
    
    def to_dict(self):
        return {'name': self._name, 'object_type': self._object_type.to_string()}

class ValueSpec:
    """
    Спецификация величины/параметра.
    Содержит метаданные о значении, такие как его имя и физическая размерность.
    """
    def __init__(self, value_name: str = '', dimension: str = '', group: str = ''):
        self.value_name = value_name  # Название величины (например, давление, температура)
        self.dimension = dimension  # Физическая размерность/единица (например, Па, К)
        self.group = group

    @classmethod
    def from_dict(cls, spec: dict):
        """Создаёт ValueSpec из словаря (для десериализации)."""
        return cls(value_name=spec.get('value_name', ''), dimension=spec.get('dimension', ''),
                   group=spec.get('group', ''))
    
    def __eq__(self, other: ValueSpec) -> bool:
        if (self.value_name, self.dimension, self.group) == (other.value_name, other.dimension, other.group):
            return True
        else:
            return False
        
    def __ne__(self, other: ValueSpec) -> bool:
        return not self == other

    def __hash__(self):
        return hash((self.value_name, self.dimension, self.group))