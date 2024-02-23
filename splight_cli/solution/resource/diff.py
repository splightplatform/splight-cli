from typing import Dict

from colorama import Fore, Style

from splight_cli.solution.dict import get_dict_value, walk_dict


def strike_text(text):
    return "".join(["\u0336{}".format(c) for c in str(text)])


def Diff(new_arguments: Dict, old_arguments: Dict) -> Dict:
    # FIXME: this try catch mechanic could be simplified by improving
    # the 'Dict' related functions.

    # FIXME: Try replacing the QueryFilter in a function for a single value.
    # The diff will show incorrectly.
    diff = []
    for path, new_value in walk_dict(new_arguments):
        try:
            get_dict_value(path, old_arguments)
        except:
            line = f"\t{Fore.GREEN}+{Style.RESET_ALL} {'.'.join([str(key) for key in path])}: {new_value}"
            diff.append(line)
            continue

        old_value = get_dict_value(path, old_arguments)
        if new_value != old_value:
            line = f"\t{Fore.YELLOW}~{Style.RESET_ALL} {'.'.join([str(key) for key in path])}: {strike_text(old_value)} -> {new_value} "
            diff.append(line)

    for path, old_value in walk_dict(old_arguments):
        try:
            get_dict_value(path, new_arguments)
        except:
            line = f"\t{Fore.RED}-{Style.RESET_ALL} {'.'.join([str(key) for key in path])}: {strike_text(old_value)}"
            diff.append(line)

    return diff
