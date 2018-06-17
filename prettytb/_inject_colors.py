import re


REX_SOURCE_LINE = re.compile(r"""(^ *File ")([^"]*\.py)(", line )([0-9]+)(, in )(.*)""")


def inject_colors(error_report):
    """ Attempts to colorize `error_report` using colorama. """

    lines = error_report.split('\n')
    lines = _gen_inject_colors(lines)
    res = '\n'.join(lines)
    return res


def _gen_inject_colors(lines):
    """ Injects color into the given error report `lines`. """

    import colorama

    previous_was_source_line = False

    for i, line in enumerate(lines):
        # colorize some parts
        match = REX_SOURCE_LINE.match(line)
        if match:
            line_parts = list(match.groups())
            line_parts[1] = colorama.Style.BRIGHT + colorama.Back.GREEN + line_parts[1] + colorama.Style.RESET_ALL
            line_parts[3] = colorama.Style.BRIGHT + colorama.Fore.YELLOW + line_parts[3] + colorama.Style.RESET_ALL
            line_parts[5] = colorama.Style.BRIGHT + colorama.Fore.YELLOW + line_parts[5] + colorama.Style.RESET_ALL
            line = "".join(line_parts)
            previous_was_source_line = True

        elif i == len(lines)-2:
            line = colorama.Style.BRIGHT+colorama.Fore.RED + line + colorama.Style.RESET_ALL

        elif previous_was_source_line:
            line = colorama.Style.BRIGHT + colorama.Fore.RED + line + colorama.Style.RESET_ALL
            previous_was_source_line = False

        yield line

