
#items on the shelves - list of lists containing unique string id.
#  eg: [['A', 'B'], ['C', 'D']] => Shelf 0 contains 'A' on position 0 and 'B' on position 1, etc

#money (for change and user's money) - int - as the number of smallest possible coins (eg 1 Cent). 
# ie value of 1000 means 1000 Cents, which can then be parsed into separate money kinds

#purchases of user - list of strings - every purchase is a unique string, determining the product purchased 
# (depends on the scenario, perhaps there is no need to store the purchases)

from typing import List, Tuple

class Item():
    def __init__(self, name: str, cost: int):
        self.name = name
        self.count = 1

        self.cost_per_item = cost

    @property
    def cost(self) -> int:
        return self.cost_per_item * self.count

    @classmethod
    def Empty(cls) -> 'Item':
        item = cls('Empty')
        item.count = 0
        item.cost_per_item = 0

        return item

    @classmethod
    def CreateMultiple(cls, name: str, count: int, cost: int) -> 'Item':
        item = cls(name)
        item.count = count
        item.cost_per_item = cost

        return item

    def IsEmpty(self):
        return self.name == 'Empty' and self.count == 0

    def __add__(self, x: int) -> int:
        self.count += x
        return self

    def __sub__(self, x: int) -> int:
        self.count -= x

        # Clipping to 0
        self.count = max(self.count, 0)

        if (self.count == 0):
            self.name = 'Empty'

        return self

    def __str__(self) -> str:
        return f"{self.name}.{self.count}.{self.cost_per_item}$"

class Shelf():
    def __init__(self):
        self.items = []

    @property
    def cost(self) -> int:
        return sum([item.cost for item in self.items])

    @classmethod
    def Empty(cls, length: int) -> 'Shelf':
        shelf = Shelf()
        shelf.items = [Item.Empty()] * length

        return shelf

    @classmethod
    def FromItems(cls, items: List[Item]) -> 'Shelf':
        shelf = Shelf()
        shelf.items = items

        return shelf

    @classmethod
    def FromItemNames(cls, names: List[Tuple[str, int]]) -> 'Shelf':
        shelf = cls()
        shelf.items = [Item(name, cost) for name, cost in names]

        return shelf

    def __getitem__(self, index: int) -> Item:
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

    def ClearItem(self, index: int) -> Item:
        self.ValidateIndex(index)

        if (self.items[index].IsEmpty()):
            raise ValueError(f"There is no item at index {index}!")

        item = self.items[index]

        self.items[index] = Item.Empty()

        return item

    def AddItem(self, index: int, item: Item) -> None:
        self.ValidateIndex(index)

        if (not self.items[index].IsEmpty()):
            raise ValueError(f"Index {index} is already occupied by another item - {self.items[index].name}")

        self.items[index] = item

    def AddItem(self, index: int, item_name: str, cost: int) -> None:
        self.ValidateIndex(index)

        if (not self.items[index].IsEmpty()):
            raise ValueError(f"Index {index} is already occupied by another item - {self.items[index].name}")

        self.items[index] = Item(item_name, cost)

    def AddItem(self, index: int):
        self.ValidateIndex(index)

        if (self.items[index].IsEmpty()):
            raise ValueError(f"There is no item at index {index}!")

        self.items[index] += 1

    def __str__(self) -> str:
        return ' '.join([str(item) for item in self.items])

class VendingMachine():
    def __init__(self):
        self.shelves = []
        self.item_locations = {}
        self.money = 100

    @property
    def cost(self):
        return sum([shelf.cost for shelf in self.shelves])

    @classmethod
    def Empty(cls, num_shelves: int, shelves_length: int) -> 'VendingMachine':
        vending_machine = cls()
        vending_machine.shelves = [Shelf.Empty(shelves_length)] * num_shelves

        return vending_machine

    @classmethod
    def FromItemNames(cls, item_names_per_shelf: List[List[Tuple[str, int]]]) -> 'VendingMachine':
        """
        Expects a list of item names for every shelf
        """

        vending_machine = cls()
        vending_machine.shelves = [Shelf.FromItemNames(item_names) for item_names in item_names_per_shelf]

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

    def __getitem__(self, index: int) -> Shelf:
        return self.shelves[index]

    def __len__(self):
        return len(self.shelves)

    def ValidateIndex(self, index: int) -> None:
        if (index >= 0 and index < len(self.shelves)):
            return

        raise ValueError(f"Index out of range for the vending machine with {len(self.shelves)} shelves")

    def AddItem(self, shelf_number: int, index: int, item: Item) -> None:
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


item_names = [[('Bread',5), ('Sandwich', 10), ('AJuice', 8)],
              [('OJuice', 9), ('Crisps', 9), ('Apple', 4)],
              [('Muffin', 6), ('Tomato', 4), ('Coffee', 7)]]

vending_machine = VendingMachine.FromItemNames(item_names)

item_names2 = [[('Bread',5), ('Sandwich', 10), ('AJuice', 8)],
              [('Apple', 4), ('Orange', 5), ('Waffles', 7)]]

vending_machine2 = VendingMachine.FromItemNames(item_names2)

# {'Bread': 2, 'Sandwich': 2, 'AJuice': 2, 'OJuice': 1, 'Crisps': 1, 'Apple': 2, 'Muffin': 1, 'Tomato': 1, 'Coffee': 1, 'Orange': 1, 'Waffles': 1}
print(VendingMachine.ContentUnion(vending_machine, vending_machine2))

# {'OJuice': 1, 'Crisps': 1, 'Muffin': 1, 'Tomato': 1, 'Coffee': 1, 'Orange': 1, 'Waffles': 1}
print(VendingMachine.ContentDifference(vending_machine, vending_machine2))

# {'Bread': 2, 'Sandwich': 2, 'AJuice': 2, 'Apple': 2}
print(VendingMachine.ContentIntersection(vending_machine, vending_machine2))

# False (they both start with 100 cash)
print(vending_machine > vending_machine2)

# True
print(vending_machine == vending_machine2)

item_name, cost = vending_machine.TakeItem(0,1)

print(f"Took {item_name} that costs {cost}")

print(f"New amount of money for vending machine = {vending_machine.money}")

# False
print(vending_machine == vending_machine2)