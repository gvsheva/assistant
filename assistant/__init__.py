from argparse import ArgumentParser
import atexit
import os
from pathlib import Path
import readline
import shelve
import shlex

from assistant.birthdays import Birthdays
from assistant.common import Cmd
from assistant.common import confirm
from assistant.phones import Phones


class AssistantApp(Cmd):
    def __init__(
            self,
            addressbook: shelve.Shelf,
            phones: Phones,
            birthdays: Birthdays,
            yes: bool,
    ):
        super().__init__()
        self._addressbook = addressbook
        self._phones = phones
        self._birthdays = birthdays
        self._yes = yes

    def do_hello(self, arg):
        """
        Say hello
        """
        print("Hello!")

    def do_list(self, arg):
        """
        List all records
        """
        for _, record in self._addressbook.items():
            print(f"{record.name}")

    def do_phones(self, arg):
        """
        Manage phone numbers
        """
        self._phones.prompt = self.prompt + "phones> "
        if arg:
            self._phones.onecmd(arg)
        else:
            self._phones.cmdloop()

    def help_phones(self):
        print("Manage phone numbers")
        print(self._phones.do_help(""))

    def complete_phones(self, text, line, begidx, endidx):
        return self._phones.completenames(text)

    def do_birthdays(self, arg):
        """
        Manage birthdays
        """
        self._birthdays.prompt = self.prompt + "birthdays> "
        if arg:
            self._birthdays.onecmd(arg)
        else:
            self._birthdays.cmdloop()

    def help_birthdays(self):
        print("Manage birthdays")
        print(self._birthdays.do_help(""))

    def complete_birthdays(self, text, line, begidx, endidx):
        return self._birthdays.completenames(text)

    def do_wipe(self, arg):
        """
        Delete all records
        """
        if not self._yes and not confirm("Are you sure you want to delete all records?"):
            return
        self._addressbook.clear()
        print("All records have been deleted")


def read_init_file(path: Path):
    try:
        readline.read_init_file(str(path))
    except FileNotFoundError:
        pass


def read_history(path: Path):
    try:
        readline.read_history_file(str(path))
    except FileNotFoundError:
        pass


def write_history(path: Path):
    readline.set_history_length(1000)
    readline.write_history_file(str(path))


def main():
    ap = ArgumentParser()
    ap.add_argument("-y", "--yes", action="store_true",
                    help="Answer yes to all questions")
    args, cmd_args = ap.parse_known_args()

    init_file = Path(os.environ.get("ASSISTANT_INIT_FILE", ".assistant_init"))
    read_init_file(init_file)

    history_file = Path(os.environ.get(
        "ASSISTANT_HISTORY_FILE", ".assistant_history"))
    read_history(history_file)
    atexit.register(write_history, history_file)

    dbdir = Path(os.environ.get("ASSISTANT_DB_DIR", "."))
    addressbook = shelve.open(str(dbdir / "addressbook"))
    atexit.register(addressbook.close)

    phones = Phones(addressbook, args.yes)
    birthdays = Birthdays(addressbook, args.yes)
    app = AssistantApp(
        addressbook,
        phones,
        birthdays,
        args.yes,
    )
    app.prompt = f"hello, {os.environ.get('USER', 'user')} > "
    if len(cmd_args) > 0:
        app.onecmd(shlex.join(cmd_args))
    else:
        app.cmdloop("Welcome to the assistant app!")
