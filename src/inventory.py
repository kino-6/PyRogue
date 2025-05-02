from item import Item


class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def has_item(self, item):
        return item in self.items

    def __str__(self):
        return str(self.items)
