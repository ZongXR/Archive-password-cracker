# %% 导入包
import AddEnvironVar
from PyQt5.QtWidgets import QApplication
from sys import argv, exit
from multiprocessing import freeze_support
from MainWindow import MainWindow


# %% 运行
if __name__ == "__main__":
    freeze_support()
    app = QApplication(argv)
    w = MainWindow()
    exit(app.exec())