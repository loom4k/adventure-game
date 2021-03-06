from termcolor import colored


class Mobile:
    """A class for things that move around (currently just the player)
        tracks inventory and location (Room object)."""

    def __init__(self, inventory, location):
        self.inventory = inventory
        self.location = location

        self.new_location = self.location.label
        self.injected = False
        # NOT A ROOM object, just the string matching the label of the new room
        # on start, matches the starting room so player stays in place
        self.victory = False

        self.item = None
        self.exit = None
        self.things_to_look_at = None

    def move(self, _exit):
        """Called if the command starts with a movement keyword compares
            the content of the command to the keywords for each exit
            in the room.
        """

        self.exit = _exit
        # check to see if the exit is valid/open
        if self.exit.label == 'not_found':
            print(colored("You can't go that way.", 'red'))

        elif self.exit.shall_pass(self):
            print(
                colored("You go through the %s to the %s.\n", 'cyan') % (
                    self.exit.name, self.exit.direction
                )
            )

            self.new_location = self.exit.destination
        else:
            print(colored("You can't go that way.", 'red'))

    def take(self, item):
        """Called if the player is trying to pick something
            in the room up.
        """
        self.item = item

        if self.item.label == "not_found":
            print(colored("I don't see one of those to pick up.\n", 'yellow'))

        elif self.item.type != "carryable":
            print(colored("You can't pick that up.\n", 'red'))

        else:
            print(colored("You pick up the %s.\n", 'green') % self.item.name)
            self.inventory.add(self.item)
            del self.location.items[self.item.label]

    def drop(self, item):
        """Called if the player is trying to drop something
            reverse of  inventory_take.
        """

        self.item = item
        if self.item.label == 'not_found':
            print(colored("You're not carrying one of those.\n", 'yellow'))
        else:
            self.inventory.remove(self.item)
            self.location.items[self.item.label] = self.item

    def can_see(self):
        """Defines the items the mobile can see,
            for use with the "look" command adds together the items
            and exits in the room along with inventory items.
        """

        self.things_to_look_at = dict(list(self.location.items.items()))
        self.things_to_look_at.update(self.location.exits)
        self.things_to_look_at.update(self.inventory.inv_list)
        # and here naming the dict of items "items" gets awkward
        # first line calls the items() property of the dictionary named "items"
        # second line mixes in the exits dictionary
        # this seems awkward but was the best way i could come up with to
        # add multiple dicts while leaving the originals intact

        return self.things_to_look_at

    def look_special(self, item):
        """Allows triggering of events when an item is looked at to add
            an event to an item, set the item's look_special to True
            then add the event as an elif branch here.
        """
        self.item = item

        if self.item.label == 'corpse':
            self.location.items['keycard'].type = "carryable"
        elif self.item.label == 'frozen_corpse':
            self.location.items['key'].type = "scenery"
        elif self.item.label == "fridge":
            self.location.items['syringe'].type = "carryable"
        else:
            # shouldn't happen
            print(colored("Look special failed.", 'red'))

    def use(self, item):
        """Called if the parser thinks the player is trying to use an item.

        calls the appropriate event function
        for whatever item they're trying to use better way?

        put flag in the Item object itself?
        """
        self.item = item

        if self.item.label == 'scalpel' or (
                self.location.label == 'garage' and self.item.label == 'key'):
            self.cut()

        elif self.item.label == "syringe":
            self.inject()

        elif self.item.label == "core" or (
                self.location.label == 'reactor' and self.item.label == 'key'):
            self.unlock_core()

        elif self.item.label == 'snowmobile':
            self.fix()
        else:
            self.use_fail()

    @staticmethod
    def use_fail():
        print(colored("You don't see how to do that.", 'red'))

    def cut(self):
        if not self.inventory.has('scalpel'):
            print(colored("You don't have anything to cut that with.", 'red'))
        elif not self.can_cut_key():
            print(
                colored(
                    "Cutting that doesn't seem like it would be a good idea.",
                    'yellow'
                )
            )
        else:
            print(
                colored(
                    "You use the scalpel to cut the key free of the frozen, "
                    "swollen fingers. The flesh is stiff and bloodless.",
                    'green'
                )
            )

            self.location.items['key'].type = "carryable"

    def can_cut_key(self):
        if self.location.label != 'garage':
            return False
        elif 'key' not in list(self.location.items.keys()):
            return False
        elif self.location.items['key'].type == 'hidden':
            return False
        else:
            return True

    def unlock_core(self):
        if not self.inventory.has('key'):
            print(
                colored(
                    "You don't have anything that fits in the lock.",
                    'red'
                )
            )

        elif self.location.label != 'reactor' or (
            "core" not in list(self.location.items.keys())
        ):
            print(
                colored("You don't see anything that key would unlock.", 'red')
            )

        else:
            print(
                colored(
                    "You put the key into the lock on top of the cylinder"
                    " and twist. There's a hiss as the top angles open.",
                    'green'
                )
            )

            del self.location.items['core']
            self.location.items['open_core'].type = "scenery"
            self.location.items['rod'].type = "carryable"

    def inject(self):
        if not self.inventory.has('syringe'):
            print(colored("You don't have anything to inject.", 'red'))

        else:
            print(
                colored(
                    "It's clear what you have to do. You "
                    " grit your teeth and plunge the syringe into your chest."
                    " You probably can't really feel the spread of the liquid "
                    "burning through your arteries, but if feels like you can.",
                    'blue'
                )
            )
            self.injected = True

    def fix(self):
        if self.inventory.has('rod') and self.location.label == 'garage':
            print(
                colored(
                    "You slide the core into the cylinder on the side of the "
                    "modified snowmobile. It slides into place snugly and "
                    "the snowmobile's electronics blink to life.",
                    'blue'
                )
            )
            self.victory = True

        elif self.location.label == 'garage':
            print(
                colored(
                    "The snowmobile is totally inert."
                    "  The gas tank and battery have both been removed, "
                    "and a strange cylindrical assembly mounted on the side."
                    " It will need some other power source.",
                    'blue'
                )
            )

        else:
            print(
                colored(
                    "You really don't think that really"
                    " needs that kind of power.",
                    'yellow'
                )
            )
