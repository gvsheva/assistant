from collections import UserString
from datetime import datetime
from enum import StrEnum
import re


class ModelError(ValueError):
    ...


class InvalidNameError(ModelError):
    ...


class InvalidPhoneError(ModelError):
    ...


class InvalidBirthdayError(ModelError):
    ...


class Name(UserString):
    def __init__(self, name: str):
        if not name.strip():
            raise InvalidNameError("Name cannot be empty")
        super().__init__(name)


class PhoneValue(UserString):
    def __init__(self, phone: str):
        if not re.match(r"\d{10}", phone):
            raise InvalidPhoneError("Invalid phone number format")
        super().__init__(phone)


class PhoneType(StrEnum):
    HOME = "home"
    MOBILE = "mobile"
    WORK = "work"


class Phone:
    def __init__(self, phone: PhoneValue, type: PhoneType):
        self.phone = phone
        self.type = type

    def __str__(self):
        return f"{self.phone} ({self.type})"


class Birthday:
    def __init__(self, birthday: str):
        try:
            v = datetime.strptime(birthday, "%Y.%m.%d")
        except ValueError:
            raise InvalidBirthdayError("Invalid date format. Use DD.MM.YYYY")
        self.birthday = v

    def __str__(self):
        return f"{self.birthday}"


class Record:
    def __init__(self, name: Name, birthday: Birthday | None = None):
        self.name = name
        self.phones: list[Phone] = []
        self.birthday = birthday

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}"

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def edit_phone(self, index: int, phone: Phone):
        self.phones[index] = phone

    def delete_phone(self, index: int):
        del self.phones[index]

    def set_birthday(self, birthday: Birthday):
        self.birthday = birthday

    def clear_birthday(self):
        self.birthday = None
