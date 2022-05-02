from typing import List, Tuple

from abc import ABC, abstractmethod, abstractclassmethod, abstractproperty

from Item import BaseItem

class BaseShelf:
    @abstractproperty
    def cost(self) -> int:
        ...

    @abstractclassmethod
    def Empty(cls, length: int) -> 'BaseShelf':
        ...

    @abstractclassmethod
    def FromItemNames(cls, names: List[Tuple[str, int]]) -> 'BaseShelf':
        ...

    def __getitem__(self, index: int) -> BaseItem:
        ...

    def __len__(self):
        ...

    def TakeItem(self, index: int) -> str:
        ...

    def ClearItem(self, index: int) -> BaseItem:
        ...

    def AddItem(self, index: int, item: BaseItem) -> None:
        ...

    def __str__(self) -> str:
        ...

class ClassicShelf(BaseShelf):
    def __init__(self, ItemType: BaseItem):
        """
        One can initialize the shelf with any Item that inherits from BaseItem,
        and it will operate accordingly
        """

        self.items = []

        self.ItemType = ItemType

    @property
    def cost(self) -> int:
        return sum([item.cost for item in self.items])

    @classmethod
    def Empty(cls, ItemType: BaseItem, length: int) -> 'ClassicShelf':
        shelf = ClassicShelf(ItemType)
        shelf.items = [ItemType.Empty()] * length

        return shelf

    @classmethod
    def FromItems(cls, ItemType: BaseItem, items: List[BaseItem]) -> 'ClassicShelf':
        shelf = ClassicShelf(ItemType)
        shelf.items = items

        return shelf

    @classmethod
    def FromItemNames(cls, ItemType: BaseItem, names: List[Tuple[str, int]]) -> 'ClassicShelf':
        shelf = cls(ItemType)
        shelf.items = [ItemType(name, cost) for name, cost in names]

        return shelf

    def __getitem__(self, index: int) -> BaseItem:
        return self.items[index]

    def __len__(self):
        return len(self.items)

    def ValidateIndex(self, index: int) -> None:
        if (index >= 0 and index < len(self.items)):
            return
        
        raise ValueError(f"Index out of range for the shelf with {len(self.items)} items") 

    def TakeItem(self, index: int) -> str:
        """
        Returns the name of the taken item and its cost
        """

        self.ValidateIndex(index)

        if (self.items[index].IsEmpty()):
            raise ValueError(f"There is no item at index {index}!")

        item_name = self.items[index].name
        cost = self.items[index].cost_per_item

        self.items[index] -= 1

        return item_name, cost

    def ClearItem(self, index: int) -> BaseItem:
        self.ValidateIndex(index)

        if (self.items[index].IsEmpty()):
            raise ValueError(f"There is no item at index {index}!")

        item = self.items[index]

        self.items[index] = self.ItemType.Empty()

        return item

    def AddItem(self, index: int, item: BaseItem) -> None:
        self.ValidateIndex(index)

        if (not self.items[index].IsEmpty()):
            raise ValueError(f"Index {index} is already occupied by another item - {self.items[index].name}")

        self.items[index] = item

    def AddItem(self, index: int, item_name: str, cost: int) -> None:
        self.ValidateIndex(index)

        if (not self.items[index].IsEmpty()):
            raise ValueError(f"Index {index} is already occupied by another item - {self.items[index].name}")

        self.items[index] = self.ItemType(item_name, cost)

    def AddItem(self, index: int):
        self.ValidateIndex(index)

        if (self.items[index].IsEmpty()):
            raise ValueError(f"There is no item at index {index}!")

        self.items[index] += 1

    def __str__(self) -> str:
        return ' '.join([str(item) for item in self.items])