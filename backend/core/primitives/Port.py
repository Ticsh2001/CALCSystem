from backend.core.primitives.DataType import BaseObject, ObjectType, ValueStatus
from backend.core.primitives.ObjectsStorage import ObjectsStorage
from backend.core.primitives.Value import Value
from typing import Union, Any, Optional, Type, TypeVar, Dict, Tuple
import uuid
from collections import Counter




class Port(BaseObject):
    def __init__(self, name: str, values_number: int=-1, direction: str='both'):
        super().__init__(name, ObjectType.PORT)
        self._direction = direction
        self._values = ObjectsStorage(f'{name}_values', ObjectType.VALUE, values_number, lock_names=True)

    def register(self, value_object: Value) -> uuid.UUID:
        key = self._values.add(value_object)
        return key
    
    def register_with_key(self, key: uuid.UUID, value_object: Value):
        self._values.add_with_key(key, value_object)

    def registered_names(self):
        return self._values.registered_names()
    
    def list_status(self) -> Dict[str, str]:
        return {val.name: val.status for val in self._values}

    def value(self, key: Union[str, uuid.UUID, int]):
        return self._values.get(key)

    def uuid(self, key: Union[str, int]):
        return self._values.get_uuid(key)
    
    def quantity(self, key: Union[str, uuid.UUID, int]):
        return self._values.get(key).value
 
    def status(self, key: Union[str, uuid.UUID, int]) -> str:
        return self._values.get(key).status

    def info(self, key: Union[str, uuid.UUID, int]) -> Optional[Tuple]:
        val = self._values.get(key)
        return val.value, val.status

    def contains(self, key: Union[uuid.UUID, str]):
        return self._values.contains(key)

    def __getitem__(self, key: Union[str, uuid.UUID, int]):
        return self._values[key]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __eq__(self, other: Port) -> bool:
        if not isinstance(other, Port):
            return NotImplemented
        self_specs = [val.spec for val in self._values]
        other_specs = [val.spec for val in other._values]
        return Counter(self_specs) == Counter(other_specs)

    def __ne__(self, other: Port) -> bool:
        return not self == other
    
    def __setitem__(self, key: Union[uuid.UUID, str, int], element: Value):
        self._values[key] = element
    
    def is_known(self):
        return all([False if val.status == 'UNKNOWN' else True for val in self._values])
    
    @property
    def direction(self):
        return self._direction
    
    def list_by_status(self, status: Union[ValueStatus, str]):
        if isinstance(status, ValueStatus):
            return [val.name for val in self._values if val.status == status.to_string()]
        elif isinstance(status, str):
            return [val.name for val in self._values if val.status == status]
        
    def to_dict(self) -> Dict:
        result = super().to_dict()
        result['direction'] = self._direction
        result['values'] = self._values.to_dict()
        return result


        
    
    

    



    


        

    
