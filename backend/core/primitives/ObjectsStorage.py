from core.primitives import ObjectType
import uuid
from typing import Any, Callable, Dict, Iterator, List, Optional, TypeVar, Union


T = TypeVar('T')

class ObjectsStorage:
    """Хранилище элементов с автоматической генерацией UUID ключей."""
    
    def __init__(self, storaged_type: ObjectType, max_size: int = -1, lock_names=False):
        self._storaged_type = storaged_type
        self._items: Dict[uuid.UUID, T] = {}
        self._max_size = max_size
        self._lock_names = lock_names
        self._names = dict()

    def _check_element(self, element: T) -> None:
        if not hasattr(element, 'object_type') or not hasattr(element, 'name'):
            raise TypeError("Element has no correct attributes")
        if self._lock_names and element.name in self._names:
            raise NameError("Value with this name already exists")
        if not element.object_type == self._storaged_type:
            raise TypeError(f"Wrong type of element. Element type: {element.object_type}, storage type: {self._storaged_type}")
        if self._max_size > 0 and len(self._items) >= self._max_size:
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
            return self._items.pop(key, None)
        elif self._lock_names and isinstance(key, str):
            return self._items.pop(self._names[key], None)
        else:
            return None
        
    def get(self, key: Union[uuid.UUID, str]) -> Optional[T]:
        """Получить элемент по ключу."""
        if isinstance(key, uuid.UUID):
            return self._items.get(key)
        elif self._lock_names and isinstance(key, str):
            return self._items.get(self._names[key])
        else:
            return None
    
    def contains(self, key: Union[uuid.UUID, str]) -> bool:
        """Проверить наличие элемента по ключу."""
        if isinstance(key, uuid.UUID):
            return key in self._items
        elif self._lock_names and isinstance(key, str):
            return self._names[key] in self._items
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
    
    # ----- Альтернатива: использовать __getitem__, __setitem__ для доступа по ключу -----
    def __getitem__(self, key: uuid.UUID) -> T:
        return self._items[key]
    
    def __delitem__(self, key: uuid.UUID) -> None:
        del self._items[key]

    def to_dict(self):
        return {key: self._items[key].to_dict() for key in self._items.keys()}
