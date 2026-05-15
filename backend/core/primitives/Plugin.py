from abc import ABC, abstractmethod
from abc import ABCMeta

from backend.core.primitives.DataType import BaseObject, ObjectType
from dataclasses import dataclass
from typing import Optional, List, Any


@dataclass
class PluginParamMeta:
    """Метаданные для одного параметра инициализации."""
    type: str = 'str'               # тип данных: 'str', 'float', 'int', 'bool'
    default: Any = None             # значение по умолчанию
    choices: Optional[List[str]] = None  # список допустимых строковых значений
    min: Optional[float] = None          # минимальное числовое значение
    max: Optional[float] = None          # максимальное числовое значение
    description: str = ''               # описание параметра для UI

    def to_dict(self):
        res = dict()
        res['type'] = self.type
        res['default'] = self.default
        res['choices'] = self.choices
        res['min'] = self.min
        res['max'] = self.max
        res['description'] = self.description
        if self.choices is not None:
            res['use_by_choice'] = True
        else:
            res['use_by_choice'] = False
        return res


class PluginMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        init_method = {}
        calc_methods = []
        for key, value in dct.items():
            if hasattr(value, '_init_params'):
                init_method[key] = value._init_params
            elif hasattr(value, '_calc_params'):
                calc_methods.append({key: value._calc_params})
        dct['_init_method'] = init_method
        dct['_calc_methods'] = calc_methods
        return super().__new__(cls, name, bases, dct)



class Plugin(BaseObject, ABC, metaclass=PluginMeta):
    def __init__(self, name, author: str='', description: str='', version: str=''):
        super().__init__(name, ObjectType.PLUGIN)
        self._description = description
        self._version = version
        self._author = author

    @staticmethod
    def init_func(**params):
        """Декоратор для метода инициализации. Параметры – ожидаемые ключевые аргументы."""
        def decorator(method):
            res = dict()
            for param_name, meta in params.items():
                if isinstance(meta, PluginParamMeta):
                    res[param_name] = meta
                elif isinstance(meta, dict):
                    res[param_name] = PluginParamMeta(**meta)
                else:
                    raise TypeError(f"Parameter {param_name} must be ParamMeta or dict")
            method._init_params = res
            return method
        return decorator

    @staticmethod
    def calc_func(**params):
        """Декоратор для методов расчёта. Указывает, какие ключевые аргументы ожидает метод."""
        def decorator(method):
            res = dict()
            for param_name, meta in params.items():
                if isinstance(meta, PluginParamMeta):
                    res[param_name] = meta
                elif isinstance(meta, dict):
                    res[param_name] = PluginParamMeta(**meta)
                else:
                    raise TypeError(f"Parameter {param_name} must be ParamMeta or dict")
            method._calc_params = res
            return method
        return decorator

    @classmethod
    def _get_init_meta(cls):
        if not cls._init_method:
            return {}
        else:
            return next(iter(cls._init_method.values()))

    @classmethod
    def _get_calc_meta(cls, index):
        if not cls._calc_methods:
            return {}
        else:
            return cls._calc_methods[index]


    @classmethod
    def _verify_params(cls, **kwargs):
        types_map = {'int': int, 'float': float, 'str': str}
        params_meta = cls._get_init_meta()
        for param_name, value in kwargs.items():
            meta_data = params_meta.get(param_name, None)
            if meta_data is None:
                raise ValueError(f'Wrong parameter name {param_name} in init function')
            if not isinstance(value, types_map[meta_data.type]):
                raise TypeError(f"Parameter {param_name} has wrong type: {str(type(value))}, "
                                f"expected: {meta_data.type}")
            if isinstance(value, int | float):
                if meta_data.min is not None:
                    if value < meta_data.min:
                        raise ValueError(f"{param_name} is out of minimum value")
                if meta_data.max is not None:
                    if value > meta_data.max:
                        raise ValueError(f"{param_name} is out of maximum value")
            if meta_data.choices is not None:
                if value not in meta_data.choices:
                    raise ValueError(f"{param_name} value is not in allowed values list")

    def init(self, **params):
        self.__class__._verify_params(**params)
        init_method_name = next(iter(self.__class__._init_method.keys()))
        init_method = getattr(self, init_method_name)
        if init_method:
            init_method(**params)



    @property
    def plugin_description(self):
        return self._description

    @property
    def plugin_version(self):
        return self._version

    @property
    def plugin_author(self):
        return self._author

    @classmethod
    def get_init_schema(cls):
        res = dict()
        for values_info in cls._init_method.values():
            for value_name, value_meta in values_info.items():
                res[value_name] = value_meta.to_dict()
        return res

    @classmethod
    def get_calc_schema(cls):
        res = dict()
        for calc_method in cls._calc_methods:
            method_name = 
            res[cls._calc_methods]
            calc_method_name =








class PL(Plugin):
    def __init__(self):
        super().__init__('test', 'fff', 'dsdds', 'sds')

    @Plugin.init_func(medium=PluginParamMeta(description= 'Среда', choices=['гелий', 'натрий'],
                                             type= 'str', default='гелий'),
                      density={'description': 'Плотность', 'min': 10., 'max': 20., 'type': 'float', 'default': 15})
    def _init_1(self, medium, density):
        self._medium = medium
        self._density = density

t = PL()
init_sc = PL.get_init_schema()
t.init(medium='натрий', density=11.0)

