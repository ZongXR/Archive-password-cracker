# %% 导入包
from os import cpu_count
from sys import argv, exit
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QSlider, QHBoxLayout, QCheckBox, \
    QSpinBox, QLineEdit, QTabWidget, QToolButton, QLCDNumber, QProgressBar, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QFileInfo, QDir
from ExportDict import ExportDict
from CrackPassword import CrackPassword
from AboutDialog import AboutDialog
# noinspection PyArgumentList


# %% 主窗口类
class MainWindow(QMainWindow):
    """
    主窗口类
    """
    # 定义一些常量
    WARNING = "警告"
    INFO = "提示"
    SELECT_BOOLEAN = "请至少勾选一项"
    SELECT_EXPORT_PATH = "请选择字典导出路径"
    SELECT_ZIPFILE_PATH = "请选择压缩文件路径"
    SELECT_EXTRACT_PATH = "请选择解压路径"
    SELECT_DICT_PATH = "请选择字典路径"
    SUPPORTED_FILE_TYPES = ["zip", "rar"]
    UNSUPPORTED_FILE_TYPES = "不支持的文件格式，目前仅支持%s文件" % ', '.join(SUPPORTED_FILE_TYPES)
    EXPORT_COMPLETED = ExportDict.EXPORT_COMPLETED
    FILE_FILTER_TXT = "文本文件 (*.txt);;全部文件 (*)"
    FILE_FILTER_ZIP = "{0}压缩文件 (*.{0});;{1}压缩文件 (*.{1})".format(*SUPPORTED_FILE_TYPES)
    START_CRACK = "开始破解"
    STOP_CRACK = "停止破解"
    START_EXPORT = "开始导出"
    STOP_EXPORT = "停止导出"

    # 定义控件
    cpu_slider: QSlider                 # 用于控制核心数的滑动条
    check_boxes: QHBoxLayout            # 最上面的复选框组
    checkBox_num: QCheckBox             # 是否包含数字复选框
    checkBox_lower_letter: QCheckBox    # 是否包含小写字母复选框
    checkBox_upper_letter: QCheckBox    # 是否包含大写字母复选框
    checkBox_symbols: QCheckBox         # 是否包含特殊符号复选框
    digit_min: QSpinBox                 # 最低位数调节框
    digit_max: QSpinBox                 # 最高位数调节框
    export_path: QLineEdit              # 导出字典路径输入框
    zipfile_path: QLineEdit             # 压缩文件路径输入框
    extract_path: QLineEdit             # 解压路径输入框
    dict_path: QLineEdit                # 外部字典路径输入框
    password: QLineEdit                 # 显示密码输入框
    dict_source: QTabWidget             # 选择内部字典还是外部字典选项卡框
    button_export_path: QToolButton     # 选择导出字典路径按钮
    button_zipfile_path: QToolButton    # 选择压缩文件按钮
    button_extract_path: QToolButton    # 选择解压路径按钮
    button_dict_path: QToolButton       # 选择外部字典按钮
    core_num: QLCDNumber                # 显示使用核心数的LCD控件
    batch_size: QLCDNumber              # 显示批量处理大小的LCD控件
    progress_export: QProgressBar       # 显示导出字典的进度
    progress_crack: QProgressBar        # 显示破解进度
    button_crack: QPushButton           # 开始破解按钮
    button_export: QPushButton          # 导出字典按钮

    def __init__(self, parent=None):
        """
        构造方法\n
        :param parent: None
        """
        super().__init__(parent)
        loadUi("UI/MainWindow.ui", self)
        # 设置进程数
        self.cpu_slider.setMaximum(cpu_count())
        self.cpu_slider.setValue(cpu_count())
        # 将最上面的几个check_box的点击信号连接到槽
        for i in range(self.check_boxes.count()):
            self.check_boxes.itemAt(i).widget().clicked.connect(self.validate_bool)
        # 初始化导出字典功能的线程
        self.export_dict_thread = None
        self.export_dict_thread: ExportDict
        # 初始化破解字典的进程
        self.password_cracker = None
        self.password_cracker: CrackPassword
        # 初始化破解按钮
        self.button_crack.setText(self.START_CRACK)
        # 初始化导出按钮
        self.button_export.setText(self.START_EXPORT)
        # 初始化关于对话框
        self.about_dlg = None
        # 显示
        self.show()

    @pyqtSlot()
    def validate_bool(self) -> (bool, ):
        """
        验证上方的几个复选框符合规则的槽函数，至少由一个勾选\n
        :return: 一个由bool组成的数组，分别对应着几个勾选情况
        """
        # 如果全为False，验证不通过
        if not any(self.get_seed_selection()):
            QMessageBox().warning(self, MainWindow.WARNING, MainWindow.SELECT_BOOLEAN, QMessageBox.Ok)
            self.sender().setChecked(True)
        return self.get_seed_selection()

    def get_seed_selection(self) -> (bool, ):
        """
        获取最上方几个复选框的勾选情况\n
        :return: 一个由bool组成的数组，分别对应着几个勾选情况
        """
        return (self.checkBox_num.isChecked(),
                self.checkBox_lower_letter.isChecked(),
                self.checkBox_upper_letter.isChecked(),
                self.checkBox_symbols.isChecked())

    def get_range(self) -> range:
        """
        获取位数范围\n
        :return: 位数范围，range类型
        """
        digit1 = self.digit_min.value()
        digit2 = self.digit_max.value()
        return range(min(digit1, digit2), max(digit1, digit2) + 1)

    @classmethod
    def check_supported_types(cls, zipfile_path: str) -> bool:
        """
        检查字符串是否是受支持的\n
        :param zipfile_path: 压缩文件路径字符串
        :return:
        """
        supported_types = ["." + x for x in cls.SUPPORTED_FILE_TYPES]
        for supported_type in supported_types:
            if zipfile_path.endswith(supported_type):
                return True
        return False

    def get_export_path(self) -> str:
        """
        获取导出字典的路径\n
        :return: 保存文件路径字符串
        """
        result = self.export_path.text()
        if result:
            return result
        elif self.dict_source.currentIndex() == 0:
            if QMessageBox().warning(
                self, MainWindow.WARNING, MainWindow.SELECT_EXPORT_PATH,
                QMessageBox.Ok | QMessageBox.Cancel
            ) == QMessageBox.Ok:
                self.button_export_path.click()

    def get_extract_path(self) -> str:
        """
        获取解压路径字符串\n
        :return: 解压路径字符串
        """
        result = self.extract_path.text()
        if QDir(result).exists():
            return result
        else:
            if QMessageBox().warning(
                self, MainWindow.WARNING, MainWindow.SELECT_EXTRACT_PATH,
                QMessageBox.Ok | QMessageBox.Cancel
            ) == QMessageBox.Ok:
                self.button_extract_path.click()

    def get_zipfile_path(self) -> str:
        """
        获取压缩文件路径\n
        :return: 压缩文件路径字符串
        """
        result = self.zipfile_path.text()
        # 如果编辑框不为空，且文件存在，且是受支持的文件格式：返回路径字符串
        if result and QFileInfo(result).isFile() and self.check_supported_types(result):
            return result
        # 如果文件存在，但不是受支持的文件格式：弹出对话框，不支持的文件格式
        elif QFileInfo(result).isFile() and (not self.check_supported_types(result)):
            if QMessageBox().warning(
                self, MainWindow.WARNING, MainWindow.UNSUPPORTED_FILE_TYPES,
                QMessageBox.Ok | QMessageBox.Cancel
            ) == QMessageBox.Ok:
                self.button_zipfile_path.click()
        # 如果编辑框为空，或文件不存在：弹出对话框，先选择压缩文件
        else:
            if QMessageBox().warning(
                self, MainWindow.WARNING, MainWindow.SELECT_ZIPFILE_PATH,
                QMessageBox.Ok | QMessageBox.Cancel
            ) == QMessageBox.Ok:
                self.button_zipfile_path.click()

    def get_dict_path(self) -> str:
        """
        获取外部字典文件路径\n
        :return:
        """
        result = self.dict_path.text()
        if result and QFileInfo(result).isFile():
            return result
        elif self.dict_source.currentIndex() == 1:
            if QMessageBox().warning(
                self, MainWindow.WARNING, MainWindow.SELECT_DICT_PATH,
                QMessageBox.Ok | QMessageBox.Cancel
            ) == QMessageBox.Ok:
                self.button_dict_path.click()

    @pyqtSlot()
    def select_export_path(self) -> str:
        """
        弹出保存路径对话框，选择文件保存路径，返回文件保存路径\n
        :return: 文件保存路径，字符串
        """
        file_path = QFileDialog().getSaveFileName(
            parent=self, caption=MainWindow.SELECT_EXPORT_PATH,
            filter=MainWindow.FILE_FILTER_TXT
        )
        self.export_path.setText(file_path[0])
        return file_path[0]

    @pyqtSlot()
    def on_export_dict(self):
        """
        导出字典的消息响应函数\n
        :return:
        """
        if self.export_dict_thread is None or self.export_dict_thread.isFinished():
            file_path = self.get_export_path()
            if file_path:
                digit_range = self.get_range()
                seed_selection = self.get_seed_selection()
                self.export_dict_thread = ExportDict(
                    "export dict thread", seed_selection, digit_range,
                    file_path, self.core_num.intValue(), self.batch_size.intValue()
                )
                # 同步更新进度条
                self.progress_export.setMaximum(self.export_dict_thread.get_batch_count() + 1)
                self.export_dict_thread.consuming_passwords_num.connect(self.on_consuming_passwords_num)
                # 同步更新状态栏
                self.export_dict_thread.producing_password.connect(self.on_exporting_dict)
                self.export_dict_thread.consuming_passwords.connect(self.on_exporting_dict)
                self.export_dict_thread.start()
                self.button_export.setText(self.STOP_EXPORT)
        else:
            self.export_dict_thread.stop()
            self.export_dict_thread = None
            self.button_export.setText(self.START_EXPORT)
            self.progress_export.setValue(self.progress_export.minimum())
            self.statusBar().showMessage("")

    @pyqtSlot(str)
    def on_exporting_dict(self, password: str):
        """
        生产者生成密码的槽函数\n
        :param password: 密码字符串
        :return:
        """
        self.statusBar().showMessage(password)

    @pyqtSlot(str)
    def on_cracking_passwords(self, passwords: str):
        """
        正在破解密码\n
        :param passwords: 正在处理的密码字符串
        :return:
        """
        self.statusBar().showMessage(passwords)
        # 密码破解成功
        if CrackPassword.CRACK_SUCCEED in passwords:
            password = passwords[len(CrackPassword.CRACK_SUCCEED):]
            self.password.setText(password)
            self.progress_crack.setValue(self.progress_crack.maximum())
            QMessageBox().information(
                self, MainWindow.INFO, passwords,
                QMessageBox.Ok
            )
        # 如果密码为空
        elif CrackPassword.NO_PASSWORD in passwords:
            self.progress_crack.setValue(self.progress_crack.maximum())
            self.password.setText("空")
            QMessageBox().information(
                self, MainWindow.INFO, CrackPassword.NO_PASSWORD,
                QMessageBox.Ok
            )
        # 如果没找到密码
        elif CrackPassword.CRACK_FAILED in passwords:
            self.progress_crack.setValue(self.progress_crack.maximum())
            self.password.setText("")
            QMessageBox().information(
                self, MainWindow.INFO, CrackPassword.CRACK_FAILED,
                QMessageBox.Ok
            )

    @pyqtSlot(int)
    def on_consuming_passwords_num(self, passwords_num: int):
        """
        消费者消费密码数量的槽函数\n
        :param passwords_num: 消费者消费密码数量
        :return:
        """
        self.progress_export.setValue(passwords_num)

    @pyqtSlot(int)
    def on_cracking_passwords_num(self, passwords_num: int):
        """
        破解密码的进度\n
        :param passwords_num: 破解密码的数量
        :return:
        """
        self.progress_crack.setValue(passwords_num)

    @pyqtSlot(int)
    def on_export_progress_changed(self, progress: int):
        """
        导出密码进度条的消息响应函数\n
        :param progress: 进度变量，int型
        :return:
        """
        if progress == self.progress_export.maximum():
            QMessageBox().information(self, MainWindow.INFO, MainWindow.EXPORT_COMPLETED, QMessageBox.Ok)
            self.button_export.setText(self.START_EXPORT)
            self.export_dict_thread.wait()
            self.export_dict_thread = None

    @pyqtSlot(int)
    def on_crack_progress_changed(self, progress: int):
        """
        破解密码的进度\n
        :param progress: 进度变量，int型
        :return:
        """
        if progress == self.progress_crack.maximum():
            self.button_crack.setText(self.START_CRACK)
            self.password_cracker.wait()
            self.password_cracker = None

    @pyqtSlot()
    def select_zipfile_path(self) -> str:
        """
        弹出选择文件对话框，选择压缩文件路径，返回压缩文件路径\n
        :return: 压缩文件路径，字符串
        """
        file_path = QFileDialog().getOpenFileName(
            parent=self, caption=MainWindow.SELECT_ZIPFILE_PATH,
            filter=MainWindow.FILE_FILTER_ZIP
        )
        self.zipfile_path.setText(file_path[0])
        return file_path[0]

    @pyqtSlot()
    def select_extract_path(self) -> str:
        """
        弹出解压路径对话框，选择解压路径，返回解压路径\n
        :return: 解压路径，字符串
        """
        extract_path = QFileDialog().getExistingDirectory(
            parent=self, caption=MainWindow.SELECT_EXTRACT_PATH
        )
        self.extract_path.setText(extract_path)
        return extract_path

    @pyqtSlot()
    def select_dict_path(self) -> str:
        """
        弹出选择字典对话框，选择外部字典，返回字典路径\n
        :return: 外部字典路径字符串
        """
        file_path = QFileDialog().getOpenFileName(
            parent=self, caption=MainWindow.SELECT_DICT_PATH,
            filter=MainWindow.FILE_FILTER_TXT
        )
        self.dict_path.setText(file_path[0])
        return file_path[0]

    @pyqtSlot()
    def on_crack_password(self):
        """
        开始破解压缩文件\n
        :return:
        """
        if self.password_cracker is None or self.password_cracker.isFinished():
            seed_selection = self.get_seed_selection()
            digit_range = self.get_range()
            dict_path = self.get_dict_path()
            consumer_number = self.core_num.intValue()
            batch_size = self.batch_size.intValue()
            dict_source = self.dict_source.currentIndex()
            zipfile_path = self.get_zipfile_path()
            extract_path = self.get_extract_path()
            if zipfile_path and extract_path:
                if dict_source == 0 or (dict_source == 1 and dict_path):
                    self.password_cracker = CrackPassword(
                        "password_crack", seed_selection, digit_range,
                        dict_path, consumer_number, batch_size, dict_source,
                        zipfile_path, extract_path
                    )
                    # 同步更新进度条
                    self.progress_crack.setMaximum(self.password_cracker.get_batch_count() + 1)
                    self.password_cracker.consuming_passwords_num.connect(self.on_cracking_passwords_num)
                    # 同步更新状态栏
                    self.password_cracker.producing_password.connect(self.on_cracking_passwords)
                    self.password_cracker.consuming_passwords.connect(self.on_cracking_passwords)
                    self.password_cracker.start()
                    self.button_crack.setText(self.STOP_CRACK)
        else:
            self.password_cracker.stop()
            self.button_crack.setText(self.START_CRACK)

    @pyqtSlot()
    def on_about(self):
        """
        点击关于软件，弹出关于界面\n
        :return:
        """
        self.about_dlg = AboutDialog(True)


# %% 运行
if __name__ == "__main__":
    app = QApplication(argv)
    w = MainWindow()
    exit(app.exec())
