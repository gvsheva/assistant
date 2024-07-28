import argparse
import atexit
import cmd
from functools import wraps
import os
from pathlib import Path
import readline
import shelve
import shlex
import sys
from typing import Callable

from assistant.model import Contact
from assistant.model import Name
from assistant.model import Phone
from assistant.model import PhoneType
from assistant.model import PhoneValue


def error(msg):
    print(msg, file=sys.stderr)


def confirm(prompt):
    while True:
        try:
            response = input(prompt + " [y/n] ").strip().lower()
        except EOFError:
            response = "n"
        if response in {"y", "n"}:
            return response == "y"


class ArgumentError(ValueError):
    def __init__(self, message: str, help: str):
        super().__init__(message)
        self.help = help


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentError(message, self.format_help())


class Cmd(cmd.Cmd):
    confirm_exit = True
    say_goodbye = True

    def do_exit(self, arg):
        """
        Exit the application
        """
        if self.confirm_exit:
            if confirm("Exit the application?"):
                self.goodbye()
                return True
            return
        self.goodbye()
        return True

    def do_EOF(self, arg):
        """
        Exit the application
        """
        return self.do_exit(arg)

    def cmdloop(self, intro=""):
        if intro:
            print(intro)
        self.do_help("")
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print("^C")
                if readline.get_line_buffer() == "" and confirm("Exit the application?"):
                    break

    def goodbye(self):
        if self.say_goodbye:
            print("Goodbye!")
        else:
            print("")


