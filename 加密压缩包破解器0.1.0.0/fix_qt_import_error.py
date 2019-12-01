# Fix qt import error
# Include this file before import PyQt5

from os import path, environ, pathsep
import sys


def _append_run_path():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        path_list = [sys._MEIPASS]

        # the application exe path
        _main_app_path = path.dirname(sys.executable)
        path_list.append(_main_app_path)

        # append to system path enviroment
        environ["PATH"] += pathsep + pathsep.join(path_list)

    print("current PATH: %s", environ['PATH'])


_append_run_path()