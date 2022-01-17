from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)


def py_error_handler(filename, line, function, err, fmt):
    pass


c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)


@contextmanager
def hideAlsaErrors():
    """
    Context for disabling ALSA errors.
    :return:
    """
    sound = cdll.LoadLibrary('libasound.so')
    sound.snd_lib_error_set_handler(c_error_handler)
    yield
    sound.snd_lib_error_set_handler(None)