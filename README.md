# Simple assistant application

## Installation

```sh
pip install dist/assistant-0.0.0a2.tar.gz
```

## Usage

You can use it in interactive mode just by typing `assistant` in your terminal.

Another way is to use it with arguments:

```sh
assistant help

```

For example, to add a contact:

```sh
assistant contacts add "John Doe" 012-345-6789
```

## Run dev code

```sh
python -m assistant
```

or with `poetry`:

```sh
poetry install
poetry run assistant
```
