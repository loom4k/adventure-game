from sys import exit
from termcolor import colored

HELP_LIST = colored(
    "_____________________________________________\n"
    "|          The Great Escape - Info          |\n"
    "|                                           |\n"
    "| pick [item] -> picks up item to inventory |\n"
    "| north, west, east, south -> directions    |\n"
    "| go -> get room details and exits          |\n"
    "| exit -> close game after confirmation     |\n"
    "| inv, inventory -> display backpack        |\n"
    "|                                           |\n"
    "|________________Version 0.1________________|\n",
    'blue'
)


VICTORY_MESSAGE = (
    "With a touch of the ignition button, the snowmobile roars"
    " with way more power than it needs. You climb on and steer"
    "it out into the blinding snow, hoping you will reach civilization"
    " while you can still be described as civilized."
    "Congratulations! You are a winner!"
)

PARSE_FAIL_TEXT = colored("I'm afraid I don't know what that means.", 'red')


class Engine:

    def __init__(self, game_map, player):
        """Parses player commands and manipulates a map object."""

        # sets up recognized keywords.
        self.map = game_map
        self.player = player

        self.movement_keywords = [
            "go", "n", "e", "s", "w",  "north", "east", "south", "west"
        ]

        self.inventory_keywords = {
            "take": "take",
            "pick": "take",
            "drop": "drop",
        }

        self.menu_keywords = ["quit", "help", "i", "inv"]
        self.look_keywords = ["look", "search", "read"]

        self.room_name = None
        self.room = None
        self.command = None
        self.item_to_try = None
        self.split_command = None
        self.first_word = None
        self.exit_to_try = None
        self.use_words = None
        self.looked_at = None
        self.use_item = None
        self.items_to_search = None
        self.command_list = None
        self.success = None

    def move_into(self, room_name):
        """Looks up the room with the right label and makes the player's
             location be that room and prints the description.
        """
        self.room_name = room_name
        self.room = self.map.all_rooms[self.room_name]
        self.player.location = self.room

        print(
            colored(
                " _______ _             _____                _   \n"
                "|__   __| |           / ____|              | |  \n"
                "   | |  | |__   ___  | |  __ _ __ ___  __ _| |_\n"
                "   | |  | '_ \\ / _ \\ | | |_ | '__/ _ \\/ _` | __|\n"
                "   | |  | | | |  __/ | |__| | | |  __/ (_| | |_\n"
                "   |_|  |_|_|_|\\___|  \\_____|_|  \\___|\\__,_|\\__|\n"
                "|  ____|\n"
                "| |__   ___  ___ __ _ _ __   ___ \n"
                "|  __| / __|/ __/ _` | '_ \\ / _ \\ \n"
                "| |____\\__ \\ (_| (_| | |_) |  __/\n"
                "|______|___/\\___\\__,_| .__/ \\___| v0.1\n"
                "                     | |\n"
                "                     |_|\n"
                "                        by Loom4k\n",
                'blue'
            ),
        )
        self.room.describe()
        return self

    @staticmethod
    def prompt():
        """Prints the prompt and returns the input."""
        print(colored("\nWhat do you want to do?", 'magenta'))
        return input(colored("> ", "green"))

    def menu_commands(self, command):
        """handles straightforward,
        always-available commands like `quit` and `inv`.
        """
        self.command = command
        if "quit" in self.command:
            print(
                "Are you sure? "
                "Press Y to quit, any other key to keep playing."
            )

            if input("> ").lower() == "y":
                exit(1)
            else:
                return False

        elif command in ('i', 'inv', 'inventory'):
            self.player.inventory.list()

        elif command in ('h', 'help', 'info'):
            print(HELP_LIST)
            return False

        else:
            print(PARSE_FAIL_TEXT)
            return False

    def inventory_parse(self, command):
        """Decides whether the command is to take, drop
            or use an item and calls the appropriate mobile function.
        """
        self.command = command

        if self.inventory_keywords[self.command[0]] == "take":
            self.item_to_try = self.mentioned_in(
                self.command, self.player.location.items
            )

            self.player.take(self.item_to_try)

        elif self.inventory_keywords[self.command[0]] == "drop":
            self.item_to_try = self.mentioned_in(
                self.command, self.player.inventory.inv_list
            )

            self.player.drop(self.item_to_try)
        else:
            # should never happen
            print(colored("Inventory parsing error", "red"))

    def look_fail(self, command):
        """Called when a look command doesn't refer to anything
            could be made more interesting by referring to the command.
        """
        self.command = command
        print(colored("You don't see anything like that.", "yellow"))

    def parse(self, action):
        """Breaks commands into categories
            and then calls an appropriate function.
        """
        self.split_command = action.split()
        # splits the input into a list of individual words
        self.first_word = self.split_command[0]

        # pulls out the first word,
        # then checks to see if it's in a recognizable category
        # then calls the appropriate function

        if self.first_word in self.menu_keywords:
            self.menu_commands(action)

        elif self.first_word in self.movement_keywords:
            self.move_parse(self.split_command)

        elif self.first_word in self.inventory_keywords:
            self.inventory_parse(self.split_command)
        elif self.first_word in self.look_keywords:
            self.look_parse(self.split_command)
        # that was the easy part, since they use predictable verbs

        else:
            self.use_words = self.use_words_lookup()
            if self.first_word in self.use_words:
                self.use_parse(self.split_command)
            else:
                print(PARSE_FAIL_TEXT)

    def use_words_lookup(self):
        self.use_words = ['use']
        for label, item in self.player.can_see().items():
            if item.use_words:
                for word in item.use_words:
                    self.use_words.append(word)
        return self.use_words

    def look_parse(self, command):
        self.command = command

        if len(self.command) == 1:
            # single-word phrases that trigger the look parser, like "look"
            # and "search" will print the location's full description
            self.player.location.describe_verbose()

        else:
            self.looked_at = self.mentioned_in(
                self.command, self.player.can_see()
            )

            if self.looked_at.label != 'not_found':
                print(colored(self.looked_at.description, "blue"))
            else:
                print(
                    colored("You don't see anything like that here.", 'red')
                )

            if self.looked_at.look_special == 'yes':
                self.player.look_special(self.looked_at)

    def move_parse(self, command):
        self.command = command
        self.exit_to_try = self.mentioned_in(
            self.command, self.player.location.exits
        )

        self.player.move(self.exit_to_try)
        self.move_into(self.player.new_location)

    def use_parse(self, command):
        """This is triggered if the command starts
            with a possible use word.
        """
        self.command = command
        self.use_item = self.mentioned_in(self.command, self.player.can_see())

        if self.use_item.label == "not_found":
            print(colored("You don't see any way to do that.", "red"))
        else:
            self.player.use(self.use_item)

    def mentioned_in(self, command, items_to_search):
        """
        to use on both exits and items
        takes a command (from the user, split into words)
        and a dictionary of either exits or items
        checks to see if the command contains any of the keywords
        attached to the items in the dictionary
        if successful, returns the mentioned item
        if not, returns the dummy item "not_found"
        """

        self.command = command
        self.items_to_search = items_to_search
        self.success = False

        for i, item in self.items_to_search.items():
            for word in self.command:
                if word in item.keywords:
                    self.exit_to_try = item
                    self.success = True

        if self.success:
            return self.exit_to_try
        else:
            return self.map.all_exits["not_found"]

    def simulate_play(self, command_list):
        """For debugging purposes,
            takes a list of commands and parses them in order.
        """

        self.command_list = command_list
        for command in self.command_list:
            self.parse(command)

    @staticmethod
    def victory():
        print(VICTORY_MESSAGE)
        exit(1)
