# %% 加载包
import fix_qt_import_error
from sys import argv, exit
from tools import write_dict, traverse_dict, generate_all_passwords, read_big_dict
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QButtonGroup, QLineEdit, QProgressBar
from PyQt5.uic import loadUi
# noinspection PyArgumentList


# %% 定义一个窗口类
class MainWindow(QMainWindow):
    """
    主窗口类，主界面窗口
    """
    # 初始化常量值
    WARNING = "警告"
    CRITICAL = "严重错误"
    INFORMATION = "提示"
    FILE_FILTER = "文本文件 (*.txt);;全部文件 (*)"
    ZIP_FILE = "zip压缩文件 (*.zip);;全部文件 (*)"
    SAVE_DICT_PATH = "请选择字典保存路径"
    SELECT_DICT_FILE = "请选择字典文件"
    SELECT_ZIP_FILE = "请选择压缩文件"
    SELECT_EXTRACT_DIR = "请选择解压路径"
    FOUND_PASSWORD = "找到了密码"
    NOT_FOUND_PASSWORD = "没找到密码"
    ENCOUNTER_ERROR = "遇到严重错误"
    NOT_FOUND_FILE = "没找到文件"
    UNSUPPORTED_FILE = "不支持的文件类型"
    USE_INTERNAL_DICT = 1
    USE_EXTERNAL_DICT = 2

    def __init__(self, parent=None):
        """
        初始化界面\n
        :param parent: QtWidgets 初始化主界面
        """
        super().__init__(parent)
        loadUi("mainUI.ui", self)
        # 将单选框分组
        self.select_dict = QButtonGroup(self)
        self.select_dict.addButton(self.radioButton_select_dict, MainWindow.USE_INTERNAL_DICT)
        self.select_dict.addButton(self.radioButton_customized_dict, MainWindow.USE_EXTERNAL_DICT)
        self.change_dict()
        # 初始化状态栏
        self.progress = QProgressBar(self.statusbar)
        self.progress.setFixedWidth(2 * self.progress.width())
        self.progress.setHidden(True)
        # 显示界面
        self.show()

    def get_file_path(self, line_edit: QLineEdit, func, prompt_text: str) -> str:
        """
        获取lineEdit控件内路径字符串，若字符串为空则调用旁边的选择路径按钮\n
        :param line_edit: QLineEdit 要获取路径字符串的控件
        :param func: 旁边选择路径按钮的消息响应函数
        :param prompt_text: str 提示文字字符串
        :return: str 控件内的路径字符串
        """
        result = line_edit.text()
        if result:
            return result
        else:
            flag = QMessageBox().warning(self, MainWindow.WARNING, prompt_text, QMessageBox.Ok | QMessageBox.Cancel)
            if flag == QMessageBox.Ok:
                result = func()
                if result:
                    return result
            raise TypeError

    def get_digit(self) -> (int, int):
        """
        获取位数取值范围\n
        :return: (int, int) 位数取值范围，闭区间，前后无大小关系
        """
        digit1_str = self.lineEdit_digit1.text()
        digit2_str = self.lineEdit_digit2.text()
        # 如果两个位数都为0，返回空值
        if len(digit1_str) + len(digit2_str) == 0:
            QMessageBox().warning(self, MainWindow.WARNING, "请输入密码位数", QMessageBox.Ok)
            return None
        # 如果两个位数有一个是0，返回仅有的那个数值
        elif len(digit1_str) * len(digit2_str) == 0:
            return int(max(digit1_str, digit2_str)), int(max(digit1_str, digit2_str))
        # 否则两个都不是0，返回int
        else:
            return int(digit1_str), int(digit2_str)

    def get_dict_bool(self) -> (bool, bool, bool, bool):
        """
        获取字典的可选项\n
        :return: (bool, bool, bool, bool) 四个复选框是否被选中
        """
        bool_num = self.checkBox_num.isChecked()
        bool_lower_letter = self.checkBox_lower_letter.isChecked()
        bool_upper_letter = self.checkBox_upper_letter.isChecked()
        bool_symbols = self.checkBox_symbols.isChecked()
        # 如果没有勾选项
        if not (bool_num or bool_lower_letter or bool_upper_letter or bool_symbols):
            QMessageBox().critical(self, MainWindow.WARNING, "可选项至少勾选一个", QMessageBox.Ok)
            return None
        else:
            return bool_num, bool_lower_letter, bool_upper_letter, bool_symbols

    def button_write_dict_clicked(self):
        """
        生成字典 按钮的消息响应函数\n
        :return: None
        """
        try:
            booleans, digits = self.get_internal_dict_info()
            file_path = self.get_file_path(self.lineEdit_save_dict, self.button_save_dict_clicked, MainWindow.SAVE_DICT_PATH)
        except TypeError:
            return None
        # 开始生成字典
        while True:
            flag = write_dict(
                path=file_path, digits1=digits[0], digits2=digits[1],
                num=booleans[0], lower_letters=booleans[1], upper_letters=booleans[2], symbols=booleans[3],
                process_num=None
            )
            # 如果生成成功
            if flag:
                print(QMessageBox().information(self, MainWindow.INFORMATION, "生成成功", QMessageBox.Ok))
                break
            # 如果生成失败
            else:
                result = QMessageBox().critical(self, MainWindow.CRITICAL, "生成失败", QMessageBox.Retry | QMessageBox.Cancel)
                print(result)
                # 如果取消则跳出循环，否则无限重试永远在循环里
                if result == QMessageBox.Cancel:
                    break

    def button_save_dict_clicked(self) -> str:
        """
        选择字典保存路径按钮的消息响应函数\n
        :return: str 字典文件的保存路径
        """
        file_path = QFileDialog().getSaveFileName(
                parent=self, caption=MainWindow.SAVE_DICT_PATH,
                filter=MainWindow.FILE_FILTER
        )
        print(file_path[0])
        self.lineEdit_save_dict.setText(file_path[0])
        return file_path[0]

    def change_dict(self):
        """
        根据单选框状态将两种字典enable或disable\n
        :return: None
        """
        # 如果使用内置字典
        if self.select_dict.checkedId() == MainWindow.USE_INTERNAL_DICT:
            self.groupBox_external_dict.setDisabled(True)
            self.groupBox_internal_dict.setEnabled(True)
        # 如果使用外置字典
        elif self.select_dict.checkedId() == MainWindow.USE_EXTERNAL_DICT:
            self.groupBox_external_dict.setEnabled(True)
            self.groupBox_internal_dict.setDisabled(True)

    def button_select_dict_clicked(self) -> str:
        """
        选择外部字典按钮的消息响应函数\n
        :return: str 外置字典的字符串路径
        """
        file_path = QFileDialog().getOpenFileName(
                parent=self, caption=MainWindow.SELECT_DICT_FILE,
                filter=MainWindow.FILE_FILTER
        )
        print(file_path[0])
        self.lineEdit_dict_path.setText(file_path[0])
        return file_path[0]

    def select_zip_file(self) -> str:
        """
        选择压缩文件路径按钮的消息响应函数\n
        :return: str 压缩文件路径字符串
        """
        file_path = QFileDialog().getOpenFileName(
            parent=self, caption=MainWindow.SELECT_ZIP_FILE,
            filter=MainWindow.ZIP_FILE
        )
        print(file_path[0])
        self.lineEdit_file_path.setText(file_path[0])
        return file_path[0]

    def select_unzip_dir(self) -> str:
        """
        选择解压路径按钮的消息响应函数\n
        :return: str 解压路径字符串
        """
        dir_path = QFileDialog.getExistingDirectory(
            parent=self, caption=MainWindow.SELECT_EXTRACT_DIR
        )
        print(dir_path)
        self.lineEdit_extract_path.setText(dir_path)
        return dir_path

    def get_internal_dict_info(self):
        """
        获取密码选项等信息，任何一项信息不全均返回None\n
        :return: 如果信息是全的，返回四个复选框是否选中以及两个位数；如果信息不全，返回None
        """
        # 获取位数
        digits = self.get_digit()
        if digits is None:
            return None
        # 获取四个bool
        booleans = self.get_dict_bool()
        if booleans is None:
            return None
        return booleans, digits

    def button_crack_clicked(self):
        """
        开始破解 按钮的消息响应函数\n
        :return: str 密码字符串
        """
        try:
            # 如果使用内置字典
            if self.select_dict.checkedId() == MainWindow.USE_INTERNAL_DICT:
                booleans, digits = self.get_internal_dict_info()
                zip_file_path = self.get_file_path(self.lineEdit_file_path, self.select_zip_file, MainWindow.SELECT_ZIP_FILE)
                extract_path = self.get_file_path(self.lineEdit_extract_path, self.select_unzip_dir, MainWindow.SELECT_EXTRACT_DIR)
                passwords = generate_all_passwords(booleans, digits)
            # 如果使用外置字典
            elif self.select_dict.checkedId() == MainWindow.USE_EXTERNAL_DICT:
                dict_file_path = self.get_file_path(self.lineEdit_dict_path, self.button_select_dict_clicked, MainWindow.SELECT_DICT_FILE)
                zip_file_path = self.get_file_path(self.lineEdit_file_path, self.select_zip_file, MainWindow.SELECT_ZIP_FILE)
                extract_path = self.get_file_path(self.lineEdit_extract_path, self.select_unzip_dir, MainWindow.SELECT_EXTRACT_DIR)
                passwords = read_big_dict(dict_file_path)
        # 获得path时出现问题
        except TypeError:
            return None
        # 读取外部字典时没找到文件
        except FileNotFoundError:
            QMessageBox().critical(self, MainWindow.CRITICAL, MainWindow.NOT_FOUND_FILE)
            return None
        try:
            password = traverse_dict(passwords, zip_file_path, extract_path, None)
        except FileNotFoundError:
            QMessageBox().critical(self, MainWindow.CRITICAL, MainWindow.NOT_FOUND_FILE)
        except AssertionError:
            QMessageBox().warning(self, MainWindow.WARNING, MainWindow.UNSUPPORTED_FILE)
        else:
            # 如果找到了密码
            if password is not None:
                self.lineEdit_password.setText(password)
                QMessageBox().information(self, MainWindow.INFORMATION, MainWindow.FOUND_PASSWORD)
            # 如果没找到密码
            else:
                QMessageBox().warning(self, MainWindow.WARNING, MainWindow.NOT_FOUND_PASSWORD)


# %% 运行
# if __name__ == "__main__":
app = QApplication(argv)
w = MainWindow()
exit(app.exec())