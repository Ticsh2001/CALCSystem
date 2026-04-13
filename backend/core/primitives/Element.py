from backend.core.primitives.DataType import BaseObject, ObjectType
from backend.core.primitives.ObjectsStorage import ObjectsStorage

class Element(BaseObject):
    def __init__(self, name: str, inlet_ports_num: int, outlet_ports_num: int,
                 parameters_num: int):
        super().__init__(name, ObjectType.ELEMENT)
        self._inlet_ports = ObjectsStorage(name='in', storage_type='PORT',
                                           max_size=inlet_ports_num, lock_names=True)
        self._outlet_ports = ObjectsStorage(name='out', storage_type='PORT',
                                            max_size=outlet_ports_num, lock_names=True)
        self._params_port = ObjectsStorage(name='param', storage_type='VALUE',
                                           max_size=parameters_num, lock_names=True)

    def port(self, idx:str):


