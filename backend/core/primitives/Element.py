from backend.core.primitives.DataType import BaseObject, ObjectType
from backend.core.primitives.ObjectsStorage import ObjectsStorage
from backend.core.primitives.Value import Value
from backend.core.primitives.Port import Port

class Element(BaseObject):
    def __init__(self, name: str, inlet_ports_num: int, outlet_ports_num: int,
                 parameters_num: int):
        super().__init__(name, ObjectType.ELEMENT)
        self._inlet_ports = ObjectsStorage(name='in', storage_type='PORT',
                                           max_size=inlet_ports_num, lock_names=True)
        self._outlet_ports = ObjectsStorage(name='out', storage_type='PORT',
                                            max_size=outlet_ports_num, lock_names=True)
        self._params_port = Port(name='param', values_number=parameters_num)
        
    def _calc_address(self, idx: str):
        address = idx.split('.')
        if len(address) == 1 and address[0] == 'param':
            return self._params_port, None
        elif len(address) == 2 and address[0] == 'param':
            return self._params_port, address[1]
        elif len(address) == 2 and address[0] == 'in':
            return self._inlet_ports[int(address[1])], None
        elif len(address) == 3 and address[0] == 'in':
            return self._inlet_ports[int(address[1])], address[2]
        elif len(address) == 2 and address[0] == 'out':
            return self._outlet_ports[ int(address[1])], None
        elif len(address) == 3 and address[0] == 'out':
            return self._outlet_ports[ int(address[1])], address[2]
        else:
            raise KeyError("Invalid address")    

    def port(self, idx: str):
        port, key = self._calc_address(idx)
        return port
       
        
    def __getitem__(self, idx: str):
        return self.port(idx)
    
    def __setitem__(self, idx: str, element: Value):
        port, key = self._calc_address(idx)
        if key is not None:
            port[key] = element
        else:
            raise KeyError("Wrong Value Name")










