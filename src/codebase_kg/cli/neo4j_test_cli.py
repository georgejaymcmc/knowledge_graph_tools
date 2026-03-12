import os
import time
from pathlib import Path

import click
from dotenv import load_dotenv
from neo4j import GraphDatabase


# --------------------------------------------------
# Load .env from project root
# --------------------------------------------------

env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)


# --------------------------------------------------
# Neo4j connection test
# --------------------------------------------------

def test_connection(uri, user, password, database):

    start = time.time()

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session(database=database) as session:

            result = session.run(
                """
                CALL dbms.components()
                YIELD name, versions
                RETURN name, versions[0] AS version
                """
            )

            for record in result:
                click.echo(f"Component: {record['name']}")
                click.echo(f"Version: {record['version']}")

            elapsed = round(time.time() - start, 3)

            click.secho("\n✔ Connection successful", fg="green", bold=True)
            click.echo(f"Database: {database}")
            click.echo(f"Component: {record['name']}")
            click.echo(f"Version: {record['version']}")
            click.echo(f"Latency: {elapsed}s\n")

    except Exception as e:

        click.secho("\n✘ Connection failed", fg="red", bold=True)
        click.echo(str(e))
        click.echo()

    finally:
        try:
            driver.close()
        except:
            pass


# --------------------------------------------------
# CLI
# --------------------------------------------------

@click.command()
@click.option(
    "--uri",
    envvar="NEO4J_URI",
    default="neo4j://127.0.0.1:7687",
    show_default=True,
    help="Neo4j connection URI",
)
@click.option(
    "--user",
    envvar="NEO4J_USER",
    help="Neo4j username",
)
@click.option(
    "--password",
    envvar="NEO4J_PASSWORD",
    help="Neo4j password",
)
@click.option(
    "--database",
    envvar="NEO4J_DATABASE",
    default="neo4j",
    show_default=True,
    help="Neo4j database name",
)
def cli(uri, user, password, database):
    """
    Test connectivity to a Neo4j instance.
    """

    click.echo("\nNeo4j Connection Test")
    click.echo("---------------------")

    click.echo(f"URI: {uri}")
    click.echo(f"User: {user}")
    click.echo(f"Database: {database}")

    if not user or not password:
        click.secho(
            "\nMissing credentials. Ensure NEO4J_USER and NEO4J_PASSWORD exist in .env",
            fg="red",
        )
        return

    test_connection(uri, user, password, database)


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    cli()