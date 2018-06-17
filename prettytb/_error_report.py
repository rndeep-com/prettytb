import sys
import types
import traceback
from pprint import pformat



def get_error_report(exception, **kwargs):
    """
        Extracts an error report from `exception` which is later
        used for logging.

        Note that exceptions can carry custom error reports if
        the magic `stored_report` attribute was set.
    """

    if hasattr(exception, "stored_report"):
        result = exception.stored_report
    else:
        if hasattr(exception, "exc_info"):
            kwargs["exception_info"] = exception.exc_info

        result = get_traceback(**kwargs)
        result += "\n{exc.__class__.__name__}: {exc}\n".format(exc=exception)
    return result


def get_traceback(limit=24, as_list=False, return_locals=True, exception_info=None, skip_frames=0):
    """
        Returns traceback string.
        Example of using get_traceback():

        try:
            1/0
        except Exception as exc:
            message = "{exc.__class__.__name__}: {exc}".format(exc=exc)
            print(message)
            print(get_traceback())
    """

    if exception_info is None:
        exception_info = sys.exc_info()

    exc_type, exc_value, exc_traceback = exception_info

    if return_locals:
        traceback_list = _extract_traceback_list(exc_traceback, limit)
        error_lines = traceback.format_list(traceback_list)
    else:
        error_lines = traceback.format_exception(exc_type, exc_value, exc_traceback, limit=limit)
    if as_list:
        return [line.rstrip() for line in error_lines][skip_frames:]
    else:
        return "\n".join(error_lines[skip_frames:])



def _extract_traceback_list(traceback_, limit=None):
    """
        Custom function to extract traceback information and local
        variables available in a frame.

        It is based on Python27/Lib/traceback.py -> extract_tb().
    """

    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    result = []
    n = 0
    while traceback_ is not None and (limit is None or n < limit):
        f = traceback_.tb_frame
        line_number = traceback_.tb_lineno
        code = f.f_code
        filename = code.co_filename
        name = code.co_name

        if filename.endswith("runpy.py") and name in ["_run_module_as_main", "_run_code"]:
            # if python runs the file as a module, skip the python module runner parts
            traceback_ = traceback_.tb_next
            continue

        traceback.linecache.checkcache(filename)
        line = traceback.linecache.getline(filename, line_number, f.f_globals)


        if line:
            line = line.strip()
            # Inject local variables
            sorted_vars = sorted(f.f_locals.items(), key=lambda t:tuple(t[0].lower()))
            line += "\n"
            for key, value in sorted_vars:
                # skip modules + internal vars
                if (key.startswith("__") and key.endswith("__")) or type(value) == types.ModuleType:
                    continue
                line += _get_variable_key_value_line(key, value)
        else:
            line = None
        result.append((filename, line_number, name, line))
        traceback_ = traceback_.tb_next
        n = n+1
    return result


def _get_variable_key_value_line(key, value):
    result = "\n"
    fallback_result = "\n    {0} = -Can't print value-".format(key)

    prefix_length = len("    {0} = ".format(key))
    try:
        value_formatted = _get_value_formatted(value, prefix_length)
        result += "    {0} = {1}".format(key, value_formatted)
    except Exception as exc:
        result = "{0} [{1}]".format(fallback_result, value.__class__.__name__)

    return result


def _get_value_formatted(value, prefix_length):
    if value.__class__.__name__ in ["WindowsPath"]:
        try:
            result = value.__repr__()
        except ValueError:
            # an old pathlib library will crash here with python 2.6 (<=nuke 7)
            result = "{0}({1!r})".format(value.__class__.__name__, value.as_posix())
    else:
        pformat_parts =     pformat(value, width=prefix_length).split("\n")
        pformat_parts[1:] = [ prefix_length * " "+part for part in pformat_parts[1:] ]
        result = "\n".join(pformat_parts)
    return result

