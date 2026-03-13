# src/codebase_kg/cli/cli.py
import click
from pathlib import Path
from dotenv import load_dotenv

from codebase_kg.infra_setup.neo4j_driver import Neo4jService
from codebase_kg.infra_setup.github_service import GithubService

# Load .env from project root
load_dotenv(Path(__file__).resolve().parents[3] / ".env")


@click.group()
def cli():
    """Knowledge Graph Tools CLI."""
    pass


# ----------------------------
# Neo4j test command
# ----------------------------
@cli.command("neo4j")
@click.option("--uri", envvar="NEO4J_URI", default="neo4j://127.0.0.1:7687")
@click.option("--user", envvar="NEO4J_USER")
@click.option("--password", envvar="NEO4J_PASSWORD")
@click.option("--database", envvar="NEO4J_DATABASE", default="neo4j")
def neo4j_test(uri, user, password, database):
    """Test Neo4j connectivity."""
    click.echo("\nNeo4j Connectivity Test")
    click.echo("----------------------")

    if not user or not password:
        click.secho("❌ NEO4J_USER or NEO4J_PASSWORD not set", fg="red")
        return

    service = Neo4jService(uri, user, password)
    try:
        service.verify_connectivity()
        info = service.get_db_info(database)
        click.secho("✔ Connection successful", fg="green")
        click.echo(f"{info['component']} version {info['version']} ({info['edition']})")
    except Exception as e:
        click.secho("❌ Connection failed", fg="red")
        click.echo(e)
    finally:
        service.close()


# ----------------------------
# GitHub test command
# ----------------------------
@cli.command("github")
@click.option("--token", envvar="GITHUB_TOKEN", help="GitHub personal access token")
def github_test(token):
    """Test GitHub connectivity."""
    click.echo("\nGitHub Connectivity Test")
    click.echo("------------------------")

    if not token:
        click.secho("❌ GITHUB_TOKEN not set", fg="red")
        return

    try:
        service = GithubService(token)
        info = service.test_connection()
        click.secho("✔ Connection successful", fg="green")
        click.echo(f"Login: {info['login']}")
        click.echo(f"Name: {info['name']}")
        click.echo(f"Public repos: {info['public_repos']}")
        click.echo(f"Private repos: {info['private_repos']}")
    except Exception as e:
        click.secho("❌ Connection failed", fg="red")
        click.echo(e)


if __name__ == "__main__":
    cli()