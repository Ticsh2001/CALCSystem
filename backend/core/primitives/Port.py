from core.primitives.DataType import BaseObject, ObjectType
from core.primitives.ObjectsStorage import ObjectsStorage
from core.primitives.Value import Value
from typing import Union, Any, Optional, Type, TypeVar
import uuid



class Port(BaseObject):
    def __init__(self, name: str, values_number: int=-1):
        super().__init__(name, ObjectType.PORT)
        self._values = ObjectsStorage(ObjectType.VALUE, values_number, lock_names=True)

    def register(self, value_object: Union[Value, dict]) -> uuid.UUID:
        if not isinstance(value_object, dict):
            key = self._values.add(value_object)
        else:
            key = self._values.add(Value.from_dict(value_object))
        return key
    
    def register_with_key(self, key, value_object: Union[Value, dict]):
        if not isinstance(value_object, dict):
            self._values.add_with_key(key, value_object)
        else:
            self._values.add_with_key(key, Value.from_dict(value_object))

    def list_names(self):
        return [val.name for val in self._values]
    



    


        

    
