from abc import ABC, abstractmethod
from abc import ABCMeta

from backend.core.primitives.DataType import BaseObject, ObjectType
from dataclasses import dataclass
from typing import Optional, List, Any


@dataclass
class PortPluginParamMeta:
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
    
class PortPluginMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        init_method = {}
        calc_methods = dict()
        for key, value in dct.items():
            if hasattr(value, '_init_params'):
                init_method[key] = value._init_params
            elif hasattr(value, '_calc_params'):
                calc_methods[key] = value._calc_params
        dct['_init_method'] = init_method
        dct['_calc_methods'] = calc_methods
        return super().__new__(cls, name, bases, dct)



class PortPlugin(BaseObject, ABC, metaclass=PortPluginMeta):
    def __init__(self, name, author: str='', description: str='', version: str=''):
        super().__init__(name, description, ObjectType.PORTPLUGIN)
        self._version = version
        self._author = author
        self._init_state = dict()
        self._last_calc = dict()


    @staticmethod
    def init_func(**params):
        """Декоратор для метода инициализации. Параметры – ожидаемые ключевые аргументы."""
        def decorator(method):
            res = dict()
            for param_name, meta in params.items():
                if isinstance(meta, PortPluginParamMeta):
                    res[param_name] = meta
                elif isinstance(meta, dict):
                    res[param_name] = PortPluginParamMeta(**meta)
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
                if isinstance(meta, PortPluginParamMeta):
                    res[param_name] = meta
                elif isinstance(meta, dict):
                    res[param_name] = PortPluginParamMeta(**meta)
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
    def _get_calc_meta(cls, name):
        return cls._calc_methods.get(name)


    @classmethod
    def _verify_params(cls, func_name=None, **kwargs):
        types_map = {'int': int, 'float': float, 'str': str}
        if func_name is None:
            params_meta = cls._get_init_meta()
        else:
            params_meta = cls._get_calc_meta(func_name)
            if params_meta is None:
                raise ValueError(f"Calculation method '{func_name}' not found")        
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
            self._init_state = params
            init_method(**params)

    def calculate(self, **params):
        matching_methods = []
        for method_name, required_params in self.__class__._calc_methods.items():
                required_keys = set(required_params.keys())
                if required_keys.issubset(params.keys()):
                    matching_methods.append(method_name)
        if not matching_methods:
                raise ValueError(f"No calculation method matches the given parameters {list(params.keys())}")
        matching_methods.sort(key=lambda m: len(self._calc_methods[m]), reverse=True)
        self.__class__._verify_params(matching_methods[0], **params)
        calc_method = getattr(self, matching_methods[0])
        self._last_calc = {matching_methods[0]: params}
        return calc_method(**params)
    
    def __call__(self, **params):
        return self.calculate(**params)

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
            res[calc_method] = {param_name: param_meta.to_dict() for param_name, param_meta in cls._calc_methods[calc_method].items()}
        return res
    





