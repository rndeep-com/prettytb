# -*- coding: utf-8 -*-
"""
    `logexc` catches and logs exceptions.

    It is primarily used as a decorator.

    Example:
        >>> @logexc()
        >>> def funcA():
        >>>     a = 1
        >>>     funcB()
        >>> def funcB():
        >>>     b = 'two'
        >>>     funcC()
        >>> def funcC():
        >>>     c = [3]
        >>>     1/0
        >>> funcA()

        The code above will result in a logged output like this:

          File "file.py", line 1, in funcA
            funcB()

            a = 1
            funcB = <function funcB at 0x00000000028364A8>

          File "file.py", line 3, in funcB
            funcC()

            b = 'two'
            funcC = <function funcC at 0x0000000002836518>

          File "file.py", line 6, in funcC
            1/0

            c = [3]

        ZeroDivisionError: integer division or modulo by zero

    Function/Decorator/:
        `logexc` can be used in 3 different ways.

        1. As a function call
        >>> try:
        >>>     raise TypeError("Hello")
        >>> except TypeError as exc:
        >>>     logexc(exc)

        2. As a decorator
        >>> @logexc()
        >>> def my_func():
        >>>     raise TypeError("Hello")

        3. As a with-statement context:
        >>> with logexc():
        >>>    raise TypeError("Hello")

    The `examples` directory shows how
    exception handling can be further customized.

    Note:
        Although `logexc` is a class, it is not written in Pascal case.
        The reason is that from a programmer's perspective
        it is used like a decorator or a function and not like class
        that must be instantiated.

    Todo:
        * In some situations the first frame is not skipped although it should be.
"""

import sys
import types
import functools
from builtins import str
from . _error_report import get_error_report
from . _inject_colors import inject_colors

try:
    # py2
    func_types = (types.FunctionType, types.MethodType, types.UnboundMethodType, types.LambdaType)
except AttributeError:
    # py3
    func_types = (types.FunctionType, types.MethodType, types.LambdaType)


class logexc(object):
    """ Decorator & function which creates error reports. """

    def __init__(self, target=Exception, log_func=None, exception_type=Exception, raises=False):
        """
            Arguments:
                You can supply your own logging function using `log_func`. By default
                logging will go to `sys.stderr`.

                When used as a function call on an exception instance,
                the `exception_type` can be used to specify a exception class to catch.
                Otherwise the class is defined by `target`.

                `raises` will re-raise the error after the error report has been printed.
        """

        self._target = target
        self._log_func = self.default_log_func if log_func is None else log_func
        self._exception_type = exception_type
        self._raises = raises
        self._mode = self._get_mode()

        if self._mode == "call":
            self._handle_exception(self._target)

    def handle_error_report(self, exception, error_message, error_report):
        """ Injects colors into `error_report` if enabled and then logs it. """

        if self.colors_supported():
            error_report = inject_colors(error_report)
        for line in error_report.split('\n'):
            self._log_func(line)


    def colors_supported(self):
        """ Checks if colored output is available in the current environment. """

        try:
            self._init_colorama()
        except Exception:
            # 'colorama' is either not installed or not working in the current environment.
            # So we turn colored output off for now.
            return False
        return True

    def _get_mode(self):
        """ Determines the internal mode, based on what kind of object `target` was. """
        if isinstance(self._target, Exception):
            return "call"

        elif isinstance(self._target, func_types):
            return "function_wrap"

        elif issubclass(self._target, Exception):
            return "with_statement"

        return "decorator"

    def _handle_exception(self, exception):
        """
            Generates an error report and forwards it to `handle_error_report`.
            If an additional error occurs it will be caught.
        """

        error_message = "{exc.__class__.__name__}: {exc}".format(exc=exception)

        # When wrapping functions, the first frame of the exception info is obsolete.
        skip_frames = 1 if self._mode in ["function_wrap"] else 0

        try:
            error_report = get_error_report(exception, skip_frames=skip_frames)
            self.handle_error_report(exception, error_message, error_report)

        except Exception as exc:
            message = "{exc.__class__.__name__}: {exc} [{original_error_message}]".format(exc=exc, original_error_message=error_message)
            self._log_func("Error generating error report.")
            self._log_func(message)

    def _init_colorama(self):
        import colorama
        colorama.init()

    def default_log_func(self, *args):
        """
            If the user didn't supply his/her own logging function,
            this output all logging to stdout.
        """

        args_unicode = map(str, args)
        message = u" ".join(args_unicode)
        sys.stderr.write(u"\n{0}".format(message))

    # Special Methods
    def __call__(self, *decorator_args, **decorator_kwargs):
        """ `__call__` enables using this class as a decorator. """

        if self._mode in ("decorator", "with_statement"):
            return self._call_decorator_with_stmt(decorator_args)

        elif self._mode == "function_wrap":
            return self._call_function_wrap(decorator_args, decorator_kwargs)

        raise NotImplementedError(self._mode)

    def _call_decorator_with_stmt(self, decorator_args):
        """ When used as a decorator and the decorated function is being called. """

        function_or_class = decorator_args[0]
        @functools.wraps(function_or_class)
        def wrapped_fn(*a, **kwa):
            try:
                return function_or_class(*a, **kwa)
            except self._target as exc:
                self._handle_exception(exc)
                if self._raises:
                    raise exc
        return wrapped_fn

    def _call_function_wrap(self, decorator_args, decorator_kwargs):
        try:
            return self._target(*decorator_args, **decorator_kwargs)
        except self._exception_type as exc:
            self._handle_exception(exc)
            if self._raises:
                raise exc

    def __enter__(self):
        """ This method is required for the 'with' statement context. """
        return None

    def __exit__(self, exception_type, exception, traceback):
        if isinstance(exception, self._target):
            self._handle_exception(exception)
            if self._raises:
                raise exception
            return True
        return False


def main():
    """ Example usage. """

    import prettytb

    @prettytb.logexc()
    def funcA():
        a = 1
        funcB()
    def funcB():
        b = 'two'
        funcC()
    def funcC():
        c = [3]
        1/0

    funcA()

if __name__ == "__main__":
    main()

