import click
from codebase_kg.services.neo4j_service import Neo4jService


@click.command("neo4j")
@click.option("--uri", envvar="NEO4J_URI", default="neo4j://127.0.0.1:7687")
@click.option("--user", envvar="NEO4J_USER")
@click.option("--password", envvar="NEO4J_PASSWORD")
@click.option("--database", envvar="NEO4J_DATABASE", default="neo4j")
def command(uri, user, password, database):
    """Test Neo4j connectivity."""

    click.echo("\nNeo4j Connectivity Test")
    click.echo("----------------------")

    service = Neo4jService(uri, user, password)

    try:

        service.verify_connectivity()

        info = service.get_db_info(database)

        click.secho("✔ Connection successful", fg="green")

        click.echo(
            f"{info['component']} version {info['version']} ({info['edition']})"
        )

    except Exception as e:

        click.secho("❌ Connection failed", fg="red")

        click.echo(e)

    finally:

        service.close()