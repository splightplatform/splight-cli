import typer


def local_environment_context(ctx: typer.Context, local_dev: bool):
    if local_dev:
        db_client_mod = "splight_lib.client.database.LocalDatabaseClient"
        ctx.obj.workspace.settings.DATABASE_CLIENT = db_client_mod
