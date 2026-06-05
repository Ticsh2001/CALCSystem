
from backend.core.primitives.DataType import BaseObject, ObjectType
from backend.core.primitives.ObjectsStorage import ObjectsStorage
from backend.core.primitives.Value import Value
from backend.core.primitives.Port import Port
from typing import Union, Any, Optional, Type, TypeVar, Iterable, Dict
import uuid


class Element(BaseObject):
    def __init__(self, name: str, description: str,
                 inlet_ports_num: int, outlet_ports_num: int,
                 parameters_num: int, registered_uuid: Optional[Dict[str, uuid.UUID]]=None):
        super().__init__(name, description, ObjectType.ELEMENT)
        self._port_groups = ObjectsStorage(name='port_groups',
                                           storage_type='STORAGE',
                                           max_size=3,
                                           lock_names=True)
        self._register_groups(inlet_ports_num,
                              outlet_ports_num,
                              parameters_num,
                              registered_uuid)

    def _register_groups(self, inlet_ports_num: int,
                         outlet_ports_num: int,
                         parameters_num: int,
                         registered_uuid: Optional[Dict[str, uuid.UUID]]=None):
        if registered_uuid is None:
            self._port_groups.add(ObjectsStorage(name='in', description='Inlet ports',
                                                 storage_type='PORT',
                                                 max_size=inlet_ports_num, lock_names=True))
            self._port_groups.add(ObjectsStorage(name='out', description='Outlet ports',
                                                 storage_type='PORT',
                                                 max_size=outlet_ports_num, lock_names=True))
            params_id = self._port_groups.add(ObjectsStorage(name='params', description='Params storage',
                                                             storage_type='PORT',
                                                             max_size=1, lock_names=True))
            self._port_groups[params_id].add(Port('params',
                                                  description='Params port',
                                                  values_numer=parameters_num,
                                                  direction='both'))
        else:
            self._port_groups.add_with_key(registered_uuid['in'], ObjectsStorage(name='in',
                                                                                 description='Inlet ports',
                                                                                 storage_type='PORT',
                                                                                 max_size=inlet_ports_num,
                                                                                 lock_names=True))
            self._port_groups.add_with_key(registered_uuid['out'], ObjectsStorage(name='out',
                                                                                  description='Outlet ports',
                                                                                  storage_type='PORT',
                                                                                  max_size=outlet_ports_num,
                                                                                  lock_names=True))
            self._port_groups.add_with_key(registered_uuid['params'], ObjectsStorage(name='params',
                                                                                     description='Params storage',
                                                                                     storage_type='PORT',
                                                                                     max_size=1,
                                                                                     lock_names=True))
            self._port_groups[registered_uuid['params']].add_with_key(registered_uuid['params_port'],
                                                                      Port('params',
                                                                           description='Params port',
                                                                           values_numer=parameters_num,
                                                                           direction='both'))


    def _gen_path(self, port_group: Union[str, uuid.UUID],
                  port_key: Optional[Union[str, uuid.UUID]],
                  value_key: Optional[Union[str, uuid.UUID]], as_uuid=False):
        try:
            group = self.get_port_group(port_group)
            if port_key is not None:
                port = self.get_port(port_group, port_key)
                if value_key is not None:
                    value = self.get_value(port_group, port_key, value_key)
                else:
                    value = None
            else:
                port = None
                value = None
        except KeyError:
            raise KeyError("Wrong path")
        res = f'{group.name}'
        if not as_uuid:
            if port is not None:
                res = '.'.join([res, f'{port.name}'])
                if value is not None:
                    res = '.'.join([res, f'{value.name}'])
        else:
            if port is not None:
                res = '.'.join([res, f'{str(group.get_uuid(port.name))}'])
                if value is not None:
                    res = '.'.join([res, f'{str(port.uuid(value.name))}'])
        return res

    def _read_path(self, path: str):
        struct = path.split('.')
        if len(struct) == 1:
            return self.get_port_group(struct[0])
        elif len(struct) == 2:
            try:
                return self.get_port(struct[0], uuid.UUID(struct[1]))
            except ValueError:
                return self.get_port(struct[0], struct[1])
        elif len(struct) == 3:
            try:
                return self.get_value(struct[0],  uuid.UUID(struct[1]), uuid.UUID(struct[2]))
            except ValueError:
                return self.get_value(struct[0], struct[1], struct[2])


    def get_port_group(self, port_group: Union[str, int, uuid.UUID]):
        return self._port_groups[port_group]

    def get_port(self, port_group: Union[str, int, uuid.UUID],
                 port_key: Optional[Union[str, int, uuid.UUID]]=None):
        group = self.get_port_group(port_group)
        return group[port_key]

    def get_value(self, port_group: Union[str, int, uuid.UUID],
                  port_key: Optional[Union[str, int, uuid.UUID]],
                  value_key: Optional[Union[str, int, uuid.UUID]]):
        port = self.get_port(port_group, port_key)
        return port[value_key]

    def register_port(self, port_group: Union[str, int, uuid.UUID], port: Port):
        group = self.get_port_group(port_group)
        return group.add(port)

    def register_port_with_key(self, port_group: Union[str, int, uuid.UUID], key: uuid.UUID,
                                port: Port):
        group = self.get_port_group(port_group)
        group.add_with_key(key, port)

    def register_value(self, port_group: Union[str, int, uuid.UUID],
                       port_key: Union[str, int, uuid.UUID], value: Value):
        port = self.get_port(port_group, port_key)
        return port.register(value)

    def register_value_with_key(self, port_group: Union[str, int, uuid.UUID],
                       port_key: Union[str, int, uuid.UUID], key: uuid.UUID, value: Value):
        port = self.get_port(port_group, port_key)
        port.register_with_key(key, value)

    def register_object(self, path: str, obj: Union[Port, Value]):
        obj_rep = self._read_path(path)
        if isinstance(obj, Port) and isinstance(obj_rep, ObjectsStorage) and obj_rep.storage_type == 'PORT':
            return obj_rep.add(obj)
        elif isinstance(obj, Value) and isinstance(obj_rep, Port):
            return obj_rep.register(obj)
        else:
            raise ValueError("Wrong path for current objects to store")

    def register_object_with_key(self, path: str, key: uuid.UUID, obj: Union[Port, Value]):
        obj_rep = self._read_path(path)
        if isinstance(obj, Port) and isinstance(obj_rep, ObjectsStorage) and obj_rep.storage_type == 'PORT':
            obj_rep.add_with_key(key, obj)
        elif isinstance(obj, Value) and isinstance(obj_rep, Port):
            obj_rep.register_with_key(key, obj)
        else:
            raise ValueError("Wrong path for current objects to store")

    def __getitem__(self, idx: str):
        return self._read_path(idx)

    def to_dict(self):
        result = super().to_dict()
        result['inlet_ports_num'] = self.get_port_group('in').max_size
        result['outlet_ports_num'] = self.get_port_group('out').max_size
        result['parameters_num'] = self.get_port('params', 'params').max_size
        result['port_groups'] = self._port_groups.to_dict()
        return result
