import click


class Context:
    def __init__(self, namespace):
        self.namespace = namespace

    def __repr__(self):
        return f"<Context {self.namespace}>"


pass_context = click.make_pass_decorator(Context)