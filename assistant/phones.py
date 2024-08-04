import shelve
import shlex

from assistant.common import Cmd
from assistant.common import CmdArgumentParser
from assistant.common import confirm
from assistant.common import error
from assistant.model import Name
from assistant.model import Phone
from assistant.model import PhoneType
from assistant.model import PhoneValue
from assistant.model import Record
from assistant import repos


class Phones(Cmd):
    confirm_exit = False
    say_goodbye = False

    _add_parser: CmdArgumentParser
    _edit_parser: CmdArgumentParser
    _show_parser: CmdArgumentParser
    _delete_parser: CmdArgumentParser

    def __init__(self, addressbook: repos.Repo[Record], yes: bool):
        super().__init__()
        self._addressbook = addressbook
        self._yes = yes

        self._add_parser = CmdArgumentParser("add", add_help=False)
        self._add_parser.add_argument(
            "name", type=Name, help="Name of the record")
        self._add_parser.add_argument(
            "phone", type=PhoneValue, help="Phone number of the record (XXXXXXXXXX)")
        self._add_parser.add_argument("--type", type=PhoneType, default=PhoneType.MOBILE,
                                      help="Type of the phone number (home, mobile, work)")

        self._edit_parser = CmdArgumentParser("edit", add_help=False)
        self._edit_parser.add_argument(
            "name", type=Name, help="Name of the record")
        self._edit_parser.add_argument(
            "index", type=int, help="Index of the phone number to edit")
        self._edit_parser.add_argument(
            "--phone", type=PhoneValue, default=None, help="Phone number of the record (XXXXXXXXXX)")
        self._edit_parser.add_argument(
            "--type", type=PhoneType, default=None, help="Type of the phone number (home, mobile, work)")

        self._show_parser = CmdArgumentParser("show", add_help=False)
        self._show_parser.add_argument(
            "name", type=Name, help="Name of the record")

        self._delete_parser = CmdArgumentParser("delete", add_help=False)
        self._delete_parser.add_argument(
            "name", type=Name, help="Name of the record to delete a phone number from")
        self._delete_parser.add_argument(
            "index", type=int, help="Index of the phone number to delete")

    def do_add(self, arg):
        """
        Add a new phone number
        """
        args = self._add_parser.parse_args(shlex.split(arg))
        record = self._addressbook.get(args.name)
        if record is None:
            record = Record(args.name)
        record.add_phone(Phone(args.phone, args.type))
        self._addressbook.set(args.name, record)
        print(f"New phone number {args.phone} has been added to {args.name}")

    def help_add(self):
        print(self._add_parser.format_help())

    def do_edit(self, arg):
        """
        Edit an existing phone number
        """
        args = self._edit_parser.parse_args(shlex.split(arg))
        record = self._addressbook.get(args.name)
        if record is None:
            error(f"Record {args.name} does not exist")
            return
        if not (0 <= args.index < len(record.phones)):
            error(f"Phone number index {args.index} out of range")
            return
        updated = False
        if args.phone is not None:
            record.phones[args.index].phone = args.phone
            updated = True
        if args.type is not None:
            record.phones[args.index].type = args.type
            updated = True
        if updated:
            self._addressbook.set(args.name, record)
            print(f"Record {args.name} has been updated")
        else:
            print(f"Nothing to update for {args.name}")

    def help_edit(self):
        print(self._edit_parser.format_help())

    def do_show(self, arg):
        """
        Show all phone numbers for a record
        """
        args = self._show_parser.parse_args(shlex.split(arg))
        record = self._addressbook.get(args.name)
        if record is None:
            error(f"Record {args.name} does not exist")
            return
        if not record.phones:
            print(f"No phone numbers found for {args.name}")
        for i, phone in enumerate(record.phones):
            print(f"{i}: {phone}")

    def help_show(self):
        print(self._show_parser.format_help())

    def do_delete(self, arg):
        """
        Delete a phone number
        """
        args = self._delete_parser.parse_args(shlex.split(arg))
        record = self._addressbook.get(args.name)
        if record is None:
            error(f"Record {args.name} does not exist")
            return
        if not self._yes and not confirm(f"Are you sure you want to delete a phone number from {args.name}?"):
            return
        if not (0 <= args.index < len(record.phones)):
            error(f"Phone number index {args.index} out of range")
            return
        del record.phones[args.index]
        self._addressbook.set(args.name, record)
        print(f"Deleted {args.name}")

    def help_delete(self):
        print(self._delete_parser.format_help())
