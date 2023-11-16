import typer


def local_environment_context(ctx: typer.Context, local_dev: bool):
    if local_dev:
        db_client_mod = "splight_lib.client.database.LocalDatabaseClient"
        dl_client_mod = "splight_lib.client.datalake.LocalDatalakeClient"
        ctx.obj.workspace.settings.DATABASE_CLIENT = db_client_mod
        ctx.obj.workspace.settings.DATALAKE_CLIENT = dl_client_mod
