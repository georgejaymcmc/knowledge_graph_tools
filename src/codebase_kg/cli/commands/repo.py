import click
import inspect
import os

from codebase_kg.services.github_repo_service import GithubRepoService


@click.group("repo")
@click.argument("repository")
@click.pass_context
def command(ctx, repository):
    """
    Repository operations.

    Example:
        kgtools repo zotero/zotero description
    """

    if "/" not in repository:
        raise click.BadParameter("Repository must be owner/repo format")

    owner, repo = repository.split("/")

    ctx.ensure_object(dict)
    ctx.obj["owner"] = owner
    ctx.obj["repo"] = repo


def create_command(method_name):

    @click.command(method_name)
    @click.option("--token", envvar="GITHUB_TOKEN")
    @click.option("--output", default="repo_files.csv", help="Output CSV file")
    @click.pass_context
    def cmd(ctx, token, output):

        service = GithubRepoService(token)

        owner = ctx.obj["owner"]
        repo = ctx.obj["repo"]

        method = getattr(service, method_name)

        # pass output only if method supports it
        try:
            result = method(owner, repo, output_csv=output)
        except TypeError:
            result = method(owner, repo)

        if isinstance(result, dict):

            click.echo(f"\n{method_name.upper()}")
            click.echo("-" * len(method_name))

            for k, v in result.items():

                if k == "file_type_counts":
                    click.echo("\nFile Type Distribution:")
                    for ft, count in v.items():
                        click.echo(f"  {ft}: {count}")
                else:
                    click.echo(f"{k}: {v}")

        else:
            click.echo(result)

    return cmd


# Automatically expose service methods
for name, func in inspect.getmembers(GithubRepoService, inspect.isfunction):

    if not name.startswith("_"):

        command.add_command(create_command(name))

