from core.primitives import ObjectType, BaseObject
import uuid
from typing import Any, Callable, Dict, Iterator, List, Optional, TypeVar, Union

T = TypeVar('T')

class ObjectsStorage(BaseObject):
    """Хранилище элементов с автоматической генерацией UUID ключей."""
    
    def __init__(self, name: str, storage_type: Union[ObjectType, str], max_size: int = -1, lock_names=False):
        super().__init__(name=name, obj_type=ObjectType.STORAGE)
        self._storage_type = ObjectType.from_input(storage_type)
        self._items: Dict[uuid.UUID, T] = {}
        self._max_size = max_size
        self._lock_names = lock_names
        self._names = dict()

    def _check_element(self, element: T) -> None:
        if not hasattr(element, 'object_type') or not hasattr(element, 'name'):
            raise TypeError("Element has no correct attributes")
        if self._lock_names and element.name in self._names:
            raise NameError("Value with this name already exists")
        if not element.object_type == self._storage_type.to_string():
            raise TypeError(f"Wrong type of element. Element type: {element.object_type}, storage type: {self._storage_type}")
        if 0 < self._max_size <= len(self._items):
            raise IndexError("Maximum elements number exceeded")
    
    def add(self, element: T) -> uuid.UUID:
        """Добавить элемент, вернуть его UUID ключ."""
        self._check_element(element)
        key = uuid.uuid4()
        self._items[key] = element
        if self._lock_names:
            self._names[element.name] = key
        return key
        
    def add_with_key(self, key: uuid.UUID, element: T) -> None:
        """Добавить элемент с заданным ключом (если такого ключа ещё нет)."""
        self._check_element(element)
        self._items[key] = element
        if self._lock_names:
            self._names[element.name] = key

    def remove(self, key: Union[uuid.UUID, str]) -> Optional[T]:
        """Удалить элемент по ключу, вернуть удалённый элемент или None."""
        if isinstance(key, uuid.UUID):
            obj = self._items.pop(key, None)
            if obj is not None and self._lock_names:
                _ = self._names.pop(obj.name, None)
            return obj
        elif self._lock_names and isinstance(key, str):
            uid = self._names.pop(key, None)
            if uid is not None:
                return self._items.pop(uid, None)
            else:
                return None
        else:
            return None
        
    def get(self, key: Union[uuid.UUID, str]) -> Optional[T]:
        """Получить элемент по ключу."""
        if isinstance(key, uuid.UUID):
            return self._items.get(key)
        elif self._lock_names and isinstance(key, str):
            uid = self._names.get(key, None)
            if uid is not None:
                return self._items.get(uid, None)
            else:
                return None
        else:
            return None
    
    def contains(self, key: Union[uuid.UUID, str]) -> bool:
        """Проверить наличие элемента по ключу."""
        if isinstance(key, uuid.UUID):
            return key in self._items
        elif self._lock_names and isinstance(key, str):
            return key in self._names and self._names[key] in self._items
        else:
            return False        
    
    def all(self) -> List[T]:
        """Вернуть все элементы (список)."""
        return list(self._items.values())
    
    def items(self) -> List[tuple[uuid.UUID, T]]:
        """Вернуть все пары (ключ, значение)."""
        return list(self._items.items())
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __iter__(self) -> Iterator[T]:
        return iter(self._items.values())

    @property
    def storage_type(self) -> str:
        return self._storage_type.to_string()

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def is_lock_names(self) -> bool:
        return self._lock_names
    
    # ----- Альтернатива: использовать __getitem__, __setitem__ для доступа по ключу -----
    def __getitem__(self, key: Union[uuid.UUID, str, int]) -> Optional[T]:
        if isinstance(key, uuid.UUID):
            return self._items.get(key, None)
        elif self._lock_names and isinstance(key, str):
            uid = self._names.get(key, None)
            return self._items.get(uid) if uid is not None else None
        elif isinstance(key, int):
            return self._items[list(self._items.keys())[key]]
        else:
            return None                               
    
    def __delitem__(self, key: Union[uuid.UUID, str]) -> None:
        if self._lock_names and isinstance(key, str):
            uid = self._names.pop(key, None)
            if uid is not None:
                del self._items[uid]
            else:
                raise KeyError(f"No element with current name {key}")
        elif self._lock_names and isinstance(key, uuid.UUID):
            obj = self._items.get(key, None)
            if obj is not None:
                name = obj.name
                del self._items[key]
                _ = self._names.pop(name, None)
            else:
                raise KeyError(f"No element with current id {key}")
        elif not self._lock_names and isinstance(key, uuid.UUID):
            del self._items[key]
        else:
            raise KeyError(f"Current storage doesn't contain names")

    def to_dict(self):
        res_1 = super().to_dict()
        res_2 = {'storage_type': self._storage_type.to_string(),
                 'max_size': self._max_size, 'lock_names': self._lock_names,
                 'items': {key: self._items[key].to_dict() for key in self._items.keys()}}
        return {**res_1, **res_2}

    def registered_names(self) -> List[str]:
        if self._lock_names:
            return list(self._names.keys())
        else:
            return []
