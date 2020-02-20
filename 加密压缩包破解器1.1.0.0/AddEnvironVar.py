# %% 导入包
from os import path, environ, pathsep
import sys


# %% 添加Qt环境变量
def _append_run_path():
    """
    添加Qt的环境变量\n
    :return:
    """
    if getattr(sys, 'frozen', False):
        path_list = [sys._MEIPASS]
        _main_app_path = path.dirname(sys.executable)
        path_list.append(_main_app_path)
        environ["PATH"] += pathsep + pathsep.join(path_list)
    # print("PATH:", environ['PATH'])


# %% 添加unrar的环境变量
def _append_unrar(filename="UnRAR64.dll"):
    """
    添加unrar的环境变量\n
    :param filename: 文件名，默认UnRAR64.dll
    :return:
    """
    dll_path = "\\".join((sys.path[0], filename))
    environ["UNRAR_LIB_PATH"] = dll_path
    # print("UNRAR_LIB_PATH:", environ["UNRAR_LIB_PATH"])


# %% 添加环境变量
_append_run_path()
_append_unrar()
