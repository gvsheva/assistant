import argparse
import cmd
import readline
import sys
from typing import Literal
from thefuzz import fuzz


def error(msg):
    print(msg, file=sys.stderr)


def confirm(prompt: str, default: Literal["y"] | Literal["n"] = "n"):
    while True:
        try:
            response = input(f"{prompt} [y/n] (default={default}): ").strip().lower() or default
        except EOFError:
            response = "n"
        if response in {"y", "n"}:
            return response == "y"


class CmdArgumentError(ValueError):
    def __init__(self, message: str, help: str):
        super().__init__(message)
        self.help = help


class CmdArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise CmdArgumentError(message, self.format_help())


class Cmd(cmd.Cmd):
    confirm_exit = True
    say_goodbye = True

    def _all_commands(self):
        return [name[3:] for name in dir(self) if name.startswith("do_")]

    def do_exit(self, arg):
        """
        Exit the application
        """
        if self.confirm_exit:
            if confirm("Exit the application?", "y"):
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
                if readline.get_line_buffer() == "" and confirm("Exit the application?", "n"):
                    break

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except CmdArgumentError as ex:
            error(str(ex))
            error(ex.help)
        except ValueError as ex:
            error(str(ex))

    def default(self, line):
        candidates = []
        for candidate in self._all_commands():
            rat = fuzz.ratio(candidate, line)
            if rat > 0:
                candidates.append((rat, candidate))
        if candidates:
            candidates.sort(reverse=True)
            error(f"Unknown command: {line}, did you mean {candidates[0][1]}?")
        else:
            error(f"Unknown command: {line}")

    def goodbye(self):
        if self.say_goodbye:
            print("Goodbye!")
        else:
            print("")
