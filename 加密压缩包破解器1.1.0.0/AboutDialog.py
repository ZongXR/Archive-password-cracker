# %% 导入包
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from sys import argv, exit
# noinspection PyArgumentList


# %% 定义窗口类
class AboutDialog(QDialog):
    """
    关于窗口
    """
    def __init__(self, modal=True, parent=None):
        """
        构造函数\n
        :param parent: None
        """
        super().__init__(parent)
        loadUi("UI/AboutDialog.ui", self)
        self.setModal(modal)
        self.show()

    @staticmethod
    def on_to_url(self):
        """
        打开网址按钮的消息响应函数\n
        :return: None
        """
        QDesktopServices().openUrl(QUrl("https://github.com/GoogleLLP/Archive-password-cracker"))


if __name__ == "__main__":
    app = QApplication(argv)
    w = AboutDialog()
    exit(app.exec())
