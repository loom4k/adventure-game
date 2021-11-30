from termcolor import colored


class Inventory:
    """Manages the player's inventory

    creates a dictionary using an item's label as the key
    linked to the Item-class object
    """

    def __init__(self):
        self.inv_list = {}
        self.item = None
        self.label = None

    def add(self, item):
        self.item = item
        if self.has(self.item):
            self.add_error(self.item)
        else:
            self.inv_list[self.item.label] = self.item

    def remove(self, item):
        self.item = item
        if self.has(self.item.label):
            del self.inv_list[self.item.label]
        else:
            self.remove_error(self.item)

    def has(self, label):
        self.label = label
        return self.label in self.inv_list.keys()

    def describe(self, item):
        self.item = item
        if self.has(self.item.label):
            print(self.item.description)
        else:
            print(
                colored("You are not carrying a %s.\n" % self.item.name, 'red')
            )

    def list(self):
        """Lists the contents of the inventory."""
        if not self.inv_list:
            return print(colored("You are not carrying anything.", 'red'))

        print(
            colored(
                "You are carrying:\n"
                + '\n'.join(item.name for item in self.inv_list.values()),
                'blue'
            )
        )

    # these should probably never happen because of how add
    # and remove are called as part of mobile.take/drop,
    # which should only be called in pre-screened circumstances

    @staticmethod
    def remove_error(item):
        print(colored("%s not found in inventory." % item.label, 'red'))

    @staticmethod
    def add_error(item):
        print(colored("%s already in inventory" % item.label, 'yellow'))
