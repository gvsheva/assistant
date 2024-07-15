# Simple notes application

## Installation

```sh
pip install dist/goit_pycore_hw_04_task_4-0.0.0a0.tar.gz
```

## Usage

You can use it in interactive mode just by typing `notes` in your terminal.

Another way is to use it with arguments:

```sh
notes help

```

For example, to add a contact:

```sh
notes contacts add "John Doe" 012-345-6789
```

## Run dev code

```sh
python -m notes
```

or with `poetry`:

```sh
poetry install
poetry run notes
```
