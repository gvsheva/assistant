from datetime import date
from datetime import timedelta
import shlex

from assistant.common import Cmd
from assistant.common import CmdArgumentParser
from assistant.common import confirm
from assistant.common import error
from assistant.model import Birthday
from assistant.model import Name
from assistant.model import Record
from assistant import repos


class Birthdays(Cmd):
    confirm_exit = False
    say_goodbye = False

    _set_parser: CmdArgumentParser
    _show_parser: CmdArgumentParser
    _clear_parser: CmdArgumentParser

    def __init__(self, addressbook: repos.Repo[Record], yes: bool):
        super().__init__()
        self._addressbook = addressbook
        self._yes = yes

        self._set_parser = CmdArgumentParser("set", add_help=False)
        self._set_parser.add_argument(
            "name", type=Name, help="Name of the record")
        self._set_parser.add_argument(
            "birthday", type=Birthday, help="Birthday of the record (YYYY.MM.DD)")

        self._show_parser = CmdArgumentParser("show", add_help=False)
        self._show_parser.add_argument(
            "name", type=Name, help="Name of the record")

        self._clear_parser = CmdArgumentParser("clear", add_help=False)
        self._clear_parser.add_argument(
            "name", type=Name, help="Name of the record to clear birthday")

    def do_set(self, arg):
        """
        Set birthday to a record, create one if it doesn't exist
        """
        args = self._set_parser.parse_args(shlex.split(arg))
        record = self._addressbook.get(args.name)
        if record is None:
            record = Record(args.name)
        record.set_birthday(args.birthday)
        self._addressbook.set(args.name, record)
        print(f"Birthday has been added to record {args.name}")

    def help_set(self):
        print(self._set_parser.format_help())

    def do_show(self, arg):
        """
        Show birthday of a record
        """
        args = self._show_parser.parse_args(shlex.split(arg))
        record = self._addressbook.get(args.name)
        if record is None:
            error(f"Record {args.name} does not exist")
            return
        if record.birthday is None:
            print(f"{args.name} has no birthday")
        else:
            print(
                f"{args.name} was born on {record.birthday.birthday.strftime('%Y.%m.%d (%A)')}")

    def help_show(self):
        print(self._show_parser.format_help())

    def do_clear(self, arg):
        """
        Clear birthday from a record
        """
        args = self._clear_parser.parse_args(shlex.split(arg))
        record = self._addressbook.get(args.name)
        if record is None:
            error(f"Record {args.name} does not exist")
            return
        if not self._yes and not confirm(f"Are you sure you want to clear birthday from {args.name}?"):
            return
        record.clear_birthday()
        self._addressbook.set(args.name, record)
        print(f"Birthday has been cleared from record {args.name}")

    def help_clear(self):
        print(self._clear_parser.format_help())

    def do_upcoming(self, arg):
        """
        Show upcoming birthdays
        """
        current_date = date.today()
        for name, record in self._addressbook.items():
            if record.birthday is None:
                continue
            congratulation_date = _get_congratulation_date(
                record.birthday.birthday, current_date.year)
            if congratulation_date < current_date:
                continue
            print(f"{name} was born on {record.birthday.birthday.strftime('%Y.%m.%d (%A)')}, "
                  f"congratulations on {congratulation_date.strftime('%Y.%m.%d (%A)')}")


def _get_congratulation_date(birthdate: date, _current_year: int):
    birthday = date(_current_year, birthdate.month, birthdate.day)
    weekday = birthday.weekday()
    if 0 <= weekday < 5:
        return birthday
    return date(_current_year, birthdate.month, birthday.day) + timedelta(days=(7 - weekday))
