import json
from core.primitives.DataType import ValueSpec
from pathlib import Path


class ClassFactory:
    def __init__(self, configs_path):
        self._config_path = configs_path
        self._register_value_specs()

    def _load_file(self, file_name: str):
        path = self._config_path / file_name
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data


    def _register_value_specs(self):
        self._values_specs = dict()
        data = self._load_file("Value_specifications")
        for group in data.keys():
            for val_spec in data[group]:
                self._values_specs[group][val_spec['value_name']] = ValueSpec(val_spec['value_name'],
                                                                              val_spec['dimension'],
                                                                              group)
                
    def _register_values(self):
        
        

