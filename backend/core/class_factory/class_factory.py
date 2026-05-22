import json
from core.primitives.DataType import ValueSpec
from pathlib import Path
import os


class ClassFactory:

    default_value_params = {'description': '', 
                            'status': 'UNKNOWN',
                            'value_type': 'FLOAT',
                            'store_prev': False,
                            'min_value': None,
                            'max_value': None,
                            'serialize_data': False}
    
    default_port_params = {'values_number': -1,
                           'direction': 'both'}


    def __init__(self, configs_path):
        self._config_path = configs_path
        self._register_value_specs()
        self._register_values()

    def _load_file(self, file_path: str):
        path = os.path.join(self._config_path, file_path)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    
    def _extract_value_data(self, data: dict):
        return {key:  data.get(key, self.default_value_params[key]) for key in ['name', 'value_spec', 'description', 'status',
                                                                                'value_type', 'store_prev', 'min_value', 'max_value', 
                                                                                'srialize_data']}
    
    def _extract_port_data(self, data: dict):
        res = dict()
        try:
            res['name'] = data['name']
        except KeyError:
            return None
        res['values_number'] = data.get('values_number', self.default_ports_params['max_size'])
        res['direction'] = data.get('direction', self.default_port_params['direction'])
        res['values'] = []
        for value in data['values']:
            if isinstance(value, str):
                try:
                    value_address = value.split('.')
                    res['values'].append(self._registered_values)


    
    def _register_value_specs(self):
        self._registered_values_specs = dict()
        data = self._load_file("Value_specifications.json")
        for group in data.keys():
            for val_spec in data[group]:
                self._registered_values_specs[group][val_spec['value_name']] = ValueSpec(val_spec['value_name'],
                                                                                         val_spec['dimension'],
                                                                                         group)
    def _register_values(self):
        self._registered_values = dict()
        files = [file for file in os.listdir(os.path.join(self._config_path, 'values')) if 'json' in file]
        for file in files:
            self._registered_values[Path(file).stem] = dict()
            data = self._load_file(os.path.join('values', file))
            for val in data:
                 self._registered_values[Path(file).stem][val['name']] = self._extract_value_data(val)

    def _register_ports(self):
        self._registered_ports = dict()
        files = [file for file in os.listdir(os.path.join(self._config_path, 'ports')) if 'json' in file]
        for file in files:
            self._registered_ports[Path(file).stem] = dict()
            data = self._load_file(os.path.join('ports', file))
            for port in data:
                self._registered_ports[Path(file).stem][port['name']] = 

        

        
cf = ClassFactory('/home/tishchenkova@lofi.pgt/Документы/Coding/CALCSystem/backend/configs')


