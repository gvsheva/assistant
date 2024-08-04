# Simple assistant application

## Installation

```sh
pip install dist/assistant-0.0.0a6.tar.gz
```

## Usage

You can use it in interactive mode just by typing `assistant` in your terminal.

Another way is to use it with arguments:

```sh
assistant help

```

For example, to add a contact:

```sh
assistant phones add "John Doe" 0123456789 --type work
```

To set birthday:

```sh
assistant birthdays set "John Doe" 1990.01.01
```

To show upcoming birthdays:

```sh
assistant birthdays upcoming
```

or with `poetry`:

```sh
poetry install
poetry run assistant
```
