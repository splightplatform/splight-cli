import click


class Printer:
    DEFAULT_COLOR = 'white'

    @staticmethod
    def print_dict(items, headers, items_colors=[]):
        format_str = "{:<50}" * len(headers)
        click.secho(format_str.format(*[h.upper() for h in headers]))
        for index, item in enumerate(items):
            try:
                fg = items_colors[index]
            except IndexError:
                fg = Printer.DEFAULT_COLOR
            click.secho(format_str.format(*[item.get(key) for key in headers]))

    @staticmethod
    def print_list(items, header=None, items_colors=[]):
        if header is not None:
            click.secho(header.upper())
        for index, item in enumerate(items):
            try:
                fg = items_colors[index]
            except IndexError:
                fg = Printer.DEFAULT_COLOR
            click.secho(item, fg=fg)
    
    @staticmethod
    def print_value(item, color=None):
        fg = color if color is not None else Printer.DEFAULT_COLOR
        click.secho(item, fg)

