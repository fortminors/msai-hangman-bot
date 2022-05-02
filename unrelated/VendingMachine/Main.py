from Item import ItemHolder
from Shelf import ClassicShelf
from VendingMachine import VendingMachine

item_names = [[('Bread',5), ('Sandwich', 10), ('AJuice', 8)],
              [('OJuice', 9), ('Crisps', 9), ('Apple', 4)],
              [('Muffin', 6), ('Tomato', 4), ('Coffee', 7)]]

vending_machine = VendingMachine.FromItemNames(ItemHolder, ClassicShelf, item_names)

item_names2 = [[('Bread',5), ('Sandwich', 10), ('AJuice', 8)],
            [('Apple', 4), ('Orange', 5), ('Waffles', 7)]]

vending_machine2 = VendingMachine.FromItemNames(ItemHolder, ClassicShelf, item_names2)

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