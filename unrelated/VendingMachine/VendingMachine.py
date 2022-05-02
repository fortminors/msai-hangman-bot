from typing import List, Tuple

from Item import BaseItem
from Shelf import BaseShelf

class VendingMachine():
    def __init__(self, ItemType: BaseItem, ShelfType: BaseShelf):
        self.shelves = []
        self.item_locations = {}
        self.money = 100

        self.ItemType = ItemType
        self.ShelfType = ShelfType

    @property
    def cost(self):
        return sum([shelf.cost for shelf in self.shelves])

    @classmethod
    def Empty(cls, ItemType: BaseItem, ShelfType: BaseShelf, num_shelves: int, shelves_length: int) -> 'VendingMachine':
        vending_machine = cls(ItemType, ShelfType)
        vending_machine.shelves = [ShelfType.Empty(ItemType, shelves_length)] * num_shelves

        return vending_machine

    @classmethod
    def FromItemNames(cls, ItemType: BaseItem, ShelfType: BaseShelf, item_names_per_shelf: List[List[Tuple[str, int]]]) -> 'VendingMachine':
        """
        Expects a list of item names for every shelf
        """

        vending_machine = cls(ItemType, ShelfType)
        vending_machine.shelves = [ShelfType.FromItemNames(ItemType, item_names) for item_names in item_names_per_shelf]

        for i in range(len(vending_machine.shelves)):
            for j in range(len(vending_machine.shelves[i])):
                name = vending_machine.shelves[i][j].name

                vending_machine.item_locations[name] = (i,j)

        return vending_machine

    @staticmethod
    def ContentDifference(vm1: 'VendingMachine', vm2: 'VendingMachine'): 
        contentDifference = {}
        
        # Adding from 1st
        for key, item in vm1.item_locations.items():
            if (key not in vm2.item_locations):
                contentDifference[key] = vm1[item[0]][item[1]].count

        # Adding from 2nd
        for key, item in vm2.item_locations.items():
            if (key not in vm1.item_locations):
                contentDifference[key] = vm2[item[0]][item[1]].count

        return contentDifference

    @staticmethod
    def ContentUnion(vm1: 'VendingMachine', vm2: 'VendingMachine'): 
        contentUnion = {}
        
        # Adding from 1st
        for key, item in vm1.item_locations.items():
            contentUnion[key] = vm1[item[0]][item[1]].count

        # Adding from 2nd
        for key, item in vm2.item_locations.items():
            if (key in contentUnion):
                contentUnion[key] += vm2[item[0]][item[1]].count
            else:
                contentUnion[key] = vm2[item[0]][item[1]].count

        return contentUnion

    @staticmethod
    def ContentIntersection(vm1: 'VendingMachine', vm2: 'VendingMachine'): 
        contentIntersection = {}
        
        # Adding from 1st the ones that are present in 2nd
        for key, item in vm1.item_locations.items():
            if (key in vm2.item_locations):
                loc2 = vm2.item_locations[key]

                contentIntersection[key] = vm1[item[0]][item[1]].count + vm2[loc2[0]][loc2[1]].count

        return contentIntersection

    def __lt__(self, other: 'VendingMachine'):
        return self.money < other.money

    def __le__(self, other: 'VendingMachine'):
        return self.money <= other.money

    def __gt__(self, other: 'VendingMachine'):
        return self.money > other.money

    def __ge__(self, other: 'VendingMachine'):
        return self.money >= other.money

    def __eq__(self, other: 'VendingMachine'):
        return self.money == other.money

    def __ne__(self, other: 'VendingMachine'):
        return self.money != other.money

    def __getitem__(self, index: int) -> BaseShelf:
        return self.shelves[index]

    def __len__(self):
        return len(self.shelves)

    def ValidateIndex(self, index: int) -> None:
        if (index >= 0 and index < len(self.shelves)):
            return

        raise ValueError(f"Index out of range for the vending machine with {len(self.shelves)} shelves")

    def AddItem(self, shelf_number: int, index: int, item: BaseItem) -> None:
        self.ValidateIndex(index)

        self.shelves[shelf_number].AddItem(index, item)

        self.item_locations[item.name] = (shelf_number, index)

    def AddItem(self, shelf_number: int, index: int, item_name: str, cost: int) -> None:
        self.ValidateIndex(index)

        self.shelves[shelf_number].AddItem(index, item_name, cost)

        self.item_locations[item_name] = (shelf_number, index)

    def AddItem(self, shelf_number: int, index: int) -> None:
        self.ValidateIndex(shelf_number)

        self.shelves[shelf_number].AddItem(index)

    def TakeItem(self, shelf_number: int, index: int) -> str:
        self.ValidateIndex(shelf_number)
        item_name, cost = self.shelves[shelf_number].TakeItem(index)

        # Removed last item
        if (self.shelves[shelf_number][index].name != item_name):
            self.item_locations.pop(item_name)

        self.money += cost

        return item_name, cost

    def __repr__(self) -> str:
        return '\n'.join([str(shelf) for shelf in self.shelves])