def handle_error(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ArgumentError as ex:
            error(str(ex))
            error(ex.help)
        except ValueError as ex:
            error(str(ex))
    return wrapper


class ContactsCmd(Cmd):
    confirm_exit = False
    say_goodbye = False

    _add_parser: ArgumentParser
    _edit_parser: ArgumentParser
    _delete_parser: ArgumentParser
    _wipe_parser: ArgumentParser

    def __init__(self, contacts_db: shelve.Shelf):
        super().__init__()
        self._contacts_db = contacts_db

        self._add_parser = ArgumentParser(
            "add", add_help=False)
        self._add_parser.add_argument(
            "name", type=Name, help="Name of the contact")
        self._add_parser.add_argument(
            "phone", type=PhoneValue, help="Phone number of the contact (XXXXXXXXXX)")
        self._add_parser.add_argument("--type", type=PhoneType, default=PhoneType.MOBILE,
                                      help="Type of the phone number (home, mobile, work)")

        self._edit_parser = ArgumentParser(
            "edit", add_help=False)
        self._edit_parser.add_argument(
            "name", type=Name, help="Name of the contact")
        self._edit_parser.add_argument(
            "index", type=int, help="Index of the phone number to edit")
        self._edit_parser.add_argument(
            "--phone", type=PhoneValue, default=None, help="Phone number of the contact (XXXXXXXXXX)")
        self._edit_parser.add_argument(
            "--type", type=PhoneType, default=None, help="Type of the phone number (home, mobile, work)")

        self._delete_parser = ArgumentParser(
            "delete", add_help=False)
        self._delete_parser.add_argument(
            "name", type=Name, help="Name of the contact to delete")
        self._delete_parser.add_argument(
            "index", type=int, help="Index of the phone number to delete")
        self._delete_parser.add_argument(
            "-f", "--force", action="store_true", help="Force deletion of the contact")

        self._wipe_parser = ArgumentParser(
            "wipe", add_help=False)
        self._wipe_parser.add_argument(
            "-f", "--force", action="store_true", help="Force deletion of all contacts")

    @handle_error
    def do_add(self, arg):
        """
        Add a new contact
        """
        args = self._add_parser.parse_args(shlex.split(arg))
        contact = self._contacts_db.get(args.name, None)
        if contact is None:
            contact = Contact(args.name)
        contact.add_phone(Phone(args.phone, args.type))
        self._contacts_db[args.name] = contact
        print(f"New phone number {args.phone} has been added to {args.name}")

    def help_add(self):
        print(self._add_parser.format_help())

    @handle_error
    def do_edit(self, arg):
        """
        Edit an existing contact
        """
        args = self._edit_parser.parse_args(shlex.split(arg))
        if args.name not in self._contacts_db:
            error(f"Contact {args.name} does not exist")
            return
        contact = self._contacts_db[args.name]
        if args.index >= len(contact.phones):
            error(f"Phone number index {args.index} out of range")
            return
        updated = False
        if args.phone is not None:
            contact.phones[args.index].phone = args.phone
            updated = True
        if args.type is not None:
            contact.phones[args.index].type = args.type
            updated = True
        if updated:
            self._contacts_db[args.name] = contact
            print(f"Updated {args.name}")
        else:
            print(f"Nothing to update for {args.name}")

    def help_edit(self):
        print(self._edit_parser.format_help())

    @handle_error
    def do_delete(self, arg):
        """
        Delete a contact
        """
        args = self._delete_parser.parse_args(shlex.split(arg))
        if args.name not in self._contacts_db:
            error(f"Contact {args.name} does not exist")
            return
        if not args.force and not confirm(f"Are you sure you want to delete a phone number from {args.name}?"):
            return
        contact = self._contacts_db[args.name]
        if args.index >= len(contact.phones):
            error(f"Phone number index {args.index} out of range")
            return
        del contact.phones[args.index]
        if not contact.phones and args.force or confirm(f"Delete {args.name} completely?"):
            del self._contacts_db[args.name]
        else:
            self._contacts_db[args.name] = contact
        print(f"Deleted {args.name}")

    def help_delete(self):
        print(self._delete_parser.format_help())

    def do_list(self, arg):
        """
        List all contacts
        """
        for name, record in self._contacts_db.items():
            print(f"{name}:")
            for i, phone in enumerate(record.phones):
                print(f"  {i}: {phone}")

    @handle_error
    def do_wipe(self, arg):
        """
        Delete all contacts
        """
        args = self._wipe_parser.parse_args(shlex.split(arg))
        if not args.force and not confirm("Are you sure you want to delete all contacts?"):
            return
        self._contacts_db.clear()
        print("All contacts deleted")

    def help_wipe(self):
        print(self._wipe_parser.format_help())


class AssistantApp(Cmd):
    def __init__(
            self,
            contacts_cmd: ContactsCmd,
    ):
        super().__init__()
        self.contacts_cmd = contacts_cmd

    def do_hello(self, arg):
        """
        Say hello
        """
        print("Hello!")

    def do_contacts(self, arg):
        """
        Manage contacts
        """
        self.contacts_cmd.prompt = self.prompt + "contacts> "
        if arg:
            self.contacts_cmd.onecmd(arg)
        else:
            self.contacts_cmd.cmdloop()

    def help_contacts(self):
        print("Manage contacts")
        print(self.contacts_cmd.do_help(""))

    def complete_contacts(self, text, line, begidx, endidx):
        return self.contacts_cmd.completenames(text)


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
    init_file = Path(os.environ.get("ASSISTANT_INIT_FILE", ".assistant_init"))
    read_init_file(init_file)

    history_file = Path(os.environ.get(
        "ASSISTANT_HISTORY_FILE", ".assistant_history"))
    read_history(history_file)
    atexit.register(write_history, history_file)

    dbdir = Path(os.environ.get("ASSISTANT_DB_DIR", "."))
    contacts_db = shelve.open(str(dbdir / "contacts"))
    atexit.register(contacts_db.close)

    contacts_cmd = ContactsCmd(contacts_db)
    app = AssistantApp(
        contacts_cmd,
    )
    app.prompt = f"hello, {os.environ.get('USER', 'user')} > "
    if len(sys.argv) > 1:
        app.onecmd(shlex.join(sys.argv[1:]))
    else:
        app.cmdloop("Welcome to the assistant app!")
