import click
import pkgutil
import importlib
from pathlib import Path
from dotenv import load_dotenv


# load .env
load_dotenv(Path(__file__).resolve().parents[3] / ".env")


@click.group()
def cli():
    """Knowledge Graph Tools CLI."""
    pass


def register_commands():

    package = "codebase_kg.cli.commands"

    for _, module_name, _ in pkgutil.iter_modules(
        importlib.import_module(package).__path__
    ):

        module = importlib.import_module(f"{package}.{module_name}")

        if hasattr(module, "command"):
            cli.add_command(module.command)


register_commands()


if __name__ == "__main__":
    cli()